import pytest

from hat import aio
from hat.drivers import udp
from hat.drivers import snmp
from hat.drivers.snmp import encoder


@pytest.fixture
def agent_address(unused_tcp_port_factory):
    return udp.Address('127.0.0.1', unused_tcp_port_factory())


@pytest.fixture
async def endpoint_factory(agent_address):
    endpoints = set()

    async def factory():
        endpoint = await udp.create(remote_addr=agent_address, local_addr=None)
        endpoints.add(endpoint)
        return endpoint

    yield factory

    for endpoint in endpoints:
        await endpoint.async_close()


@pytest.fixture
async def agent_factory(agent_address):
    agents = set()

    async def factory(request_cb):
        agent = await snmp.create_agent(request_cb, agent_address)
        agents.add(agent)
        return agent

    yield factory

    for agent in agents:
        await agent.async_close()


@pytest.mark.parametrize("req_msg, req_expected, res", [
    (encoder.v1.Msg(type=encoder.v1.MsgType.GET_REQUEST,
                    community='abc',
                    pdu=encoder.v1.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=100)])),
     snmp.GetDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.INTEGER, name=(1, 2, 3), value=100)]),

    (encoder.v1.Msg(type=encoder.v1.MsgType.GET_NEXT_REQUEST,
                    community='abc',
                    pdu=encoder.v1.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=100)])),
     snmp.GetNextDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.OBJECT_ID,
                name=(1, 2, 3),
                value=(1, 6, 7))]),

    (encoder.v1.Msg(type=encoder.v1.MsgType.SET_REQUEST,
                    community='abc',
                    pdu=encoder.v1.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=55)])),
     snmp.SetDataReq([snmp.Data(type=snmp.DataType.INTEGER,
                                name=(1, 2, 3),
                                value=55)]),
     [snmp.Data(type=snmp.DataType.INTEGER, name=(1, 2, 3), value=55)]),

    (encoder.v1.Msg(type=encoder.v1.MsgType.SET_REQUEST,
                    community='abc',
                    pdu=encoder.v1.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=55)])),
     snmp.SetDataReq([snmp.Data(type=snmp.DataType.INTEGER,
                                name=(1, 2, 3),
                                value=55)]),
     snmp.Error(type=snmp.ErrorType.NO_SUCH_NAME, index=3)),

    (encoder.v2c.Msg(type=encoder.v2c.MsgType.GET_REQUEST,
                     community='abc',
                     pdu=encoder.v2c.BasicPdu(
                         request_id=1,
                         error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                         data=[snmp.Data(
                             type=snmp.DataType.INTEGER,
                             name=(1, 2, 3),
                             value=100)])),
     snmp.GetDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.INTEGER, name=(1, 2, 3), value=100)]),

    (encoder.v2c.Msg(type=encoder.v2c.MsgType.GET_BULK_REQUEST,
                     community='abc',
                     pdu=encoder.v2c.BulkPdu(
                         request_id=1,
                         non_repeaters=0,
                         max_repetitions=0,
                         data=[snmp.Data(
                             type=snmp.DataType.INTEGER,
                             name=(1, 2, 3),
                             value=100)])),
     snmp.GetBulkDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.INTEGER, name=(1, 2, 3), value=100)]),

    (encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                    id=1,
                    reportable=False,
                    context=snmp.Context(engine_id='abc', name='xyz'),
                    pdu=encoder.v3.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=100)])),
     snmp.GetDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.INTEGER, name=(1, 2, 3), value=100)]),
])
async def test_request_response(req_msg, req_expected, res,
                                agent_factory, endpoint_factory):
    req_queue = aio.Queue()
    res_queue = aio.Queue()

    async def request_cb(context, request):
        req_queue.put_nowait((context, request))
        return await res_queue.get()

    await agent_factory(request_cb)
    endpoint = await endpoint_factory()

    endpoint.send(encoder.encode(req_msg))
    context, received_req = await req_queue.get()

    assert received_req == req_expected
    if not isinstance(req_msg, encoder.v3.Msg):
        assert context == snmp.Context(None, req_msg.community)
    else:
        assert context == req_msg.context

    res_queue.put_nowait(res)
    msg_bytes, _ = await endpoint.receive()
    msg_res = encoder.decode(msg_bytes)

    if not isinstance(res, snmp.Error):
        expected_data = res
        expected_error = snmp.Error(snmp.ErrorType.NO_ERROR, 0)
    else:
        expected_data = req_msg.pdu.data
        expected_error = res

    assert msg_res.pdu.error == expected_error
    assert msg_res.pdu.data == expected_data
    assert msg_res.pdu.request_id == req_msg.pdu.request_id

    if isinstance(req_msg, encoder.v1.Msg):
        assert isinstance(msg_res, encoder.v1.Msg)
        assert msg_res.type == encoder.v1.MsgType.GET_RESPONSE
        assert msg_res.community == req_msg.community

    elif isinstance(req_msg, encoder.v2c.Msg):
        assert isinstance(msg_res, encoder.v2c.Msg)
        assert msg_res.type == encoder.v2c.MsgType.RESPONSE
        assert msg_res.community == req_msg.community

    elif isinstance(req_msg, encoder.v3.Msg):
        assert isinstance(msg_res, encoder.v3.Msg)
        assert msg_res.type == encoder.v3.MsgType.RESPONSE
        assert msg_res.id == req_msg.id
        assert msg_res.reportable == req_msg.reportable
        assert msg_res.context == req_msg.context


