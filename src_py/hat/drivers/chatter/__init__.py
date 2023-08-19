"""Chatter communication protocol"""

import asyncio
import importlib.resources
import itertools
import logging
import math
import typing

from hat import aio
from hat import sbs
from hat import util

from hat.drivers import tcp


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""

TimeoutCb: typing.TypeAlias = aio.AsyncCallable[['Conversation'], None]
"""Timeout callback"""


class Data(typing.NamedTuple):
    type: str
    data: util.Bytes


class Conversation(typing.NamedTuple):
    owner: bool
    first_id: int


class Msg(typing.NamedTuple):
    data: Data
    conv: Conversation
    first: bool
    last: bool
    token: bool


async def connect(addr: tcp.Address,
                  *,
                  ping_delay: float = 20,
                  ping_timeout: float = 20,
                  receive_queue_size: int = 1024,
                  send_queue_size: int = 1024,
                  **kwargs
                  ) -> 'Connection':
    """Connect to remote server

    Argument `addr` specifies remote server listening address.

    If `ping_delay` is ``None`` or 0, ping service is not registered,
    otherwise it represents cyclic ping delay in seconds.

    Additional arguments are passed directly to `hat.drivers.tcp.connect`.

    """
    conn = await tcp.connect(addr, **kwargs)

    try:
        return Connection(conn=conn,
                          ping_delay=ping_delay,
                          ping_timeout=ping_timeout,
                          receive_queue_size=receive_queue_size,
                          send_queue_size=send_queue_size)

    except Exception:
        await aio.uncancellable(conn.async_close())
        raise


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address,
                 *,
                 ping_delay: float = 20,
                 ping_timeout: float = 20,
                 receive_queue_size: int = 1024,
                 send_queue_size: int = 1024,
                 bind_connections: bool = True,
                 **kwargs
                 ) -> tcp.Server:
    """Create listening server.

    Argument `addr` specifies local server listening address.

    If `ping_delay` is ``None`` or 0, ping service is not registered,
    otherwise it represents cyclic ping delay in seconds.

    Additional arguments are passed directly to `hat.drivers.tcp.listen`.

    """

    async def on_connection(conn):
        try:
            conn = Connection(conn=conn,
                              ping_delay=ping_delay,
                              ping_timeout=ping_timeout,
                              receive_queue_size=receive_queue_size,
                              send_queue_size=send_queue_size)

            await aio.call(connection_cb, conn)

        except Exception as e:
            mlog.warning('connection callback error: %s', e, exc_info=e)
            await aio.uncancellable(conn.async_close())

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise

    return await tcp.listen(on_connection, addr,
                            bind_connections=bind_connections,
                            **kwargs)


