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
        if version == snmp.Version.V1:
            return v1.MsgType.GET_REQUEST
        elif version in [snmp.Version.V2C,
                         snmp.Version.V3]:
            return v2c.MsgType.GET_REQUEST
    if isinstance(req, snmp.GetNextDataReq):
        if version == snmp.Version.V1:
            return v1.MsgType.GET_NEXT_REQUEST
        elif version in [snmp.Version.V2C,
                         snmp.Version.V3]:
            return v2c.MsgType.GET_NEXT_REQUEST
    if isinstance(req, snmp.SetDataReq):
        if version == snmp.Version.V1:
            return v1.MsgType.SET_REQUEST
        elif version in [snmp.Version.V2C,
                         snmp.Version.V3]:
            return v2c.MsgType.SET_REQUEST
    if isinstance(req, snmp.GetBulkDataReq):
        if version in [snmp.Version.V2C,
                       snmp.Version.V3]:
            return v2c.MsgType.GET_BULK_REQUEST


def req_to_data(req, version):
    if isinstance(req, (snmp.GetDataReq,
                        snmp.GetNextDataReq,
                        snmp.GetBulkDataReq)):
        dtype = (snmp.DataType.EMPTY if version == snmp.Version.V1
                 else snmp.DataType.UNSPECIFIED)
        return [snmp.Data(type=dtype,
                          name=i,
                          value=None) for i in req.names]
    if isinstance(req, snmp.SetDataReq):
        return req.data


def resp_msg_from_resp(resp, community, request_id, version):
    if isinstance(resp, list):
        data = resp
        error = snmp.Error(type=snmp.ErrorType.NO_ERROR,
                           index=0)
    elif isinstance(resp, snmp.Error):
        data = []
        error = resp
    if version == snmp.Version.V1:
        return v1.Msg(type=v1.MsgType.GET_RESPONSE,
                      community=community,
                      pdu=v1.BasicPdu(
                        request_id=request_id,
                        error=error,
                        data=data))
    elif version == snmp.Version.V2C:
        return v2c.Msg(type=v2c.MsgType.RESPONSE,
                       community=community,
                       pdu=v1.BasicPdu(
                            request_id=request_id,
                            error=error,
                            data=data))
    elif version == snmp.Version.V3:
        return v3.Msg(type=v3.MsgType.RESPONSE,
                      id=request_id,
                      reportable=False,
                      context=snmp.Context(engine_id='',
                                           name=community),
                      pdu=v1.BasicPdu(
                            request_id=request_id,
                            error=error,
                            data=data))


@pytest.mark.parametrize("version", [snmp.Version.V1,
                                     snmp.Version.V2C,
                                     snmp.Version.V3])
async def test_create(agent_addr, version):
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='def'),
        remote_addr=agent_addr,
        version=version)
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
    snmp.SetDataReq(data=[
        snmp.Data(type=dt,
                  name=(1, 2, 3),
                  value=v) for dt, v in ((snmp.DataType.UNSIGNED, 123),
                                         (snmp.DataType.COUNTER, 4567),
                                         (snmp.DataType.STRING, 'abcd'),
                                         (snmp.DataType.OBJECT_ID, (1, 2, 3)),
                                         (snmp.DataType.IP_ADDRESS, (1, 2, 3)),
                                         (snmp.DataType.TIME_TICKS, 123456),
                                         (snmp.DataType.ARBITRARY, b'abc123'),
                                         )]),
    ])
@pytest.mark.parametrize("response_exp", [
    [],
    [snmp.Data(type=snmp.DataType.INTEGER,
               name=(1, 2, 3, i),
               value=123 + i) for i in range(10)],
    [snmp.Data(type=dtype,
               name=(1, 2, 3, 4, 5, 10),
               value=value) for dtype, value in (
                    (snmp.DataType.UNSIGNED, 123),
                    (snmp.DataType.COUNTER, 4567),
                    (snmp.DataType.STRING, 'abcd'),
                    (snmp.DataType.OBJECT_ID, (1, 2, 3)),
                    (snmp.DataType.IP_ADDRESS, (192, 168, 1, 11)),
                    (snmp.DataType.TIME_TICKS, 123456),
                    (snmp.DataType.ARBITRARY, b'abc123'),)],
    snmp.Error(type=snmp.ErrorType.TOO_BIG, index=0),
    snmp.Error(type=snmp.ErrorType.NO_SUCH_NAME, index=0),
    snmp.Error(type=snmp.ErrorType.BAD_VALUE, index=0),
    snmp.Error(type=snmp.ErrorType.READ_ONLY, index=0),
    snmp.Error(type=snmp.ErrorType.GEN_ERR, index=0),
    ])
