import asyncio
import collections

import pytest

from hat import aio
from hat.drivers import serial
from hat.drivers.iec60870.link import unbalanced


@pytest.fixture
async def mock_serial(monkeypatch):
    mock_connections = collections.deque()

    async def mock_create(*args, **kwargs):
        mock_connection = _MockSerialConnection(mock_connections)
        mock_connections.append(mock_connection)
        return mock_connection

    monkeypatch.setattr(serial, 'create', mock_create)


class _MockSerialConnection(aio.Resource):

    def __init__(self, mock_connections):
        self._async_group = aio.Group()
        self._mock_connections = mock_connections
        self._data = bytearray()
        self._cv = asyncio.Condition()

    @property
    def async_group(self):
        return self._async_group

    async def read(self, size):
        async with self._cv:
            await self._cv.wait_for(lambda: len(self._data) >= size)
            result = self._data[:size]
            self._data = self._data[size:]
            return bytes(result)

    async def write(self, data):
        for m_conn in self._mock_connections:
            if self is m_conn:
                continue
            if self.is_open and m_conn.is_open:
                m_conn._data.extend(data)
                async with m_conn._cv:
                    m_conn._cv.notify()


async def test_create(mock_serial):
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1', addrs=[1])
    assert master.is_open
    assert slave.is_open
    await master.async_close()
    await slave.async_close()


async def test_connect(mock_serial):
    queue = asyncio.Queue()
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1',
                                                addrs=[1],
                                                connection_cb=queue.put_nowait)
    master_conn = await master.connect(addr=1)
    slave_conn = await queue.get()

    assert master_conn.is_open
    assert slave_conn.is_open
    await master.async_close()
    await slave.async_close()


async def test_send_receive(mock_serial):
    queue = asyncio.Queue()
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1',
                                                addrs=[1],
                                                connection_cb=queue.put_nowait)
    master_conn = await master.connect(addr=1, poll_delay=0.01)
    slave_conn = await queue.get()

    await master_conn.send(b'hello')
    received = await slave_conn.receive()
    assert received == b'hello'

    await slave_conn.send(b'hi')
    received = await master_conn.receive()
    assert received == b'hi'

    await master_conn.send(b'sup')
    received = await slave_conn.receive()
    assert received == b'sup'

    await slave_conn.send(b'nth')
    received = await master_conn.receive()
    assert received == b'nth'

    await master.async_close()
    await slave.async_close()


async def test_slave_range(mock_serial):
    queue = asyncio.Queue()
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1',
                                                addrs=[1, 2],
                                                connection_cb=queue.put_nowait)
    master_conn_1 = await master.connect(addr=1, poll_delay=0.01)
    slave_conn_1 = await queue.get()
    master_conn_2 = await master.connect(addr=2, poll_delay=0.01)
    slave_conn_2 = await queue.get()

    await master_conn_1.send(b'hello')
    received = await slave_conn_1.receive()
    assert received == b'hello'

    await slave_conn_1.send(b'hi')
    received = await master_conn_1.receive()
    assert received == b'hi'

    await master_conn_2.send(b'sup')
    received = await slave_conn_2.receive()
    assert received == b'sup'

    await slave_conn_2.send(b'nth')
    received = await master_conn_2.receive()
    assert received == b'nth'

    await master.async_close()
    await slave.async_close()


@pytest.mark.parametrize("slave_count, poll_delay", [
    (1, 0.01),
    (2, 0.01),
    (5, 0.05)
])
async def test_multiple_slaves(mock_serial, slave_count, poll_delay):
    queue = asyncio.Queue()
    master = await unbalanced.master.create_master(port='1')
    slaves = []
    master_conns = []
    slave_conns = []
    for i in range(slave_count):
        slave = await unbalanced.slave.create_slave(
            port='1',
            addrs=[i],
            connection_cb=queue.put_nowait)
        master_conn = await master.connect(addr=i, poll_delay=poll_delay)
        slave_conn = await queue.get()
        slaves.append(slave)
        master_conns.append(master_conn)
        slave_conns.append(slave_conn)
    for i in range(slave_count):
        await master_conns[i].send(f'mtos {i}'.encode('utf-8'))
        received = await slave_conns[i].receive()
        assert received == f'mtos {i}'.encode('utf-8')

        await slave_conns[i].send(f'stom {i}'.encode('utf-8'))
        received = await master_conns[i].receive()
        assert received == f'stom {i}'.encode('utf-8')
    for i in range(slave_count):
        await slaves[i].async_close()
    await master.async_close()
