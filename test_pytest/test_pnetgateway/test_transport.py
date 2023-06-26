import pytest

from hat import util
from hat import aio

from hat.drivers import tcp
from hat.drivers.pnetgateway import transport


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.mark.parametrize("data", [
    123,
    None,
    'abc',
    {'a': [1, True, {}]}
])
async def test_transport(data, addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)
    conn1 = await tcp.connect(addr)
    conn2 = await conn_queue.get()

    conn1 = transport.Transport(conn1)
    conn2 = transport.Transport(conn2)

    assert conn1.is_open
    assert conn2.is_open

    await conn1.send(data)
    received = await conn2.receive()
    assert data == received

    await conn2.send(data)
    received = await conn1.receive()
    assert data == received

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()
