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

        if isinstance(req, transport.UnbindReq):
            return transport.UnbindRes()

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


async def test_connect_error(addr):
    client_system_id = 'client'
    password = 'password'

    def on_request(req):
        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)

    with pytest.raises(Exception):
        await smpp.connect(addr=addr,
                           system_id=client_system_id,
                           password=password)

    await server.async_close()


async def test_close(addr):
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

        if isinstance(req, transport.UnbindReq):
            return transport.UnbindRes()

        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)
    client = await smpp.connect(addr=addr,
                                system_id=client_system_id,
                                password=password)

    req = await req_queue.get()
    assert isinstance(req, transport.BindReq)

    await client.async_close()

    req = await req_queue.get()
    assert isinstance(req, transport.UnbindReq)

    await server.async_close()

    assert req_queue.empty()


async def test_enquire_link(addr):
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

        if isinstance(req, transport.UnbindReq):
            return transport.UnbindRes()

        if isinstance(req, transport.EnquireLinkReq):
            return transport.EnquireLinkRes()

        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)
    client = await smpp.connect(addr=addr,
                                system_id=client_system_id,
                                password=password,
                                enquire_link_delay=0.01)

    req = await req_queue.get()
    assert isinstance(req, transport.BindReq)

    for _ in range(5):
        req = await req_queue.get()
        assert isinstance(req, transport.EnquireLinkReq)

    await client.async_close()

    req = await req_queue.get()
    assert isinstance(req, transport.UnbindReq)

    await server.async_close()

    assert req_queue.empty()


async def test_enquire_link_timeout(addr):
    server_system_id = 'server'
    client_system_id = 'client'
    password = 'password'

    async def on_request(req):
        if isinstance(req, transport.BindReq):
            return transport.BindRes(bind_type=req.bind_type,
                                     system_id=server_system_id,
                                     optional_params={})

        if isinstance(req, transport.UnbindReq):
            return transport.UnbindRes()

        if isinstance(req, transport.EnquireLinkReq):
            await asyncio.sleep(1)
            return transport.EnquireLinkRes()

        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)
    client = await smpp.connect(addr=addr,
                                system_id=client_system_id,
                                password=password,
                                enquire_link_delay=0.01,
                                enquire_link_timeout=0.01,
                                close_timeout=0.01)

    await client.wait_closed()

    await server.async_close()


@pytest.mark.parametrize('short_message', [True, False])
@pytest.mark.parametrize('priority', transport.Priority)
@pytest.mark.parametrize('data_coding', list(transport.DataCoding)[:2])
@pytest.mark.parametrize('udhi', [True, False])
async def test_send_message(addr, short_message, priority, data_coding, udhi):
    req_queue = aio.Queue()

    server_system_id = 'server'
    client_system_id = 'client'
    password = 'password'
    message_id = b'123'
    dst_addr = '123456789'
    msg = b'message'

    def on_request(req):
        req_queue.put_nowait(req)

        if isinstance(req, transport.BindReq):
            return transport.BindRes(bind_type=req.bind_type,
                                     system_id=server_system_id,
                                     optional_params={})

        if isinstance(req, transport.UnbindReq):
            return transport.UnbindRes()

        if isinstance(req, transport.SubmitSmReq):
            return transport.SubmitSmRes(message_id=message_id)

        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)
    client = await smpp.connect(addr=addr,
                                system_id=client_system_id,
                                password=password)

    req = await req_queue.get()
    assert isinstance(req, transport.BindReq)

    res_message_id = await client.send_message(
        dst_addr=dst_addr,
        msg=msg,
        short_message=short_message,
        priority=priority,
        udhi=udhi,
        data_coding=data_coding)
    assert res_message_id == message_id

    req = await req_queue.get()
    assert isinstance(req, transport.SubmitSmReq)
    assert req.destination_addr == dst_addr
    assert req.priority_flag == priority
    assert req.data_coding == data_coding

    if short_message:
        assert req.short_message == msg
        assert transport.OptionalParamTag.MESSAGE_PAYLOAD not in req.optional_params  # NOQA

    else:
        assert req.short_message == b''
        assert req.optional_params[transport.OptionalParamTag.MESSAGE_PAYLOAD] == msg  # NOQA

    if udhi:
        assert transport.GsmFeature.UDHI in req.esm_class.gsm_features

    else:
        assert transport.GsmFeature.UDHI not in req.esm_class.gsm_features

    await client.async_close()
    await server.async_close()


async def test_send_message_error(addr):
    server_system_id = 'server'
    client_system_id = 'client'
    password = 'password'
    dst_addr = '123456789'
    msg = b'message'

    def on_request(req):
        if isinstance(req, transport.BindReq):
            return transport.BindRes(bind_type=req.bind_type,
                                     system_id=server_system_id,
                                     optional_params={})

        if isinstance(req, transport.UnbindReq):
            return transport.UnbindRes()

        if isinstance(req, transport.SubmitSmReq):
            return transport.CommandStatus.ESME_RSYSERR

        return transport.CommandStatus.ESME_RINVCMDID

    server = await create_server(addr,
                                 request_cb=on_request)
    client = await smpp.connect(addr=addr,
                                system_id=client_system_id,
                                password=password)

    with pytest.raises(Exception):
        await client.send_message(dst_addr=dst_addr,
                                  msg=msg)

    await client.async_close()
    await server.async_close()
