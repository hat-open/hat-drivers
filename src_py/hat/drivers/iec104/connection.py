import collections
import ssl
import typing

from hat import aio

from hat.drivers import tcp
from hat.drivers.iec104 import common
from hat.drivers.iec104 import encoder
from hat.drivers.iec60870 import apci


ConnectionCb = aio.AsyncCallable[['Connection'], None]


async def connect(addr: tcp.Address,
                  response_timeout: float = 15,
                  supervisory_timeout: float = 10,
                  test_timeout: float = 20,
                  send_window_size: int = 12,
                  receive_window_size: int = 8,
                  ssl_ctx: typing.Optional[ssl.SSLContext] = None
                  ) -> 'Connection':
    apci_conn = await apci.connect(addr=addr,
                                   response_timeout=response_timeout,
                                   supervisory_timeout=supervisory_timeout,
                                   test_timeout=test_timeout,
                                   send_window_size=send_window_size,
                                   receive_window_size=receive_window_size,
                                   ssl_ctx=ssl_ctx)
    return Connection(apci_conn)


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 2404),
                 response_timeout: float = 15,
                 supervisory_timeout: float = 10,
                 test_timeout: float = 20,
                 send_window_size: int = 12,
                 receive_window_size: int = 8,
                 ssl_ctx: typing.Optional[ssl.SSLContext] = None
                 ) -> 'Server':
    server = Server()
    server._connection_cb = connection_cb
    server._srv = await apci.listen(connection_cb=server._on_connection,
                                    addr=addr,
                                    response_timeout=response_timeout,
                                    supervisory_timeout=supervisory_timeout,
                                    test_timeout=test_timeout,
                                    send_window_size=send_window_size,
                                    receive_window_size=receive_window_size,
                                    ssl_ctx=ssl_ctx)
    return server


class Server(aio.Resource):

    @property
    def async_group(self):
        return self._srv.async_group

    async def _on_connection(self, apci_conn):
        conn = Connection(apci_conn)

        try:
            await aio.call(self._connection_cb, conn)

        except BaseException:
            await aio.uncancellable(conn.async_close())


class Connection(aio.Resource):

    def __init__(self, conn: apci.Connection):
        self._conn = conn
        self._encoder = encoder.Encoder()

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        return self._conn.info

    def send(self, msgs: typing.List[common.Msg]):
        for data in self._encoder.encode(msgs):
            self._conn.send(data)

    async def send_wait_ack(self, msgs: typing.List[common.Msg]):
        data = collections.deque(self._encoder.encode(msgs))
        if not data:
            return

        last = data.pop()
        for i in data:
            self._conn.send(i)

        await self._conn.send_wait_ack(last)

    async def drain(self, wait_ack: bool = False):
        await self._conn.drain(wait_ack)

    async def receive(self) -> typing.List[common.Msg]:
        data = await self._conn.receive()
        return list(self._encoder.decode(data))
