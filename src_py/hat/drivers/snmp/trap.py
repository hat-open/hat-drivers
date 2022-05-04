import itertools
import logging
import typing

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_trap_sender(remote_addr: udp.Address,
                             version: common.Version = common.Version.V2C
                             ) -> 'TrapSender':
    sender = TrapSender()
    sender._version = version
    sender._next_request_id = itertools.count(1)

    sender._endpoint = await udp.create(local_addr=None,
                                        remote_addr=remote_addr)

    local_addr = sender._endpoint.info.local_addr
    sender._addr = tuple(int(i) for i in local_addr.split('.'))

    return sender


async def create_trap_listener(local_addr: udp.Address = udp.Address('0.0.0.0', 162)  # NOQA
                               ) -> 'TrapListener':
    """Create trap listener"""
    listener = TrapListener()
    listener._receive_queue = aio.Queue()

    listener._endpoint = await udp.create(local_addr=local_addr,
                                          remote_addr=None)

    listener.async_group.spawn(listener._receive_loop)

    return listener


class TrapSender(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    def send(self, trap: common.Trap):
        request_id = next(self._next_request_id)
        msg = _encode_trap(self._version, self._addr, request_id, trap)
        msg_bytes = encoder.encode(msg)

        self._endpoint.send(msg_bytes)


class TrapListener(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    async def receive(self) -> typing.Tuple[common.Trap,
                                            udp.Address]:
        """Receive trap

        For v1 and v2c, context's name is used as community name.

        """
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _receive_loop(self):
        try:
            while True:
                msg_bytes, addr = await self._udp.receive()

                try:
                    msg = encoder.decode(msg_bytes)
                    trap = _decode_trap(msg)
                    self._receive_queue.put_nowait((trap, addr))

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


def _encode_trap(version, addr, request_id, trap):
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
        pdu = encoder.v2.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=data)
        return encoder.v2c.Msg(type=encoder.v2.MsgType.SNMPV2_TRAP,
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


def _decode_trap(msg):
    if isinstance(msg, encoder.v1.Msg):
        if msg.type != encoder.v1.MsgType.TRAP:
            raise ValueError('invalid trap message type')

        context = common.Context(None, msg.community)
        cause = msg.pdu.cause
        oid = msg.pdu.enterprise
        timestamp = msg.pdu.timestamp
        data = msg.pdu.data

    elif isinstance(msg, encoder.v2c.Msg):
        if msg.type != encoder.v2c.MsgType.SNMPV2_TRAP:
            raise ValueError('invalid trap message type')

        if (len(msg.pdu.data) < 2 or
                msg.pdu.data[0].type != common.DataType.TIME_TICKS or
                msg.pdu.data[1].type != common.DataType.OBJECT_ID):
            raise ValueError('invalid trap data')

        # TODO: check data names

        context = common.Context(None, msg.community)
        cause = None
        timestamp = msg.pdu.data[0].value
        oid = msg.pdu.data[1].value
        data = msg.pdu.data[2:]

    elif isinstance(msg, encoder.v3.Msg):
        if msg.type != encoder.v3.MsgType.SNMPV2_TRAP:
            raise ValueError('invalid trap message type')

        if (len(msg.pdu.data) < 2 or
                msg.pdu.data[0].type != common.DataType.TIME_TICKS or
                msg.pdu.data[1].type != common.DataType.OBJECT_ID):
            raise ValueError('invalid trap data')

        # TODO: check data names

        context = msg.context
        cause = None
        timestamp = msg.pdu.data[0].value
        oid = msg.pdu.data[1].value
        data = msg.pdu.data[2:]

    else:
        raise ValueError('unsupported message type')

    return common.Trap(context=context,
                       cause=cause,
                       oid=oid,
                       timestamp=timestamp,
                       data=data)
