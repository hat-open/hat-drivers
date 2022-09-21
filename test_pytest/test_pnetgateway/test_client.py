import asyncio

import pytest

from hat import util
from hat import aio
from hat.drivers import tcp

from hat.drivers.pnetgateway import client
from hat.drivers.pnetgateway import common
from hat.drivers.pnetgateway import encoder
from hat.drivers.pnetgateway import transport


data = common.Data(key='key',
                   value=123,
                   quality=common.Quality.GOOD,
                   timestamp=123456,
                   type=common.DataType.NUMERIC,
                   source=common.Source.REMOTE_SRC)

change = common.Change(key='key',
                       value=123,
                       quality=common.Quality.GOOD,
                       timestamp=123456,
                       source=common.Source.REMOTE_SRC)

cmd = common.Command(key='key',
                     value=123)


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def test_connect(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)

    status_queue = aio.Queue()
    data_queue = aio.Queue()
    conn1_future = asyncio.ensure_future(
        client.connect(addr=addr,
                       username='user1',
                       password='pass1',
                       status_cb=status_queue.put_nowait,
                       data_cb=data_queue.put_nowait))

    conn2 = await conn_queue.get()
    conn2 = transport.Transport(conn2)

    assert conn2.is_open
    assert not conn1_future.done()

    msg = await conn2.receive()
    assert msg == {'type': 'authentication_request',
                   'body': {'username': 'user1',
                            'password': 'pass1',
                            'subscriptions': None}}
    assert not conn1_future.done()

    conn2.send({'type': 'authentication_response',
                'body': {'success': True,
                         'status': 'CONNECTED',
                         'data': []}})
    conn1 = await conn1_future
    assert conn1.is_open

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


async def test_data_changed(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)

    status_queue = aio.Queue()
    data_queue = aio.Queue()
    conn1_future = asyncio.ensure_future(
        client.connect(addr=addr,
                       username='user1',
                       password='pass1',
                       status_cb=status_queue.put_nowait,
                       data_cb=data_queue.put_nowait))

    conn2 = await conn_queue.get()
    conn2 = transport.Transport(conn2)
    msg = await conn2.receive()
    assert msg['type'] == 'authentication_request'
    conn2.send({'type': 'authentication_response',
                'body': {'success': True,
                         'status': 'CONNECTED',
                         'data': [encoder.data_to_json(data)]}})
    conn1 = await conn1_future

    assert data_queue.empty()
    assert conn1.data == {data.key: data}

    for i in range(10):
        new_data = data._replace(value=i)
        conn2.send({'type': 'data_changed_unsolicited',
                    'body': {'data': [encoder.data_to_json(new_data)]}})
        change = await data_queue.get()
        assert change == [new_data]
        assert conn1.data == {new_data.key: new_data}

    assert data_queue.empty()

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


async def test_status_changed(addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)

    status_queue = aio.Queue()
    data_queue = aio.Queue()
    conn1_future = asyncio.ensure_future(
        client.connect(addr=addr,
                       username='user1',
                       password='pass1',
                       status_cb=status_queue.put_nowait,
                       data_cb=data_queue.put_nowait))

    conn2 = await conn_queue.get()
    conn2 = transport.Transport(conn2)
    msg = await conn2.receive()
    assert msg['type'] == 'authentication_request'
    conn2.send({'type': 'authentication_response',
                'body': {'success': True,
                         'status': 'CONNECTED',
                         'data': [encoder.data_to_json(data)]}})
    conn1 = await conn1_future

    assert conn1.pnet_status == common.Status.CONNECTED
    assert conn1.data == {data.key: data}

    conn2.send({'type': 'status_changed_unsolicited',
                'body': {'status': 'DISCONNECTED',
                         'data': []}})

    status = await status_queue.get()
    assert status == common.Status.DISCONNECTED
    assert conn1.data == {}

    conn2.send({'type': 'status_changed_unsolicited',
                'body': {'status': 'CONNECTED',
                         'data': [encoder.data_to_json(data)]}})

    status = await status_queue.get()
    assert conn1.pnet_status == common.Status.CONNECTED
    assert conn1.data == {data.key: data}

    assert data_queue.empty()

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


@pytest.mark.parametrize("success", [True, False])
async def test_change_data(success, addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)

    status_queue = aio.Queue()
    data_queue = aio.Queue()
    conn1_future = asyncio.ensure_future(
        client.connect(addr=addr,
                       username='user1',
                       password='pass1',
                       status_cb=status_queue.put_nowait,
                       data_cb=data_queue.put_nowait))

    conn2 = await conn_queue.get()
    conn2 = transport.Transport(conn2)
    msg = await conn2.receive()
    assert msg['type'] == 'authentication_request'
    conn2.send({'type': 'authentication_response',
                'body': {'success': True,
                         'status': 'CONNECTED',
                         'data': []}})
    conn1 = await conn1_future

    future = asyncio.ensure_future(
        conn1.change_data([change]))

    msg = await conn2.receive()
    assert msg['type'] == 'change_data_request'
    assert msg['body']['data'] == [encoder.change_to_json(change)]
    assert not future.done()

    conn2.send({'type': 'change_data_response',
                'body': {'id': msg['body']['id'],
                         'success': success}})
    result = await future

    assert result == success

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


@pytest.mark.parametrize("success", [True, False])
async def test_send_commands(success, addr):
    conn_queue = aio.Queue()
    srv = await tcp.listen(conn_queue.put_nowait, addr)

    status_queue = aio.Queue()
    data_queue = aio.Queue()
    conn1_future = asyncio.ensure_future(
        client.connect(addr=addr,
                       username='user1',
                       password='pass1',
                       status_cb=status_queue.put_nowait,
                       data_cb=data_queue.put_nowait))

    conn2 = await conn_queue.get()
    conn2 = transport.Transport(conn2)
    msg = await conn2.receive()
    assert msg['type'] == 'authentication_request'
    conn2.send({'type': 'authentication_response',
                'body': {'success': True,
                         'status': 'CONNECTED',
                         'data': []}})
    conn1 = await conn1_future

    future = asyncio.ensure_future(
        conn1.send_commands([cmd]))

    msg = await conn2.receive()
    assert msg['type'] == 'command_request'
    assert msg['body']['data'] == [encoder.command_to_json(cmd)]
    assert not future.done()

    conn2.send({'type': 'command_response',
                'body': {'id': msg['body']['id'],
                         'success': success}})
    result = await future

    assert result == success

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()
