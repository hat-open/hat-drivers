import asyncio

import pytest

from hat import aio
from hat import util

from hat.drivers import snmp
from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp.encoder import v1, v2c, v3


@pytest.fixture
def agent_addr():
    return udp.Address('127.0.0.1', util.get_unused_udp_port())


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


def req_to_msg_type(req):
    if isinstance(req, snmp.GetDataReq):
        return v1.MsgType.GET_REQUEST
    if isinstance(req, snmp.GetNextDataReq):
        return v1.MsgType.GET_NEXT_REQUEST
    if isinstance(req, snmp.SetDataReq):
        return v1.MsgType.SET_REQUEST


def req_to_data(req):
    if isinstance(req, snmp.SetDataReq):
        return req.data

    return [snmp.EmptyData(name=i) for i in req.names]


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
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community='abc')

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
        snmp.IntegerData(name=(1, 2, 3, i),
                         value=123 + i) for i in range(10)]),
    snmp.SetDataReq(data=[
        snmp.UnsignedData(name=(1, 2, 3),
                          value=123),
        snmp.CounterData(name=(1, 2, 3),
                         value=4567),
        snmp.StringData(name=(1, 2, 3),
                        value=b'abcd'),
        snmp.ObjectIdData(name=(1, 2, 3),
                          value=(1, 2, 3)),
        snmp.IpAddressData(name=(1, 2, 3),
                           value=(1, 2, 3)),
        snmp.TimeTicksData(name=(1, 2, 3),
                           value=123456),
        snmp.ArbitraryData(name=(1, 2, 3),
                           value=b'abc123')]),
    ])
@pytest.mark.parametrize("response_exp", [
    [],
    [snmp.IntegerData(
        name=(1, 2, 3, i),
        value=123 + i) for i in range(10)],
    [snmp.UnsignedData(name=(1, 2, 3),
                       value=123),
     snmp.CounterData(name=(1, 2, 3),
                      value=4567),
     snmp.StringData(name=(1, 2, 3),
                     value=b'abcd'),
     snmp.ObjectIdData(name=(1, 2, 3),
                       value=(1, 2, 3)),
     snmp.IpAddressData(name=(1, 2, 3),
                        value=(1, 2, 3)),
     snmp.TimeTicksData(name=(1, 2, 3),
                        value=123456),
     snmp.ArbitraryData(name=(1, 2, 3),
                        value=b'abc123')],
    snmp.Error(type=snmp.ErrorType.TOO_BIG, index=1),
    snmp.Error(type=snmp.ErrorType.NO_SUCH_NAME, index=2),
    snmp.Error(type=snmp.ErrorType.BAD_VALUE, index=3),
    snmp.Error(type=snmp.ErrorType.READ_ONLY, index=4),
    snmp.Error(type=snmp.ErrorType.GEN_ERR, index=5),
    ])
@pytest.mark.parametrize('community', ['xyz', 'abcdefg'])
async def test_send(agent_addr, req, response_exp, community):
    agent = await create_mock_agent(agent_addr)

    manager = await snmp.create_v1_manager(remote_addr=agent_addr,
                                           community=community)

    async with aio.Group() as group:
        # sends request
        req_f = group.spawn(manager.send, req)
        req_bytes, manager_addr = await agent.receive_queue.get()
        req_msg = encoder.decode(req_bytes)
        assert req_msg.type == req_to_msg_type(req)
        assert req_msg.community == community
        request_id = req_msg.pdu.request_id
        assert isinstance(request_id, int)
        assert req_msg.pdu == v1.BasicPdu(
            request_id=request_id,
            error=snmp.Error(type=snmp.ErrorType.NO_ERROR,
                             index=0),
            data=req_to_data(req))
        assert not req_f.done()

        # receives response
        resp_msg = resp_msg_from_resp(
            response_exp, community, req_msg.pdu.request_id)
        agent.send(resp_msg, manager_addr)
        response = await req_f
        assert response == response_exp
        assert agent.receive_queue.empty()

    await manager.async_close()
    await agent.async_close()


async def test_send_no_agent(agent_addr):
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community='comm_xyz')

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(manager.send(snmp.GetDataReq(names=[])), 0.1)

    await manager.async_close()


async def test_send_on_closing(agent_addr):
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community='comm_xyz')
    assert manager.is_open

    manager.close()
    await manager.wait_closing()
    with pytest.raises(ConnectionError):
        await manager.send(snmp.GetDataReq(names=[]))

    await manager.async_close()


