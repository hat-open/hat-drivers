import collections
import os

import pytest

from hat import aio
from hat import util

from hat.drivers import net


pytestmark = pytest.mark.perf

stream_types = [net.StreamType.TCP]
if os.name == 'posix':
    stream_types.append(net.StreamType.UNIX)


@pytest.fixture
def create_addr(tmp_path):

    def create_addr(stream_type):
        if stream_type == net.StreamType.TCP:
            return net.TcpAddress('127.0.0.1', util.get_unused_tcp_port())

        if stream_type == net.StreamType.UNIX:
            return tmp_path / 'socket'

        raise ValueError('unsupported stream type')

    return create_addr


@pytest.mark.parametrize("stream_type", stream_types)
@pytest.mark.parametrize("data_count", [1, 100, 10000])
@pytest.mark.parametrize("data_size", [1, 10, 100])
async def test_read_write(duration, create_addr, stream_type, data_count,
                          data_size):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    server = await net.listen(conn_queue.put_nowait, addr)
    conn1 = await net.connect(addr)
    conn2 = await conn_queue.get()

    data = b'x' * data_size
    with duration(f'stream_type: {stream_type.name}; '
                  f'data_count: {data_count}; '
                  f'data_size: {data_size}'):
        for i in range(data_count):
            await conn1.write(data)
            await conn2.readexactly(len(data))

    await conn1.async_close()
    await conn2.async_close()
    await server.async_close()


@pytest.mark.parametrize("stream_type", stream_types)
@pytest.mark.parametrize("bind_connections", [True, False])
@pytest.mark.parametrize("conn_count", [0, 1, 5, 100])
async def test_server_close(duration, create_addr, stream_type,
                            bind_connections, conn_count):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    server = await net.listen(conn_queue.put_nowait, addr,
                              bind_connections=bind_connections)

    conns = collections.deque()
    for _ in range(conn_count):
        conn = await net.connect(addr)
        conns.append(conn)

    with duration(f'stream_type: {stream_type.name}; '
                  f'bind: {bind_connections}; '
                  f'count: {conn_count}'):
        await server.async_close()

    for conn in conns:
        await conn.async_close()