@pytest.mark.parametrize("version", [snmp.Version.V1,
                                     snmp.Version.V2C,
                                     snmp.Version.V3])
async def test_send(agent_addr, req, response_exp, version):
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
    msg_community = (
        req_msg.community if version in [snmp.Version.V1, snmp.Version.V2C]
        else req_msg.context.name)
    assert msg_community == community
    assert req_msg.pdu == v1.BasicPdu(
        request_id=1,
        error=snmp.Error(type=snmp.ErrorType.NO_ERROR,
                         index=0),
        data=req_to_data(req, version))
    assert not req_f.done()

    # receives response
    resp_msg = resp_msg_from_resp(
        response_exp, community, req_msg.pdu.request_id, version)
    agent.send(resp_msg, manager_addr)
    response = await req_f
    assert isinstance(response, (list,
                                 snmp.Error))
    assert response == response_exp
    assert agent.receive_queue.empty()

    await manager.async_close()
    await agent.async_close()


@pytest.mark.parametrize("req", [
    snmp.GetBulkDataReq(names=[]),
    snmp.GetBulkDataReq(names=[(1, 2), (1, 2, 3), (1, 2, 456)]),
    snmp.SetDataReq(data=[
        snmp.Data(type=snmp.DataType.BIG_COUNTER,
                  name=(1, 2, 3, 456),
                  value=123456)]),
    snmp.SetDataReq(data=[
        snmp.Data(type=snmp.DataType.NO_SUCH_OBJECT,
                  name=(1, 2, 3, 4, 5, 5678),
                  value=None)]),
    snmp.SetDataReq(data=[
        snmp.Data(type=dt,
                  name=(1, 2, 3, 4, 5, 5678),
                  value=v) for dt, v in (
                    (snmp.DataType.UNSPECIFIED, None),
                    (snmp.DataType.NO_SUCH_OBJECT, None),
                    (snmp.DataType.NO_SUCH_INSTANCE, None),
                    (snmp.DataType.END_OF_MIB_VIEW, None),
                    )]),
    ])
@pytest.mark.parametrize("response_exp", [
    [],
    [snmp.Data(type=snmp.DataType.BIG_COUNTER,
               name=(1, 2, 3, i),
               value=123 + i) for i in range(10)],
    [snmp.Data(type=dtype,
               name=(1, 2, 3, 4, 5, 10),
               value=value) for dtype, value in (
                    (snmp.DataType.BIG_COUNTER, 1234567),
                    (snmp.DataType.UNSPECIFIED, None),
                    (snmp.DataType.NO_SUCH_OBJECT, None),
                    (snmp.DataType.NO_SUCH_INSTANCE, None),
                    (snmp.DataType.END_OF_MIB_VIEW, None))],
    snmp.Error(type=snmp.ErrorType.NO_ACCESS, index=0),
    snmp.Error(type=snmp.ErrorType.WRONG_TYPE, index=1),
    snmp.Error(type=snmp.ErrorType.WRONG_ENCODING, index=1),
    snmp.Error(type=snmp.ErrorType.INCONSISTENT_VALUE, index=2),
    snmp.Error(type=snmp.ErrorType.RESOURCE_UNAVAILABLE, index=3),
    snmp.Error(type=snmp.ErrorType.AUTHORIZATION_ERROR, index=4),
    ])
@pytest.mark.parametrize("version", [snmp.Version.V2C,
                                     snmp.Version.V3])
async def test_send_v2_v3(agent_addr, req, response_exp, version):
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
    msg_community = (
        req_msg.community if version in [snmp.Version.V1, snmp.Version.V2C]
        else req_msg.context.name)
    assert msg_community == community
    if isinstance(req, snmp.GetBulkDataReq):
        assert req_msg.pdu == v2c.BulkPdu(
            request_id=1,
            non_repeaters=0,
            max_repetitions=0,
            data=req_to_data(req, version))
    else:
        assert req_msg.pdu == v1.BasicPdu(
            request_id=1,
            error=snmp.Error(type=snmp.ErrorType.NO_ERROR,
                             index=0),
            data=req_to_data(req, version))
    assert not req_f.done()

    # receives response
    resp_msg = resp_msg_from_resp(
        response_exp, community, req_msg.pdu.request_id, version)
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


