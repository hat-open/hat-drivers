"""Transport Service on top of TCP"""

import asyncio
import itertools
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import tcp


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


async def connect(addr: tcp.Address,
                  *,
                  tpkt_receive_queue_size: int = 1024,
                  **kwargs
                  ) -> 'Connection':
    """Create new TPKT connection

    Additional arguments are passed directly to `hat.drivers.tcp.connect`.

    """
    conn = await tcp.connect(addr, **kwargs)
    return Connection(conn=conn,
                      receive_queue_size=tpkt_receive_queue_size)


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 102),
                 *,
                 tpkt_receive_queue_size: int = 1024,
                 **kwargs
                 ) -> 'Server':
    """Create new TPKT listening server

    Additional arguments are passed directly to `hat.drivers.tcp.listen`.

    """
    server = Server()
    server._connection_cb = connection_cb
    server._receive_queue_size = tpkt_receive_queue_size
    server._log = _create_server_logger(kwargs.get('name'), None)

    server._srv = await tcp.listen(server._on_connection, addr, **kwargs)

    server._log = _create_server_logger(kwargs.get('name'), server._srv.info)

    return server


class Server(aio.Resource):
    """TPKT listening server

    For creation of new instance see `listen` coroutine.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._srv.async_group

    @property
    def info(self) -> tcp.ServerInfo:
        """Server info"""
        return self._srv.info

    async def _on_connection(self, conn):
        try:
            conn = Connection(conn=conn,
                              receive_queue_size=self._receive_queue_size)
            await aio.call(self._connection_cb, conn)

        except Exception as e:
            self._log.warning('connection callback error: %s', e, exc_info=e)
            await aio.uncancellable(conn.async_close())

        except asyncio.CancelledError:
            await aio.uncancellable(conn.async_close())
            raise


class Connection(aio.Resource):
    """TPKT connection"""

    def __init__(self,
                 conn: tcp.Connection,
                 receive_queue_size: int):
        self._conn = conn
        self._receive_queue = aio.Queue(receive_queue_size)
        self._log = _create_connection_logger(conn.info)

        self.async_group.spawn(self._read_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        """Connection info"""
        return self._conn.info

    async def receive(self) -> util.Bytes:
        """Receive data"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send(self, data: util.Bytes):
        """Send data"""
        data_len = len(data)

        if data_len > 0xFFFB:
            raise ValueError("data length greater than 0xFFFB")

        if data_len < 3:
            raise ValueError("data length less than 3")

        packet_length = data_len + 4
        packet = bytes(itertools.chain(
            [3, 0, packet_length >> 8, packet_length & 0xFF],
            data))

        await self._conn.write(packet)

    async def drain(self):
        """Drain output buffer"""
        await self._conn.drain()

    async def _read_loop(self):
        self._log.debug('starting read loop')

        try:
            while True:
                header = await self._conn.readexactly(4)
                if header[0] != 3:
                    raise Exception(f"invalid vrsn number "
                                    f"(received {header[0]})")

                packet_length = (header[2] << 8) | header[3]
                if packet_length < 7:
                    raise Exception(f"invalid packet length "
                                    f"(received {packet_length})")

                data_length = packet_length - 4
                data = await self._conn.readexactly(data_length)

                await self._receive_queue.put(data)

        except ConnectionError:
            pass

        except Exception as e:
            self._log.warning("read loop error: %s", e, exc_info=e)

        finally:
            self._log.debug('stopping read loop')

            self.close()
            self._receive_queue.close()


def _create_server_logger(name, info):
    extra = {'meta': {'type': 'TpktServer',
                      'name': name}}

    if info is not None:
        extra['meta']['addresses'] = [{'host': addr.host,
                                       'port': addr.port}
                                      for addr in info.addresses]

    return logging.LoggerAdapter(mlog, extra)


def _create_connection_logger(info):
    extra = {'meta': {'type': 'TpktConnection',
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(mlog, extra)
