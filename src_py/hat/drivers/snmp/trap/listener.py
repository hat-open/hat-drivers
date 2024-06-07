from collections.abc import Collection
import logging
import typing

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder
from hat.drivers.snmp import key


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

V1TrapCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.CommunityName, common.Trap],
    None]
"""V1 trap callback"""

V2CTrapCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.CommunityName, common.Trap],
    None]
"""V2c trap callback"""

V2CInformCb: typing.TypeAlias = aio.AsyncCallable[
    [udp.Address, common.CommunityName, common.Inform],
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
                               users: Collection[common.User] = []
                               ) -> 'TrapListener':
    """Create trap listener"""
    endpoint = await udp.create(local_addr=local_addr,
                                remote_addr=None)

    try:
        return TrapListener(endpoint=endpoint,
                            v1_trap_cb=v1_trap_cb,
                            v2c_trap_cb=v2c_trap_cb,
                            v2c_inform_cb=v2c_inform_cb,
                            v3_trap_cb=v3_trap_cb,
                            v3_inform_cb=v3_inform_cb,
                            users=users)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class TrapListener(aio.Resource):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 v1_trap_cb: V1TrapCb | None,
                 v2c_trap_cb: V2CTrapCb | None,
                 v2c_inform_cb: V2CInformCb | None,
                 v3_trap_cb: V3TrapCb | None,
                 v3_inform_cb: V3InformCb | None,
                 users: Collection[common.User]):
        self._endpoint = endpoint
        self._v1_trap_cb = v1_trap_cb
        self._v2c_trap_cb = v2c_trap_cb
        self._v2c_inform_cb = v2c_inform_cb
        self._v3_trap_cb = v3_trap_cb
        self._v3_inform_cb = v3_inform_cb
        self._users = {}
        self._auth_keys = {}
        self._priv_keys = {}

        for user in users:
            common.validate_user(user)
            self._users[user.name] = user

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    def _on_auth_key(self, engine_id, username):
        user = self._users.get(username)
        if not user or not user.auth_type:
            return

        auth_key = self._auth_keys.get((engine_id, username))
        if auth_key:
            return auth_key

        key_type = key.auth_type_to_key_type(user.auth_type)
        auth_key = key.create_key(key_type=key_type,
                                  password=user.auth_password,
                                  engine_id=engine_id)

        self._auth_keys[(engine_id, username)] = auth_key
        return auth_key

    def _on_priv_key(self, engine_id, username):
        user = self._users.get(username)
        if not user or not user.priv_type:
            return

        priv_key = self._priv_keys.get((engine_id, username))
        if priv_key:
            return priv_key

        key_type = key.priv_type_to_key_type(user.priv_type)
        priv_key = key.create_key(key_type=key_type,
                                  password=user.priv_password,
                                  engine_id=engine_id)

        self._priv_keys[(engine_id, username)] = priv_key
        return priv_key

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
                            trap_cb=self._v1_trap_cb)

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
                            inform_cb=self._v3_inform_cb)

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


async def _process_v1_req_msg(req_msg, addr, trap_cb):
    if req_msg.type == encoder.v1.MsgType.TRAP:
        return await _process_v1_trap(req_msg, addr, trap_cb)

    raise Exception('invalid request message type')


async def _process_v2c_req_msg(req_msg, addr, trap_cb, inform_cb):
    if req_msg.type == encoder.v2c.MsgType.SNMPV2_TRAP:
        return await _process_v2c_trap(req_msg, addr, trap_cb)

    if req_msg.type == encoder.v2c.MsgType.INFORM_REQUEST:
        return await _process_v2c_inform(req_msg, addr, inform_cb)

    raise Exception('invalid request message type')


async def _process_v3_req_msg(req_msg, addr, trap_cb, inform_cb):
    if req_msg.type == encoder.v3.MsgType.SNMPV2_TRAP:
        return await _process_v3_trap(req_msg, addr, trap_cb)

    if req_msg.type == encoder.v3.MsgType.INFORM_REQUEST:
        return await _process_v3_inform(req_msg, addr, inform_cb)

    raise Exception('invalid request message type')


async def _process_v1_trap(req_msg, addr, trap_cb):
    if not trap_cb:
        raise Exception('not accepting V1 trap')

    req = common.Trap(cause=req_msg.pdu.cause,
                      oid=req_msg.pdu.enterprise,
                      timestamp=req_msg.pdu.timestamp,
                      data=req_msg.pdu.data)

    await aio.call(trap_cb, addr, req_msg.community, req)


async def _process_v2c_trap(req_msg, addr, trap_cb):
    if not trap_cb:
        raise Exception('not accepting V2C trap')

    if (len(req_msg.pdu.data) < 2 or
            not isinstance(req_msg.pdu.data[0], common.TimeTicksData) or
            not isinstance(req_msg.pdu.data[1], common.ObjectIdData)):
        raise Exception('invalid trap data')

    # TODO: check data names

    req = common.Trap(cause=None,
                      oid=req_msg.pdu.data[1].value,
                      timestamp=req_msg.pdu.data[0].value,
                      data=req_msg.pdu.data[2:])

    await aio.call(trap_cb, addr, req_msg.community, req)


async def _process_v2c_inform(req_msg, addr, inform_cb):
    if not inform_cb:
        raise Exception('not accepting V2C inform')

    req = common.Inform(data=req_msg.pdu.data)

    error = await aio.call(inform_cb, addr, req_msg.community, req)

    if not error:
        error = common.Error(common.ErrorType.NO_ERROR, 0)

    res_pdu = encoder.v2c.BasicPdu(request_id=req_msg.pdu.request_id,
                                   error=error,
                                   data=req.data)

    res_msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.RESPONSE,
                              community=req_msg.community,
                              pdu=res_pdu)

    return res_msg


async def _process_v3_trap(req_msg, addr, trap_cb):
    if not trap_cb:
        raise Exception('not accepting V3 trap')

    # TODO check user

    if (len(req_msg.pdu.data) < 2 or
            not isinstance(req_msg.pdu.data[0], common.TimeTicksData) or
            not isinstance(req_msg.pdu.data[1], common.ObjectIdData)):
        raise Exception('invalid trap data')

    # TODO: check data names

    req = common.Trap(cause=None,
                      oid=req_msg.pdu.data[1].value,
                      timestamp=req_msg.pdu.data[0].value,
                      data=req_msg.pdu.data[2:])

    await aio.call(trap_cb, addr, req_msg.user, req_msg.context, req)


async def _process_v3_inform(req_msg, addr, inform_cb):
    if not inform_cb:
        raise Exception('not accepting V3 inform')

    # TODO check user

    req = common.Inform(data=req_msg.pdu.data)

    error = await aio.call(inform_cb, addr, req_msg.user, req_msg.context, req)

    if not error:
        error = common.Error(common.ErrorType.NO_ERROR, 0)

    res_pdu = encoder.v3.BasicPdu(request_id=req_msg.pdu.request_id,
                                  error=error,
                                  data=req.data)

    # TODO can we reuser req_msg id for res_msg id?

    res_msg = encoder.v3.Msg(type=encoder.v3.MsgType.RESPONSE,
                             id=req_msg.id,
                             reportable=False,
                             auth=req_msg.auth,
                             priv=req_msg.priv,
                             authorative_engine=req_msg.authorative_engine,
                             user=req_msg.user,
                             context=req_msg.context,
                             pdu=res_pdu)

    return res_msg
