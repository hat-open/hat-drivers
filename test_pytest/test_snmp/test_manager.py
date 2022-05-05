import asyncio
import pytest

from hat import aio
from hat import util
from hat.drivers import snmp
from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp.encoder import v1, v2c


@pytest.fixture
def agent_addr():
    return udp.Address('127.0.0.1', util.get_unused_tcp_port())


async def create_mock_agent(addr):
    agent = MockAgent()
    agent._receive_queue = aio.Queue()
    agent._endpoint = await udp.create(local_addr=addr,
                                       remote_addr=None)
    agent.async_group.spawn(agent._receive_loop)
    return agent


class MockAgent(aio.Resource):

    @property
    def async_group(self):
        return self._endpoint.async_group

    @property
    def receive_queue(self):
        return self._receive_queue

    def send(self, msg, manager_addr):
        self._endpoint.send(encoder.encode(msg), manager_addr)

    async def _receive_loop(self):
        while True:
            received = await self._endpoint.receive()
            self._receive_queue.put_nowait(received)


def req_to_msg_type(req, version):
    if isinstance(req, snmp.GetDataReq):
        return v1.MsgType.GET_REQUEST
    if isinstance(req, snmp.GetNextDataReq):
        return v1.MsgType.GET_NEXT_REQUEST
    if isinstance(req, snmp.SetDataReq):
        return v1.MsgType.SET_REQUEST


def req_to_data(req):
    if isinstance(req, (snmp.GetDataReq,
                        snmp.GetNextDataReq,
                        snmp.GetBulkDataReq)):
        return [snmp.Data(type=snmp.DataType.EMPTY,
                          name=i,
                          value=None) for i in req.names]
    if isinstance(req, (snmp.SetDataReq,
                        snmp.InformReq)):
        return req.data


def resp_msg_from_resp(resp, community, request_id):
    if isinstance(resp, list):
        data = resp
        error = snmp.Error(type=snmp.ErrorType.NO_ERROR,
                           index=0)
    elif isinstance(resp, snmp.Error):
        data = []
        error = resp
    return v1.Msg(type=v1.MsgType.GET_RESPONSE,
                  community=community,
                  pdu=v1.BasicPdu(
                    request_id=request_id,
                    error=error,
                    data=data))


async def test_create(agent_addr):
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='def'),
        remote_addr=agent_addr,
        version=snmp.Version.V1)
    assert isinstance(manager, snmp.Manager)
    assert manager.is_open

    manager.close()
    await manager.wait_closing()
    assert manager.is_closing
    await manager.wait_closed()
    assert manager.is_closed


@pytest.mark.parametrize("req", [
    snmp.GetDataReq(names=[]),
    snmp.GetDataReq(names=[(1, 2), (1, 2, 3), (1, 2, 456)]),
    snmp.GetNextDataReq(names=[]),
    snmp.GetNextDataReq(names=[(1, 2), (1, 2, 3), (1, 2, 456)]),
    snmp.SetDataReq(data=[]),
    snmp.SetDataReq(data=[
        snmp.Data(type=snmp.DataType.INTEGER,
                  name=(1, 2, 3, i),
                  value=123 + i) for i in range(10)]),
    ])
@pytest.mark.parametrize("response_exp", [
    [],
    [snmp.Data(type=snmp.DataType.INTEGER,
               name=(1, 2, 3, i),
               value=123 + i) for i in range(10)],
    [snmp.Data(type=dtype,
               name=(1, 2, 3, 4, 5, 10),
               value=value) for dtype, value in (
                    (snmp.DataType.INTEGER, 123),
                    (snmp.DataType.IP_ADDRESS, (192, 168, 11, 33)))],
    snmp.Error(type=snmp.ErrorType.TOO_BIG, index=0),
    snmp.Error(type=snmp.ErrorType.NO_SUCH_NAME, index=0),
    snmp.Error(type=snmp.ErrorType.BAD_VALUE, index=0),
    snmp.Error(type=snmp.ErrorType.READ_ONLY, index=0),
    snmp.Error(type=snmp.ErrorType.GEN_ERR, index=0),
    ])
