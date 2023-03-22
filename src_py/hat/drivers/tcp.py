"""Asyncio TCP wrapper"""

import asyncio
import contextlib
import enum
import logging
import pathlib
import ssl
import typing

from hat import aio


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


Bytes = typing.Union[bytes, bytearray, memoryview]


class SslProtocol(enum.Enum):
    TLS_CLIENT = ssl.PROTOCOL_TLS_CLIENT
    TLS_SERVER = ssl.PROTOCOL_TLS_SERVER


class Address(typing.NamedTuple):
    host: str
    port: int


class ConnectionInfo(typing.NamedTuple):
    local_addr: Address
    remote_addr: Address


ConnectionCb = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


async def connect(addr: Address,
                  **kwargs
                  ) -> 'Connection':
    """Create TCP connection

    Additional arguments are passed directly to `asyncio.open_connection`.

    """
    reader, writer = await asyncio.open_connection(addr.host, addr.port,
                                                   **kwargs)
    return Connection(reader, writer)


async def listen(connection_cb: ConnectionCb,
                 addr: Address,
                 *,
                 bind_connections: bool = False,
                 **kwargs
                 ) -> 'Server':
    """Create listening server

    If `bind_connections` is ``True``, closing server will close all open
    incoming connections.

    Additional arguments are passed directly to `asyncio.start_server`.

    """
    server = Server()
    server._connection_cb = connection_cb
    server._bind_connections = bind_connections
    server._async_group = aio.Group()

    def on_connection(reader, writer):
        try:
            server.async_group.spawn(server._on_connection, reader, writer)

        except Exception:
            reader.close()

    server._srv = await asyncio.start_server(on_connection,
                                             addr.host, addr.port, **kwargs)
    server._async_group.spawn(aio.call_on_cancel, server._on_close)

    socknames = (socket.getsockname() for socket in server._srv.sockets)
    server._addresses = [Address(*sockname[:2]) for sockname in socknames]

    return server


def create_ssl_ctx(protocol: SslProtocol,
                   verify_cert: bool = False,
                   cert_path: typing.Optional[pathlib.PurePath] = None,
                   key_path: typing.Optional[pathlib.PurePath] = None,
                   ca_path: typing.Optional[pathlib.PurePath] = None,
                   password: typing.Optional[str] = None
                   ) -> ssl.SSLContext:
    ctx = ssl.SSLContext(protocol.value)
    ctx.check_hostname = False

    if verify_cert:
        ctx.verify_mode = ssl.VerifyMode.CERT_REQUIRED
        ctx.load_default_certs(ssl.Purpose.CLIENT_AUTH
                               if protocol == SslProtocol.TLS_SERVER
                               else ssl.Purpose.SERVER_AUTH)
        if ca_path:
            ctx.load_verify_locations(cafile=str(ca_path))

    else:
        ctx.verify_mode = ssl.VerifyMode.CERT_NONE

    if cert_path:
        ctx.load_cert_chain(certfile=str(cert_path),
                            keyfile=str(key_path) if key_path else None,
                            password=password)

    return ctx


