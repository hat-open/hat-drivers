from collections.abc import Collection
import logging
import time
import typing

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder
from hat.drivers.snmp import key


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


V1RequestCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.CommunityName, common.Request],
    common.Response]

V2CRequestCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.CommunityName, common.Request],
    common.Response]

V3RequestCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.UserName, common.Context, common.Request],
    common.Response]


async def create_agent(local_addr: udp.Address = udp.Address('0.0.0.0', 161),
                       v1_request_cb: V1RequestCb | None = None,
                       v2c_request_cb: V2CRequestCb | None = None,
                       v3_request_cb: V3RequestCb | None = None,
                       authoritative_engine_id: common.EngineId | None = None,
                       users: Collection[common.User] = []
                       ) -> 'Agent':
    """Create agent"""
    endpoint = await udp.create(local_addr=local_addr,
                                remote_addr=None)

    try:
        return Agent(endpoint=endpoint,
                     v1_request_cb=v1_request_cb,
                     v2c_request_cb=v2c_request_cb,
                     v3_request_cb=v3_request_cb,
                     authoritative_engine_id=authoritative_engine_id,
                     users=users)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class Agent(aio.Resource):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 v1_request_cb: V1RequestCb | None,
                 v2c_request_cb: V2CRequestCb | None,
                 v3_request_cb: V3RequestCb | None,
                 authoritative_engine_id: common.EngineId | None,
                 users: Collection[common.User] = []):
        self._endpoint = endpoint
        self._v1_request_cb = v1_request_cb
        self._v2c_request_cb = v2c_request_cb
        self._v3_request_cb = v3_request_cb
        self._auth_engine_id = authoritative_engine_id
        self._auth_keys = {}
        self._priv_keys = {}

        for user in users:
            common.validate_user(user)

            if user.auth_type:
                key_type = key.auth_type_to_key_type(user.auth_type)
                self._auth_keys[user.name] = key.create_key(
                    key_type=key_type,
                    password=user.auth_password,
                    engine_id=authoritative_engine_id)

            else:
                self._auth_keys[user.name] = None

            if user.priv_type:
                key_type = key.priv_type_to_key_type(user.priv_type)
                self._priv_keys[user.name] = key.create_key(
                    key_type=key_type,
                    password=user.priv_password,
                    engine_id=authoritative_engine_id)

            else:
                self._priv_keys[user.name] = None

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    def _on_auth_key(self, engine_id, username):
        if engine_id != self._auth_engine_id:
            raise Exception('invalid authoritative engine id')

        if username not in self._auth_keys:
            raise Exception('invalid user')
        return self._auth_keys[username]

    def _on_priv_key(self, engine_id, username):
        if engine_id != self._auth_engine_id:
            raise Exception('invalid authoritative engine id')

        if username not in self._priv_keys:
            raise Exception('invalid user')
        return self._priv_keys[username]

    async def _receive_loop(self):
        try:
            while True:
                req_msg_bytes, addr = await self._endpoint.receive()

                try:
                    req_msg = encoder.decode(msg_bytes=req_msg_bytes,
                                             auth_key_cb=self._on_auth_key,
                                             priv_key_cb=self._on_priv_key)

                except Exception as e:
                    mlog.warning("error decoding message from %s: %s",
                                 addr, e, exc_info=e)
                    continue

                try:
                    if isinstance(req_msg, encoder.v1.Msg):
                        res_msg = await _process_v1_req_msg(
                            req_msg=req_msg,
                            addr=addr,
                            request_cb=self._v1_request_cb)

                    elif isinstance(req_msg, encoder.v2c.Msg):
                        res_msg = await _process_v2c_req_msg(
                            req_msg=req_msg,
                            addr=addr,
                            request_cb=self._v2c_request_cb)

                    elif isinstance(req_msg, encoder.v3.Msg):
                        res_msg = await _process_v3_req_msg(
                            req_msg=req_msg,
                            addr=addr,
                            request_cb=self._v3_request_cb,
                            authoritative_engine_id=self._auth_engine_id,
                            auth_keys=self._auth_keys,
                            priv_keys=self._priv_keys)

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
                            self._on_auth_key(res_msg.authorative_engine.id,
                                              res_msg.user)
                            if res_msg.auth else None)
                        priv_key = (
                            self._on_priv_key(res_msg.authorative_engine.id,
                                              res_msg.user)
                            if res_msg.priv else None)

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


async def _process_v1_req_msg(req_msg, addr, request_cb):
    if not request_cb:
        raise Exception('not accepting V1')

    if req_msg.type == encoder.v1.MsgType.GET_REQUEST:
        req = common.GetDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v1.MsgType.GET_NEXT_REQUEST:
        req = common.GetNextDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v1.MsgType.SET_REQUEST:
        req = common.SetDataReq(data=req_msg.pdu.data)

    else:
        raise Exception('invalid request message type')

    try:
        res = await aio.call(request_cb, addr, req_msg.community, req)

        if isinstance(res, common.Error):
            if res.type.value > common.ErrorType.GEN_ERR.value:
                raise Exception('invalid error type')

            res_error = res
            res_data = []

        else:
            res_error = common.Error(common.ErrorType.NO_ERROR, 0)
            res_data = res

    except Exception as e:
        mlog.warning("error processing request: %s", e, exc_info=e)

        res_error = common.Error(common.ErrorType.GEN_ERR, 0)
        res_data = []

    res_pdu = encoder.v1.BasicPdu(
        request_id=req_msg.pdu.request_id,
        error=res_error,
        data=res_data)

    res_msg = encoder.v1.Msg(
        type=encoder.v1.MsgType.GET_RESPONSE,
        community=req_msg.community,
        pdu=res_pdu)

    return res_msg


