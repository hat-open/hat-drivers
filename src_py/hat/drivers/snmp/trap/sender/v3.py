import asyncio
import itertools
import logging
import time

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp import key
from hat.drivers.snmp.trap.sender import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

_default_user = common.User(name='public',
                            auth_type=None,
                            auth_password=None,
                            priv_type=None,
                            priv_password=None)


async def create_v3_trap_sender(remote_addr: udp.Address,
                                authoritative_engine_id: common.EngineId,
                                context: common.Context | None = None,
                                user: common.User = _default_user
                                ) -> common.TrapSender:
    """Create v3 trap sender"""
    endpoint = await udp.create(local_addr=None,
                                remote_addr=remote_addr)

    try:
        return V3TrapSender(endpoint=endpoint,
                            authoritative_engine_id=authoritative_engine_id,
                            context=context,
                            user=user)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class V3TrapSender(common.TrapSender):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 authoritative_engine_id: common.EngineId,
                 context: common.Context | None,
                 user: common.User):
        self._endpoint = endpoint
        self._authoritative_engine_id = authoritative_engine_id
        self._context = context
        self._user = user
        self._loop = asyncio.get_running_loop()
        self._req_msg_futures = {}
        self._next_request_ids = itertools.count(1)
        self._auth_key = None
        self._priv_key = None

        common.validate_user(user)

        if user.auth_type:
            key_type = key.auth_type_to_key_type(user.auth_type)
            self._auth_key = key.create_key(key_type=key_type,
                                            password=user.auth_password,
                                            engine_id=authoritative_engine_id)

        if user.priv_type:
            key_type = key.priv_type_to_key_type(user.priv_type)
            self._priv_key = key.create_key(key_type=key_type,
                                            password=user.priv_password,
                                            engine_id=authoritative_engine_id)

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    def send_trap(self, trap: common.Trap):
        """Send trap"""
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_ids)

        authorative_engine = encoder.v3.AuthorativeEngine(
            id=self._authoritative_engine_id,
            boots=0,
            time=round(time.monotonic()))

        context = (self._context or
                   common.Context(id=self.authoritative_engine_id,
                                  name=''))

        error = common.Error(common.ErrorType.NO_ERROR, 0)
        data = [common.TimeTicksData(name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                                     value=trap.timestamp),
                common.ObjectIdData(name=(1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0),
                                    value=trap.oid),
                *trap.data]

        pdu = encoder.v3.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=data)

        msg = encoder.v3.Msg(type=encoder.v3.MsgType.SNMPV2_TRAP,
                             id=request_id,
                             reportable=False,
                             auth=self._auth_key is not None,
                             priv=self._priv_key is not None,
                             authorative_engine=authorative_engine,
                             user=self._user.name,
                             context=context,
                             pdu=pdu)
        msg_bytes = encoder.encode(msg=msg,
                                   auth_key=self._auth_key,
                                   priv_key=self._priv_key)

        self._endpoint.send(msg_bytes)

    async def send_inform(self,
                          inform: common.Inform
                          ) -> common.Error | None:
        """Send inform"""
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_ids)

        authorative_engine = encoder.v3.AuthorativeEngine(
            id=self._authoritative_engine_id,
            boots=0,
            time=round(time.monotonic()))

        context = (self._context or
                   common.Context(id=self.authoritative_engine_id,
                                  name=''))

        error = common.Error(common.ErrorType.NO_ERROR, 0)

        pdu = encoder.v3.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=inform.data)

        req_msg = encoder.v3.Msg(type=encoder.v3.MsgType.INFORM_REQUEST,
                                 id=request_id,
                                 reportable=False,
                                 auth=self._auth_key is not None,
                                 priv=self._priv_key is not None,
                                 authorative_engine=authorative_engine,
                                 user=self._user.name,
                                 context=context,
                                 pdu=pdu)
        req_msg_bytes = encoder.encode(msg=req_msg,
                                       auth_key=self._auth_key,
                                       priv_key=self._priv_key)

        future = self._loop.create_future()
        self._req_msg_futures[request_id] = req_msg, future
        try:
            self._endpoint.send(req_msg_bytes)
            return await future

        finally:
            del self._req_msg_futures[request_id]

    def _on_auth_key(self, engine_id, username):
        if (engine_id != self._authoritative_engine_id or
                username != self._user.name):
            return

        return self._auth_key

    def _on_priv_key(self, engine_id, username):
        if (engine_id != self._authoritative_engine_id or
                username != self._user.name):
            return

        return self._priv_key

    async def _receive_loop(self):
        try:
            while True:
                res_msg_bytes, addr = await self._endpoint.receive()

                # TODO check address

                try:
                    res_msg = encoder.decode(msg_bytes=res_msg_bytes,
                                             auth_key_cb=self._on_auth_key,
                                             priv_key_cb=self._on_priv_key)

                    if not isinstance(res_msg, encoder.v3.Msg):
                        raise Exception('invalid version')

                    if res_msg.type != encoder.v3.MsgType.RESPONSE:
                        raise Exception('invalid response message type')

                    req_msg, future = self._req_msg_futures[res_msg.id]

                    if res_msg.auth != req_msg.auth:
                        raise Exception('invalid auth flag')

                    if res_msg.priv != req_msg.priv:
                        raise Exception('invalid priv flag')

                    if res_msg.context != req_msg.context:
                        raise Exception('invalid context')

                    # TODO check authorative engine and user

                    res = (
                        None
                        if res_msg.pdu.error.type == common.ErrorType.NO_ERROR
                        else res_msg.pdu.error)

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

            for _, future in self._req_msg_futures.values():
                if not future.done():
                    future.set_exception(ConnectionError())
