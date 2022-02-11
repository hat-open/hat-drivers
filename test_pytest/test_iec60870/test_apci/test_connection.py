import asyncio
import contextlib

import pytest

from hat import aio
from hat.drivers import tcp
from hat.drivers.iec60870 import apci
from hat.drivers.iec60870.apci import common
from hat.drivers.iec60870.apci import encoder


pytestmark = pytest.mark.timeout(1)


@pytest.fixture
def server_port(unused_tcp_port_factory):
    return unused_tcp_port_factory()


@contextlib.asynccontextmanager
async def server(port,
                 connection_cb=lambda _: None,
                 response_timeout=15,
                 supervisory_timeout=10,
                 test_timeout=20,
                 send_window_size=12,
                 receive_window_size=8):
    server = await apci.listen(connection_cb=connection_cb,
                               addr=tcp.Address(host='localhost',
                                                port=port),
                               response_timeout=response_timeout,
                               supervisory_timeout=supervisory_timeout,
                               test_timeout=test_timeout,
                               send_window_size=send_window_size,
                               receive_window_size=receive_window_size)
    try:
        yield server
    finally:
        await server.async_close()


@contextlib.asynccontextmanager
async def server_conn_queue(port,
                            response_timeout=15,
                            supervisory_timeout=10,
                            test_timeout=20,
                            send_window_size=12,
                            receive_window_size=8):
    conn_queue = aio.Queue()
    async with server(port=port,
                      connection_cb=conn_queue.put_nowait,
                      response_timeout=response_timeout,
                      supervisory_timeout=supervisory_timeout,
                      test_timeout=test_timeout,
                      send_window_size=send_window_size,
                      receive_window_size=receive_window_size):
        yield conn_queue


@contextlib.asynccontextmanager
async def mock_server(server_port,
                      connection_cb=lambda _: None,
                      bind_connections=True):
    server = await tcp.listen(connection_cb=connection_cb,
                              addr=tcp.Address(host='localhost',
                                               port=server_port),
                              bind_connections=bind_connections)
    try:
        yield server
    finally:
        await server.async_close()


@pytest.fixture
async def conn_queue(server_port):
    async with server_conn_queue(server_port) as cq:
        yield cq


async def test_connect(server_port):
    # connect failure, no server
    addr_srv = tcp.Address(host='127.0.0.1', port=server_port)
    with pytest.raises(ConnectionRefusedError):
        await apci.connect(addr=addr_srv)

    # mock_server does not respont with STARTDT_CON -> connect does not end
    async with mock_server(server_port):
        # response_timeout expires
        with pytest.raises(Exception):
            await apci.connect(addr=addr_srv, response_timeout=0.1)
        # response_timeout expires
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                apci.connect(addr=addr_srv, response_timeout=15), 0.1)

    async with server(server_port):
        conn = await apci.connect(addr=addr_srv, response_timeout=0.1)
        assert isinstance(conn, apci.Connection)
        assert conn.is_open

    assert conn.is_closed


async def test_server(server_port):
    conn_queue = aio.Queue()
    addr_srv = tcp.Address(host='127.0.0.1', port=server_port)

    server = await apci.listen(connection_cb=conn_queue.put_nowait,
                               addr=addr_srv)

    assert isinstance(server, apci.Server)
    assert server.is_open
    assert server.addresses == [addr_srv]

    conn_cli = await apci.connect(addr=addr_srv)
    conn_srv = await conn_queue.get()

    assert isinstance(conn_srv, apci.Connection)
    assert conn_srv.is_open
    assert conn_srv.info.local_addr == addr_srv

    assert conn_srv.info.local_addr == conn_cli.info.remote_addr
    assert conn_srv.info.remote_addr == conn_cli.info.local_addr

    await server.async_close()
    assert server.is_closed
    assert conn_cli.is_closed
    assert conn_srv.is_closed


