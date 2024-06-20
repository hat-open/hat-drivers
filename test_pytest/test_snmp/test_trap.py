import pytest

from hat import aio
from hat import util

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder
from hat.drivers.snmp import key
from hat.drivers.snmp import trap


@pytest.fixture
def udp_addr():
    return udp.Address('127.0.0.1', util.get_unused_udp_port())


def _data(version):
    yield common.IntegerData(name=(1, 0), value=-10)
    yield common.UnsignedData(name=(1, 1), value=10)
    yield common.CounterData(name=(1, 2), value=10)
    yield common.StringData(name=(1, 3), value=b'bunny')
    yield common.ObjectIdData(name=(1, 4), value=(1, 6, 3, 4, 5))
    yield common.IpAddressData(name=(1, 5), value=(127, 0, 0, 1))
    yield common.TimeTicksData(name=(1, 6), value=10)
    yield common.ArbitraryData(name=(1, 7), value=b'bunny')
    if version == 'v1':
        yield common.EmptyData(name=(1, 8))
    elif version in ('v2c', 'v3'):
        yield common.BigCounterData(name=(1, 8), value=129041231)
        yield common.UnspecifiedData(name=(1, 9))
        yield common.NoSuchObjectData(name=(1, 10))
        yield common.NoSuchInstanceData(name=(1, 11))
        yield common.EndOfMibViewData(name=(1, 12))


async def test_listener_create(udp_addr):
    listener = await trap.create_trap_listener(udp_addr)
    assert isinstance(listener, trap.TrapListener)
    assert listener.is_open

    await listener.async_close()
    assert listener.is_closed


@pytest.mark.parametrize("version", ['v1', 'v2c', 'v3'])
async def test_sender_create(version, udp_addr):
    if version == 'v1':
        sender = await trap.create_v1_trap_sender(udp_addr, 'community')
    elif version == 'v2c':
        sender = await trap.create_v2c_trap_sender(udp_addr, 'community')
    elif version == 'v3':
        sender = await trap.create_v3_trap_sender(udp_addr, b'')
    assert isinstance(sender, trap.TrapSender)
    assert sender.is_open

    await sender.async_close()
    assert sender.is_closed


@pytest.mark.parametrize("data", [list(_data('v1'))])
@pytest.mark.parametrize("cause_type", common.CauseType)
async def test_sender_send_trap_v1(udp_addr, data, cause_type):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_v1_trap_sender(udp_addr, 'community')
    sender.send_trap(
        common.Trap(cause=common.Cause(type=cause_type, value=13),
                    oid=(1, 2, 3, 4),
                    timestamp=12345,
                    data=data))

    msg_bytes, _ = await listener.receive()
    msg = encoder.decode(msg_bytes)

    assert isinstance(msg, encoder.v1.Msg)
    assert msg.type == encoder.v1.MsgType.TRAP
    assert msg.community == 'community'
    assert isinstance(msg.pdu, encoder.v1.TrapPdu)
    assert msg.pdu.enterprise == (1, 2, 3, 4)
    assert msg.pdu.addr == (127, 0, 0, 1)
    assert msg.pdu.cause.type == cause_type
    assert msg.pdu.cause.value == 13
    assert msg.pdu.timestamp == 12345
    assert msg.pdu.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_sender_send_trap_v2c(udp_addr, data):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_v2c_trap_sender(udp_addr, 'community')
    sender.send_trap(common.Trap(cause=None,
                                 oid=(1, 2, 3, 4),
                                 timestamp=12345,
                                 data=data))

    msg_bytes, _ = await listener.receive()
    msg = encoder.decode(msg_bytes)

    assert isinstance(msg, encoder.v2c.Msg)
    assert msg.type == encoder.v2c.MsgType.SNMPV2_TRAP
    assert msg.community == 'community'

    assert isinstance(msg.pdu, encoder.v2c.BasicPdu)
    assert isinstance(msg.pdu.request_id, int)
    assert msg.pdu.error.type == common.ErrorType.NO_ERROR

    timestamp, oid, *pdu_data = msg.pdu.data
    assert timestamp.name == (1, 3, 6, 1, 2, 1, 1, 3, 0)
    assert timestamp.value == 12345
    assert oid.name == (1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0)
    assert oid.value == (1, 2, 3, 4)
    assert pdu_data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
@pytest.mark.parametrize('auth, priv', [
    (False, False),
    (True, False),
    (True, True)])
