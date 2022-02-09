import asyncio
import collections

import pytest

from hat import aio
from hat.drivers import serial
from hat.drivers.iec60870.link import unbalanced

pytestmark = pytest.mark.asyncio


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

    async def write(self, data: bytes):
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