async def _process_v2c_req_msg(req_msg, addr, request_cb):
    if not request_cb:
        raise Exception('not accepting V2C')

    if req_msg.type == encoder.v2c.MsgType.GET_REQUEST:
        req = common.GetDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v2c.MsgType.GET_NEXT_REQUEST:
        req = common.GetNextDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v2c.MsgType.GET_BULK_REQUEST:
        req = common.GetBulkDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v2c.MsgType.SET_REQUEST:
        req = common.SetDataReq(data=req_msg.pdu.data)

    else:
        raise Exception('invalid request message type')

    try:
        res = await aio.call(request_cb, addr, req_msg.community, req)

        if isinstance(res, common.Error):
            res_error = res
            res_data = []

        else:
            res_error = common.Error(common.ErrorType.NO_ERROR, 0)
            res_data = res

    except Exception as e:
        mlog.warning("error processing request: %s", e, exc_info=e)

        res_error = common.Error(common.ErrorType.GEN_ERR, 0)
        res_data = []

    res_pdu = encoder.v2c.BasicPdu(
        request_id=req_msg.pdu.request_id,
        error=res_error,
        data=res_data)

    res_msg = encoder.v2c.Msg(
        type=encoder.v2c.MsgType.RESPONSE,
        community=req_msg.community,
        pdu=res_pdu)

    return res_msg


async def _process_v3_req_msg(req_msg, addr, request_cb,
                              authoritative_engine_id, auth_keys, priv_keys):
    if not request_cb or authoritative_engine_id is None:
        raise Exception('not accepting V3')

    if req_msg.type == encoder.v3.MsgType.GET_REQUEST:
        req = common.GetDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v3.MsgType.GET_NEXT_REQUEST:
        req = common.GetNextDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v3.MsgType.GET_BULK_REQUEST:
        req = common.GetBulkDataReq(names=[i.name for i in req_msg.pdu.data])

    elif req_msg.type == encoder.v3.MsgType.SET_REQUEST:
        req = common.SetDataReq(data=req_msg.pdu.data)

    else:
        raise Exception('invalid request message type')

    if req_msg.authorative_engine.id != authoritative_engine_id:
        if req_msg.reportable:

            # TODO report data and conditions for sending reports

            authorative_engine = encoder.v3.AuthorativeEngine(
                id=authoritative_engine_id,
                boots=0,
                time=round(time.monotonic()))

            res_pdu = encoder.v3.BasicPdu(
                request_id=req_msg.pdu.request_id,
                error=common.Error(common.ErrorType.NO_ERROR, 0),
                data=[])

            res_msg = encoder.v3.Msg(
                type=encoder.v3.MsgType.REPORT,
                id=req_msg.id,
                reportable=False,
                auth=False,
                priv=False,
                authorative_engine=authorative_engine,
                user='',
                context=req_msg.context,
                pdu=res_pdu)

            return res_msg

        raise Exception('invalid authoritative engine id')

    # TODO check authoritative engine boot and time

    if req_msg.user not in auth_keys or req_msg.user not in priv_keys:
        raise Exception('invalid user')

    if auth_keys[req_msg.user] is not None and not req_msg.auth:
        raise Exception('invalid auth flag')

    if priv_keys[req_msg.user] is not None and not req_msg.priv:
        raise Exception('invalid priv flag')

    try:
        res = await aio.call(request_cb, addr, req_msg.user, req_msg.context,
                             req)

        if isinstance(res, common.Error):
            res_error = res
            res_data = []

        else:
            res_error = common.Error(common.ErrorType.NO_ERROR, 0)
            res_data = res

    except Exception as e:
        mlog.warning("error processing request: %s", e, exc_info=e)

        res_error = common.Error(common.ErrorType.GEN_ERR, 0)
        res_data = []

    authorative_engine = encoder.v3.AuthorativeEngine(
        id=req_msg.authorative_engine.id,
        boots=0,
        time=round(time.monotonic()))

    res_pdu = encoder.v3.BasicPdu(
        request_id=req_msg.pdu.request_id,
        error=res_error,
        data=res_data)

    # TODO can we reuse request id for res msg id

    res_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.RESPONSE,
        id=req_msg.id,
        reportable=False,
        auth=req_msg.auth,
        priv=req_msg.priv,
        authorative_engine=authorative_engine,
        user=req_msg.user,
        context=req_msg.context,
        pdu=res_pdu)

    return res_msg
