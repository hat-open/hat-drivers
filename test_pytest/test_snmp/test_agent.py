import asyncio
import pytest

from hat import util
from hat import aio

from hat.drivers import snmp
from hat.drivers import udp
from hat.drivers.snmp import encoder


@pytest.fixture
def addr():
    return udp.Address('127.0.0.1', util.get_unused_udp_port())


async def test_create(addr):
    agent = await snmp.create_agent(local_addr=addr)

    assert isinstance(agent, snmp.Agent)
    assert agent.is_open

    agent.close()
    await agent.wait_closing()
    assert agent.is_closing
    await agent.wait_closed()
    assert agent.is_closed


@pytest.mark.parametrize('msg_type', [encoder.v1.MsgType.GET_REQUEST,
                                      encoder.v1.MsgType.GET_NEXT_REQUEST])
@pytest.mark.parametrize('data', [
    [],
    [snmp.IntegerData(name=(1, 2, 3), value=100)],
    [snmp.StringData(name=(1, 2, 3), value='xyz'),
     snmp.ArbitraryData(name=(1, 3, 2), value=b'zyx')]
])
@pytest.mark.parametrize('error', [
    None,
    snmp.Error(type=snmp.ErrorType.NO_SUCH_NAME, index=3)
])
async def test_v1_get_req_res(addr, msg_type, data, error):
    request_id = 42
    community = 'abc'

    def on_request_cb(addr, comm, req):
        assert comm == community
        assert list(req.names) == [i.name for i in data]
        return error or data

    agent = await snmp.create_agent(local_addr=addr,
                                    v1_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v1.Msg(
        type=msg_type,
        community=community,
        pdu=encoder.v1.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.EmptyData(name=i.name) for i in data]))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v1.MsgType.GET_RESPONSE
    assert res_msg.community == community
    assert res_msg.pdu.request_id == request_id

    if error:
        assert res_msg.pdu.error == error
        assert list(res_msg.pdu.data) == []

    else:
        assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
        assert list(res_msg.pdu.data) == data

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('data', [
    [],
    [snmp.IntegerData(name=(1, 2, 3), value=100)],
    [snmp.StringData(name=(1, 2, 3), value='xyz'),
     snmp.ArbitraryData(name=(1, 3, 2), value=b'zyx')]
])
@pytest.mark.parametrize('error', [
    None,
    snmp.Error(type=snmp.ErrorType.GEN_ERR, index=42)
])
async def test_v1_set_req_res(addr, data, error):
    request_id = 42
    community = 'abc'

    def on_request_cb(addr, comm, req):
        assert comm == community
        assert isinstance(req, snmp.SetDataReq)
        assert list(req.data) == data
        return error or data

    agent = await snmp.create_agent(local_addr=addr,
                                    v1_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v1.Msg(
        type=encoder.v1.MsgType.SET_REQUEST,
        community=community,
        pdu=encoder.v1.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=data))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v1.MsgType.GET_RESPONSE
    assert res_msg.community == community
    assert res_msg.pdu.request_id == request_id

    if error:
        assert res_msg.pdu.error == error
        assert list(res_msg.pdu.data) == []

    else:
        assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
        assert list(res_msg.pdu.data) == data

    await endpoint.async_close()
    await agent.async_close()


async def test_v1_request_cb_exception(addr, caplog):
    request_id = 42
    community = 'abc'
    exception_msg = 'test request cb exception'

    def on_request_cb(addr, comm, req):
        raise Exception(exception_msg)

    agent = await snmp.create_agent(local_addr=addr,
                                    v1_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v1.Msg(
        type=encoder.v1.MsgType.GET_REQUEST,
        community=community,
        pdu=encoder.v1.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.IntegerData(
                name=(1, 2, 3),
                value=100)]))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v1.MsgType.GET_RESPONSE
    assert res_msg.community == community
    assert res_msg.pdu.request_id == request_id
    assert res_msg.pdu.error.type == snmp.ErrorType.GEN_ERR
    assert res_msg.pdu.data == []

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert exception_msg in log_record.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('response', [
    [snmp.UnspecifiedData(name=(1, 2, 3))],
    ])
