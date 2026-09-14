from collections.abc import Callable
import asyncio
import collections
import enum
import functools
import logging
import pathlib
import sys
import typing

from hat import aio
from hat import json
from hat import util

from hat.drivers import ssl
from hat.drivers.net import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


class TcpAddress(typing.NamedTuple):
    host: str
    port: int


StreamAddress: typing.TypeAlias = TcpAddress | common.UnixAddress


class TcpConnectionInfo(typing.NamedTuple):
    name: str | None
    local_addr: TcpAddress
    remote_addr: TcpAddress


class UnixConnectionInfo(typing.NamedTuple):
    name: str | None
    addr: common.UnixAddress


class TcpServerInfo(typing.NamedTuple):
    name: str | None
    addresses: list[TcpAddress]


class UnixServerInfo(typing.NamedTuple):
    name: str | None
    addresses: list[common.UnixAddress]


ConnectionInfo: typing.TypeAlias = TcpConnectionInfo | UnixConnectionInfo

ServerInfo: typing.TypeAlias = TcpServerInfo | UnixServerInfo


class StreamType(enum.Enum):
    TCP = 0
    UNIX = 1


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


def connection_info_to_json(info: ConnectionInfo) -> json.Data:
    if isinstance(info, TcpConnectionInfo):
        return {'name': info.name,
                'local_addr': {'host': info.local_addr.host,
                               'port': info.local_addr.port},
                'remote_addr': {'host': info.remote_addr.host,
                                'port': info.remote_addr.port}}

    if isinstance(info, UnixConnectionInfo):
        return {'name': info.name,
                'addr': str(info.addr)}

    raise TypeError('unsupported info type')


def server_info_to_json(info: ServerInfo) -> json.Data:
    if isinstance(info, TcpServerInfo):
        return {'name': info.name,
                'addresses': [{'host': addr.host,
                               'port': addr.port}
                              for addr in info.addresses]}

    if isinstance(info, UnixServerInfo):
        return {'name': info.name,
                'addresses': [str(addr) for addr in info.addresses]}

    raise TypeError('unsupported info type')


async def connect(addr: StreamAddress,
                  *,
                  name: str | None = None,
                  input_buffer_limit: int = 64 * 1024,
                  **kwargs
                  ) -> 'Connection':
    """Create TCP or Unix Domain Socket connection

    Argument `addr` specifies remote server listening address.

    Argument `name` defines connection name available in property `info`.

    Argument `input_buffer_limit` defines number of bytes in input buffer
    that whill temporary pause data receiving. Once number of bytes
    drops bellow `input_buffer_limit`, data receiving is resumed. If this
    argument is ``0``, data receive pausing is disabled.

    Additional arguments are passed directly to `asyncio.create_connection` or
    `asyncio.create_unix_connection`.

    """
    loop = asyncio.get_running_loop()
    stream_type = _get_stream_type(addr)
    create_protocol = functools.partial(_Protocol, stream_type, None, name,
                                        input_buffer_limit)

    if stream_type == StreamType.TCP:
        _, protocol = await loop.create_connection(create_protocol,
                                                   addr.host, addr.port,
                                                   **kwargs)

    elif stream_type == StreamType.UNIX:
        _, protocol = await loop.create_unix_connection(create_protocol, addr,
                                                        **kwargs)

    else:
        raise ValueError('unsupported stream type')

    return _create_connection(protocol)


async def listen(connection_cb: ConnectionCb,
                 addr: StreamAddress,
                 *,
                 name: str | None = None,
                 bind_connections: bool = False,
                 input_buffer_limit: int = 64 * 1024,
                 **kwargs
                 ) -> 'Server':
    """Create listening TCP or Unix Domain Socket server

    Argument `name` defines server name available in property `info`. This
    name is used for all incomming connections.

    If `bind_connections` is ``True``, closing server will close all open
    incoming connections.

    Argument `input_buffer_limit` is associated with newly created connections
    (see `connect`).

    Additional arguments are passed directly to `asyncio.create_server` or
    `asyncio.create_unix_server`.

    """
    server = Server()
    server._connection_cb = connection_cb
    server._bind_connections = bind_connections
    server._stream_type = _get_stream_type(addr)
    server._async_group = aio.Group()
    server._log = mlog

    loop = asyncio.get_running_loop()
    on_connection = functools.partial(server.async_group.spawn,
                                      server._on_connection)
    create_protocol = functools.partial(_Protocol, server._stream_type,
                                        on_connection, name,
                                        input_buffer_limit)

    if server._stream_type == StreamType.TCP:
        server._srv = await loop.create_server(create_protocol,
                                               addr.host, addr.port, **kwargs)

    elif server._stream_type == StreamType.UNIX:
        server._srv = await loop.create_unix_server(create_protocol,
                                                    addr, **kwargs)

    else:
        raise ValueError('unsupported stream type')

    server.async_group.spawn(aio.call_on_cancel, server._on_close)

    try:
        server._info = _get_server_info(server._stream_type, name, server._srv)
        server._log = _create_server_logger(server._info)

    except Exception:
        await aio.uncancellable(server.async_close())
        raise

    server._log.debug('listening for incomming connections')

    return server


