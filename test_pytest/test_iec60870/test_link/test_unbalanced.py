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

    async def extend_data(self, data):
        if self.is_open:
            self._data.extend(data)
            async with self._cv:
                self._cv.notify()

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
            if self.is_open:
                await m_conn.extend_data(data)


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
    master_conn = await master.connect(addr=1, poll_class1_delay=0.01)
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
    master_conn_1 = await master.connect(addr=1, poll_class1_delay=0.01)
    slave_conn_1 = await queue.get()
    master_conn_2 = await master.connect(addr=2, poll_class1_delay=0.01)
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
        master_conn = await master.connect(addr=i,
                                           poll_class1_delay=poll_delay)
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


async def test_disconnect_slave(mock_serial):
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1',
                                                addrs=[1])
    master_conn = await master.connect(addr=1,
                                       response_timeout=0.01,
                                       send_retry_count=1)
    assert master_conn.is_open
    await slave.async_close()
    await master_conn.wait_closed()
    with pytest.raises(ConnectionError):
        await master_conn.send(b'hi')
    with pytest.raises(ConnectionError):
        await master_conn.receive()
    await master.async_close()


async def test_disconnect_master(mock_serial):
    queue = asyncio.Queue()
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1',
                                                addrs=[1],
                                                connection_cb=queue.put_nowait,
                                                keep_alive_timeout=0.1)
    await master.connect(addr=1,
                         response_timeout=0.01,
                         send_retry_count=1)
    slave_conn = await queue.get()
    assert slave_conn.is_open
    await master.async_close()
    await slave_conn.wait_closed()
    with pytest.raises(ConnectionError):
        await slave_conn.send(b'hi')
    with pytest.raises(ConnectionError):
        await slave_conn.receive()
    await slave.async_close()


@pytest.mark.parametrize("noise", [
    b'noise',  # add noise to the channel
    b'\xe5',   # start of the short ack
    b'\x10',   # start of the fixed length frame
    b'\x68',   # start of the variable length frame
    b'\x10\x00\x01\x00',              # res uncomplete fix
    b'\x10\x00\x01\x00\xff\x16',      # res invalid checksum fix
    b'\x10\x00\x01\x00\x00\x01\x16',  # res too long fix
    b'\x10\x40\x01\x00',              # req uncomplete fix
    b'\x10\x40\x01\x00\xff\x16',      # req invalid checksum fix
    b'\x10\x40\x01\x00\x00\x41\x16',  # req too long fix
    b'\x68\x03\x03\x68\x00\x01\x00',              # res uncomplete var
    b'\x68\x03\x03\x68\x00\x01\x00\xff\x16',      # res invalid checksum var
    b'\x68\x03\x03\x68\x00\x01\x00\x00\x01\x16',  # res too long variable
    b'\x68\x03\x03\x68\x40\x01\x00',              # req uncomplete variable
    b'\x68\x03\x03\x68\x40\x01\x00\xff\x16',      # req invalid checksum var
    b'\x68\x03\x03\x68\x40\x01\x00\x00\x41\x16',  # req too long variable
    ])
async def test_channel_noise(mock_serial, noise):
    queue = asyncio.Queue()
    master = await unbalanced.master.create_master(port='1')
    slave = await unbalanced.slave.create_slave(port='1',
                                                addrs=[1],
                                                connection_cb=queue.put_nowait,
                                                keep_alive_timeout=0.1)
    master_conn = await master.connect(addr=1,
                                       response_timeout=0.01,
                                       poll_class1_delay=0.01)
    slave_conn = await queue.get()

    await slave._endpoint._conn.extend_data(noise)

    await master_conn.send(b'hello')
    received = await slave_conn.receive()
    assert received == b'hello'

    await master._endpoint._conn.extend_data(noise)

    await slave_conn.send(b'hi')
    received = await master_conn.receive()
    assert received == b'hi'

    await master.async_close()
    await slave.async_close()
