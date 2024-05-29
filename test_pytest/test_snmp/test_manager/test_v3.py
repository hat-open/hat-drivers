import pytest

from hat import aio
from hat import util

from hat.drivers import snmp
from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp import key
from hat.drivers.snmp.encoder import v3


md5_key = key.Key(type=key.KeyType.MD5,
                  data=b'1234567890abcdef')
sha_key = key.Key(type=key.KeyType.SHA,
                  data=b'1234567890abcdefghij')
des_key = key.Key(type=key.KeyType.DES,
                  data=b'1234567890abcdef')


@pytest.fixture
def agent_addr():
    return udp.Address('127.0.0.1', util.get_unused_udp_port())


async def create_mock_agent(addr, auth_key=None, priv_key=None):
    agent = MockAgent()
    agent._auth_key = auth_key
    agent._priv_key = priv_key
    agent._manager_addr = None
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

    def send(self, msg):
        if not self._manager_addr:
            raise Exception('no manager address')
        msg_bytes = encoder.encode(msg,
                                   auth_key=self._auth_key,
                                   priv_key=self._priv_key)
        self._endpoint.send(msg_bytes, self._manager_addr)

    def _on_auth_key(self, engine_id, user):
        return self._auth_key

    def _on_priv_key(self, engine_id, user):
        return self._priv_key

    async def _receive_loop(self):
        while True:
            received_bytes, manager_addr = await self._endpoint.receive()
            self._manager_addr = manager_addr
            received_msg = encoder.decode(
                received_bytes,
                auth_key_cb=self._on_auth_key,
                priv_key_cb=self._on_priv_key)
            self._receive_queue.put_nowait(received_msg)


def req_to_msg_type(req):
    if isinstance(req, snmp.GetDataReq):
        return v3.MsgType.GET_REQUEST
    if isinstance(req, snmp.GetNextDataReq):
        return v3.MsgType.GET_NEXT_REQUEST
    if isinstance(req, snmp.GetBulkDataReq):
        return v3.MsgType.GET_BULK_REQUEST
    if isinstance(req, snmp.SetDataReq):
        return v3.MsgType.SET_REQUEST


def resp_msg_from_resp(resp, request):
    if isinstance(resp, list):
        data = resp
        error = snmp.Error(type=snmp.ErrorType.NO_ERROR,
                           index=0)
    elif isinstance(resp, snmp.Error):
        data = []
        error = resp
    return v3.Msg(type=v3.MsgType.RESPONSE,
                  id=request.id,
                  reportable=False,
                  auth=request.auth,
                  priv=request.priv,
                  authorative_engine=request.authorative_engine,
                  user=request.user,
                  context=request.context,
                  pdu=v3.BasicPdu(
                   request_id=request.pdu.request_id,
                   error=error,
                   data=data))


def create_sync_msg_response(req, user, context, auth_engine_id,
                             auth=False, priv=False):
    return v3.Msg(
        type=v3.MsgType.RESPONSE,
        id=req.id,
        reportable=False,
        auth=auth,
        priv=priv,
        authorative_engine=auth_engine_id,
        user=user,
        context=context,
        pdu=v3.BasicPdu(
            request_id=req.pdu.request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[]))


@pytest.mark.parametrize("auth_key, priv_key", [
    (None, None),
    (md5_key, None),
    (sha_key, None),
    (md5_key, des_key),
    (sha_key, des_key)])
async def test_create(agent_addr, auth_key, priv_key):
    agent = await create_mock_agent(agent_addr)

    context = snmp.Context(
        engine_id=b'context_engine_xyz',
        name='context_xyz')
    user = 'user_xyz'
    auth_engine_id = v3.AuthorativeEngine(
        id=b'auth_engine_xyz',
        boots=123,
        time=456789)
    async with aio.Group() as group:
        manager_fut = group.spawn(snmp.create_v3_manager,
                                  remote_addr=agent_addr,
                                  context=context,
                                  user=user,
                                  auth_key=auth_key,
                                  priv_key=priv_key)

        sync_msg = await agent.receive_queue.get()

        # response on sync
        sync_msg_resp = create_sync_msg_response(
            sync_msg, user, context, auth_engine_id)
        agent.send(sync_msg_resp)

        manager = await manager_fut

    assert isinstance(manager, snmp.Manager)
    assert manager.is_open

    manager.close()
    await manager.wait_closing()
    assert manager.is_closing
    await manager.wait_closed()
    assert manager.is_closed

    await agent.async_close()


@pytest.mark.parametrize("context", [
    snmp.Context(engine_id=b'context_engine_xyz1',
                 name='context_xyz'),
    snmp.Context(engine_id=b'context_engine_xyz2',
                 name='')])
@pytest.mark.parametrize("user", ['user_abc', 'user_xyz'])
@pytest.mark.parametrize("auth_engine_id", [
    v3.AuthorativeEngine(id=b'auth_engine_xyz',
                         boots=123,
                         time=456789),
    v3.AuthorativeEngine(id=b'abc',
                         boots=0,
                         time=12345),
    ])
@pytest.mark.parametrize("auth_key, priv_key", [
    (None, None),
    (md5_key, None),
    (sha_key, None),
    (md5_key, des_key),
    (sha_key, des_key)])