@pytest.mark.parametrize("req_msg, req_expected, res", [
    (encoder.v1.Msg(type=encoder.v1.MsgType.GET_REQUEST,
                    community='abc',
                    pdu=encoder.v1.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=100)])),
     snmp.GetDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.UNSPECIFIED, name=(1, 2, 3), value=None)]),

    (encoder.v2c.Msg(type=encoder.v2c.MsgType.GET_REQUEST,
                     community='abc',
                     pdu=encoder.v2c.BasicPdu(
                         request_id=1,
                         error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                         data=[snmp.Data(
                             type=snmp.DataType.INTEGER,
                             name=(1, 2, 3),
                             value=100)])),
     snmp.GetDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.EMPTY, name=(1, 2, 3), value=None)]),

    (encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                    id=1,
                    reportable=False,
                    context=snmp.Context(engine_id='abc', name='xyz'),
                    pdu=encoder.v3.BasicPdu(
                        request_id=1,
                        error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
                        data=[snmp.Data(
                            type=snmp.DataType.INTEGER,
                            name=(1, 2, 3),
                            value=100)])),
     snmp.GetDataReq([(1, 2, 3)]),
     [snmp.Data(type=snmp.DataType.EMPTY, name=(1, 2, 3), value=None)]),
])
async def test_request_response_invalid(req_msg, req_expected, res,
                                        agent_factory, endpoint_factory):
    req_queue = aio.Queue()
    res_queue = aio.Queue()

    async def request_cb(context, request):
        req_queue.put_nowait((context, request))
        return await res_queue.get()

    await agent_factory(request_cb)
    endpoint = await endpoint_factory()

    endpoint.send(encoder.encode(req_msg))
    context, received_req = await req_queue.get()

    assert received_req == req_expected
    if not isinstance(req_msg, encoder.v3.Msg):
        assert context == snmp.Context(None, req_msg.community)
    else:
        assert context == req_msg.context

    res_queue.put_nowait(res)
    msg_bytes, _ = await endpoint.receive()
    msg_res = encoder.decode(msg_bytes)

    assert msg_res.pdu.error == snmp.Error(snmp.ErrorType.GEN_ERR, 0)
    assert msg_res.pdu.data == req_msg.pdu.data
    assert msg_res.pdu.request_id == req_msg.pdu.request_id

    if isinstance(req_msg, encoder.v1.Msg):
        assert isinstance(msg_res, encoder.v1.Msg)
        assert msg_res.type == encoder.v1.MsgType.GET_RESPONSE
        assert msg_res.community == req_msg.community

    elif isinstance(req_msg, encoder.v2c.Msg):
        assert isinstance(msg_res, encoder.v2c.Msg)
        assert msg_res.type == encoder.v2c.MsgType.RESPONSE
        assert msg_res.community == req_msg.community

    elif isinstance(req_msg, encoder.v3.Msg):
        assert isinstance(msg_res, encoder.v3.Msg)
        assert msg_res.type == encoder.v3.MsgType.RESPONSE
        assert msg_res.id == req_msg.id
        assert msg_res.reportable == req_msg.reportable
        assert msg_res.context == req_msg.context