async def test_v1_invalid_response(addr, response, caplog):
    request_id = 42
    community = 'abc'

    def on_request_cb(addr, comm, req):
        return response

    agent = await snmp.create_agent(local_addr=addr,
                                    v1_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v1.Msg(
        type=encoder.v1.MsgType.GET_REQUEST,
        community=community,
        pdu=encoder.v1.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.EmptyData(name=(1, 2, 3))]))
    endpoint.send(encoder.encode(req_msg))

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('req_msg, log_msg', [
    (encoder.v2c.Msg(
            type=encoder.v2c.MsgType.GET_REQUEST,
            community='abc',
            pdu=encoder.v2c.BasicPdu(
                request_id=1,
                error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                data=[])),
     'not accepting V2C'),

    (encoder.v3.Msg(
                type=encoder.v3.MsgType.GET_REQUEST,
                id=1,
                reportable=False,
                context=snmp.Context(engine_id=b'', name=''),
                user='user_xyz',
                auth=False,
                priv=False,
                authorative_engine=encoder.v3.AuthorativeEngine(
                    id=b'',
                    boots=1234,
                    time=456),
                pdu=encoder.v3.BasicPdu(
                    request_id=1,
                    error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                    data=[snmp.IntegerData(name=(1, 2, 3), value=100)])),
     "not accepting V3")
    ])
async def test_v1_invalid_version(addr, caplog, req_msg, log_msg):

    def on_request_cb(addr, comm, req):
        pass

    agent = await snmp.create_agent(local_addr=addr,
                                    v1_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    endpoint.send(encoder.encode(req_msg))

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert log_msg in log_record.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('msg_type', [encoder.v2c.MsgType.GET_REQUEST,
                                      encoder.v2c.MsgType.GET_NEXT_REQUEST,
                                      encoder.v2c.MsgType.GET_BULK_REQUEST])
@pytest.mark.parametrize('data', [
    [],
    [snmp.IntegerData(name=(1, 2, 3), value=100)],
    [snmp.StringData(name=(1, 2, 3), value='xyz'),
     snmp.ArbitraryData(name=(1, 3, 2), value=b'zyx')]
])
@pytest.mark.parametrize('error', [
    None,
    snmp.Error(type=snmp.ErrorType.AUTHORIZATION_ERROR, index=3)
])
async def test_v2c_get_req_res(addr, msg_type, data, error):
    request_id = 42
    community = 'abc'

    def on_request_cb(addr, comm, req):
        assert comm == community
        assert list(req.names) == [i.name for i in data]
        return error or data

    agent = await snmp.create_agent(local_addr=addr,
                                    v2c_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    if msg_type == encoder.v2c.MsgType.GET_BULK_REQUEST:
        req_pdu = encoder.v2c.BulkPdu(
            request_id=request_id,
            non_repeaters=1,
            max_repetitions=2,
            data=[snmp.UnspecifiedData(name=i.name) for i in data])

    else:
        req_pdu = encoder.v2c.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.UnspecifiedData(name=i.name) for i in data])

    req_msg = encoder.v2c.Msg(type=msg_type,
                              community=community,
                              pdu=req_pdu)
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v2c.MsgType.RESPONSE
    assert res_msg.community == community
    assert res_msg.pdu.request_id == request_id

    if error:
        assert res_msg.pdu.error == error
        assert list(res_msg.pdu.data) == []

    else:
        assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
        assert list(res_msg.pdu.data) == data

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('data', [
    [],
    [snmp.IntegerData(name=(1, 2, 3), value=100)],
    [snmp.StringData(name=(1, 2, 3), value='xyz'),
     snmp.ArbitraryData(name=(1, 3, 2), value=b'zyx')]
])
@pytest.mark.parametrize('error', [
    None,
    snmp.Error(type=snmp.ErrorType.WRONG_TYPE, index=42)
])
async def test_v2c_set_req_res(addr, data, error):
    request_id = 42
    community = 'abc'

    def on_request_cb(addr, comm, req):
        assert comm == community
        assert isinstance(req, snmp.SetDataReq)
        assert list(req.data) == data
        return error or data

    agent = await snmp.create_agent(local_addr=addr,
                                    v2c_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v2c.Msg(
        type=encoder.v2c.MsgType.SET_REQUEST,
        community=community,
        pdu=encoder.v2c.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=data))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v2c.MsgType.RESPONSE
    assert res_msg.community == community
    assert res_msg.pdu.request_id == request_id

    if error:
        assert res_msg.pdu.error == error
        assert list(res_msg.pdu.data) == []

    else:
        assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
        assert list(res_msg.pdu.data) == data

    await endpoint.async_close()
    await agent.async_close()