async def test_connection(conn_queue, server_port):
    conn_cli = await apci.connect(
        addr=tcp.Address(host='127.0.0.1', port=server_port))
    conn_srv = await conn_queue.get()

    # client -> server
    asdu_data = b'\xab\x12'
    conn_cli.send(asdu_data)
    res = await conn_srv.receive()
    assert asdu_data == res

    # server -> client
    asdu_data = b'\xcd\x34\x56'
    conn_srv.send(asdu_data)
    res = await conn_cli.receive()
    assert asdu_data == res

    await conn_srv.async_close()
    await conn_cli.wait_closed()

    with pytest.raises(ConnectionError):
        conn_cli.send(asdu_data)

    with pytest.raises(ConnectionError):
        await conn_cli.receive()


@pytest.mark.skip(reason="implementation not done")
async def test_drain(server_port):
    supervisory_timeout = 0.1
    async with server_conn_queue(server_port,
                                 supervisory_timeout=supervisory_timeout,
                                 receive_window_size=15) as conn_queue:
        conn_cli = await apci.connect(
            addr=tcp.Address(host='127.0.0.1', port=server_port),
            send_window_size=10)
        conn_srv = await conn_queue.get()

        conn_cli.send(b'\xab\x12')
        await asyncio.wait_for(conn_cli.drain(), 0.1)

        conn_srv.send(b'\xab\x12')
        await asyncio.wait_for(conn_srv.drain(), 0.1)

        # ack does not arrive until receive window size is full or
        # until supervisory timeout elapsed
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(conn_cli.drain(wait_ack=True), 0.05)
        await conn_cli.drain(wait_ack=True)

        # messages are not sent becaues there are more than send_window_size
        # so drain should not end until supervisory timeout elapses
        for _ in range(15):
            conn_cli.send(b'\xab\x12')
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(conn_cli.drain(), 0.05)
        await conn_cli.drain()

        await conn_cli.async_close()


async def test_window_size_supervisory_timeout(server_port):
    send_window_size = 10
    receive_window_size = 15
    supervisory_timeout = 0.1
    async with server_conn_queue(
            server_port,
            receive_window_size=receive_window_size,
            supervisory_timeout=supervisory_timeout) as conn_queue:

        conn_cli = await apci.connect(
            addr=tcp.Address(host='127.0.0.1', port=server_port),
            send_window_size=send_window_size)
        conn_srv = await conn_queue.get()

        for i in range(send_window_size + 5):
            conn_cli.send((i).to_bytes(1, byteorder='little'))

        for i in range(send_window_size):
            asdu_bytes = await conn_srv.receive()
            assert i == int.from_bytes(asdu_bytes, byteorder='little')

        # client sends 10 (send_window_size) out of 15 because waits for ack,
        # but server does not send ack until receives 15 (receive_window_size)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(conn_srv.receive(), 0.05)

        for i in range(send_window_size, send_window_size + 5):
            asdu_bytes = await conn_srv.receive()
            assert i == int.from_bytes(asdu_bytes, byteorder='little')


async def test_test_timeout(server_port):
    conn_queue = aio.Queue()

    async def on_conn(conn):
        conn_queue.put_nowait(conn)
        await conn.readexactly(6)
        conn.write(
            encoder.encode(common.APDUU(common.ApduFunction.STARTDT_CON)))

    test_timeout = 0.1
    response_timeout = 0.1
    async with mock_server(server_port, connection_cb=on_conn,
                           bind_connections=False):
        conn = await apci.connect(
            addr=tcp.Address(host='127.0.0.1', port=server_port),
            test_timeout=test_timeout, response_timeout=response_timeout)
        assert conn.is_open
        conn_srv = await conn_queue.get()

    # tcp server is closed, apci conn closes after ->
    # test_timeout + response_timeout
    await asyncio.sleep(0.05)
    assert conn.is_open
    await conn.wait_closed()

    await conn_srv.async_close()
