import asyncio
import itertools
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import cotp
from hat.drivers import tcp
from hat.drivers.cosp import common
from hat.drivers.cosp import encoder


mlog = logging.getLogger(__name__)

_params_requirements = b'\x00\x02'

_params_version = 2

_ab_spdu = common.Spdu(type=common.SpduType.AB,
                       transport_disconnect=True)

_dn_spdu = common.Spdu(type=common.SpduType.DN)


class ConnectionInfo(typing.NamedTuple):
    local_addr: tcp.Address
    local_tsel: int | None
    local_ssel: int | None
    remote_addr: tcp.Address
    remote_tsel: int | None
    remote_ssel: int | None


ValidateCb: typing.TypeAlias = aio.AsyncCallable[[util.Bytes],
                                                 util.Bytes | None]
"""Validate callback"""

ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


async def connect(addr: tcp.Address,
                  user_data: util.Bytes | None = None,
                  *,
                  local_ssel: int | None = None,
                  remote_ssel: int | None = None,
                  cosp_receive_queue_size: int = 1024,
                  cosp_send_queue_size: int = 1024,
                  **kwargs
                  ) -> 'Connection':
    """Connect to COSP server

    Additional arguments are passed directly to `hat.drivers.cotp.connect`.

    """
    conn = await cotp.connect(addr, **kwargs)

    try:
        cn_spdu = common.Spdu(type=common.SpduType.CN,
                              extended_spdus=False,
                              version_number=_params_version,
                              requirements=_params_requirements,
                              calling_ssel=local_ssel,
                              called_ssel=remote_ssel,
                              user_data=user_data)
        cn_spdu_bytes = encoder.encode(cn_spdu)
        await conn.send(cn_spdu_bytes)

        ac_spdu_bytes = await conn.receive()
        ac_spdu = encoder.decode(memoryview(ac_spdu_bytes))
        _validate_connect_response(cn_spdu, ac_spdu)

        calling_ssel, called_ssel = _get_ssels(cn_spdu, ac_spdu)
        return Connection(conn, cn_spdu, ac_spdu, calling_ssel, called_ssel,
                          cosp_receive_queue_size, cosp_send_queue_size)

    except BaseException:
        await aio.uncancellable(_close_cotp(conn, _ab_spdu))
        raise


async def listen(validate_cb: ValidateCb,
                 connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 102),
                 *,
                 bind_connections: bool = False,
                 cosp_receive_queue_size: int = 1024,
                 cosp_send_queue_size: int = 1024,
                 **kwargs
                 ) -> 'Server':
    """Create COSP listening server

    Additional arguments are passed directly to `hat.drivers.cotp.listen`.

    Args:
        validate_cb: callback function or coroutine called on new
            incomming connection request prior to creating new connection
        connection_cb: new connection callback
        addr: local listening address

    """
    server = Server()
    server._validate_cb = validate_cb
    server._connection_cb = connection_cb
    server._bind_connections = bind_connections
    server._receive_queue_size = cosp_receive_queue_size
    server._send_queue_size = cosp_send_queue_size

    server._srv = await cotp.listen(server._on_connection, addr,
                                    bind_connections=False,
                                    **kwargs)

    return server


