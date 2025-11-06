import typing

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.iec104 import common
from hat.drivers.iec104.connection import regular
from hat.drivers.iec104.connection import secure
from hat.drivers.iec60870 import apci


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[[common.Connection], None]


async def connect(addr: tcp.Address,
                  response_timeout: float = 15,
                  supervisory_timeout: float = 10,
                  test_timeout: float = 20,
                  send_window_size: int = 12,
                  receive_window_size: int = 8,
                  update_key: util.Bytes | None = None,
                  critical_functions: set[common.Function] = secure.default_critical_functions,  # NOQA
                  **kwargs
                  ) -> common.Connection:
    apci_conn = await apci.connect(addr=addr,
                                   response_timeout=response_timeout,
                                   supervisory_timeout=supervisory_timeout,
                                   test_timeout=test_timeout,
                                   send_window_size=send_window_size,
                                   receive_window_size=receive_window_size,
                                   **kwargs)

    if update_key is not None:
        return secure.SecureConnection(apci_conn, True, update_key,
                                       critical_functions)

    return regular.RegularConnection(apci_conn)


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 2404),
                 response_timeout: float = 15,
                 supervisory_timeout: float = 10,
                 test_timeout: float = 20,
                 send_window_size: int = 12,
                 receive_window_size: int = 8,
                 update_key: util.Bytes | None = None,
                 critical_functions: set[common.Function] = secure.default_critical_functions,  # NOQA
                 **kwargs
                 ) -> 'Server':
    server = Server()
    server._connection_cb = connection_cb
    server._update_key = update_key
    server._critical_functions = critical_functions
    server._srv = await apci.listen(connection_cb=server._on_connection,
                                    addr=addr,
                                    response_timeout=response_timeout,
                                    supervisory_timeout=supervisory_timeout,
                                    test_timeout=test_timeout,
                                    send_window_size=send_window_size,
                                    receive_window_size=receive_window_size,
                                    **kwargs)
    return server


class Server(aio.Resource):

    @property
    def async_group(self):
        return self._srv.async_group

    async def _on_connection(self, apci_conn):
        if self._update_key is None:
            conn = regular.RegularConnection(apci_conn)

        else:
            conn = secure.SecureConnection(apci_conn, False, self._update_key,
                                           self._critical_functions)

        try:
            await aio.call(self._connection_cb, conn)

        except BaseException:
            await aio.uncancellable(conn.async_close())
