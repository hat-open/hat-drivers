import asyncio
import enum
import sys

import pytest

from hat import aio
from hat import util

from hat.drivers import net
from hat.drivers import serial
from hat.drivers.tls import l1


CommType = enum.Enum('CommType', ['TCP', 'UNIX', 'SERIAL'])


if sys.platform == 'win32':
    comm_types = [CommType.TCP]
else:
    comm_types = [CommType.TCP,
                  CommType.UNIX,
                  CommType.SERIAL]

net_comm_types = [i for i in comm_types if i != CommType.SERIAL]


@pytest.fixture
def tcp_addr():
    return net.TcpAddress('127.0.0.1', util.get_unused_tcp_port())


@pytest.fixture
def unix_addr(tmp_path):
    return tmp_path / 'sock'


@pytest.fixture
def patch_serial_read_timeout(monkeypatch):
    monkeypatch.setattr(serial.py_serial, 'read_timeout', 0.01)


@pytest.fixture
async def create_endpoints(tcp_addr, unix_addr, nullmodem,
                           patch_serial_read_timeout):
    endpoints = []

    async def create_endpoints(comm_type, link_cb_1=None, link_cb_2=None):
        queue_1 = aio.Queue()
        queue_2 = aio.Queue()

        if comm_type == CommType.SERIAL:
            endpoint_1 = await l1.create_serial_endpoint(
                link_cb=link_cb_1 or queue_1.put_nowait,
                port=str(nullmodem[0]),
                reconnect_delay=0.01)
            endpoint_2 = await l1.create_serial_endpoint(
                link_cb=link_cb_2 or queue_2.put_nowait,
                port=str(nullmodem[1]),
                reconnect_delay=0.01)

        else:
            addr = tcp_addr if comm_type == CommType.TCP else unix_addr
            endpoint_1 = await l1.create_net_server_endpoint(
                link_cb=link_cb_1 or queue_1.put_nowait,
                addr=addr)
            endpoint_2 = await l1.create_net_client_endpoint(
                link_cb=link_cb_2 or queue_2.put_nowait,
                addr=addr,
                reconnect_delay=0.01)

        endpoints.extend([endpoint_2, endpoint_1])
        return endpoint_1, endpoint_2, queue_1, queue_2

    yield create_endpoints

    for endpoint in endpoints:
        await endpoint.async_close()


async def get_link(queue):
    link = await asyncio.wait_for(queue.get(), 0.1)
    assert link.is_open
    return link


async def assert_no_link(queue):
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get(), 0.1)


async def write(link, data):
    await link.write(data)
    await link.drain()


async def read(link, size):
    return await asyncio.wait_for(link.read(size), 0.1)


@pytest.mark.parametrize('comm_type', comm_types)
async def test_create(create_endpoints, tcp_addr, nullmodem, comm_type):
    _, _, queue_1, queue_2 = await create_endpoints(comm_type)

    link_1 = await get_link(queue_1)
    link_2 = await get_link(queue_2)

    await assert_no_link(queue_1)
    await assert_no_link(queue_2)

    if comm_type == CommType.TCP:
        assert isinstance(link_1.info, net.TcpConnectionInfo)
        assert link_1.info.local_addr == tcp_addr
        assert link_1.info.remote_addr == link_2.info.local_addr

    elif comm_type == CommType.UNIX:
        assert isinstance(link_1.info, net.UnixConnectionInfo)

    else:
        assert isinstance(link_1.info, serial.EndpointInfo)
        assert link_1.info.port == str(nullmodem[0])
        assert link_2.info.port == str(nullmodem[1])


@pytest.mark.parametrize('comm_type', comm_types)
async def test_link_close(create_endpoints, comm_type):
    endpoint_1, endpoint_2, queue_1, queue_2 = await create_endpoints(
        comm_type)
    link_1 = await get_link(queue_1)
    link_2 = await get_link(queue_2)

    await link_2.async_close()

    with pytest.raises(Exception):
        await link_2.read(1)

    with pytest.raises(Exception):
        await write(link_2, b'\xe5')

    if comm_type == CommType.SERIAL:
        await asyncio.sleep(0.01)
        assert link_1.is_open

    else:
        await asyncio.wait_for(link_1.wait_closed(), 0.1)

    assert endpoint_1.is_open
    assert endpoint_2.is_open
    new_link_2 = await get_link(queue_2)

    await write(new_link_2, b'\xe5')
    new_link_1 = (link_1 if comm_type == CommType.SERIAL
                  else await get_link(queue_1))

    data = await read(new_link_1, 1)
    assert data == b'\xe5'


