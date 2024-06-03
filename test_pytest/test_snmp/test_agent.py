import pytest

from hat import util

from hat.drivers import snmp
from hat.drivers import udp
from hat.drivers.snmp import encoder


@pytest.fixture
def addr():
    return udp.Address('127.0.0.1', util.get_unused_udp_port())


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
