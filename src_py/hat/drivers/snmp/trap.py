import asyncio
import itertools
import logging
import typing

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


InformCb = aio.AsyncCallable[[common.Version, common.Inform, udp.Address],
                             typing.Optional[common.Error]]
"""Inform callback"""


async def create_trap_sender(remote_addr: udp.Address,
                             version: common.Version = common.Version.V2C
                             ) -> 'TrapSender':
    """Create trap sender"""
    sender = TrapSender()
    sender._version = version
    sender._next_request_id = itertools.count(1)
    sender._receive_futures = {}

    sender._endpoint = await udp.create(local_addr=None,
                                        remote_addr=remote_addr)

    sender.async_group.spawn(sender._receive_loop)

    local_addr = sender._endpoint.info.local_addr
    sender._addr = tuple(int(i) for i in local_addr.host.split('.'))

    return sender


async def create_trap_listener(local_addr: udp.Address = udp.Address('0.0.0.0', 162),  # NOQA
                               inform_cb: typing.Optional[InformCb] = None
                               ) -> 'TrapListener':
    """Create trap listener"""
    listener = TrapListener()
    listener._inform_cb = inform_cb
    listener._receive_queue = aio.Queue()

    listener._endpoint = await udp.create(local_addr=local_addr,
                                          remote_addr=None)

    listener.async_group.spawn(listener._receive_loop)

    return listener


class TrapSender(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    def send_trap(self, trap: common.Trap):
        """Send trap"""
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_id)
        msg = _encode_trap_req(self._version, self._addr, request_id, trap)
        msg_bytes = encoder.encode(msg)

        self._endpoint.send(msg_bytes)

    async def send_inform(self,
                          inform: common.Inform
                          ) -> typing.Optional[common.Error]:
        """Send inform"""
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_id)
        req_msg = _encode_inform_req(self._version, request_id, inform)
        req_msg_bytes = encoder.encode(req_msg)

        future = asyncio.Future()
        self._receive_futures[request_id] = future
        try:
            self._endpoint.send(req_msg_bytes)
            return await future

        finally:
            del self._receive_futures[request_id]

    async def _receive_loop(self):
        try:
            while True:
                msg_bytes, addr = await self._endpoint.receive()

                # TODO check address

                try:
                    version, request_id, res = _decode_inform_res(msg_bytes)

                    if version != self._version:
                        mlog.warning(('received response with version '
                                      'mismatch (received version %s)'),
                                     version)

                    future = self._receive_futures[request_id]
                    if not future.done():
                        future.set_result(res)

                except Exception as e:
                    mlog.warning("dropping message from %s: %s",
                                 addr, e, exc_info=e)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
            for future in self._receive_futures.values():
                if not future.done():
                    future.set_exception(ConnectionError())


