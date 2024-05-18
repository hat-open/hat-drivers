import logging
import typing

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

V1TrapCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.ComunityName, common.Trap],
    None]
"""V1 trap callback"""

V2CTrapCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.ComunityName, common.Trap],
    None]
"""V2c trap callback"""

V2CInformCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.ComunityName, common.Inform],
    common.Error | None]
"""V2c inform callback"""

V3TrapCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.UserName, common.Context, common.Trap],
    None]
"""V3 trap callback"""

V3InformCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.UserName, common.Context, common.Inform],
    common.Error | None]
"""V3 inform callback"""


async def create_trap_listener(local_addr: udp.Address = udp.Address('0.0.0.0', 162),  # NOQA
                               v1_trap_cb: V1TrapCb | None = None,
                               v2c_trap_cb: V2CTrapCb | None = None,
                               v2c_inform_cb: V2CInformCb | None = None,
                               v3_trap_cb: V3TrapCb | None = None,
                               v3_inform_cb: V3InformCb | None = None,
                               auth_key_cb: common.KeyCb | None = None,
                               priv_key_cb: common.KeyCb | None = None
                               ) -> 'TrapListener':
    """Create trap listener"""
    endpoint = await udp.create(local_addr=local_addr,
                                remote_addr=None)

    try:
        return TrapListener(endpoint=endpoint,
                            v1_trap_cb=v1_trap_cb,
                            v1_inform_cb=v1_inform_cb,
                            v2c_trap_cb=v2c_trap_cb,
                            v2c_inform_cb=v2c_inform_cb,
                            v3_trap_cb=v3_trap_cb,
                            v3_inform_cb=v3_inform_cb,
                            auth_key_cb=auth_key_cb,
                            priv_key_cb=priv_key_cb)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class TrapListener(aio.Resource):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 v1_trap_cb: V1TrapCb | None,
                 v1_inform_cb: V1InformCb | None,
                 v2c_trap_cb: V2CTrapCb | None,
                 v2c_inform_cb: V2CInformCb | None,
                 v3_trap_cb: V3TrapCb | None,
                 v3_inform_cb: V3InformCb | None,
                 auth_key_cb: common.KeyCb | None,
                 priv_key_cb: common.KeyCb | None):
        self._endpoint = endpoint
        self._v1_trap_cb = v1_trap_cb
        self._v1_inform_cb = v1_inform_cb
        self._v2c_trap_cb = v2c_trap_cb
        self._v2c_inform_cb = v2c_inform_cb
        self._v3_trap_cb = v3_trap_cb
        self._v3_inform_cb = v3_inform_cb
        self._auth_key_cb = auth_key_cb
        self._priv_key_cb = priv_key_cb

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    async def _receive_loop(self):
        try:
            while True:
                req_msg_bytes, addr = await self._endpoint.receive()

                try:
                    req_msg = encoder.decode(msg_bytes=req_msg_bytes,
                                             auth_key_cb=self._auth_key_cb,
                                             priv_key_cb=self._priv_key_cb)

                except Exception as e:
                    mlog.warning("error decoding message from %s: %s",
                                 addr, e, exc_info=e)
                    continue

                try:
                    if isinstance(req_msg, encoder.v1.Msg):
                        res_msg = await _process_v1_req_msg(
                            req_msg=req_msg,
                            addr=addr,
                            trap_cb=self._v1_trap_cb,
                            inform_cb=self._v1_inform_cb)

                    elif isinstance(req_msg, encoder.v2c.Msg):
                        res_msg = await _process_v2c_req_msg(
                            req_msg=req_msg,
                            addr=addr,
                            trap_cb=self._v2c_trap_cb,
                            inform_cb=self._v2c_inform_cb)

                    elif isinstance(req_msg, encoder.v3.Msg):
                        res_msg = await _process_v3_req_msg(
                            req_msg=req_msg,
                            addr=addr,
                            trap_cb=self._v3_trap_cb,
                            inform_cb=self._v3_inform_cb,
                            auth_key_cb=self._auth_key_cb,
                            priv_key_cb=self._priv_key_cb)

                    else:
                        raise ValueError('unsupported message type')

                except Exception as e:
                    mlog.warning("error processing message from %s: %s",
                                 addr, e, exc_info=e)
                    continue

                if not res_msg:
                    continue

                try:
                    if isinstance(res_msg, encoder.v3.Msg):
                        auth_key = (
                            self._auth_key_cb(res_msg.authorative_engine.id,
                                              res_msg.user)
                            if self._auth_key_cb and res_msg.auth else None)
                        priv_key = (
                            self._priv_key_cb(res_msg.authorative_engine.id,
                                              res_msg.user)
                            if self._priv_key_cb and res_msg.priv else None)

                    else:
                        auth_key = None
                        priv_key = None

                    res_msg_bytes = encoder.encode(msg=res_msg,
                                                   auth_key=auth_key,
                                                   priv_key=priv_key)

                except Exception as e:
                    mlog.warning("error encoding message: %s", e, exc_info=e)
                    continue

                self._endpoint.send(res_msg_bytes, addr)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()