async def test_sync(agent_addr, context, user, auth_engine_id,
                    auth_key, priv_key):
    agent = await create_mock_agent(agent_addr, auth_key, priv_key)

    user = 'user_xyz'
    async with aio.Group() as group:
        manager_fut = group.spawn(snmp.create_v3_manager,
                                  remote_addr=agent_addr,
                                  context=context,
                                  user=user,
                                  auth_key=auth_key,
                                  priv_key=priv_key)

        sync_msg = await agent.receive_queue.get()

        assert sync_msg.type == v3.MsgType.GET_REQUEST
        assert isinstance(sync_msg, v3.Msg)
        assert sync_msg.reportable
        assert sync_msg.auth is False
        assert sync_msg.priv is False
        assert sync_msg.authorative_engine == v3.AuthorativeEngine(
            id=b'',
            boots=0,
            time=0)
        assert sync_msg.user == ''
        assert sync_msg.context == snmp.Context(
            engine_id=b'',
            name='')
        assert sync_msg.pdu == v3.BasicPdu(
            request_id=sync_msg.pdu.request_id,
            error=snmp.Error(snmp.ErrorType.NO_ERROR, 0),
            data=[])

        # response on auto sync
        sync_msg_resp = create_sync_msg_response(
            sync_msg, user, context, auth_engine_id)
        agent.send(sync_msg_resp)
        manager = await manager_fut

        # manual sync
        sync_fut = group.spawn(manager.sync)
        sync_msg2 = await agent.receive_queue.get()

        assert sync_msg2.id > sync_msg.id
        assert sync_msg2.pdu.request_id > sync_msg.pdu.request_id
        assert sync_msg2 == sync_msg._replace(
            id=sync_msg2.id,
            pdu=sync_msg.pdu._replace(request_id=sync_msg2.pdu.request_id))

        # response on manual sync
        sync_msg_resp = create_sync_msg_response(
            sync_msg2, user, context, auth_engine_id)
        agent.send(sync_msg_resp)
        sync_res = await sync_fut
        assert sync_res is None

        assert manager.is_open

        # synced response info is used in next request
        req = snmp.GetDataReq(names=[])
        group.spawn(manager.send, req)

        req_msg = await agent.receive_queue.get()
        assert req_msg.context == sync_msg_resp.context
        assert req_msg.user == sync_msg_resp.user
        assert req_msg.authorative_engine == sync_msg_resp.authorative_engine

    await manager.async_close()
    await agent.async_close()


@pytest.mark.parametrize("req", [
    snmp.GetDataReq(names=[]),
    snmp.GetDataReq(names=[(1, 2), (1, 2, 3), (1, 2, 456)]),
    snmp.GetNextDataReq(names=[]),
    snmp.GetNextDataReq(names=[(1, 2), (1, 2, 3), (1, 2, 456)]),
    snmp.GetBulkDataReq(names=[]),
    snmp.GetBulkDataReq(names=[(1, 2), (1, 2, 3), (1, 2, 456)]),
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
                        value='abcd'),
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
                     value='abcd'),
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
@pytest.mark.parametrize("auth_key, priv_key", [
    (None, None),
    (md5_key, None),
    (sha_key, None),
    (md5_key, des_key),
    (sha_key, des_key)])
async def test_send(agent_addr, req, response_exp, auth_key, priv_key):
    agent = await create_mock_agent(
        agent_addr, auth_key=auth_key, priv_key=priv_key)

    context = snmp.Context(
        engine_id=b'engine_xyz',
        name='context_xyz')
    user = 'user_xyz'
    auth_engine_id = v3.AuthorativeEngine(
        id=b'auth_engine_xyz',
        boots=123,
        time=456)
    auth = bool(auth_key)
    priv = bool(priv_key)
    async with aio.Group() as group:
        manager_fut = group.spawn(snmp.create_v3_manager,
                                  remote_addr=agent_addr,
                                  context=context,
                                  user=user,
                                  auth_key=auth_key,
                                  priv_key=priv_key)

        sync_msg = await agent.receive_queue.get()

        sync_msg_resp = create_sync_msg_response(
            sync_msg, user, context, auth_engine_id, auth, priv)
        agent.send(sync_msg_resp)

        manager = await manager_fut

        # sends request
        req_fut = group.spawn(manager.send, req)

        req_msg = await agent.receive_queue.get()

        assert isinstance(req_msg, v3.Msg)
        assert req_msg.type == req_to_msg_type(req)
        assert req_msg.id != sync_msg.id
        assert req_msg.reportable

        assert req_msg.auth is bool(auth_key)
        assert req_msg.priv is bool(priv_key)
        assert req_msg.authorative_engine == auth_engine_id
        assert req_msg.user == user
        assert req_msg.context == context

        expected_data = (req.data if isinstance(req, snmp.SetDataReq)
                         else [snmp.UnspecifiedData(name=i)
                               for i in req.names])
        if isinstance(req, snmp.GetBulkDataReq):
            expected_pdu = v3.BulkPdu(
                request_id=req_msg.pdu.request_id,
                non_repeaters=0,
                max_repetitions=0,
                data=expected_data)
        else:
            expected_pdu = v3.BasicPdu(
                request_id=req_msg.pdu.request_id,
                error=snmp.Error(type=snmp.ErrorType.NO_ERROR,
                                 index=0),
                data=expected_data)
        assert req_msg.pdu == expected_pdu
        assert isinstance(req_msg.pdu.request_id, int)
        assert not req_fut.done()

        # receives response
        resp_msg = resp_msg_from_resp(response_exp, req_msg)
        agent.send(resp_msg)
        response = await req_fut
        assert response == response_exp
        assert agent.receive_queue.empty()

    await manager.async_close()
    await agent.async_close()
