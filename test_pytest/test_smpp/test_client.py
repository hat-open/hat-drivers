import asyncio

import pytest

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers import smpp
from hat.drivers.smpp import transport


async def create_server(addr,
                        connection_cb=None,
                        request_cb=None,
                        notification_cb=None):

    async def on_connection(conn):
        try:
            conn = transport.Connection(conn=conn,
                                        request_cb=request_cb,
                                        notification_cb=notification_cb)

            if connection_cb is not None:
                await aio.call(connection_cb, conn)

            await conn.wait_closing()

        finally:
            await aio.uncancellable(conn.async_close())

    return await tcp.listen(connection_cb=on_connection,
                            addr=addr,
                            bind_connections=True)


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def test_connect(addr):
    req_queue = aio.Queue()

    server_system_id = 'server'
    client_system_id = 'client'
    password = 'password'

    def on_request(req):
        req_queue.put_nowait(req)

        if isinstance(req, transport.BindReq):
            return transport.BindRes(bind_type=req.bind_type,
                                     system_id=server_system_id,
                                     optional_params={})

        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)
    client = await smpp.connect(addr=addr,
                                system_id=client_system_id,
                                password=password)

    req = await req_queue.get()
    assert isinstance(req, transport.BindReq)
    assert req.bind_type == transport.BindType.TRANSCEIVER
    assert req.system_id == client_system_id
    assert req.password == password

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(req_queue.get(), 0.01)

    assert client.is_open

    await client.async_close()
    await server.async_close()


async def test_close():
    pass


async def test_enquire_link():
    pass


async def test_send_message():
    pass


async def test_send_message_error():
    pass