class TrapListener(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    async def receive(self) -> typing.Tuple[common.Trap,
                                            udp.Address]:
        """Receive trap"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _receive_loop(self):
        try:
            while True:
                req_msg_bytes, addr = await self._endpoint.receive()

                try:
                    req_msg = encoder.decode(req_msg_bytes)
                    version, request_id, req = _decode_listener_req(req_msg)

                    if isinstance(req, common.Trap):
                        self._receive_queue.put_nowait((req, addr))

                    elif isinstance(req, common.Inform):
                        try:
                            res = await aio.call(self._inform_cb, version, req,
                                                 addr)

                        except Exception as e:
                            mlog.warning("error in inform callback: %s",
                                         e, exc_info=e)
                            res = common.Error(type=common.ErrorType.GEN_ERR,
                                               index=0)

                        res_msg = _encode_inform_res(version, request_id, req,
                                                     res)
                        res_msg_bytes = encoder.encode(res_msg)
                        self._endpoint.send(res_msg_bytes, addr)

                    else:
                        raise ValueError('unsupported request')

                except Exception as e:
                    mlog.warning("error decoding message from %s: %s",
                                 addr, e, exc_info=e)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._receive_queue.close()


def _encode_trap_req(version, addr, request_id, trap):
    if version == common.Version.V1:
        pdu = encoder.v1.TrapPdu(enterprise=trap.oid,
                                 addr=addr,
                                 cause=trap.cause,
                                 timestamp=trap.timestamp,
                                 data=trap.data)
        return encoder.v1.Msg(type=encoder.v1.MsgType.TRAP,
                              community=trap.context.name,
                              pdu=pdu)

    if version == common.Version.V2C:
        error = common.Error(common.ErrorType.NO_ERROR, 0)
        data = [common.Data(type=common.DataType.TIME_TICKS,
                            name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                            value=trap.timestamp),
                common.Data(type=common.DataType.OBJECT_ID,
                            name=(1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0),
                            value=trap.oid),
                *trap.data]
        pdu = encoder.v2c.BasicPdu(request_id=request_id,
                                   error=error,
                                   data=data)
        return encoder.v2c.Msg(type=encoder.v2c.MsgType.SNMPV2_TRAP,
                               community=trap.context.name,
                               pdu=pdu)

    if version == common.Version.V3:
        error = common.Error(common.ErrorType.NO_ERROR, 0)
        data = [common.Data(type=common.DataType.TIME_TICKS,
                            name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                            value=trap.timestamp),
                common.Data(type=common.DataType.OBJECT_ID,
                            name=(1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0),
                            value=trap.oid),
                *trap.data]
        pdu = encoder.v3.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=data)
        return encoder.v3.Msg(type=encoder.v3.MsgType.SNMPV2_TRAP,
                              id=request_id,
                              reportable=False,
                              context=trap.context,
                              pdu=pdu)

    raise ValueError('unsupported version')


def _encode_inform_req(version, request_id, inform):
    if version == common.Version.V2C:
        error = common.Error(common.ErrorType.NO_ERROR, 0)
        pdu = encoder.v2c.BasicPdu(request_id=request_id,
                                   error=error,
                                   data=inform.data)
        return encoder.v2c.Msg(type=encoder.v2c.MsgType.INFORM_REQUEST,
                               community=inform.context.name,
                               pdu=pdu)

    if version == common.Version.V3:
        error = common.Error(common.ErrorType.NO_ERROR, 0)
        pdu = encoder.v3.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=inform.data)
        return encoder.v3.Msg(type=encoder.v3.MsgType.INFORM_REQUEST,
                              id=request_id,
                              reportable=False,
                              context=inform.context,
                              pdu=pdu)

    raise ValueError('unsupported version')


def _encode_inform_res(version, request_id, inform, res):
    error = res if res else common.Error(common.ErrorType.NO_ERROR, 0)

    if version == common.Version.V2C:
        pdu = encoder.v2c.BasicPdu(request_id=request_id,
                                   error=error,
                                   data=inform.data)
        return encoder.v2c.Msg(type=encoder.v2c.MsgType.RESPONSE,
                               community=inform.context.name,
                               pdu=pdu)

    if version == common.Version.V3:
        pdu = encoder.v3.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=inform.data)
        return encoder.v3.Msg(type=encoder.v3.MsgType.RESPONSE,
                              id=request_id,
                              reportable=False,
                              context=inform.context,
                              pdu=pdu)

    raise ValueError('unsupported version')


def _decode_inform_res(msg_bytes):
    msg = encoder.decode(msg_bytes)

    if isinstance(msg, encoder.v2c.Msg):
        version = common.Version.V2C

    elif isinstance(msg, encoder.v3.Msg):
        version = common.Version.V3

    else:
        raise ValueError('unsupported nessage')

    if msg.type != encoder.v2c.MsgType.RESPONSE:
        raise ValueError('invalid response message type')

    if msg.pdu.error.type == common.ErrorType.NO_ERROR:
        return version, msg.pdu.request_id, None

    return version, msg.pdu.request_id, msg.pdu.error


def _decode_listener_req(msg):
    if isinstance(msg, encoder.v1.Msg):
        version = common.Version.V1
        context = common.Context(None, msg.community)

    elif isinstance(msg, encoder.v2c.Msg):
        version = common.Version.V2C
        context = common.Context(None, msg.community)

    elif isinstance(msg, encoder.v3.Msg):
        version = common.Version.V3
        context = msg.context

    else:
        raise ValueError('unsupported message')

    if version == common.Version.V1:
        if msg.type != encoder.v1.MsgType.TRAP:
            raise ValueError('unsupported message type')

        req = common.Trap(context=context,
                          cause=msg.pdu.cause,
                          oid=msg.pdu.enterprise,
                          timestamp=msg.pdu.timestamp,
                          data=msg.pdu.data)

    elif msg.type == encoder.v2c.MsgType.SNMPV2_TRAP:
        if (len(msg.pdu.data) < 2 or
                msg.pdu.data[0].type != common.DataType.TIME_TICKS or
                msg.pdu.data[1].type != common.DataType.OBJECT_ID):
            raise ValueError('invalid trap data')

        # TODO: check data names

        req = common.Trap(context=context,
                          cause=None,
                          oid=msg.pdu.data[1].value,
                          timestamp=msg.pdu.data[0].value,
                          data=msg.pdu.data[2:])

    elif msg.type == encoder.v2c.MsgType.INFORM_REQUEST:
        req = common.Inform(context=context,
                            data=msg.pdu.data)

    else:
        raise ValueError('unsupported message type')

    request_id = None if version == common.Version.V1 else msg.pdu.request_id
    return version, request_id, req
