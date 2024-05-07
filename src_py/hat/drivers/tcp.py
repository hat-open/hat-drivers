"""Asyncio TCP wrapper"""

import asyncio
import collections
import functools
import logging
import sys
import typing

from hat import aio
from hat import util

from hat.drivers import ssl


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


class Address(typing.NamedTuple):
    host: str
    port: int


class ConnectionInfo(typing.NamedTuple):
    local_addr: Address
    remote_addr: Address


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


async def connect(addr: Address,
                  *,
                  input_buffer_limit: int = 64 * 1024,
                  **kwargs
                  ) -> 'Connection':
    """Create TCP connection

    Argument `addr` specifies remote server listening address.

    Argument `input_buffer_limit` defines number of bytes in input buffer
    that whill temporary pause data receiving. Once number of bytes
    drops bellow `input_buffer_limit`, data receiving is resumed. If this
    argument is ``0``, data receive pausing is disabled.

    Additional arguments are passed directly to `asyncio.create_connection`.

    """
    loop = asyncio.get_running_loop()
    create_transport = functools.partial(Protocol, None, input_buffer_limit)
    _, protocol = await loop.create_connection(create_transport,
                                               addr.host, addr.port,
                                               **kwargs)
    return Connection(protocol)


async def listen(connection_cb: ConnectionCb,
                 addr: Address,
                 *,
                 bind_connections: bool = False,
                 input_buffer_limit: int = 64 * 1024,
                 **kwargs
                 ) -> 'Server':
    """Create listening server

    If `bind_connections` is ``True``, closing server will close all open
    incoming connections.

    Argument `input_buffer_limit` is associated with newly created connections
    (see `connect`).

    Additional arguments are passed directly to `asyncio.create_server`.

    """
    server = Server()
    server._connection_cb = connection_cb
    server._bind_connections = bind_connections
    server._async_group = aio.Group()

    on_connection = functools.partial(server.async_group.spawn,
                                      server._on_connection)
    create_transport = functools.partial(Protocol, on_connection,
                                         input_buffer_limit)

    loop = asyncio.get_running_loop()
    server._srv = await loop.create_server(create_transport, addr.host,
                                           addr.port, **kwargs)

    server.async_group.spawn(aio.call_on_cancel, server._on_close)

    try:
        socknames = (socket.getsockname() for socket in server._srv.sockets)
        server._addresses = [Address(*sockname[:2]) for sockname in socknames]

    except Exception:
        await aio.uncancellable(server.async_close())
        raise

    return server