@pytest.mark.parametrize('auth_type', common.AuthType)
async def test_sender_send_trap_v3(udp_addr, data, auth, auth_type, priv):
    username = 'user_xyz'
    engine_id = b'ctx_engine_id'
    context = common.Context(engine_id=engine_id, name='name')
    auth_pass = 'authpass'
    priv_pass = 'privpass'
    auth_key = (key.create_key(key_type=key.KeyType[auth_type.name],
                               password=auth_pass,
                               engine_id=context.engine_id)
                if auth else None)
    priv_key = (key.create_key(key_type=key.KeyType.DES,
                               password=priv_pass,
                               engine_id=context.engine_id)
                if priv else None)

    def on_auth_key(eid, usr):
        return auth_key

    def on_priv_key(eid, usr):
        return priv_key

    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_v3_trap_sender(
        remote_addr=udp_addr,
        authoritative_engine_id=engine_id,
        context=context,
        user=common.User(
            name=username,
            auth_type=auth_type if auth else None,
            auth_password=auth_pass if auth else None,
            priv_type=common.PrivType.DES if priv else None,
            priv_password=priv_pass if priv else None))

    sender.send_trap(common.Trap(cause=None,
                                 oid=(1, 2, 3, 4),
                                 timestamp=12345,
                                 data=data))

    msg_bytes, _ = await listener.receive()
    msg = encoder.decode(msg_bytes,
                         auth_key_cb=on_auth_key,
                         priv_key_cb=on_priv_key)

    assert isinstance(msg, encoder.v3.Msg)
    assert msg.type == encoder.v3.MsgType.SNMPV2_TRAP
    assert msg.id is not None
    assert msg.reportable is False
    assert msg.auth is auth
    assert msg.priv is priv
    assert msg.authorative_engine.id == context.engine_id
    assert msg.authorative_engine.boots == 0
    assert msg.authorative_engine.time is not None
    assert msg.user == username
    assert msg.context == context
    assert msg.pdu.error.type == common.ErrorType.NO_ERROR

    timestamp, oid, *pdu_data = msg.pdu.data
    assert timestamp.name == (1, 3, 6, 1, 2, 1, 1, 3, 0)
    assert timestamp.value == 12345
    assert oid.name == (1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0)
    assert oid.value == (1, 2, 3, 4)
    assert pdu_data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v1'))])
@pytest.mark.parametrize("cause_type", common.CauseType)
async def test_listener_receive_trap_v1(udp_addr, data, cause_type):
    trap_queue = aio.Queue()
    listener = await trap.create_trap_listener(
        local_addr=udp_addr,
        v1_trap_cb=lambda _, community, tr: trap_queue.put_nowait(
            (community, tr)))

    sender = await udp.create(remote_addr=udp_addr)

    msg = encoder.v1.Msg(type=encoder.v1.MsgType.TRAP,
                         community='community',
                         pdu=encoder.v1.TrapPdu(
                             enterprise=(1, 2, 3, 4),
                             addr=(127, 0, 0, 1),
                             cause=common.Cause(type=cause_type, value=13),
                             timestamp=12345,
                             data=data))
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    community, tr = await trap_queue.get()
    assert community == 'community'
    assert tr.cause.type == cause_type
    assert tr.cause.value == 13
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_listener_receive_trap_v2c(udp_addr, data):
    trap_queue = aio.Queue()
    listener = await trap.create_trap_listener(
        local_addr=udp_addr,
        v2c_trap_cb=lambda _, community, tr: trap_queue.put_nowait(
            (community, tr)))

    sender = await udp.create(remote_addr=udp_addr)

    msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.SNMPV2_TRAP,
                          community='community',
                          pdu=encoder.v2c.BasicPdu(
                              request_id=12345,
                              error=common.Error(
                                  type=common.ErrorType.NO_ERROR,
                                  index=0),
                              data=[common.TimeTicksData(
                                        name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                                        value=12345),
                                    common.ObjectIdData(
                                        name=(1, 6, 3, 1, 1, 4, 1, 0),
                                        value=(1, 2, 3, 4)),
                                    *data]))
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    community, tr = await trap_queue.get()
    assert community == 'community'
    assert tr.cause is None
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
@pytest.mark.parametrize('auth, priv', [(False, False),
                                        (True, False),
                                        (True, True)])
