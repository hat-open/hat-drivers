import asyncio
import subprocess

import pytest

from hat import aio
from hat import util
from hat.drivers import ssl
from hat.drivers import tcp


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


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


@pytest.mark.parametrize("with_ssl", [True, False])
async def test_connect_listen(addr, pem_path, with_ssl):
    srv_ssl_ctx = (ssl.create_ssl_ctx(ssl.SslProtocol.TLS_SERVER,
                                      cert_path=pem_path)
                   if with_ssl else None)
    conn_ssl_ctx = (ssl.create_ssl_ctx(ssl.SslProtocol.TLS_CLIENT)
                    if with_ssl else None)

    with pytest.raises(ConnectionError):
        await tcp.connect(addr, ssl=conn_ssl_ctx)

    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr, ssl=srv_ssl_ctx)
    conn1 = await tcp.connect(addr, ssl=conn_ssl_ctx)
    conn2 = await conn_queue.get()

    assert srv.is_open
    assert conn1.is_open
    assert conn2.is_open

    assert srv.addresses == [addr]
    assert conn1.info.local_addr == conn2.info.remote_addr
    assert conn1.info.remote_addr == conn2.info.local_addr

    if with_ssl:
        assert conn1.ssl_object is not None
        assert conn2.ssl_object is not None
    else:
        assert conn1.ssl_object is None
        assert conn2.ssl_object is None

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


async def test_read(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)
    conn1 = await tcp.connect(addr)
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


async def test_readexactly(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)
    conn1 = await tcp.connect(addr)
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


async def test_cancel_concurent_read(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)
    conn1 = await tcp.connect(addr)
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


@pytest.mark.parametrize("bind_connections", [True, False])
@pytest.mark.parametrize("conn_count", [1, 2, 5])
async def test_bind_connections(addr, bind_connections, conn_count):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr,
                           bind_connections=bind_connections)

    conns = []
    for _ in range(conn_count):
        conn1 = await tcp.connect(addr)
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
    addr = tcp.Address('127.0.0.1', util.get_unused_tcp_port())

    conn2_future = asyncio.Future()
    srv = await tcp.listen(conn2_future.set_result, addr)
    conn1 = await tcp.connect(addr)
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


@pytest.mark.parametrize(
    "write_block_count, write_block_size, read_block_size",
    [(10000, 1024 + 123, 512 - 123),
     (10000, 512 - 123, 1024 + 123),
     (100, 102400 + 123, 512 - 123)])
async def test_large(addr, write_block_count, write_block_size,
                     read_block_size):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)
    conn1 = await tcp.connect(addr)
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