class Server(aio.Resource):
    """TCP listening server

    Closing server will cancel all running `connection_cb` coroutines.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def addresses(self) -> list[Address]:
        """Listening addresses"""
        return self._addresses

    async def _on_close(self):
        self._srv.close()

        if self._bind_connections or sys.version_info[:2] < (3, 12):
            await self._srv.wait_closed()

    async def _on_connection(self, protocol):
        conn = Connection(protocol)

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

    def __init__(self, protocol: 'Protocol'):
        self._protocol = protocol
        self._async_group = aio.Group()

        self.async_group.spawn(aio.call_on_cancel, protocol.async_close)
        self.async_group.spawn(aio.call_on_done, protocol.wait_closed(),
                               self.close)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> ConnectionInfo:
        """Connection info"""
        return self._protocol.info

    @property
    def ssl_object(self) -> ssl.SSLObject | ssl.SSLSocket | None:
        """SSL Object"""
        return self._protocol.ssl_object

    async def write(self, data: util.Bytes):
        """Write data

        This coroutine will wait until `data` can be added to output buffer.

        """
        if not self.is_open:
            raise ConnectionError()

        await self._protocol.write(data)

    async def drain(self):
        """Drain output buffer"""
        await self._protocol.drain()

    async def read(self, n: int = -1) -> util.Bytes:
        """Read up to `n` bytes

        If EOF is detected and no new bytes are available, `ConnectionError`
        is raised.

        """
        return await self._protocol.read(n)

    async def readexactly(self, n: int) -> util.Bytes:
        """Read exactly `n` bytes

        If exact number of bytes could not be read, `ConnectionError` is
        raised.

        """
        return await self._protocol.readexactly(n)

    def reset_input_buffer(self) -> int:
        """Reset input buffer

        Returns number of bytes cleared from buffer.

        """
        return self._protocol.reset_input_buffer()


class Protocol(asyncio.Protocol):
    """Asyncio protocol implementation"""

    def __init__(self,
                 on_connected: typing.Callable[['Protocol'], None] | None,
                 input_buffer_limit: int):
        self._on_connected = on_connected
        self._input_buffer_limit = input_buffer_limit
        self._loop = asyncio.get_running_loop()
        self._input_buffer = util.BytesBuffer()
        self._transport = None
        self._read_queue = None
        self._write_queue = None
        self._drain_futures = None
        self._closed_futures = None
        self._info = None
        self._ssl_object = None

    @property
    def info(self) -> ConnectionInfo:
        return self._info

    @property
    def ssl_object(self) -> ssl.SSLObject | ssl.SSLSocket | None:
        return self._ssl_object

    def connection_made(self, transport: asyncio.Transport):
        self._transport = transport
        self._read_queue = collections.deque()
        self._closed_futures = collections.deque()

        try:
            sockname = transport.get_extra_info('sockname')
            peername = transport.get_extra_info('peername')
            self._info = ConnectionInfo(
                local_addr=Address(sockname[0], sockname[1]),
                remote_addr=Address(peername[0], peername[1]))
            self._ssl_object = transport.get_extra_info('ssl_object')

            if self._on_connected:
                self._on_connected(self)

        except Exception:
            transport.abort()
            return

    def connection_lost(self, exc: Exception | None):
        self._transport = None
        write_queue, self._write_queue = self._write_queue, None
        drain_futures, self._drain_futures = self._drain_futures, None
        closed_futures, self._closed_futures = self._closed_futures, None

        self.eof_received()

        while write_queue:
            _, future = write_queue.popleft()
            if not future.done():
                future.set_exception(ConnectionError())

        while drain_futures:
            future = drain_futures.popleft()
            if not future.done():
                future.set_result(None)

        while closed_futures:
            future = closed_futures.popleft()
            if not future.done():
                future.set_result(None)

    def pause_writing(self):
        self._write_queue = collections.deque()
        self._drain_futures = collections.deque()

    def resume_writing(self):
        write_queue, self._write_queue = self._write_queue, None
        drain_futures, self._drain_futures = self._drain_futures, None

        while self._write_queue is None and write_queue:
            data, future = write_queue.popleft()
            if future.done():
                continue

            self._transport.write(data)
            future.set_result(None)

        if write_queue:
            write_queue.extend(self._write_queue)
            self._write_queue = write_queue

            drain_futures.extend(self._drain_futures)
            self._drain_futures = drain_futures

            return

        while drain_futures:
            future = drain_futures.popleft()
            if not future.done():
                future.set_result(None)

    def data_received(self, data: util.Bytes):
        self._input_buffer.add(data)
        self._process_input_buffer()

    def eof_received(self):
        while self._read_queue:
            exact, n, future = self._read_queue.popleft()
            if future.done():
                continue

            if exact and n <= len(self._input_buffer):
                future.set_result(self._input_buffer.read(n))

            elif not exact and self._input_buffer:
                future.set_result(self._input_buffer.read(n))

            else:
                future.set_exception(ConnectionError())

        self._read_queue = None

    async def write(self, data: util.Bytes):
        if self._transport is None:
            raise ConnectionError()

        if self._write_queue is None:
            self._transport.write(data)
            return

        future = self._loop.create_future()
        self._write_queue.append((data, future))
        await future

    async def drain(self):
        if self._drain_futures is None:
            return

        future = self._loop.create_future()
        self._drain_futures.append(future)
        await future

    async def read(self, n: int) -> util.Bytes:
        if n == 0:
            return b''

        if self._input_buffer and not self._read_queue:
            data = self._input_buffer.read(n)
            self._process_input_buffer()
            return data

        if self._read_queue is None:
            raise ConnectionError()

        future = self._loop.create_future()
        future.add_done_callback(self._on_read_future_done)
        self._read_queue.append((False, n, future))
        return await future

    async def readexactly(self, n: int) -> util.Bytes:
        if n == 0:
            return b''

        if n <= len(self._input_buffer) and not self._read_queue:
            data = self._input_buffer.read(n)
            self._process_input_buffer()
            return data

        if self._read_queue is None:
            raise ConnectionError()

        future = self._loop.create_future()
        future.add_done_callback(self._on_read_future_done)
        self._read_queue.append((True, n, future))
        self._process_input_buffer()
        return await future

    def reset_input_buffer(self) -> int:
        count = self._input_buffer.clear()
        self._transport.resume_reading()
        return count

    async def async_close(self):
        if self._transport is not None:
            self._transport.close()

        await self.wait_closed()

    async def wait_closed(self):
        if self._closed_futures is None:
            return

        future = self._loop.create_future()
        self._closed_futures.append(future)
        await future

    def _on_read_future_done(self, future):
        if not self._read_queue:
            return

        if not future.cancelled():
            return

        for _ in range(len(self._read_queue)):
            i = self._read_queue.popleft()
            if not i[2].done():
                self._read_queue.append(i)

        self._process_input_buffer()

    def _process_input_buffer(self):
        while self._input_buffer and self._read_queue:
            exact, n, future = self._read_queue.popleft()
            if future.done():
                continue

            if not exact:
                future.set_result(self._input_buffer.read(n))

            elif n <= len(self._input_buffer):
                future.set_result(self._input_buffer.read(n))

            else:
                self._read_queue.appendleft((exact, n, future))
                break

        if not self._transport:
            return

        pause = (self._input_buffer_limit > 0 and
                 len(self._input_buffer) > self._input_buffer_limit and
                 not self._read_queue)

        if pause:
            self._transport.pause_reading()

        else:
            self._transport.resume_reading()
