import pytest

from hat import aio
from hat import util

from hat.drivers import chatter
from hat.drivers import tcp


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def test_connect_listen(addr):
    with pytest.raises(Exception):
        await chatter.connect(addr)

    conn_queue = aio.Queue()
    srv = await chatter.listen(conn_queue.put_nowait, addr)
    conn1 = await chatter.connect(addr)
    conn2 = await conn_queue.get()

    assert srv.is_open
    assert conn1.is_open
    assert conn2.is_open

    assert srv.addresses == [addr]
    assert conn1.info.remote_addr == addr
    assert conn2.info.local_addr == addr

    await conn1.async_close()
    await srv.async_close()

    await conn2.wait_closed()


async def test_send_receive(addr):
    conn_queue = aio.Queue()
    srv = await chatter.listen(conn_queue.put_nowait, addr)
    conn1 = await chatter.connect(addr)
    conn2 = await conn_queue.get()

    data = chatter.Data('abc', b'xyz')

    conv1 = await conn1.send(data, last=False)
    assert conv1.owner is True

    msg = await conn2.receive()
    assert msg.data == data
    assert msg.conv.owner is False
    assert msg.conv.first_id == conv1.first_id
    assert msg.first is True
    assert msg.last is False
    assert msg.token is True

    data = chatter.Data('xyz', b'abc')

    conv2 = await conn2.send(data, conv=msg.conv)
    assert conv2 == msg.conv

    msg = await conn1.receive()
    assert msg.data == data
    assert msg.conv == conv1
    assert msg.first is False
    assert msg.last is True
    assert msg.token is True

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()

    with pytest.raises(ConnectionError):
        await conn1.send(data)

    with pytest.raises(ConnectionError):
        await conn2.receive()


async def test_ping_timeout(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)
    conn = await chatter.connect(addr,
                                 ping_delay=0.01,
                                 ping_timeout=0.01)

    assert conn.is_open
    await aio.wait_for(conn.wait_closed(), 0.1)

    await srv.async_close()