class Server(aio.Resource):
    """TCP or Unix Domain Socket listening server

    Closing server will cancel all running `connection_cb` coroutines.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> ServerInfo:
        """Server info"""
        return self._info

    async def _on_close(self):
        self._srv.close()

        if self._bind_connections or sys.version_info[:2] < (3, 12):
            await self._srv.wait_closed()

    async def _on_connection(self, protocol):
        self._log.debug('new incomming connection')

        conn = _create_connection(protocol)

        try:
            await aio.call(self._connection_cb, conn)

            if self._bind_connections:
                await conn.wait_closing()

            else:
                conn = None

        except Exception as e:
            self._log.warning('connection callback error: %s', e, exc_info=e)

        finally:
            if conn:
                await aio.uncancellable(conn.async_close())


def _create_connection(protocol: '_Protocol') -> 'Connection':
    conn = Connection()
    conn._protocol = protocol
    conn._async_group = aio.Group()

    conn.async_group.spawn(aio.call_on_cancel, protocol.async_close)
    conn.async_group.spawn(aio.call_on_done, protocol.wait_closed(),
                           conn.close)

    return conn


class Connection(aio.Resource):
    """TCP or Unix Domain Socket connection"""

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

    def clear_input_buffer(self) -> int:
        """Clear input buffer

        Returns number of bytes cleared from buffer.

        """
        return self._protocol.clear_input_buffer()


class _Protocol(asyncio.Protocol):

    def __init__(self,
                 stream_type: StreamType,
                 on_connected: Callable[['_Protocol'], None] | None,
                 name: str | None,
                 input_buffer_limit: int):
        self._stream_type = stream_type
        self._on_connected = on_connected
        self._name = name
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
        self._log = mlog
        self._comm_log = _CommunicationLogger(None)

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def info(self) -> ConnectionInfo | None:
        return self._info

    @property
    def ssl_object(self) -> ssl.SSLObject | ssl.SSLSocket | None:
        return self._ssl_object

    def connection_made(self, transport: asyncio.Transport):
        self._transport = transport
        self._read_queue = collections.deque()
        self._closed_futures = collections.deque()

        try:
            self._info = _get_connection_info(
                self._stream_type, self._name, transport)
            self._ssl_object = transport.get_extra_info('ssl_object')

            self._log = _create_connection_logger(self._info)
            self._comm_log = _CommunicationLogger(self._info)

            self._comm_log.log(common.CommLogAction.OPEN)

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

        self._comm_log.log(common.CommLogAction.CLOSE)

    def pause_writing(self):
        self._log.debug('pause writing')

        self._write_queue = collections.deque()
        self._drain_futures = collections.deque()

    def resume_writing(self):
        self._log.debug('resume writing')

        write_queue, self._write_queue = self._write_queue, None
        drain_futures, self._drain_futures = self._drain_futures, None

        while self._write_queue is None and write_queue:
            data, future = write_queue.popleft()
            if future.done():
                continue

            self._comm_log.log(common.CommLogAction.SEND, data)

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
        self._comm_log.log(common.CommLogAction.RECEIVE, data)

        self._input_buffer.add(data)
        self._process_input_buffer()

    def eof_received(self):
        self._log.debug('eof received')

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
            self._comm_log.log(common.CommLogAction.SEND, data)

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

    def clear_input_buffer(self) -> int:
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


def _get_stream_type(addr: StreamAddress) -> StreamType:
    if isinstance(addr, TcpAddress):
        return StreamType.TCP

    if isinstance(addr, common.UnixAddress):
        return StreamType.UNIX

    raise TypeError('unsupported address type')


def _get_server_info(stream_type: StreamType,
                     name: str | None,
                     srv: asyncio.Server
                     ) -> ServerInfo:
    socknames = (socket.getsockname() for socket in srv.sockets)

    if stream_type == StreamType.TCP:
        return TcpServerInfo(
            name=name,
            addresses=[TcpAddress(*sockname[:2]) for sockname in socknames])

    if stream_type == StreamType.UNIX:
        return UnixServerInfo(
            name=name,
            addresses=[pathlib.Path(sockname) for sockname in socknames])

    raise ValueError('unsupported streaming type')


def _get_connection_info(stream_type: StreamType,
                         name: str | None,
                         transport: asyncio.Transport
                         ) -> ConnectionInfo:
    sockname = transport.get_extra_info('sockname')
    peername = transport.get_extra_info('peername')

    if stream_type == StreamType.TCP:
        return TcpConnectionInfo(
            name=name,
            local_addr=TcpAddress(sockname[0], sockname[1]),
            remote_addr=TcpAddress(peername[0], peername[1]))

    if stream_type == StreamType.UNIX:
        if sockname:
            addr = pathlib.Path(sockname)

        elif peername:
            addr = pathlib.Path(peername)

        else:
            raise Exception('unknown address')

        return UnixConnectionInfo(name=name,
                                  addr=addr)

    raise ValueError('unsupported streaming type')


def _create_server_logger(info: ServerInfo) -> logging.LoggerAdapter:
    if isinstance(info, TcpServerInfo):
        meta_type = 'TcpServer'

    elif isinstance(info, UnixServerInfo):
        meta_type = 'UnixServer'

    else:
        raise TypeError('unsupported info type')

    extra = {'meta': {'type': meta_type,
                      **server_info_to_json(info)}}

    return logging.LoggerAdapter(mlog, extra)


def _create_connection_logger(info: ConnectionInfo) -> logging.LoggerAdapter:
    if isinstance(info, TcpConnectionInfo):
        meta_type = 'TcpConnection'

    elif isinstance(info, UnixConnectionInfo):
        meta_type = 'UnixConnection'

    else:
        raise TypeError('unsupported info type')

    extra = {'meta': {'type': meta_type,
                      **connection_info_to_json(info)}}

    return logging.LoggerAdapter(mlog, extra)


class _CommunicationLogger:

    def __init__(self, info: ConnectionInfo | None):
        if info:
            self._log = _create_connection_logger(info)
            self._log.extra['meta']['communication'] = True

        else:
            self._log = mlog

    def log(self,
            action: common.CommLogAction,
            data: util.Bytes | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if data is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s (%s)', action.value, data.hex(' '),
                            stacklevel=2)
