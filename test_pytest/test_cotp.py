import asyncio

import pytest

from hat import util

from hat.drivers import cotp
from hat.drivers import tcp


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def test_example_docs():
    addr = tcp.Address('127.0.0.1', util.get_unused_tcp_port())

    conn2_future = asyncio.Future()
    srv = await cotp.listen(conn2_future.set_result, addr)
    conn1 = await cotp.connect(addr)
    conn2 = await conn2_future

    # send from conn1 to conn2
    data = b'123'
    await conn1.send(data)
    result = await conn2.receive()
    assert result == data

    # send from conn2 to conn1
    data = b'321'
    await conn2.send(data)
    result = await conn1.receive()
    assert result == data

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()