async def test_v2c_request_cb_exception(addr, caplog):
    request_id = 42
    community = 'abc'
    exception_msg = 'test request cb exception'

    def on_request_cb(addr, comm, req):
        raise Exception(exception_msg)

    agent = await snmp.create_agent(local_addr=addr,
                                    v2c_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v2c.Msg(
        type=encoder.v2c.MsgType.GET_REQUEST,
        community=community,
        pdu=encoder.v2c.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.IntegerData(
                name=(1, 2, 3),
                value=100)]))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v2c.MsgType.RESPONSE
    assert res_msg.community == community
    assert res_msg.pdu.request_id == request_id
    assert res_msg.pdu.error.type == snmp.ErrorType.GEN_ERR
    assert res_msg.pdu.data == []

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert exception_msg in log_record.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('response', [
    [snmp.EmptyData(name=(1, 2, 3))],
    ])
async def test_v2c_invalid_response(addr, response, caplog):
    request_id = 42
    community = 'abc'

    def on_request_cb(addr, comm, req):
        return response

    agent = await snmp.create_agent(local_addr=addr,
                                    v2c_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v2c.Msg(
        type=encoder.v2c.MsgType.GET_REQUEST,
        community=community,
        pdu=encoder.v2c.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.UnspecifiedData(name=(1, 2, 3))]))
    endpoint.send(encoder.encode(req_msg))

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('req_msg, log_msg', [
    (encoder.v1.Msg(
            type=encoder.v1.MsgType.GET_REQUEST,
            community='abc',
            pdu=encoder.v1.BasicPdu(
                request_id=1,
                error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                data=[])),
     'not accepting V1'),

    (encoder.v3.Msg(
                type=encoder.v3.MsgType.GET_REQUEST,
                id=1,
                reportable=False,
                context=snmp.Context(engine_id=b'', name=''),
                user='user_xyz',
                auth=False,
                priv=False,
                authorative_engine=encoder.v3.AuthorativeEngine(
                    id=b'',
                    boots=1234,
                    time=456),
                pdu=encoder.v3.BasicPdu(
                    request_id=1,
                    error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                    data=[snmp.IntegerData(name=(1, 2, 3), value=100)])),
     "not accepting V3")
    ])
