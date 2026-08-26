import asyncio
import collections

import pytest

from hat import aio

from hat.drivers import serial
from hat.drivers.iec60870.link import balanced
from hat.drivers.iec60870.link import endpoint
from hat.drivers.iec60870.link import common


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

    @property
    def info(self):
        return serial.EndpointInfo(name=None,
                                   port='')

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

    async def drain(self):
        pass


async def test_create(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE, addrs=[1])

    assert a.is_open
    assert b.is_open

    await a.async_close()
    await b.async_close()


async def test_connect(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_fut = a.async_group.spawn(
        a.open_connection, direction=common.Direction.A_TO_B, addr=1)
    b_conn = await b.open_connection(direction=common.Direction.B_TO_A, addr=1)

    a_conn = await a_conn_fut

    assert a_conn.is_open
    assert b_conn.is_open

    await a.async_close()
    await b.async_close()


async def test_response_ack(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)

    ep = await endpoint.create(port='1',
                               address_size=common.AddressSize.ONE,
                               direction_valid=True)

    a_conn_fut = a.async_group.spawn(
        a.open_connection, direction=common.Direction.A_TO_B, addr=1)
    req = await ep.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.RESET_LINK

    await ep.send(common.ResFrame(direction=common.Direction.B_TO_A,
                                  access_demand=False,
                                  data_flow_control=False,
                                  function=common.ResFunction.ACK,
                                  address=req.address,
                                  data=b''))
    a_conn = await a_conn_fut
    assert a_conn.is_open

    await a.async_close()
    await ep.async_close()


@pytest.mark.parametrize('exceeded', [True, False])
@pytest.mark.parametrize('send_retry_count', [1, 5])
async def test_send_retry_count(mock_serial, send_retry_count, exceeded):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)

    b_endpoint = await endpoint.create(
        port='1',
        address_size=common.AddressSize.ONE,
        direction_valid=True)

    a_conn_fut = a.async_group.spawn(
        a.open_connection,
        direction=common.Direction.A_TO_B,
        addr=1,
        send_retry_count=send_retry_count,
        response_timeout=0.01)
    req = await b_endpoint.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.RESET_LINK

    await b_endpoint.send(common.ShortFrame())
    a_conn = await a_conn_fut
    assert a_conn.is_open

    send_group = a.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(a_conn.send, b'hello')
    received_first = await b_endpoint.receive()
    assert received_first.data == b'hello'

    for i in range(send_retry_count):
        received_retry = await b_endpoint.receive()
        assert received_retry == received_first

    assert not send_future.done()

    if exceeded:
        # no response after send_retry_count exceeded
        with pytest.raises(Exception):
            await send_future
        await a_conn.wait_closed()

    else:
        await b_endpoint.send(common.ShortFrame())
        await send_future
        assert a_conn.is_open

    await a.async_close()
    await b_endpoint.async_close()