class Server(aio.Resource):
    """COSP listening server

    For creating new server see `listen`.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._srv.async_group

    @property
    def addresses(self) -> list[tcp.Address]:
        """Listening addresses"""
        return self._srv.addresses

    async def _on_connection(self, cotp_conn):
        try:
            try:
                cn_spdu_bytes = await cotp_conn.receive()
                cn_spdu = encoder.decode(memoryview(cn_spdu_bytes))
                _validate_connect_request(cn_spdu)

                res_user_data = await aio.call(self._validate_cb,
                                               cn_spdu.user_data)

                ac_spdu = common.Spdu(type=common.SpduType.AC,
                                      extended_spdus=False,
                                      version_number=_params_version,
                                      requirements=_params_requirements,
                                      calling_ssel=cn_spdu.calling_ssel,
                                      called_ssel=cn_spdu.called_ssel,
                                      user_data=res_user_data)
                ac_spdu_bytes = encoder.encode(ac_spdu)
                await cotp_conn.send(ac_spdu_bytes)

                calling_ssel, called_ssel = _get_ssels(cn_spdu, ac_spdu)
                conn = Connection(cotp_conn, cn_spdu, ac_spdu,
                                  called_ssel, calling_ssel,
                                  self._receive_queue_size,
                                  self._send_queue_size)

            except BaseException:
                await aio.uncancellable(_close_cotp(cotp_conn, _ab_spdu))
                raise

            try:
                await aio.call(self._connection_cb, conn)

            except BaseException:
                await aio.uncancellable(conn.async_close())
                raise

        except Exception as e:
            mlog.error("error creating new incomming connection: %s", e,
                       exc_info=e)
            return

        if not self._bind_connections:
            return

        try:
            await conn.wait_closed()

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise


class Connection(aio.Resource):
    """COSP connection

    For creating new connection see `connect` or `listen`.

    """

    def __init__(self,
                 conn: cotp.Connection,
                 cn_spdu: common.Spdu,
                 ac_spdu: common.Spdu,
                 local_ssel: int | None,
                 remote_ssel: int | None,
                 receive_queue_size: int,
                 send_queue_size: int):
        self._conn = conn
        self._conn_req_user_data = cn_spdu.user_data
        self._conn_res_user_data = ac_spdu.user_data
        self._loop = asyncio.get_running_loop()
        self._info = ConnectionInfo(local_ssel=local_ssel,
                                    remote_ssel=remote_ssel,
                                    **conn.info._asdict())
        self._close_spdu = None
        self._receive_queue = aio.Queue(receive_queue_size)
        self._send_queue = aio.Queue(send_queue_size)
        self._async_group = aio.Group()

        self.async_group.spawn(aio.call_on_cancel, self._on_close)
        self.async_group.spawn(self._receive_loop)
        self.async_group.spawn(self._send_loop)
        self.async_group.spawn(aio.call_on_done, conn.wait_closing(),
                               self.close)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> ConnectionInfo:
        """Connection info"""
        return self._info

    @property
    def conn_req_user_data(self) -> util.Bytes:
        """Connect request's user data"""
        return self._conn_req_user_data

    @property
    def conn_res_user_data(self) -> util.Bytes:
        """Connect response's user data"""
        return self._conn_res_user_data

    def close(self, user_data: util.Bytes | None = None):
        """Close connection"""
        self._close(common.Spdu(common.SpduType.FN,
                                transport_disconnect=True,
                                user_data=user_data))

    async def async_close(self, user_data: util.Bytes | None = None):
        """Async close"""
        self.close(user_data)
        await self.wait_closed()

    async def receive(self) -> util.Bytes:
        """Receive data"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send(self, data: util.Bytes):
        """Send data"""
        try:
            await self._send_queue.put((data, None))

        except aio.QueueClosedError:
            raise ConnectionError()

    async def drain(self):
        """Drain output buffer"""
        try:
            future = self._loop.create_future()
            await self._send_queue.put((None, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _on_close(self):
        await _close_cotp(self._conn, self._close_spdu)

    def _close(self, spdu):
        if not self.is_open:
            return

        self._close_spdu = spdu
        self._async_group.close()

    async def _receive_loop(self):
        try:
            data = bytearray()
            while True:
                spdu_bytes = await self._conn.receive()
                spdu = encoder.decode(memoryview(spdu_bytes))

                if spdu.type == common.SpduType.DT:
                    data.extend(spdu.data)

                    if spdu.end is None or spdu.end:
                        await self._receive_queue.put(data)
                        data = bytearray()

                elif spdu.type == common.SpduType.FN:
                    self._close(_dn_spdu)
                    break

                elif spdu.type == common.SpduType.AB:
                    self._close(None)
                    break

                else:
                    self._close(_ab_spdu)
                    break

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._receive_queue.close()

    async def _send_loop(self):
        future = None
        try:
            while True:
                data, future = await self._send_queue.get()

                if data is None:
                    await self._conn.drain()

                else:
                    spdu = common.Spdu(type=common.SpduType.DT,
                                       data=data)
                    spdu_bytes = encoder.encode(spdu)

                    msg = bytes(itertools.chain(common.give_tokens_spdu_bytes,
                                                spdu_bytes))

                    await self._conn.send(msg)

                if future and not future.done():
                    future.set_result(None)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("send loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_result(None)
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()


async def _close_cotp(cotp_conn, spdu):
    try:
        if not cotp_conn.is_open or not spdu:
            return

        spdu_bytes = encoder.encode(spdu)
        await cotp_conn.send(spdu_bytes)
        await cotp_conn.drain()

    except Exception as e:
        mlog.error('close cotp error: %s', e, exc_info=e)

    finally:
        await cotp_conn.async_close()


def _get_ssels(cn_spdu, ac_spdu):
    calling_ssel = (cn_spdu.calling_ssel
                    if cn_spdu.calling_ssel is not None
                    else ac_spdu.calling_ssel)

    called_ssel = (cn_spdu.called_ssel
                   if cn_spdu.called_ssel is not None
                   else ac_spdu.called_ssel)

    return calling_ssel, called_ssel


def _validate_connect_request(cn_spdu):
    if cn_spdu.type != common.SpduType.CN:
        raise Exception("received message is not of type CN")


def _validate_connect_response(cn_spdu, ac_spdu):
    if ac_spdu.type != common.SpduType.AC:
        raise Exception("received message is not of type AC")

    if (cn_spdu.calling_ssel is not None and
            ac_spdu.calling_ssel is not None and
            cn_spdu.calling_ssel != ac_spdu.calling_ssel):
        raise Exception(f"received calling ssel  {ac_spdu.calling_ssel} "
                        f"(expecting {cn_spdu.calling_ssel})")

    if (cn_spdu.called_ssel is not None and
            ac_spdu.called_ssel is not None and
            cn_spdu.called_ssel != ac_spdu.called_ssel):
        raise Exception(f"received calling ssel {ac_spdu.called_ssel} "
                        f"(expecting {cn_spdu.called_ssel})")