class Server(aio.Resource):
    """TCP listening server

    Closing server will cancel all running `connection_cb` coroutines.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def addresses(self) -> typing.List[Address]:
        """Listening addresses"""
        return self._addresses

    async def _on_close(self):
        self._srv.close()
        await self._srv.wait_closed()

    async def _on_connection(self, reader, writer):
        try:
            conn = Connection(reader, writer)

        except Exception:
            reader.close()
            return

        try:
            await aio.call(self._connection_cb, conn)

            if self._bind_connections:
                await conn.wait_closing()

            else:
                conn = None

        except Exception as e:
            mlog.warning('connection callback error: %s', e, exc_info=e)

        finally:
            if conn:
                await aio.uncancellable(conn.async_close())


class Connection(aio.Resource):
    """TCP connection"""

    def __init__(self,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self._reader = reader
        self._writer = writer
        self._read_queue = aio.Queue()
        self._async_group = aio.Group()

        self.async_group.spawn(self._read_loop)

        sockname = writer.get_extra_info('sockname')
        peername = writer.get_extra_info('peername')
        self._info = ConnectionInfo(
            local_addr=Address(sockname[0], sockname[1]),
            remote_addr=Address(peername[0], peername[1]))

        self._ssl_object = writer.get_extra_info('ssl_object')

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> ConnectionInfo:
        """Connection info"""
        return self._info

    @property
    def ssl_object(self) -> typing.Union[ssl.SSLObject, ssl.SSLSocket, None]:
        """SSL Object"""
        return self._ssl_object

    def write(self, data: Bytes):
        """Write data

        See `asyncio.StreamWriter.write`.

        """
        self._writer.write(data)

    async def drain(self):
        """Drain stream writer

        See `asyncio.StreamWriter.drain`.

        """
        await self._writer.drain()

    async def read(self,
                   n: int = -1
                   ) -> Bytes:
        """Read up to `n` bytes

        If EOF is detected and no new bytes are available, `ConnectionError`
        is raised.

        See `asyncio.StreamReader.read`.

        """
        future = asyncio.Future()
        try:
            self._read_queue.put_nowait((future, False, n))
            return await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def readexactly(self,
                          n: int
                          ) -> Bytes:
        """Read exactly `n` bytes

        If exact number of bytes could not be read, `ConnectionError` is
        raised.

        See `asyncio.StreamReader.readexactly`.

        """
        future = asyncio.Future()
        try:
            self._read_queue.put_nowait((future, True, n))
            return await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def reset_input_buffer(self) -> int:
        """Reset input buffer

        Returns number of bytes cleared from buffer.

        """
        future = asyncio.Future()
        try:
            self._read_queue.put_nowait((future, False, None))
            return await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _read_loop(self):
        future = None
        buffer = bytearray()
        try:
            while True:
                future, is_exact, n = await self._read_queue.get()

                while not future.done():
                    if n is None:

                        # HACK read until asyncio.StreamReader internal buffer
                        #      empty
                        if hasattr(self._reader, '_buffer'):
                            while not future.done() and self._reader._buffer:
                                count = len(self._reader._buffer)
                                data = await self._reader.read(count)
                                buffer.extend(data)

                        if future.done():
                            break

                        future.set_result(len(buffer))
                        buffer = bytearray()
                        break

                    if n >= 0 and len(buffer) >= n:
                        break

                    if n < 0 and is_exact:
                        future.set_exception(
                            ValueError('invalid number of bytes'))
                        break

                    if buffer and not is_exact:
                        break

                    if not self.is_open:
                        return

                    async with self.async_group.create_subgroup() as subgroup:
                        fn = (self._reader.readexactly if is_exact
                              else self._reader.read)
                        count = n - len(buffer) if n > 0 else n
                        result = asyncio.Future()
                        subgroup.spawn(_set_future_with_result, result, fn,
                                       count)

                        await asyncio.wait([result, future],
                                           return_when=asyncio.FIRST_COMPLETED)

                        if not result.done():
                            break

                    data = result.result()
                    if not data:
                        raise EOFError()

                    buffer.extend(data)

                if future.done():
                    continue

                if n > 0:
                    buffer = memoryview(buffer)
                    data, buffer = buffer[:n], bytearray(buffer[n:])
                    future.set_result(data)

                elif n < 0:
                    future.set_result(buffer)
                    buffer = bytearray()

                else:
                    future.set_result(b'')

        except EOFError:
            pass

        except Exception as e:
            mlog.warning("read loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._read_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())
                if self._read_queue.empty():
                    break
                future, _, __ = self._read_queue.get_nowait()

            self._writer.close()
            with contextlib.suppress(Exception):
                await aio.uncancellable(self._writer.wait_closed())


async def _set_future_with_result(future, fn, *args):
    try:
        future.set_result(await fn(*args))

    except Exception as e:
        future.set_exception(e)