@pytest.mark.parametrize("version", [snmp.Version.V1,
                                     snmp.Version.V2C,
                                     snmp.Version.V3])
async def test_request_id(agent_addr, version):
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
        if version == snmp.Version.V3:
            assert req_msg.id == req_id_exp
        assert req_msg.pdu.request_id == req_id_exp
    assert agent.receive_queue.empty()

    await manager.async_close()
    await agent.async_close()


@pytest.mark.parametrize("invalid_request", [
    snmp.GetBulkDataReq(names=[]),
    ])
async def test_invalid_request(agent_addr, invalid_request):
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='def'),
        remote_addr=agent_addr,
        version=snmp.Version.V1)
    assert manager.is_open

    with pytest.raises(ValueError):
        await manager.send(invalid_request)

    await manager.async_close()


@pytest.mark.parametrize(
    "msg_version, msg_type, request_id, community, version", [
        (v1, v1.MsgType.GET_RESPONSE, 2, 'xyz', snmp.Version.V1),  # request_id
        # (v1, v1.MsgType.GET_RESPONSE, 1, 'abc', snmp.Version.V1), # community
        (v1, v1.MsgType.GET_NEXT_REQUEST,
            1, 'xyz', snmp.Version.V1),  # msg_type
        (v1, v1.MsgType.GET_REQUEST, 1, 'xyz', snmp.Version.V1),  # msg_type
        (v2c, v2c.MsgType.RESPONSE, 2, 'xyz', snmp.Version.V1),  # version
        (v3, v3.MsgType.RESPONSE, 2, 'xyz', snmp.Version.V1),  # version
        (v2c, v2c.MsgType.RESPONSE, 2, 'xyz', snmp.Version.V2C),  # request_id
        # (v2c, v2c.MsgType.RESPONSE, 1, 'abc', snmp.Version.V2C),  # community
        (v2c, v2c.MsgType.REPORT, 1, 'xyz', snmp.Version.V2C),  # msg_type
        # (v2c, v2c.MsgType.RESPONSE, 1, 'xyz', snmp.Version.V3),  # version
        (v3, v3.MsgType.RESPONSE, 2, 'xyz', snmp.Version.V3),  # request_id
        # (v3, v3.MsgType.RESPONSE, 1, 'abc', snmp.Version.V3),  # community
        (v3, v3.MsgType.REPORT, 1, 'xyz', snmp.Version.V3),  # msg_type
        # (v3, v3.MsgType.RESPONSE, 1, 'xyz', snmp.Version.V2C),  # version
    ])
async def test_invalid_response(agent_addr, msg_version, msg_type, request_id,
                                community, version, caplog):
    agent = await create_mock_agent(agent_addr)
    manager = await snmp.create_manager(
        context=snmp.Context(engine_id='abc',
                             name='xyz'),
        remote_addr=agent_addr,
        version=version)

    req_f = manager.async_group.spawn(manager.send, snmp.GetDataReq(names=[]))

    _, manager_addr = await agent.receive_queue.get()
    error = snmp.Error(type=snmp.ErrorType.NO_ERROR, index=0)
    msg_class = getattr(msg_version, 'Msg')
    if msg_class == v3.Msg:
        resp_msg = v3.Msg(type=msg_type,
                          id=request_id,
                          reportable=False,
                          context=snmp.Context(engine_id='',
                                               name=community),
                          pdu=v1.BasicPdu(
                               request_id=request_id,
                               error=error,
                               data=[]))
    else:
        resp_msg = msg_class(
            type=msg_type,
            community=community,
            pdu=v1.BasicPdu(
                request_id=request_id,
                error=error,
                data=[]))

    agent.send(resp_msg, manager_addr)
    await asyncio.sleep(0.01)
    assert not req_f.done()
    invalid_response_log = caplog.records[0]
    assert invalid_response_log.levelname == 'WARNING'

    await manager.async_close()
    await agent.async_close()
