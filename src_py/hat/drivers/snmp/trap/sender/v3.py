import asyncio
import itertools
import logging
import time

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_v3_trap_sender(remote_addr: udp.Address,
                                context: common.Contex,
                                user: common.UserName,
                                auth_key: common.Key | None = None,
                                priv_key: common.Key | None = None
                                ) -> common.TrapSender:
    """Create v3 trap sender"""
    endpoint = await udp.create(local_addr=None,
                                remote_addr=remote_addr)

    try:
        return V3TrapSender(endpoint=endpoint,
                            context=context,
                            user=user,
                            auth_key=auth_key,
                            priv_key=priv_key)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class V3TrapSender(common.TrapSender):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 context: common.Contex,
                 user: common.UserName,
                 auth_key: common.Key | None,
                 priv_key: common.Key | None):
        self._endpoint = endpoint
        self._context = context
        self._user = user
        self._auth_key = auth_key
        self._priv_key = priv_key
        self._loop = asyncio.get_running_loop()
        self._req_msg_futures = {}
        self._next_request_ids = itertools.count(1)

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
            id=self._context.engine_id,
            boots=0,
            time=round(time.monotonic()))

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

        msg = encoder.v3.Msg(type=encoder.v3.MsgType.SNMPV2_TRAP,
                             id=request_id,
                             reportable=False,
                             auth=self._auth_key is not None,
                             priv=self._priv_key is not None,
                             authorative_engine=authorative_engine,
                             user=self._user,
                             context=self._context,
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
            id=self._context.engine_id,
            boots=0,
            time=round(time.monotonic()))

        error = common.Error(common.ErrorType.NO_ERROR, 0)

        pdu = encoder.v3.BasicPdu(request_id=request_id,
                                  error=error,
                                  data=inform.data)

        req_msg = encoder.v3.Msg(type=encoder.v3.MsgType.SNMPV2_TRAP,
                                 id=request_id,
                                 reportable=False,
                                 auth=self._auth_key is not None,
                                 priv=self._priv_key is not None,
                                 authorative_engine=authorative_engine,
                                 user=self._user,
                                 context=self._context,
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

    def _on_auth_key(self, engine_id, user):

        # TODO check engine_id and user

        return self._auth_key

    def _on_priv_key(self, engine_id, user):

        # TODO check engine_id and user

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

                    if res_msg.type != encoder.v2c.MsgType.RESPONSE:
                        raise Exception('invalid response message type')

                    req_msg, future = self._req_msg_futures[res_msg.request_id]

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

                    if future.done():
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
