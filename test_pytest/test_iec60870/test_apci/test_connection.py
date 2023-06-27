import asyncio

import pytest

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.iec60870 import apci
from hat.drivers.iec60870.apci import common
from hat.drivers.iec60870.apci import encoder


pytestmark = pytest.mark.timeout(1)


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def test_connect(addr):
    srv_conn_queue = aio.Queue()
    srv = await apci.listen(srv_conn_queue.put_nowait, addr)

    conn = await apci.connect(addr)
    assert conn.is_open

    await conn.async_close()
    await srv.async_close()


async def test_connect_no_server(addr):
    with pytest.raises(ConnectionRefusedError):
        await apci.connect(addr)


async def test_connect_no_startdt_con(addr):
    srv_conn_queue = aio.Queue()
    srv = await tcp.listen(srv_conn_queue.put_nowait, addr)

    with pytest.raises(Exception):
        await apci.connect(addr, response_timeout=0.1)

    srv_conn = await srv_conn_queue.get()
    await srv_conn.async_close()
    await srv.async_close()


async def test_listen(addr):
    srv_conn_queue = aio.Queue()
    srv = await apci.listen(srv_conn_queue.put_nowait, addr)

    assert srv.is_open
    assert srv.addresses == [addr]

    conn = await apci.connect(addr)
    srv_conn = await srv_conn_queue.get()

    assert srv_conn.is_open
    assert srv_conn.info.local_addr == addr

    assert srv_conn.info.local_addr == conn.info.remote_addr
    assert srv_conn.info.remote_addr == conn.info.local_addr

    await srv.async_close()
    assert srv_conn.is_closed

    await conn.wait_closed()


async def test_send_receive(addr):
    conn_queue = aio.Queue()
    srv = await apci.listen(conn_queue.put_nowait, addr)
    conn1 = await apci.connect(addr)
    conn2 = await conn_queue.get()

    asdu_data = b'\xab\x12'
    await conn1.send(asdu_data)
    res = await conn2.receive()
    assert asdu_data == res

    asdu_data = b'\xcd\x34\x56'
    await conn2.send(asdu_data)
    res = await conn1.receive()
    assert asdu_data == res

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()

    with pytest.raises(ConnectionError):
        await conn1.send(asdu_data)

    with pytest.raises(ConnectionError):
        await conn2.receive()


async def test_drain(addr):
    conn_queue = aio.Queue()
    srv = await apci.listen(conn_queue.put_nowait, addr,
                            supervisory_timeout=0.1,
                            receive_window_size=15)
    conn1 = await apci.connect(addr,
                               send_window_size=10)
    conn2 = await conn_queue.get()

    await conn1.send(b'\xab\x12')
    await asyncio.wait_for(conn1.drain(), 0.1)

    await conn2.send(b'\xab\x12')
    await asyncio.wait_for(conn2.drain(), 0.1)

    # messages are not sent becaues there are more than send_window_size
    # so drain should not end until supervisory timeout elapses
    for _ in range(15):
        await conn1.send(b'\xab\x12')
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(conn1.drain(), 0.05)
    await conn1.drain()

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


async def test_window_size_supervisory_timeout(addr):
    send_window_size = 10
    receive_window_size = 15

    conn_queue = aio.Queue()
    srv = await apci.listen(conn_queue.put_nowait, addr,
                            supervisory_timeout=0.1,
                            receive_window_size=receive_window_size)
    conn1 = await apci.connect(addr,
                               send_window_size=send_window_size)
    conn2 = await conn_queue.get()

    for i in range(send_window_size + 5):
        await conn1.send((i).to_bytes(1, byteorder='little'))

    for i in range(send_window_size):
        asdu_bytes = await conn2.receive()
        assert i == int.from_bytes(asdu_bytes, byteorder='little')

    # client sends 10 (send_window_size) out of 15 because waits for ack,
    # but server does not send ack until receives 15 (receive_window_size)
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(conn2.receive(), 0.05)

    for i in range(send_window_size, send_window_size + 5):
        asdu_bytes = await conn2.receive()
        assert i == int.from_bytes(asdu_bytes, byteorder='little')

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


async def test_test_timeout(addr):
    conn_queue = aio.Queue()

    async def on_connection(conn):
        conn_queue.put_nowait(conn)

        await conn.readexactly(6)

        apdu = common.APDUU(common.ApduFunction.STARTDT_CON)
        apdu_bytes = encoder.encode(apdu)
        await conn.write(apdu_bytes)

    srv = await tcp.listen(on_connection, addr,
                           bind_connections=False)
    conn1 = await apci.connect(addr,
                               test_timeout=0.1,
                               response_timeout=0.1)
    conn2 = await conn_queue.get()
    await srv.async_close()

    # tcp server is closed, apci conn closes after ->
    # test_timeout + response_timeout
    await asyncio.sleep(0.05)
    assert conn1.is_open
    await conn1.wait_closed()

    await conn2.async_close()