@pytest.mark.parametrize('auth_type', common.AuthType)
async def test_listener_receive_trap_v3(udp_addr, data, auth, auth_type, priv):
    username = 'user_xyz'
    engine_id = b'engine_id'
    context = common.Context(engine_id=b'ctx_engine_id',
                             name='name')
    auth_pass = 'authpass'
    priv_pass = 'privpass'
    auth_key = (key.create_key(key_type=key.KeyType[auth_type.name],
                               password=auth_pass,
                               engine_id=engine_id)
                if auth else None)
    priv_key = (key.create_key(key_type=key.KeyType.DES,
                               password=priv_pass,
                               engine_id=engine_id)
                if priv else None)
    user = common.User(
        name=username,
        auth_type=auth_type if auth else None,
        auth_password=auth_pass if auth else None,
        priv_type=common.PrivType.DES if priv else None,
        priv_password=priv_pass if priv else None)

    trap_queue = aio.Queue()
    listener = await trap.create_trap_listener(
        local_addr=udp_addr,
        v3_trap_cb=lambda _, user, context, tr: trap_queue.put_nowait(
            (user, context, tr)),
        users=[user])

    sender = await udp.create(remote_addr=udp_addr)

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.SNMPV2_TRAP,
                         id=12345,
                         reportable=False,
                         auth=auth,
                         priv=priv,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                             id=engine_id,
                             boots=0,
                             time=0),
                         user=username,
                         context=context,
                         pdu=encoder.v2c.BasicPdu(
                             request_id=12345,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=0),
                             data=[common.TimeTicksData(
                                       name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                                       value=12345),
                                   common.ObjectIdData(
                                       name=(1, 6, 3, 1, 1, 4, 1, 0),
                                       value=(1, 2, 3, 4)),
                                   *data]))

    msg_bytes = encoder.encode(msg,
                               auth_key=auth_key,
                               priv_key=priv_key)
    sender.send(msg_bytes)

    user, context, tr = await trap_queue.get()
    assert user == username
    assert context == context
    assert tr.cause is None
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_sender_send_inform_v2c(udp_addr, data):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_v2c_trap_sender(udp_addr, 'community')

    inform_req = common.Inform(data=data)
    res_f = sender.async_group.spawn(sender.send_inform, inform_req)

    msg_bytes, addr = await listener.receive()
    msg = encoder.decode(msg_bytes)
    req_id = msg.pdu.request_id

    assert msg.type == encoder.v2c.MsgType.INFORM_REQUEST
    assert msg.community == 'community'
    assert msg.pdu.error.type == common.ErrorType.NO_ERROR
    assert msg.pdu.data == data
    assert not res_f.done()

    msg = encoder.v2c.Msg(
        type=encoder.v2c.MsgType.RESPONSE,
        community='community',
        pdu=encoder.v2c.BasicPdu(
            request_id=req_id,
            error=common.Error(
                type=common.ErrorType.NO_ERROR,
                index=0),
            data=data))
    msg_bytes = encoder.encode(msg)
    listener.send(msg_bytes, addr)

    send_inform_res = await res_f
    assert send_inform_res is None

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
@pytest.mark.parametrize('auth, priv', [
    (False, False),
    (True, False),
    (True, True)])
@pytest.mark.parametrize('auth_type', common.AuthType)
async def test_sender_send_inform_v3(udp_addr, data, auth, auth_type, priv):
    username = 'user_xyz'
    engine_id = b'ctx_engine_id'
    context = common.Context(engine_id=engine_id,
                             name='name')
    auth_pass = 'authpass'
    priv_pass = 'privpass'
    auth_key = (key.create_key(key_type=key.KeyType[auth_type.name],
                               password=auth_pass,
                               engine_id=context.engine_id)
                if auth else None)
    priv_key = (key.create_key(key_type=key.KeyType.DES,
                               password=priv_pass,
                               engine_id=context.engine_id)
                if priv else None)

    def on_auth_key(eid, usr):
        return auth_key

    def on_priv_key(eid, usr):
        return priv_key

    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_v3_trap_sender(
        remote_addr=udp_addr,
        authoritative_engine_id=engine_id,
        context=context,
        user=common.User(
            name=username,
            auth_type=auth_type if auth else None,
            auth_password=auth_pass if auth else None,
            priv_type=common.PrivType.DES if priv else None,
            priv_password=priv_pass if priv else None))

    inform_req = common.Inform(data=data)
    res_f = sender.async_group.spawn(sender.send_inform, inform_req)

    msg_bytes, addr = await listener.receive()
    msg = encoder.decode(msg_bytes,
                         auth_key_cb=on_auth_key,
                         priv_key_cb=on_priv_key)
    req_id = msg.pdu.request_id

    assert msg.type == encoder.v3.MsgType.INFORM_REQUEST
    assert msg.id is not None
    assert msg.reportable is False
    assert msg.auth is auth
    assert msg.priv is priv
    assert msg.authorative_engine.id == context.engine_id
    assert msg.authorative_engine.boots == 0
    assert msg.authorative_engine.time is not None
    assert msg.user == username
    assert msg.context == context
    assert msg.pdu.error.type == common.ErrorType.NO_ERROR
    assert msg.pdu.data == data
    assert not res_f.done()

    msg = encoder.v3.Msg(
        type=encoder.v3.MsgType.RESPONSE,
        id=msg.id,
        reportable=False,
        auth=auth,
        priv=priv,
        authorative_engine=encoder.v3.AuthorativeEngine(
            id=context.engine_id,
            boots=0,
            time=0),
        user=username,
        context=context,
        pdu=encoder.v3.BasicPdu(
            request_id=req_id,
            error=common.Error(
                type=common.ErrorType.NO_ERROR,
                index=0),
            data=data))
    msg_bytes = encoder.encode(msg,
                               auth_key=auth_key,
                               priv_key=priv_key)
    listener.send(msg_bytes, addr)

    send_inform_res = await res_f
    assert send_inform_res is None

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_listener_receive_inform_v2c(udp_addr, data):
    data = [common.TimeTicksData(name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                                 value=12345),
            common.ObjectIdData(name=(1, 6, 3, 1, 1, 4, 1, 0),
                                value=(1, 2, 3, 4)),
            *data]

    def inform_cb(addr, community, inform_req):
        assert addr == sender.info.local_addr
        assert community == 'community'
        assert inform_req.data == data

    listener = await trap.create_trap_listener(local_addr=udp_addr,
                                               v2c_inform_cb=inform_cb)

    sender = await udp.create(remote_addr=udp_addr)

    msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.INFORM_REQUEST,
                          community='community',
                          pdu=encoder.v2c.BasicPdu(
                              request_id=4531,
                              error=common.Error(
                                  type=common.ErrorType.NO_ERROR,
                                  index=0),
                              data=data))
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    msg_bytes, _ = await sender.receive()
    msg = encoder.decode(msg_bytes)

    assert isinstance(msg, encoder.v2c.Msg)
    assert msg.type == encoder.v2c.MsgType.RESPONSE
    assert msg.community == 'community'
    assert isinstance(msg.pdu, encoder.v2c.BasicPdu)
    assert msg.pdu.request_id == 4531
    assert msg.pdu.error.type == common.ErrorType.NO_ERROR
    assert msg.pdu.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