async def test_close_on_send(agent_addr):
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community='comm_xyz')

    async with aio.Group(log_exceptions=False) as group:
        send_future = group.spawn(manager.send, snmp.GetDataReq(names=[]))
        await asyncio.sleep(0.01)

        manager.close()

        with pytest.raises(ConnectionError):
            await send_future

    await manager.async_close()


async def test_request_id(agent_addr, caplog):
    community = 'comm_xyz'

    agent = await create_mock_agent(agent_addr)
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community=community)

    async with aio.Group() as group:
        send_future = group.spawn(manager.send, snmp.GetDataReq(names=[]))
        req_bytes, manager_addr = await agent.receive_queue.get()
        req_msg = encoder.decode(req_bytes)
        assert req_msg.pdu.request_id

        # no response on wrong request_id
        resp_msg = resp_msg_from_resp(
            [], community, req_msg.pdu.request_id + 123)
        agent.send(resp_msg, manager_addr)
        with pytest.raises(asyncio.TimeoutError):
            await aio.wait_for(asyncio.shield(send_future), 0.05)
        assert manager.is_open
        invalid_response_log = caplog.records[0]
        assert invalid_response_log.levelname == 'WARNING'

        # response on correct request_id
        resp_msg = resp_msg_from_resp([], community, req_msg.pdu.request_id)
        agent.send(resp_msg, manager_addr)
        await send_future

        # next request has greater request_id
        send_future = group.spawn(manager.send, snmp.GetDataReq(names=[]))
        req_bytes, manager_addr = await agent.receive_queue.get()
        req_msg_2 = encoder.decode(req_bytes)
        assert req_msg_2.pdu.request_id > req_msg.pdu.request_id

    await manager.async_close()
    await agent.async_close()


@pytest.mark.parametrize('invalid_request', [
    snmp.GetBulkDataReq(names=[]),  # not supported in v1
    snmp.GetDataReq(names=[('a')]),  # invalid object identifier
    ])
async def test_invalid_request(agent_addr, invalid_request):
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community='comm_xyz')

    with pytest.raises(ValueError):
        await manager.send(invalid_request)

    assert manager.is_open

    await manager.async_close()


@pytest.mark.parametrize(
    "version_module, msg_type, community", [
        (v1, v1.MsgType.GET_RESPONSE, 'abc'),  # community
        (v1, v1.MsgType.GET_NEXT_REQUEST, 'comm_xyz'),  # msg_type
        (v1, v1.MsgType.GET_REQUEST, 'comm_xyz'),  # msg_type
        (v2c, v2c.MsgType.RESPONSE, 'comm_xyz'),  # version
        (v3, v3.MsgType.RESPONSE, 'comm_xyz'),  # version
    ])
async def test_invalid_response(agent_addr, version_module, msg_type,
                                community, caplog):
    agent = await create_mock_agent(agent_addr)
    manager = await snmp.create_v1_manager(
        remote_addr=agent_addr,
        community='comm_xyz')

    async with aio.Group() as group:
        req_f = group.spawn(manager.send, snmp.GetDataReq(names=[]))

        req_bytes, manager_addr = await agent.receive_queue.get()
        req_msg = encoder.decode(req_bytes)

        pdu = version_module.BasicPdu(
            request_id=req_msg.pdu.request_id,
            error=snmp.Error(type=snmp.ErrorType.NO_ERROR, index=0),
            data=[])

        if version_module.__name__.endswith('v3'):
            resp_msg = v3.Msg(
                type=msg_type,
                id=123,
                reportable=False,
                auth=False,
                priv=False,
                authorative_engine=v3.AuthorativeEngine(
                    id=b'abc',
                    boots=1234,
                    time=456),
                user='user_xyz',
                context=snmp.Context(
                    engine_id=b'engine_abc',
                    name='comm_xyz'),
                pdu=pdu)
        else:
            resp_msg = version_module.Msg(
                type=msg_type,
                community=community,
                pdu=pdu)

        agent.send(resp_msg, manager_addr)
        await asyncio.sleep(0.01)

        assert not req_f.done()
        invalid_response_log = caplog.records[0]
        assert invalid_response_log.levelname == 'WARNING'

    await manager.async_close()
    await agent.async_close()
