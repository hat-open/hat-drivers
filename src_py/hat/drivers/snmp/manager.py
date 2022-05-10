import asyncio
import itertools
import logging

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_manager(context: common.Context,
                         remote_addr: udp.Address,
                         version: common.Version = common.Version.V2C
                         ) -> 'Manager':
    """Create manager

    For v1 and v2c, context's name is used as community name.

    """
    manager = Manager()
    manager._context = context
    manager._version = version
    manager._receive_futures = {}
    manager._next_request_id = itertools.count(1)

    manager._endpoint = await udp.create(local_addr=None,
                                         remote_addr=remote_addr)

    manager.async_group.spawn(manager._receive_loop)

    return manager


class Manager(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    async def send(self, req: common.Request) -> common.Response:
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_id)
        req_msg = _req_to_msg(self._version, self._context, request_id, req)
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
                    version, context, request_id, res = _decode_res(msg_bytes)

                    if version != self._version:
                        mlog.warning(('received response with version '
                                      'mismatch (received version %s)'),
                                     version)

                    if context != self._context:
                        mlog.warning(('received response with context '
                                      'mismatch (received context %s)'),
                                     context)

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


def _decode_res(msg_bytes):
    msg = encoder.decode(msg_bytes)

    if isinstance(msg, encoder.v1.Msg):
        if msg.type != encoder.v1.MsgType.GET_RESPONSE:
            raise ValueError('invalid response message type')

        version = common.Version.V1
        context = common.Context(engine_id=None,
                                 name=msg.community)

    elif isinstance(msg, encoder.v2c.Msg):
        if msg.type != encoder.v2c.MsgType.RESPONSE:
            raise ValueError('invalid response message type')

        version = common.Version.V2C
        context = common.Context(engine_id=None,
                                 name=msg.community)

    elif isinstance(msg, encoder.v3.Msg):
        if msg.type != encoder.v3.MsgType.RESPONSE:
            raise ValueError('invalid response message type')

        version = common.Version.V3
        context = msg.context

    else:
        raise ValueError('unsupported message')

    if msg.pdu.error.type == common.ErrorType.NO_ERROR:
        return version, context, msg.pdu.request_id, msg.pdu.data

    else:
        return version, context, msg.pdu.request_id, msg.pdu.error


def _req_to_msg(version, context, request_id, req):
    msg_type = _req_to_msg_type(version, req)
    pdu = _req_to_pdu(version, request_id, req)

    if version == common.Version.V1:
        return encoder.v1.Msg(type=msg_type,
                              community=context.name,
                              pdu=pdu)

    if version == common.Version.V2C:
        return encoder.v2c.Msg(type=msg_type,
                               community=context.name,
                               pdu=pdu)

    if version == common.Version.V3:
        return encoder.v3.Msg(type=msg_type,
                              id=request_id,
                              reportable=False,
                              context=context,
                              pdu=pdu)

    raise ValueError('unsupported version')


def _req_to_msg_type(version, req):
    if version == common.Version.V1:
        if isinstance(req, common.GetDataReq):
            return encoder.v1.MsgType.GET_REQUEST

        elif isinstance(req, common.GetNextDataReq):
            return encoder.v1.MsgType.GET_NEXT_REQUEST

        elif isinstance(req, common.SetDataReq):
            return encoder.v1.MsgType.SET_REQUEST

    elif version in (common.Version.V2C, common.Version.V3):
        if isinstance(req, common.GetDataReq):
            return encoder.v2c.MsgType.GET_REQUEST

        elif isinstance(req, common.GetNextDataReq):
            return encoder.v2c.MsgType.GET_NEXT_REQUEST

        elif isinstance(req, common.GetBulkDataReq):
            return encoder.v2c.MsgType.GET_BULK_REQUEST

        elif isinstance(req, common.SetDataReq):
            return encoder.v1.MsgType.SET_REQUEST

    raise ValueError('unsupported version / request')


def _req_to_pdu(version, request_id, req):
    data = _req_to_data(version, req)

    if isinstance(req, (common.GetDataReq,
                        common.GetNextDataReq,
                        common.SetDataReq)):
        return encoder.v1.BasicPdu(
            request_id=request_id,
            error=common.Error(common.ErrorType.NO_ERROR, 0),
            data=data)

    elif isinstance(req, common.GetBulkDataReq):
        return encoder.v2c.BulkPdu(request_id=request_id,
                                   non_repeaters=0,
                                   max_repetitions=0,
                                   data=data)

    raise ValueError('unsupported request')


def _req_to_data(version, req):
    if isinstance(req, (common.GetDataReq,
                        common.GetNextDataReq,
                        common.GetBulkDataReq)):
        return [_name_to_data(version, name)
                for name in req.names]

    elif isinstance(req, common.SetDataReq):
        return req.data

    raise ValueError('unsupported request')


def _name_to_data(version, name):
    if version == common.Version.V1:
        return common.Data(type=common.DataType.EMPTY,
                           name=name,
                           value=None)

    if version == common.Version.V2C:
        return common.Data(type=common.DataType.UNSPECIFIED,
                           name=name,
                           value=None)

    if version == common.Version.V3:
        return common.Data(type=common.DataType.UNSPECIFIED,
                           name=name,
                           value=None)

    raise ValueError('unsupported version')