@pytest.mark.parametrize('auth, priv', [(False, False),
                                        (True, False),
                                        (True, True)])
@pytest.mark.parametrize('auth_type', common.AuthType)
async def test_listener_receive_inform_v3(udp_addr, data, auth, auth_type,
                                          priv):
    username = 'user_xyz'
    engine_id = b'engine_id'
    context = common.Context(engine_id=b'ctx_engine_id',
                             name='name')
    auth_pass = 'authpass'
    priv_pass = 'privpass'
    auth_key = (key.create_key(key_type=key.KeyType[auth_type.name],
                               password=auth_pass,
                               engine_id=engine_id)
                if auth else None)
    priv_key = (key.create_key(key_type=key.KeyType.DES,
                               password=priv_pass,
                               engine_id=engine_id)
                if priv else None)

    def on_auth_key(eid, usr):
        return auth_key

    def on_priv_key(eid, usr):
        return priv_key

    user = common.User(
        name=username,
        auth_type=auth_type if auth else None,
        auth_password=auth_pass if auth else None,
        priv_type=common.PrivType.DES if priv else None,
        priv_password=priv_pass if priv else None)

    data = [common.TimeTicksData(name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                                 value=12345),
            common.ObjectIdData(name=(1, 6, 3, 1, 1, 4, 1, 0),
                                value=(1, 2, 3, 4)),
            *data]

    def inform_cb(addr, user, context, inform_req):
        assert addr == sender.info.local_addr
        assert user == username
        assert context == context
        assert inform_req.data == data

    listener = await trap.create_trap_listener(
        local_addr=udp_addr,
        v3_inform_cb=inform_cb,
        users=[user])

    sender = await udp.create(remote_addr=udp_addr)

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.INFORM_REQUEST,
                         id=4531,
                         reportable=False,
                         auth=auth,
                         priv=priv,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                             id=engine_id,
                             boots=0,
                             time=0),
                         user=username,
                         context=context,
                         pdu=encoder.v2c.BasicPdu(
                             request_id=4531,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=0),
                             data=data))

    msg_bytes = encoder.encode(msg,
                               auth_key=auth_key,
                               priv_key=priv_key)
    sender.send(msg_bytes)

    msg_bytes, _ = await sender.receive()
    msg = encoder.decode(msg_bytes,
                         auth_key_cb=on_auth_key,
                         priv_key_cb=on_priv_key)

    assert isinstance(msg, encoder.v3.Msg)
    assert msg.type == encoder.v3.MsgType.RESPONSE
    assert msg.context == context
    assert isinstance(msg.pdu, encoder.v3.BasicPdu)
    assert msg.pdu.request_id == 4531
    assert msg.pdu.error.type == common.ErrorType.NO_ERROR
    assert msg.pdu.data == data

    await sender.async_close()
    await listener.async_close()
