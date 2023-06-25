import pytest

from hat import aio
from hat import util

from hat.drivers import tcp


pytestmark = pytest.mark.perf


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.mark.parametrize("data_count", [1, 100, 10000])
@pytest.mark.parametrize("data_size", [1, 10, 100])
async def test_read_write(duration, addr, data_count, data_size):
    conn_queue = aio.Queue()
    server = await tcp.listen(conn_queue.put_nowait, addr)
    conn1 = await tcp.connect(addr)
    conn2 = await conn_queue.get()

    data = b'x' * data_size
    with duration(f'data_count: {data_count}; data_size: {data_size}'):
        for i in range(data_count):
            await conn1.write(data)
            await conn2.readexactly(len(data))

    await conn1.async_close()
    await conn2.async_close()
    await server.async_close()