async def test_send_receive(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_fut = a.async_group.spawn(
        a.open_connection, direction=common.Direction.A_TO_B, addr=1)
    b_conn = await b.open_connection(direction=common.Direction.B_TO_A, addr=1)
    a_conn = await a_conn_fut

    await a_conn.send(b'hello')
    received = await b_conn.receive()
    assert received == b'hello'

    await b_conn.send(b'hi')
    received = await a_conn.receive()
    assert received == b'hi'

    await a_conn.send(b'sup')
    received = await b_conn.receive()
    assert received == b'sup'

    await b_conn.send(b'nth')
    received = await a_conn.receive()
    assert received == b'nth'

    await a.async_close()
    await b.async_close()


@pytest.mark.parametrize('with_ack, req_function', [
    (True, common.ReqFunction.DATA),
    (False, common.ReqFunction.DATA_NO_RES)])
async def test_send_with_ack(mock_serial, with_ack, req_function):
    send_retry_count = 3

    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_fut = a.async_group.spawn(
        a.open_connection,
        direction=common.Direction.A_TO_B,
        addr=1,
        send_retry_count=send_retry_count,
        response_timeout=0.01)

    b_endpoint = await endpoint.create(
        port='1',
        address_size=common.AddressSize.ONE,
        direction_valid=True)
    await b_endpoint.receive()
    await b_endpoint.send(common.ShortFrame())
    await b_endpoint.drain()

    a_conn = await a_conn_fut

    send_group = a.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(a_conn.send, b'hello', with_ack=with_ack)
    req_first = await b_endpoint.receive()
    assert req_first.data == b'hello'
    assert req_first.function == req_function

    if with_ack:
        for i in range(send_retry_count):
            req_retry = await b_endpoint.receive()
            assert req_retry == req_first

        assert not send_future.done()
        with pytest.raises(Exception):
            await send_future
        await a_conn.wait_closed()

    else:
        await send_future
        assert a_conn.is_open

    await a.async_close()
    await b_endpoint.async_close()


async def test_multiple(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_1_fut = a.async_group.spawn(
        a.open_connection, direction=common.Direction.A_TO_B, addr=1)
    b_conn_1 = await b.open_connection(
        direction=common.Direction.B_TO_A, addr=1)
    a_conn_2_fut = a.async_group.spawn(
        a.open_connection, direction=common.Direction.A_TO_B, addr=2)
    b_conn_2 = await b.open_connection(
        direction=common.Direction.B_TO_A, addr=2)

    a_conn_1 = await a_conn_1_fut
    a_conn_2 = await a_conn_2_fut

    await a_conn_1.send(b'hello')
    received = await b_conn_1.receive()
    assert received == b'hello'

    await b_conn_1.send(b'hi')
    received = await a_conn_1.receive()
    assert received == b'hi'

    await a_conn_2.send(b'sup')
    received = await b_conn_2.receive()
    assert received == b'sup'

    await b_conn_2.send(b'nth')
    received = await a_conn_2.receive()
    assert received == b'nth'

    await a.async_close()
    await b.async_close()


async def test_link_close(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_fut = a.async_group.spawn(a.open_connection,
                                     direction=common.Direction.A_TO_B,
                                     addr=1,
                                     response_timeout=0.01,
                                     send_retry_count=1,
                                     status_delay=0.01)
    await b.open_connection(direction=common.Direction.B_TO_A,
                            addr=1,
                            response_timeout=0.01,
                            send_retry_count=1,
                            status_delay=0.01)
    a_conn = await a_conn_fut

    assert a_conn.is_open
    await b.async_close()
    await a_conn.wait_closed()
    with pytest.raises(ConnectionError):
        await a_conn.send(b'hi')
    with pytest.raises(ConnectionError):
        await a_conn.receive()

    await a.async_close()


async def test_connection_close(mock_serial):
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_fut = a.async_group.spawn(a.open_connection,
                                     direction=common.Direction.A_TO_B,
                                     addr=1,
                                     response_timeout=0.01,
                                     send_retry_count=1,
                                     status_delay=0.01)
    b_conn = await b.open_connection(direction=common.Direction.B_TO_A,
                                     addr=1,
                                     response_timeout=0.01,
                                     send_retry_count=1,
                                     status_delay=0.01)
    a_conn = await a_conn_fut

    assert a_conn.is_open
    await b_conn.async_close()
    await a_conn.wait_closed()
    assert a.is_open
    assert b.is_open
    with pytest.raises(ConnectionError):
        await a_conn.send(b'hi')
    with pytest.raises(ConnectionError):
        await a_conn.receive()

    await a.async_close()
    await b.async_close()


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
    a = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    b = await balanced.create_balanced_link(
        port='1', address_size=common.AddressSize.ONE)
    a_conn_fut = a.async_group.spawn(a.open_connection,
                                     direction=common.Direction.A_TO_B,
                                     addr=1,
                                     response_timeout=0.01,
                                     send_retry_count=1)
    b_conn = await b.open_connection(direction=common.Direction.B_TO_A,
                                     addr=1,
                                     response_timeout=0.01,
                                     send_retry_count=1)
    a_conn = await a_conn_fut

    # TODO should not use private
    await b._endpoint._endpoint.extend_data(noise)

    await a_conn.send(b'hello')
    received = await b_conn.receive()
    assert received == b'hello'

    # TODO should not use private
    await a._endpoint._endpoint.extend_data(noise)

    await b_conn.send(b'hi')
    received = await a_conn.receive()
    assert received == b'hi'

    await a.async_close()
    await b.async_close()