@pytest.mark.parametrize('comm_type', comm_types)
async def test_endpoint_close(create_endpoints, comm_type):
    _, endpoint_2, queue_1, queue_2 = await create_endpoints(comm_type)
    link_1 = await get_link(queue_1)
    link_2 = await get_link(queue_2)

    await endpoint_2.async_close()
    assert link_2.is_closed

    if comm_type != CommType.SERIAL:
        await asyncio.wait_for(link_1.wait_closed(), 0.1)

    await assert_no_link(queue_2)
    await assert_no_link(queue_1)


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('is_async', [False, True])
async def test_link_cb_error(create_endpoints, comm_type, is_async):
    links = aio.Queue()

    def on_link(link):
        links.put_nowait(link)
        raise Exception('error')

    async def on_link_async(link):
        on_link(link)

    endpoint_1, endpoint_2, _, _ = await create_endpoints(
        comm_type, link_cb_2=on_link_async if is_async else on_link)

    link = await asyncio.wait_for(links.get(), 0.1)
    await asyncio.wait_for(link.wait_closed(), 0.1)

    assert endpoint_2.is_open
    await asyncio.wait_for(links.get(), 0.1)


@pytest.mark.parametrize('comm_type', net_comm_types)
async def test_net_server_close(create_endpoints, comm_type):
    server, client, server_queue, client_queue = await create_endpoints(
        comm_type)
    server_link = await get_link(server_queue)
    client_link = await get_link(client_queue)

    await server.async_close()

    assert server_link.is_closed
    await asyncio.wait_for(client_link.wait_closed(), 0.1)

    assert client.is_open
    await assert_no_link(client_queue)


@pytest.mark.parametrize('comm_type', net_comm_types)
async def test_net_client_before_server(tcp_addr, unix_addr, comm_type):
    addr = tcp_addr if comm_type == CommType.TCP else unix_addr
    client_queue = aio.Queue()
    server_queue = aio.Queue()

    client = await l1.create_net_client_endpoint(
        link_cb=client_queue.put_nowait, addr=addr, reconnect_delay=0.01)

    await assert_no_link(client_queue)
    assert client.is_open

    server = await l1.create_net_server_endpoint(
        link_cb=server_queue.put_nowait, addr=addr)

    await get_link(client_queue)
    await get_link(server_queue)

    await client.async_close()
    await server.async_close()


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('data', [b'\xe5',
                                  b'\x10\x49\x01\x4a\x16',
                                  bytes(range(256))])
async def test_write_read(create_endpoints, comm_type, data):
    _, _, queue_1, queue_2 = await create_endpoints(comm_type)
    link_1 = await get_link(queue_1)
    link_2 = await get_link(queue_2)

    await write(link_1, data)
    read_data = await read(link_2, len(data))
    assert read_data == data

    await write(link_2, data)
    read_data = await read(link_1, len(data))
    assert read_data == data


@pytest.mark.parametrize('comm_type', comm_types)
async def test_read_exact_size(create_endpoints, comm_type):
    _, _, queue_1, queue_2 = await create_endpoints(comm_type)
    link_1 = await get_link(queue_1)
    link_2 = await get_link(queue_2)

    read_future = link_1.async_group.spawn(link_1.read, 5)

    # not enough
    await write(link_2, b'\x10\x49')
    await asyncio.sleep(0.01)
    assert not read_future.done()

    await write(link_2, b'\x01\x4a\x16\xe5')

    data = await asyncio.wait_for(read_future, 0.1)
    assert data == b'\x10\x49\x01\x4a\x16'

    await read_future

    data = await read(link_1, 1)
    assert data == b'\xe5'