class Connection(aio.Resource):
    """Single connection

    For creating new connection see `connect` function.

    """

    def __init__(self,
                 conn: tcp.Connection,
                 ping_delay: float,
                 ping_timeout: float,
                 receive_queue_size: int,
                 send_queue_size: int):
        self._conn = conn
        self._receive_queue = aio.Queue(receive_queue_size)
        self._send_queue = aio.Queue(receive_queue_size)
        self._loop = asyncio.get_running_loop()
        self._next_msg_ids = itertools.count(1)
        self._conv_timeouts = {}

        self.async_group.spawn(self._read_loop)
        self.async_group.spawn(self._write_loop)

        if ping_delay:
            self.async_group.spawn(self._ping_loop, ping_delay, ping_timeout)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        """Connection info"""
        return self._conn.info

    async def receive(self) -> Msg:
        """Receive message"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send(self,
                   data: Data,
                   *,
                   conv: Conversation | None = None,
                   last: bool = True,
                   token: bool = True,
                   timeout: float | None = None,
                   timeout_cb: TimeoutCb | None = None
                   ) -> Conversation:
        """Send message

        If `conv` is ``None``, new conversation is created.

        `timeout` represents conversation timeout in seconds. If this argument
        is ``None``, conversation timeout will not be triggered. Conversation
        timeout callbacks are triggered only for opened connection. Once
        connection is closed, all active conversations are closed without
        triggering timeout callbacks.

        """
        if self.is_closing:
            raise ConnectionError()

        msg_id = next(self._next_msg_ids)

        if not conv:
            conv = Conversation(owner=True,
                                first_id=msg_id)

        msg = {'id': msg_id,
               'first': conv.first_id,
               'owner': conv.owner,
               'token': token,
               'last': last,
               'data': {'type': data.type,
                        'data': data.data}}

        conv_timeout = self._conv_timeouts.pop(conv, None)
        if conv_timeout:
            mlog.debug("canceling existing conversation timeout")
            conv_timeout.cancel()

        if not last and timeout and timeout_cb:
            mlog.debug("registering conversation timeout")
            self._conv_timeouts[conv] = self._loop.call_later(
                timeout, self._on_conv_timeout, conv, timeout_cb)

        await self._send_queue.put((msg, None))

        return conv

    async def drain(self):
        """Drain output buffer"""
        future = self._loop.create_future()
        try:
            await self._send_queue.put((None, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    def _on_conv_timeout(self, conv, timeout_cb):
        if not self._conv_timeouts.pop(conv, None):
            return

        mlog.debug("conversation's timeout triggered")
        self.async_group.spawn(aio.call, timeout_cb, conv)

    def _on_ping_timeout(self, conv):
        mlog.debug("ping response timeout - closing connection")
        self.close()

    async def _read_loop(self):
        mlog.debug("connection's read loop started")
        try:
            while True:
                mlog.debug("waiting for incoming message")
                data = await self._read()
                msg = Msg(
                    data=Data(type=data['data']['type'],
                              data=data['data']['data']),
                    conv=Conversation(owner=not data['owner'],
                                      first_id=data['first']),
                    first=data['owner'] and data['first'] == data['id'],
                    last=data['last'],
                    token=data['token'])

                conv_timeout = self._conv_timeouts.pop(msg.conv, None)
                if conv_timeout:
                    mlog.debug("canceling existing conversation timeout")
                    conv_timeout.cancel()

                if msg.data.type == 'HatChatter.Ping':
                    mlog.debug("received ping request - sending ping response")
                    await self.send(Data('HatChatter.Pong', b''),
                                    conv=msg.conv)

                elif msg.data.type == 'HatChatter.Pong':
                    mlog.debug("received ping response")

                else:
                    mlog.debug("received message %s", msg.data.type)
                    await self._receive_queue.put(msg)

        except ConnectionError:
            mlog.debug("connection error")

        except Exception as e:
            mlog.error("read loop error: %s", e, exc_info=e)

        finally:
            mlog.debug("connection's read loop stopping")
            self.close()
            self._receive_queue.close()

    async def _write_loop(self):
        mlog.debug("connection's write loop started")
        future = None

        try:
            while True:
                mlog.debug("waiting for outgoing message")
                msg, future = await self._send_queue.get()

                if msg is None:
                    mlog.debug("draining output buffer")
                    await self._conn.drain()

                else:
                    mlog.debug("writing message %s", msg['data']['type'])
                    await self._write(msg)

                if future and not future.done():
                    future.set_result(None)

        except ConnectionError:
            mlog.debug("connection error")

        except Exception as e:
            mlog.error("write loop error: %s", e, exc_info=e)

        finally:
            mlog.debug("connection's write loop stopping")
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()

            for conv_timeout in self._conv_timeouts.values():
                conv_timeout.cancel()
            self._conv_timeouts = {}

    async def _ping_loop(self, delay, timeout):
        mlog.debug("ping loop started")
        try:
            while True:
                mlog.debug("ping loop - waiting for %ss", delay)
                await asyncio.sleep(delay)

                mlog.debug("sending ping request")
                await self.send(Data('HatChatter.Ping', b''),
                                last=False,
                                timeout=timeout,
                                timeout_cb=self._on_ping_timeout)

        except ConnectionError:
            pass

        finally:
            mlog.debug("ping loop stopped")
            self.close()

    async def _read(self):
        msg_len_len_bytes = await self._conn.readexactly(1)
        msg_len_len = msg_len_len_bytes[0]

        msg_len_bytes = await self._conn.readexactly(msg_len_len)
        msg_len = _bebytes_to_uint(msg_len_bytes)

        msg_bytes = await self._conn.readexactly(msg_len)
        msg = _sbs_repo.decode('HatChatter.Msg', msg_bytes)

        return msg

    async def _write(self, msg):
        msg_bytes = _sbs_repo.encode('HatChatter.Msg', msg)
        msg_len = len(msg_bytes)
        msg_len_bytes = _uint_to_bebytes(msg_len)
        msg_len_len_bytes = [len(msg_len_bytes)]

        await self._conn.write(bytes(itertools.chain(msg_len_len_bytes,
                                                     msg_len_bytes,
                                                     msg_bytes)))


def _uint_to_bebytes(x):
    bytes_len = max(math.ceil(x.bit_length() / 8), 1)
    return x.to_bytes(bytes_len, 'big')


def _bebytes_to_uint(b):
    return int.from_bytes(b, 'big')


with importlib.resources.as_file(importlib.resources.files(__package__) /
                                 'sbs_repo.json') as _path:
    _sbs_repo = sbs.Repository.from_json(_path)