async def _process_v1_req_msg(req_msg, addr, trap_cb, inform_cb):
    raise NotImplementedError()


async def _process_v2c_req_msg(req_msg, addr, trap_cb, inform_cb):
    raise NotImplementedError()


async def _process_v3_req_msg(req_msg, addr, trap_cb, inform_cb, auth_key_cb,
                              priv_key_cb):
    raise NotImplementedError()


# try:
#     req_msg = encoder.decode(req_msg_bytes)
#     version, request_id, req = _decode_listener_req(req_msg)

#     if isinstance(req, common.Trap):
#         self._receive_queue.put_nowait((req, addr))

#     elif isinstance(req, common.Inform):
#         try:
#             res = await aio.call(self._inform_cb, version, req,
#                                  addr)

#         except Exception as e:
#             mlog.warning("error in inform callback: %s",
#                          e, exc_info=e)
#             res = common.Error(type=common.ErrorType.GEN_ERR,
#                                index=0)

#         res_msg = _encode_inform_res(version, request_id, req,
#                                      res)
#         res_msg_bytes = encoder.encode(res_msg)
#         self._endpoint.send(res_msg_bytes, addr)

#     else:
#         raise ValueError('unsupported request')

# except Exception as e:
#     mlog.warning("error decoding message from %s: %s",
#                  addr, e, exc_info=e)


# def _encode_inform_res(version, request_id, inform, res):
#     error = res if res else common.Error(common.ErrorType.NO_ERROR, 0)

#     if version == common.Version.V2C:
#         pdu = encoder.v2c.BasicPdu(request_id=request_id,
#                                    error=error,
#                                    data=inform.data)
#         return encoder.v2c.Msg(type=encoder.v2c.MsgType.RESPONSE,
#                                community=inform.context.name,
#                                pdu=pdu)

#     if version == common.Version.V3:
#         pdu = encoder.v3.BasicPdu(request_id=request_id,
#                                   error=error,
#                                   data=inform.data)
#         return encoder.v3.Msg(type=encoder.v3.MsgType.RESPONSE,
#                               id=request_id,
#                               reportable=False,
#                               context=inform.context,
#                               pdu=pdu)

#     raise ValueError('unsupported version')


# def _decode_listener_req(msg):
#     if isinstance(msg, encoder.v1.Msg):
#         version = common.Version.V1
#         context = common.Context(None, msg.community)

#     elif isinstance(msg, encoder.v2c.Msg):
#         version = common.Version.V2C
#         context = common.Context(None, msg.community)

#     elif isinstance(msg, encoder.v3.Msg):
#         version = common.Version.V3
#         context = msg.context

#     else:
#         raise ValueError('unsupported message')

#     if version == common.Version.V1:
#         if msg.type != encoder.v1.MsgType.TRAP:
#             raise ValueError('unsupported message type')

#         req = common.Trap(context=context,
#                           cause=msg.pdu.cause,
#                           oid=msg.pdu.enterprise,
#                           timestamp=msg.pdu.timestamp,
#                           data=msg.pdu.data)

#     elif msg.type == encoder.v2c.MsgType.SNMPV2_TRAP:
#         if (len(msg.pdu.data) < 2 or
#                 msg.pdu.data[0].type != common.DataType.TIME_TICKS or
#                 msg.pdu.data[1].type != common.DataType.OBJECT_ID):
#             raise ValueError('invalid trap data')

#         # TODO: check data names

#         req = common.Trap(context=context,
#                           cause=None,
#                           oid=msg.pdu.data[1].value,
#                           timestamp=msg.pdu.data[0].value,
#                           data=msg.pdu.data[2:])

#     elif msg.type == encoder.v2c.MsgType.INFORM_REQUEST:
#         req = common.Inform(context=context,
#                             data=msg.pdu.data)

#     else:
#         raise ValueError('unsupported message type')

#     request_id = None if version == common.Version.V1 else msg.pdu.request_id
#     return version, request_id, req