async def test_v2c_invalid_version(addr, caplog, req_msg, log_msg):

    def on_request_cb(addr, comm, req):
        pass

    agent = await snmp.create_agent(local_addr=addr,
                                    v2c_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    endpoint.send(encoder.encode(req_msg))

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert log_msg in log_record.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('msg_type', [encoder.v3.MsgType.GET_REQUEST,
                                      encoder.v3.MsgType.GET_NEXT_REQUEST,
                                      encoder.v3.MsgType.GET_BULK_REQUEST])
@pytest.mark.parametrize('data', [
    [],
    [snmp.IntegerData(name=(1, 2, 3), value=100)],
    [snmp.StringData(name=(1, 2, 3), value='xyz'),
     snmp.ArbitraryData(name=(1, 3, 2), value=b'zyx')]
])
@pytest.mark.parametrize('error', [
    None,
    snmp.Error(type=snmp.ErrorType.AUTHORIZATION_ERROR, index=3)
])
@pytest.mark.parametrize('auth, priv', [
    (False, False),
    (True, False),
    (True, True)
])
async def test_v3_get_req_res(addr, msg_type, data, error, auth, priv):
    request_id = 42
    user = 'user name'
    engine_id = b'engine id'

    context = snmp.Context(engine_id=engine_id,
                           name='ctx name')

    auth_key = (snmp.create_key(key_type=snmp.KeyType.MD5,
                                password='pass',
                                engine_id=engine_id)
                if auth else None)
    priv_key = (snmp.create_key(key_type=snmp.KeyType.DES,
                                password='pass',
                                engine_id=engine_id)
                if priv else None)

    def on_request_cb(addr, usr, ctx, req):
        assert usr == user
        assert ctx == context
        assert list(req.names) == [i.name for i in data]
        return error or data

    def on_auth_key(eid, usr):
        assert eid == engine_id
        assert usr == user
        return auth_key

    def on_priv_key(eid, usr):
        assert eid == engine_id
        assert usr == user
        return priv_key

    agent = await snmp.create_agent(local_addr=addr,
                                    v3_request_cb=on_request_cb,
                                    engine_ids=[engine_id],
                                    auth_key_cb=on_auth_key,
                                    priv_key_cb=on_priv_key)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=1,
        reportable=True,
        auth=False,
        priv=False,
        authorative_engine=encoder.v3.AuthorativeEngine(id=b'',
                                                        boots=0,
                                                        time=0),
        user='',
        context=snmp.Context(engine_id=b'',
                             name=''),
        pdu=encoder.v3.BasicPdu(
            request_id=1,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[]))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v3.MsgType.REPORT
    authorative_engine = res_msg.authorative_engine

    if msg_type == encoder.v3.MsgType.GET_BULK_REQUEST:
        req_pdu = encoder.v3.BulkPdu(
            request_id=request_id,
            non_repeaters=1,
            max_repetitions=2,
            data=[snmp.UnspecifiedData(name=i.name) for i in data])

    else:
        req_pdu = encoder.v3.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.UnspecifiedData(name=i.name) for i in data])

    req_msg = encoder.v3.Msg(type=msg_type,
                             id=123,
                             reportable=True,
                             auth=auth,
                             priv=priv,
                             authorative_engine=authorative_engine,
                             user=user,
                             context=context,
                             pdu=req_pdu)
    endpoint.send(encoder.encode(req_msg,
                                 auth_key=auth_key,
                                 priv_key=priv_key))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes,
                             auth_key_cb=on_auth_key,
                             priv_key_cb=on_priv_key)

    assert res_msg.type == encoder.v3.MsgType.RESPONSE
    assert res_msg.context == context
    assert res_msg.pdu.request_id == request_id

    if error:
        assert res_msg.pdu.error == error
        assert list(res_msg.pdu.data) == []

    else:
        assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
        assert list(res_msg.pdu.data) == data

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('auth, priv', [
    (False, False),
    (True, False),
    (True, True)
])
async def test_v3_sync_report(addr, auth, priv):
    engine_id = b'engine id'

    auth_key = (snmp.create_key(key_type=snmp.KeyType.MD5,
                                password='pass',
                                engine_id=engine_id)
                if auth else None)
    priv_key = (snmp.create_key(key_type=snmp.KeyType.DES,
                                password='pass',
                                engine_id=engine_id)
                if priv else None)

    def on_request_cb(addr, usr, ctx, req):
        return []

    def on_auth_key(eid, usr):
        return auth_key

    def on_priv_key(eid, usr):
        return priv_key

    agent = await snmp.create_agent(local_addr=addr,
                                    v3_request_cb=on_request_cb,
                                    engine_ids=[engine_id],
                                    auth_key_cb=on_auth_key,
                                    priv_key_cb=on_priv_key)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=123,
        reportable=True,
        auth=False,
        priv=False,
        authorative_engine=encoder.v3.AuthorativeEngine(id=b'',
                                                        boots=0,
                                                        time=0),
        user='',
        context=snmp.Context(engine_id=b'',
                             name=''),
        pdu=encoder.v3.BasicPdu(
            request_id=456,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[]))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v3.MsgType.REPORT
    assert res_msg.authorative_engine.id == engine_id
    assert res_msg.id == req_msg.id
    assert res_msg.reportable is False
    assert res_msg.context == req_msg.context
    assert res_msg.user == req_msg.user
    assert res_msg.auth is False
    assert res_msg.priv is False
    assert res_msg.authorative_engine.boots == 0
    assert res_msg.authorative_engine.time > 0

    assert res_msg.pdu.request_id == req_msg.pdu.request_id
    assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
    assert res_msg.pdu.data == []

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('data', [
    [],
    [snmp.IntegerData(name=(1, 2, 3), value=100)],
    [snmp.StringData(name=(1, 2, 3), value='xyz'),
     snmp.ArbitraryData(name=(1, 3, 2), value=b'zyx')]
])
@pytest.mark.parametrize('error', [
    None,
    snmp.Error(type=snmp.ErrorType.AUTHORIZATION_ERROR, index=3)
])
@pytest.mark.parametrize('auth, priv', [
    (False, False),
    (True, False),
    (True, True)
])
async def test_v3_set_req_res(addr, data, error, auth, priv):
    user = 'user name'
    engine_id = b'engine id'

    context = snmp.Context(engine_id=engine_id,
                           name='ctx name')

    auth_key = (snmp.create_key(key_type=snmp.KeyType.MD5,
                                password='pass',
                                engine_id=engine_id)
                if auth else None)
    priv_key = (snmp.create_key(key_type=snmp.KeyType.DES,
                                password='pass',
                                engine_id=engine_id)
                if priv else None)

    def on_request_cb(addr, usr, ctx, req):
        assert usr == user
        assert ctx == context
        assert list(req.data) == data
        return error or data

    def on_auth_key(eid, usr):
        assert eid == engine_id
        assert usr == user
        return auth_key

    def on_priv_key(eid, usr):
        assert eid == engine_id
        assert usr == user
        return priv_key

    agent = await snmp.create_agent(local_addr=addr,
                                    v3_request_cb=on_request_cb,
                                    engine_ids=[engine_id],
                                    auth_key_cb=on_auth_key,
                                    priv_key_cb=on_priv_key)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.SET_REQUEST,
        id=12345,
        reportable=False,
        auth=auth,
        priv=priv,
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=engine_id,
            boots=0,
            time=123),
        user=user,
        context=context,
        pdu=encoder.v3.BasicPdu(
            request_id=23456,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=data))
    endpoint.send(encoder.encode(req_msg,
                                 auth_key=auth_key,
                                 priv_key=priv_key))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes,
                             auth_key_cb=on_auth_key,
                             priv_key_cb=on_priv_key)

    assert res_msg.type == encoder.v3.MsgType.RESPONSE
    assert res_msg.context == context
    assert res_msg.id == req_msg.id
    assert res_msg.pdu.request_id == req_msg.pdu.request_id

    if error:
        assert res_msg.pdu.error == error
        assert list(res_msg.pdu.data) == []

    else:
        assert res_msg.pdu.error == snmp.Error(snmp.ErrorType.NO_ERROR, 0)
        assert list(res_msg.pdu.data) == data

    await endpoint.async_close()
    await agent.async_close()