async def test_send(agent_addr, req, response_exp):
    version = snmp.Version.V1
    community = 'xyz'
    agent = await create_mock_agent(agent_addr)
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name=community),
        remote_addr=agent_addr,
        version=version)

    # sends request
    req_f = manager.async_group.spawn(manager.send, req)
    req_bytes, manager_addr = await agent.receive_queue.get()
    req_msg = encoder.decode(req_bytes)
    assert req_msg.type == req_to_msg_type(req, version)
    assert req_msg.community == community
    assert req_msg.pdu == v1.BasicPdu(
        request_id=1,
        error=snmp.Error(type=snmp.ErrorType.NO_ERROR,
                         index=0),
        data=req_to_data(req))
    assert not req_f.done()

    # receives response
    resp_msg = resp_msg_from_resp(
        response_exp, community, req_msg.pdu.request_id)
    agent.send(resp_msg, manager_addr)
    response = await req_f
    assert isinstance(response, (list,
                                 snmp.Error))
    assert response == response_exp
    assert agent.receive_queue.empty()

    await manager.async_close()
    await agent.async_close()


async def test_send_on_closing(agent_addr):
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='def'),
        remote_addr=agent_addr,
        version=snmp.Version.V1)
    assert manager.is_open

    manager.close()
    await manager.wait_closing()
    with pytest.raises(ConnectionError):
        await manager.send(snmp.GetDataReq(names=[]))

    await manager.async_close()


async def test_request_id(agent_addr):
    version = snmp.Version.V1
    agent = await create_mock_agent(agent_addr)
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='xyz'),
        remote_addr=agent_addr,
        version=version)

    for req_id_exp in range(1, 10 + 1):
        manager.async_group.spawn(
            manager.send, snmp.GetDataReq(names=[(1, 2, 3)]))
        req_bytes, _ = await agent.receive_queue.get()
        req_msg = encoder.decode(req_bytes)
        assert req_msg.pdu.request_id == req_id_exp
    assert agent.receive_queue.empty()

    await manager.async_close()
    await agent.async_close()


@pytest.mark.parametrize("invalid_request", [
    snmp.GetBulkDataReq(names=[]),
    snmp.InformReq(data=[]),
    ])
async def test_invalid_request(agent_addr, invalid_request):
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='def'),
        remote_addr=agent_addr,
        version=snmp.Version.V1)
    assert manager.is_open

    with pytest.raises(ValueError):
        await manager.send(snmp.GetBulkDataReq(names=[]))

    await manager.async_close()


@pytest.mark.parametrize("msg_class, msg_type, request_id", [
    (v1.Msg, v1.MsgType.GET_RESPONSE, 2),
    (v1.Msg, v1.MsgType.GET_NEXT_REQUEST, 1),
    (v1.Msg, v1.MsgType.GET_REQUEST, 1),
    (v1.Msg, v1.MsgType.GET_REQUEST, 1),
    (v2c.Msg, v2c.MsgType.RESPONSE, 2),
    ])
async def test_invalid_response(agent_addr, msg_class, msg_type, request_id,
                                caplog):
    version = snmp.Version.V1
    community = 'xyz'
    agent = await create_mock_agent(agent_addr)
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name=community),
        remote_addr=agent_addr,
        version=version)

    req_f = manager.async_group.spawn(manager.send, snmp.GetDataReq(names=[]))

    _, manager_addr = await agent.receive_queue.get()

    resp_msg = msg_class(
        type=msg_type,
        community=community,
        pdu=v1.BasicPdu(
            request_id=request_id,
            error=snmp.Error(type=snmp.ErrorType.NO_ERROR,
                             index=0),
            data=[]))
    agent.send(resp_msg, manager_addr)
    await asyncio.sleep(0.01)
    assert not req_f.done()
    invalid_response_log = caplog.records[0]
    assert invalid_response_log.levelname == 'WARNING'

    await manager.async_close()
    await agent.async_close()

    await manager.async_close()
