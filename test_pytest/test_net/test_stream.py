import asyncio
import os
import subprocess

import pytest

from hat import aio
from hat import util
from hat.drivers import net
from hat.drivers import ssl


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


@pytest.fixture(scope="session")
def pem_path(tmp_path_factory):
    path = tmp_path_factory.mktemp('syslog') / 'pem'
    subprocess.run(['openssl', 'req', '-batch', '-x509', '-noenc',
                    '-newkey', 'rsa:2048',
                    '-days', '1',
                    '-keyout', str(path),
                    '-out', str(path)],
                   stderr=subprocess.DEVNULL,
                   check=True)
    return path


@pytest.mark.parametrize("stream_type", stream_types)
@pytest.mark.parametrize("with_ssl", [True, False])
async def test_connect_listen(create_addr, pem_path, stream_type, with_ssl):
    addr = create_addr(stream_type)

    if with_ssl:
        srv_kwargs = {'ssl': ssl.create_ssl_ctx(ssl.SslProtocol.TLS_SERVER,
                                                cert_path=pem_path)}
        conn_kwargs = {'ssl': ssl.create_ssl_ctx(ssl.SslProtocol.TLS_CLIENT)}

        if stream_type == net.StreamType.UNIX:
            conn_kwargs['server_hostname'] = ''

    else:
        srv_kwargs = {}
        conn_kwargs = {}

    with pytest.raises(Exception):
        await net.connect(addr, **conn_kwargs)

    conn_queue = aio.Queue()
    srv = await net.listen(conn_queue.put_nowait, addr, **srv_kwargs)
    conn1 = await net.connect(addr, **conn_kwargs)
    conn2 = await conn_queue.get()

    assert srv.is_open
    assert conn1.is_open
    assert conn2.is_open

    assert srv.info.addresses == [addr]

    if stream_type == net.StreamType.TCP:
        assert conn1.info.local_addr == conn2.info.remote_addr
        assert conn1.info.remote_addr == conn2.info.local_addr

    elif stream_type == net.StreamType.UNIX:
        assert conn1.info.addr == conn2.info.addr

    else:
        raise ValueError('unsupported stream type')

    if with_ssl:
        assert conn1.ssl_object is not None
        assert conn2.ssl_object is not None

    else:
        assert conn1.ssl_object is None
        assert conn2.ssl_object is None

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


@pytest.mark.parametrize("stream_type", stream_types)
async def test_read(create_addr, stream_type):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    srv = await net.listen(conn_queue.put_nowait, addr)
    conn1 = await net.connect(addr)
    conn2 = await conn_queue.get()

    data = b'123'

    result = await conn1.read(0)
    assert result == b''

    await conn1.write(data)
    await conn1.drain()
    result = await conn2.read(len(data))
    assert result == data

    await conn2.write(data)
    result = await conn1.read(len(data) - 1)
    assert result == data[:-1]
    result = await conn1.read(1)
    assert result == data[-1:]

    await conn2.write(data)
    result = await conn1.read(len(data) + 1)
    assert result == data

    await conn2.write(data)
    await conn2.async_close()
    result = await conn1.read()
    assert result == data

    with pytest.raises(ConnectionError):
        await conn1.read()
    with pytest.raises(ConnectionError):
        await conn2.read()

    await conn1.async_close()
    await srv.async_close()


@pytest.mark.parametrize("stream_type", stream_types)
async def test_readexactly(create_addr, stream_type):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    srv = await net.listen(conn_queue.put_nowait, addr)
    conn1 = await net.connect(addr)
    conn2 = await conn_queue.get()

    data = b'123'

    result = await conn1.readexactly(0)
    assert result == b''

    await conn1.write(data)
    result = await conn2.readexactly(len(data))
    assert result == data

    await conn2.write(data)
    result = await conn1.readexactly(len(data) - 1)
    assert result == data[:-1]
    result = await conn1.readexactly(1)
    assert result == data[-1:]

    await conn2.write(data)
    await conn2.async_close()
    with pytest.raises(ConnectionError):
        await conn1.readexactly(len(data) + 1)

    # TODO
    # result = await conn1.readexactly(len(data))
    # assert result == data
    # with pytest.raises(ConnectionError):
    #     await conn1.readexactly(1)

    await conn1.async_close()
    await srv.async_close()


@pytest.mark.parametrize("stream_type", stream_types)
async def test_cancel_concurent_read(create_addr, stream_type):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    srv = await net.listen(conn_queue.put_nowait, addr)
    conn1 = await net.connect(addr)
    conn2 = await conn_queue.get()

    data = b'123'

    read_task_1 = asyncio.create_task(conn1.read())
    read_task_2 = asyncio.create_task(conn1.read())

    await asyncio.sleep(0.001)

    assert not read_task_1.done()
    assert not read_task_2.done()

    read_task_1.cancel()

    await conn2.write(data)

    result = await read_task_2
    assert result == data

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


@pytest.mark.parametrize("stream_type", stream_types)
@pytest.mark.parametrize("bind_connections", [True, False])
@pytest.mark.parametrize("conn_count", [1, 2, 5])
async def test_bind_connections(create_addr, stream_type, bind_connections,
                                conn_count):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    srv = await net.listen(conn_queue.put_nowait, addr,
                           bind_connections=bind_connections)

    conns = []
    for _ in range(conn_count):
        conn1 = await net.connect(addr)
        conn2 = await conn_queue.get()

        conns.append((conn1, conn2))

    for conn1, conn2 in conns:
        assert conn1.is_open
        assert conn2.is_open

    await srv.async_close()

    for conn1, conn2 in conns:
        if bind_connections:
            with pytest.raises(ConnectionError):
                await conn1.read()
            assert not conn1.is_open
            assert not conn2.is_open

        else:
            assert conn1.is_open
            assert conn2.is_open

        await conn1.async_close()
        await conn2.async_close()


async def test_example_docs():
    addr = net.TcpAddress('127.0.0.1', util.get_unused_tcp_port())

    conn2_future = asyncio.Future()
    srv = await net.listen(conn2_future.set_result, addr)
    conn1 = await net.connect(addr)
    conn2 = await conn2_future

    # send from conn1 to conn2
    data = b'123'
    await conn1.write(data)
    result = await conn2.readexactly(len(data))
    assert result == data

    # send from conn2 to conn1
    data = b'321'
    await conn2.write(data)
    result = await conn1.readexactly(len(data))
    assert result == data

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


@pytest.mark.parametrize("stream_type", stream_types)
@pytest.mark.parametrize(
    "write_block_count, write_block_size, read_block_size",
    [(10000, 1024 + 123, 512 - 123),
     (10000, 512 - 123, 1024 + 123),
     (100, 102400 + 123, 512 - 123)])
async def test_large(create_addr, stream_type,
                     write_block_count, write_block_size, read_block_size):
    addr = create_addr(stream_type)

    conn_queue = aio.Queue()
    srv = await net.listen(conn_queue.put_nowait, addr)
    conn1 = await net.connect(addr)
    conn2 = await conn_queue.get()

    for _ in range(write_block_count):
        conn1.async_group.spawn(conn1.write, b'x' * write_block_size)

    read_len = 0
    while read_len < write_block_size * write_block_count:
        data = await conn2.read(read_block_size)
        read_len += len(data)

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


# TODO
async def test_input_buffer():
    pass