async def test_v3_request_cb_exception(addr, caplog):
    request_id = 42
    context = snmp.Context(engine_id=b'engine_cntx', name='xyz')
    exception_msg = 'test request cb exception'
    engine_id = b'engine id'

    def on_request_cb(addr, usr, ctx, req):
        raise Exception(exception_msg)

    agent = await snmp.create_agent(local_addr=addr,
                                    engine_ids=[engine_id],
                                    v3_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=1,
        reportable=False,
        context=context,
        user='user_xyz',
        auth=False,
        priv=False,
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=engine_id,
            boots=1234,
            time=456),
        pdu=encoder.v3.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.IntegerData(name=(1, 2, 3), value=100)]))
    endpoint.send(encoder.encode(req_msg))

    res_msg_bytes, _ = await endpoint.receive()
    res_msg = encoder.decode(res_msg_bytes)

    assert res_msg.type == encoder.v2c.MsgType.RESPONSE
    assert res_msg.context == context
    assert res_msg.pdu.request_id == request_id
    assert res_msg.pdu.error.type == snmp.ErrorType.GEN_ERR
    assert res_msg.pdu.data == []

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert exception_msg in log_record.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('auth, priv', [
    (False, False),
    (True, False),
    (True, True)
])
async def test_invalid_auth_engine_id(addr, caplog, auth, priv):

    engine_id = b'engine'
    invalid_engine_id = b'invalid engine'

    auth_key = (snmp.create_key(key_type=snmp.KeyType.MD5,
                                password='pass',
                                engine_id=engine_id)
                if auth else None)
    priv_key = (snmp.create_key(key_type=snmp.KeyType.DES,
                                password='pass',
                                engine_id=engine_id)
                if priv else None)

    req_queue = aio.Queue()

    async def request_cb(address, user, context, request):
        req_queue.put_nowait(request)
        return []

    def on_auth_key(engine_id, user):
        return auth_key

    def on_priv_key(engine_id, user):
        return priv_key

    agent = await snmp.create_agent(
        local_addr=addr,
        v3_request_cb=request_cb,
        engine_ids=[engine_id],
        auth_key_cb=on_auth_key,
        priv_key_cb=on_priv_key)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=1,
        reportable=False,
        context=snmp.Context(engine_id=b'engine_cntx', name='xyz'),
        user='user_xyz',
        auth=bool(auth_key),
        priv=bool(priv_key),
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=invalid_engine_id,
            boots=1234,
            time=456),
        pdu=encoder.v3.BasicPdu(
            request_id=1,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[]))

    endpoint.send(encoder.encode(req_msg,
                                 auth_key=auth_key, priv_key=priv_key))
    await asyncio.sleep(0.01)
    assert req_queue.empty()

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_msg = caplog.records[0]
    assert log_msg.levelname == 'WARNING'
    assert "invalid authorative engine id" in log_msg.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('key_type', [
    snmp.KeyType.MD5,
    snmp.KeyType.SHA
])
async def test_invalid_auth_flag(addr, caplog, key_type):

    engine_id = b'engine'

    auth_key = snmp.create_key(key_type=key_type,
                               password='pass',
                               engine_id=engine_id)

    req_queue = aio.Queue()

    async def request_cb(address, user, context, request):
        req_queue.put_nowait(request)
        return []

    def on_auth_key(engine_id, user):
        return auth_key

    agent = await snmp.create_agent(
        local_addr=addr,
        v3_request_cb=request_cb,
        engine_ids=[engine_id],
        auth_key_cb=on_auth_key)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=1,
        reportable=False,
        context=snmp.Context(engine_id=b'engine_cntx', name='xyz'),
        user='user_xyz',
        auth=False,
        priv=False,
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=engine_id,
            boots=1234,
            time=456),
        pdu=encoder.v3.BasicPdu(
            request_id=1,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[]))

    endpoint.send(encoder.encode(req_msg,
                                 auth_key=auth_key))
    await asyncio.sleep(0.01)
    assert req_queue.empty()

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_msg = caplog.records[0]
    assert log_msg.levelname == 'WARNING'
    assert "invalid auth flag" in log_msg.message

    await endpoint.async_close()
    await agent.async_close()


