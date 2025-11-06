import collections
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.iec104 import common
from hat.drivers.iec104 import encoder
from hat.drivers.iec104 import logger
from hat.drivers.iec60870 import apci


mlog: logging.Logger = logging.getLogger(__name__)


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]


async def connect(addr: tcp.Address,
                  *,
                  response_timeout: float = 15,
                  supervisory_timeout: float = 10,
                  test_timeout: float = 20,
                  send_window_size: int = 12,
                  receive_window_size: int = 8,
                  **kwargs
                  ) -> 'Connection':
    conn = await apci.connect(addr=addr,
                              response_timeout=response_timeout,
                              supervisory_timeout=supervisory_timeout,
                              test_timeout=test_timeout,
                              send_window_size=send_window_size,
                              receive_window_size=receive_window_size,
                              **kwargs)

    return Connection(conn)


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 2404),
                 *,
                 response_timeout: float = 15,
                 supervisory_timeout: float = 10,
                 test_timeout: float = 20,
                 send_window_size: int = 12,
                 receive_window_size: int = 8,
                 **kwargs
                 ) -> tcp.Server:
    log = logger.create_server_logger(mlog, kwargs.get('name'), None)

    async def on_connection(conn):
        try:
            try:
                conn = Connection(conn)
                await aio.call(connection_cb, conn)

            except BaseException:
                await aio.uncancellable(conn.async_close())
                raise

        except Exception as e:
            log.error("on connection error: %s", e, exc_info=e)

    server = await apci.listen(connection_cb=on_connection,
                               addr=addr,
                               response_timeout=response_timeout,
                               supervisory_timeout=supervisory_timeout,
                               test_timeout=test_timeout,
                               send_window_size=send_window_size,
                               receive_window_size=receive_window_size,
                               **kwargs)

    log = logger.create_server_logger(mlog, server.info.name, server.info)

    return server


class Connection(aio.Resource):

    def __init__(self, conn: apci.Connection):
        self._conn = conn
        self._encoder = encoder.Encoder()
        self._comm_log = logger.CommunicationLogger(mlog, conn.info)

        self.async_group.spawn(aio.call_on_cancel, self._comm_log.log,
                               common.CommLogAction.CLOSE)
        self._comm_log.log(common.CommLogAction.OPEN)

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        return self._conn.info

    @property
    def is_enabled(self) -> bool:
        return self._conn.is_enabled

    def register_enabled_cb(self,
                            cb: typing.Callable[[bool], None]
                            ) -> util.RegisterCallbackHandle:
        return self._conn.register_enabled_cb(cb)

    async def send(self,
                   msgs: typing.List[common.Msg],
                   wait_ack: bool = False):
        self._comm_log.log(common.CommLogAction.SEND, msgs)

        data = collections.deque(self._encoder.encode(msgs))
        while data:
            head = data.popleft()
            head_wait_ack = False if data else wait_ack
            await self._conn.send(head, head_wait_ack)

    async def drain(self, wait_ack: bool = False):
        await self._conn.drain(wait_ack)

    async def receive(self) -> list[common.Msg]:
        data = await self._conn.receive()
        msgs = list(self._encoder.decode(data))

        self._comm_log.log(common.CommLogAction.RECEIVE, msgs)

        return msgs
