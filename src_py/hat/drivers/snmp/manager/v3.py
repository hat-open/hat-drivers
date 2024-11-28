import asyncio
import itertools
import logging
import time

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp import key
from hat.drivers.snmp.manager import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

_default_user = common.User(name='public',
                            auth_type=None,
                            auth_password=None,
                            priv_type=None,
                            priv_password=None)


async def create_v3_manager(remote_addr: udp.Address,
                            context: common.Context | None = None,
                            user: common.User = _default_user
                            ) -> common.Manager:
    """Create v3 manager"""
    endpoint = await udp.create(local_addr=None,
                                remote_addr=remote_addr)

    try:
        manager = V3Manager(endpoint=endpoint,
                            context=context,
                            user=user)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise

    try:
        await manager.sync()

    except BaseException:
        await aio.uncancellable(manager.async_close())
        raise

    return manager


class V3Manager(common.Manager):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 context: common.Context | None,
                 user: common.User):
        self._endpoint = endpoint
        self._context = context
        self._user = user
        self._loop = asyncio.get_running_loop()
        self._req_msg_futures = {}
        self._next_request_ids = itertools.count(1)
        self._authorative_engine = None
        self._authorative_engine_set_time = time.monotonic()
        self._auth_key = None
        self._priv_key = None

        common.validate_user(user)

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    async def sync(self):
        req = common.GetDataReq(names=[])
        authorative_engine = encoder.v3.AuthorativeEngine(id='',
                                                          boots=0,
                                                          time=0)
        context = common.Context(engine_id=b'',
                                 name='')

        await self._send(req=req,
                         authorative_engine=authorative_engine,
                         context=context,
                         username='',
                         auth_key=None,
                         priv_key=None)

    async def send(self, req: common.Request) -> common.Response:
        if self._authorative_engine is None:
            raise Exception('manager not synchronized')

        dt = time.monotonic() - self._authorative_engine_set_time
        authorative_engine = self._authorative_engine._replace(
            time=round(self._authorative_engine.time + dt))

        context = (self._context if self._context is not None
                   else common.Context(engine_id=authorative_engine.id,
                                       name=''))

        return await self._send(req=req,
                                authorative_engine=authorative_engine,
                                context=context,
                                username=self._user.name,
                                auth_key=self._auth_key,
                                priv_key=self._priv_key)

    async def _send(self, req, authorative_engine, context, username, auth_key,
                    priv_key):
        if not self.is_open:
            raise ConnectionError()

        if isinstance(req, common.GetDataReq):
            msg_type = encoder.v3.MsgType.GET_REQUEST

        elif isinstance(req, common.GetNextDataReq):
            msg_type = encoder.v3.MsgType.GET_NEXT_REQUEST

        elif isinstance(req, common.GetBulkDataReq):
            msg_type = encoder.v3.MsgType.GET_BULK_REQUEST

        elif isinstance(req, common.SetDataReq):
            msg_type = encoder.v3.MsgType.SET_REQUEST

        else:
            raise ValueError('unsupported request')

        request_id = next(self._next_request_ids)

        if isinstance(req, common.SetDataReq):
            data = req.data

        else:
            data = [common.UnspecifiedData(name=name) for name in req.names]

        if isinstance(req, common.GetBulkDataReq):
            pdu = encoder.v3.BulkPdu(request_id=request_id,
                                     non_repeaters=0,
                                     max_repetitions=0,
                                     data=data)

        else:
            pdu = encoder.v3.BasicPdu(
                request_id=request_id,
                error=common.Error(common.ErrorType.NO_ERROR, 0),
                data=data)

        req_msg = encoder.v3.Msg(type=msg_type,
                                 id=request_id,
                                 reportable=True,
                                 auth=auth_key is not None,
                                 priv=priv_key is not None,
                                 authorative_engine=authorative_engine,
                                 user=username,
                                 context=context,
                                 pdu=pdu)
        req_msg_bytes = encoder.encode(msg=req_msg,
                                       auth_key=auth_key,
                                       priv_key=priv_key)

        future = self._loop.create_future()
        self._req_msg_futures[request_id] = req_msg, future
        try:
            self._endpoint.send(req_msg_bytes)
            return await future

        finally:
            del self._req_msg_futures[request_id]

    def _on_auth_key(self, engine_id, username):

        # TODO check engine_id and username

        return self._auth_key

    def _on_priv_key(self, engine_id, username):

        # TODO check engine_id and username

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

                    if res_msg.type not in (encoder.v3.MsgType.RESPONSE,
                                            encoder.v3.MsgType.REPORT):
                        raise Exception('invalid response message type')

                    if (self._authorative_engine and
                            self._authorative_engine.id !=
                            res_msg.authorative_engine.id):
                        raise Exception('authorative engine id changed')

                    if self._authorative_engine is None:
                        if self._user.auth_type:
                            key_type = key.auth_type_to_key_type(
                                self._user.auth_type)
                            self._auth_key = key.create_key(
                                key_type=key_type,
                                password=self._user.auth_password,
                                engine_id=res_msg.authorative_engine.id)

                        if self._user.priv_type:
                            key_type = key.priv_type_to_key_type(
                                self._user.priv_type)
                            self._priv_key = key.create_key(
                                key_type=key_type,
                                password=self._user.priv_password,
                                engine_id=res_msg.authorative_engine.id)

                    self._authorative_engine = res_msg.authorative_engine
                    self._authorative_engine_set_time = time.monotonic()

                    req_msg, future = self._req_msg_futures[res_msg.id]

                    if res_msg.auth != req_msg.auth:
                        raise Exception('invalid auth flag')

                    if res_msg.priv != req_msg.priv:
                        raise Exception('invalid priv flag')

                    if (res_msg.type == encoder.v3.MsgType.RESPONSE and
                            res_msg.context != req_msg.context):
                        raise Exception('invalid context')

                    # TODO check user

                    res = (
                        res_msg.pdu.data
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