async def test_invalid_priv_flag(addr, caplog):

    engine_id = b'engine'

    auth_key = snmp.create_key(key_type=snmp.KeyType.MD5,
                               password='pass',
                               engine_id=engine_id)

    priv_key = snmp.create_key(key_type=snmp.KeyType.DES,
                               password='pass',
                               engine_id=engine_id)

    req_queue = aio.Queue()

    async def request_cb(address, user, context, request):
        req_queue.put_nowait(request)
        return []

    def on_auth_key(engine_id, user):
        return auth_key

    def on_priv_key(engine_id, user):
        return priv_key

    agent = await snmp.create_agent(
        local_addr=addr,
        v3_request_cb=request_cb,
        engine_ids=[engine_id],
        auth_key_cb=on_auth_key,
        priv_key_cb=on_priv_key)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=1,
        reportable=False,
        context=snmp.Context(engine_id=b'engine_cntx', name='xyz'),
        user='user_xyz',
        auth=True,
        priv=False,
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=engine_id,
            boots=1234,
            time=456),
        pdu=encoder.v3.BasicPdu(
            request_id=1,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[]))

    endpoint.send(encoder.encode(req_msg,
                                 auth_key=auth_key))
    await asyncio.sleep(0.01)
    assert req_queue.empty()

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_msg = caplog.records[0]
    assert log_msg.levelname == 'WARNING'
    assert "invalid priv flag" in log_msg.message

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('response', [
    [snmp.EmptyData(name=(1, 2, 3))],
    ])
async def test_v3_invalid_response(addr, caplog, response):
    request_id = 42
    context = snmp.Context(engine_id=b'engine_cntx', name='xyz')
    engine_id = b'engine id'

    def on_request_cb(addr, usr, ctx, req):
        return response

    agent = await snmp.create_agent(local_addr=addr,
                                    engine_ids=[engine_id],
                                    v3_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    req_msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.GET_REQUEST,
        id=1,
        reportable=False,
        context=context,
        user='user_xyz',
        auth=False,
        priv=False,
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=engine_id,
            boots=1234,
            time=456),
        pdu=encoder.v3.BasicPdu(
            request_id=request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[snmp.IntegerData(name=(1, 2, 3), value=100)]))
    endpoint.send(encoder.encode(req_msg))

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'

    await endpoint.async_close()
    await agent.async_close()


@pytest.mark.parametrize('req_msg, log_msg', [
    (encoder.v1.Msg(
            type=encoder.v1.MsgType.GET_REQUEST,
            community='abc',
            pdu=encoder.v1.BasicPdu(
                request_id=1,
                error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                data=[])),
     'not accepting V1'),

    (encoder.v2c.Msg(
            type=encoder.v2c.MsgType.GET_REQUEST,
            community='abc',
            pdu=encoder.v2c.BasicPdu(
                request_id=1,
                error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                data=[])),
     'not accepting V2C'),
    ])
async def test_v3_invalid_version(addr, caplog, req_msg, log_msg):

    def on_request_cb(addr, comm, req):
        pass

    agent = await snmp.create_agent(local_addr=addr,
                                    v3_request_cb=on_request_cb)

    endpoint = await udp.create(remote_addr=addr)

    endpoint.send(encoder.encode(req_msg))

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.receive(), timeout=0.01)

    assert caplog.records
    log_record = caplog.records[0]
    assert log_record.levelname == 'WARNING'
    assert log_msg in log_record.message

    await endpoint.async_close()
    await agent.async_close()
