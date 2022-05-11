import pytest

from hat import util
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder
from hat.drivers.snmp import trap


@pytest.fixture
def udp_addr():
    return udp.Address('127.0.0.1', util.get_unused_udp_port())


def _data(version):
    yield common.Data(type=common.DataType.INTEGER,
                      name=(1, 0),
                      value=-10)
    yield common.Data(type=common.DataType.UNSIGNED,
                      name=(1, 1),
                      value=10)
    yield common.Data(type=common.DataType.COUNTER,
                      name=(1, 2),
                      value=10)
    yield common.Data(type=common.DataType.STRING,
                      name=(1, 3),
                      value='bunny')
    yield common.Data(type=common.DataType.OBJECT_ID,
                      name=(1, 4),
                      value=(1, 6, 3, 4, 5))
    yield common.Data(type=common.DataType.IP_ADDRESS,
                      name=(1, 5),
                      value=(127, 0, 0, 1))
    yield common.Data(type=common.DataType.TIME_TICKS,
                      name=(1, 6),
                      value=10)
    yield common.Data(type=common.DataType.ARBITRARY,
                      name=(1, 7),
                      value=b'bunny')
    if version == 'v1':
        yield common.Data(type=common.DataType.EMPTY,
                          name=(1, 8),
                          value=None)
    elif version in ('v2c', 'v3'):
        yield common.Data(type=common.DataType.BIG_COUNTER,
                          name=(1, 8),
                          value=129041231)
        yield common.Data(type=common.DataType.UNSPECIFIED,
                          name=(1, 9),
                          value=None)
        yield common.Data(type=common.DataType.NO_SUCH_OBJECT,
                          name=(1, 10),
                          value=None)
        yield common.Data(type=common.DataType.NO_SUCH_INSTANCE,
                          name=(1, 11),
                          value=None)
        yield common.Data(type=common.DataType.END_OF_MIB_VIEW,
                          name=(1, 12),
                          value=None)


async def test_listener_create(udp_addr):
    listener = await trap.create_trap_listener(udp_addr)
    assert isinstance(listener, trap.TrapListener)
    assert listener.is_open

    await listener.async_close()
    assert listener.is_closed


async def test_sender_create(udp_addr):
    sender = await trap.create_trap_sender(udp_addr)
    assert isinstance(sender, trap.TrapSender)
    assert sender.is_open

    await sender.async_close()
    assert sender.is_closed


@pytest.mark.parametrize("data", [list(_data('v1'))])
@pytest.mark.parametrize("cause_type", common.CauseType)
async def test_sender_send_trap_v1(udp_addr, data, cause_type):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_trap_sender(udp_addr, common.Version.V1)
    sender.send_trap(
        common.Trap(context=common.Context(
                        engine_id=None, name='community'),
                    cause=common.Cause(type=cause_type, value=13),
                    oid=(1, 2, 3, 4),
                    timestamp=12345,
                    data=data))

    msg_bytes, _ = await listener.receive()
    msg = encoder.decode(msg_bytes)
    version, _, tr = trap._decode_listener_req(msg)
    assert version == common.Version.V1
    assert tr.context.engine_id is None
    assert tr.context.name == 'community'
    assert tr.cause.type == cause_type
    assert tr.cause.value == 13
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_sender_send_trap_v2c(udp_addr, data):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_trap_sender(udp_addr, common.Version.V2C)
    sender.send_trap(
        common.Trap(context=common.Context(
                        engine_id=None, name='community'),
                    cause=None,
                    oid=(1, 2, 3, 4),
                    timestamp=12345,
                    data=data))

    msg_bytes, _ = await listener.receive()
    msg = encoder.decode(msg_bytes)
    version, _, tr = trap._decode_listener_req(msg)
    assert version == common.Version.V2C
    assert tr.context.engine_id is None
    assert tr.context.name == 'community'
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
async def test_sender_send_trap_v3(udp_addr, data):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_trap_sender(udp_addr, common.Version.V3)

    sender.send_trap(
        common.Trap(context=common.Context(
                        engine_id='engine_id', name='name'),
                    cause=None,
                    oid=(1, 2, 3, 4),
                    timestamp=12345,
                    data=data))

    msg_bytes, _ = await listener.receive()
    msg = encoder.decode(msg_bytes)
    version, _, tr = trap._decode_listener_req(msg)
    assert version == common.Version.V3
    assert tr.context.engine_id == 'engine_id'
    assert tr.context.name == 'name'
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v1'))])
@pytest.mark.parametrize("cause_type", common.CauseType)
async def test_listener_receive_trap_v1(udp_addr, data, cause_type):
    listener = await trap.create_trap_listener(udp_addr)

    sender = await udp.create(remote_addr=udp_addr)
    sender_addr = tuple(
        [int(i) for i in sender.info.local_addr.host.split('.')])

    tr = common.Trap(context=common.Context(
                        engine_id=None, name='community'),
                     cause=common.Cause(type=cause_type, value=13),
                     oid=(1, 2, 3, 4),
                     timestamp=12345,
                     data=data)
    msg = trap._encode_trap_req(common.Version.V1, sender_addr, None, tr)
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    tr, _ = await listener.receive()
    assert tr.context.engine_id is None
    assert tr.context.name == 'community'
    assert tr.cause.type == cause_type
    assert tr.cause.value == 13
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_listener_receive_trap_v2c(udp_addr, data):
    listener = await trap.create_trap_listener(udp_addr)

    sender = await udp.create(remote_addr=udp_addr)
    sender_addr = tuple(
        [int(i) for i in sender.info.local_addr.host.split('.')])

    tr = common.Trap(context=common.Context(
                        engine_id=None, name='community'),
                     cause=None,
                     oid=(1, 2, 3, 4),
                     timestamp=12345,
                     data=data)
    msg = trap._encode_trap_req(common.Version.V2C, sender_addr, 4531, tr)
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    tr, _ = await listener.receive()
    assert tr.context.engine_id is None
    assert tr.context.name == 'community'
    assert tr.cause is None
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
async def test_listener_receive_trap_v3(udp_addr, data):
    listener = await trap.create_trap_listener(udp_addr)

    sender = await udp.create(remote_addr=udp_addr)
    sender_addr = tuple(
        [int(i) for i in sender.info.local_addr.host.split('.')])

    tr = common.Trap(context=common.Context(
                        engine_id='engine_id', name='name'),
                     cause=None,
                     oid=(1, 2, 3, 4),
                     timestamp=12345,
                     data=data)
    msg = trap._encode_trap_req(common.Version.V3, sender_addr, 4531, tr)
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    tr, _ = await listener.receive()
    assert tr.context.engine_id == 'engine_id'
    assert tr.context.name == 'name'
    assert tr.cause is None
    assert tr.oid == (1, 2, 3, 4)
    assert tr.timestamp == 12345
    assert tr.data == data

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_sender_send_inform_v2c(udp_addr, data):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_trap_sender(udp_addr, common.Version.V2C)

    inform_req = common.Inform(
        context=common.Context(engine_id=None, name='community'),
        data=data)
    res_f = sender.async_group.spawn(sender.send_inform, inform_req)

    msg_bytes, addr = await listener.receive()
    msg = encoder.decode(msg_bytes)
    version, req_id, inform_req = trap._decode_listener_req(msg)
    assert version == common.Version.V2C
    assert inform_req.context.engine_id is None
    assert inform_req.context.name == 'community'
    assert inform_req.data == data
    assert not res_f.done()

    msg = trap._encode_inform_res(version, req_id, inform_req, None)
    msg_bytes = encoder.encode(msg)
    listener.send(msg_bytes, addr)

    send_inform_res = await res_f
    assert send_inform_res is None

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
async def test_sender_send_inform_v3(udp_addr, data):
    listener = await udp.create(local_addr=udp_addr)

    sender = await trap.create_trap_sender(udp_addr, common.Version.V3)

    inform_req = common.Inform(
        context=common.Context(engine_id='engine_id', name='name'),
        data=data)
    res_f = sender.async_group.spawn(sender.send_inform, inform_req)

    msg_bytes, addr = await listener.receive()
    msg = encoder.decode(msg_bytes)
    version, req_id, inform_req = trap._decode_listener_req(msg)
    assert version == common.Version.V3
    assert inform_req.context.engine_id == 'engine_id'
    assert inform_req.context.name == 'name'
    assert inform_req.data == data
    assert not res_f.done()

    msg = trap._encode_inform_res(version, req_id, inform_req, None)
    msg_bytes = encoder.encode(msg)
    listener.send(msg_bytes, addr)

    send_inform_res = await res_f
    assert send_inform_res is None

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v2c'))])
async def test_listener_receive_inform_v2c(udp_addr, data):

    def inform_cb(version, inform_req, addr):
        assert addr == sender.info.local_addr
        assert version == common.Version.V2C
        assert inform_req.context.engine_id is None
        assert inform_req.context.name == 'community'
        assert inform_req.data == data

    listener = await trap.create_trap_listener(udp_addr, inform_cb)

    sender = await udp.create(remote_addr=udp_addr)

    inform_req = common.Inform(
        context=common.Context(engine_id=None, name='community'),
        data=data)
    msg = trap._encode_inform_req(common.Version.V2C, 4531, inform_req)
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    msg_bytes, addr = await sender.receive()
    version, req_id, error = trap._decode_inform_res(msg_bytes)
    assert version == common.Version.V2C
    assert req_id == 4531
    assert error is None

    await sender.async_close()
    await listener.async_close()


@pytest.mark.parametrize("data", [list(_data('v3'))])
async def test_listener_receive_inform_v3(udp_addr, data):

    def inform_cb(version, inform_req, addr):
        assert addr == sender.info.local_addr
        assert version == common.Version.V3
        assert inform_req.context.engine_id == 'engine_id'
        assert inform_req.context.name == 'name'
        assert inform_req.data == data

    listener = await trap.create_trap_listener(udp_addr, inform_cb)

    sender = await udp.create(remote_addr=udp_addr)

    inform_req = common.Inform(
        context=common.Context(engine_id='engine_id', name='name'),
        data=data)
    msg = trap._encode_inform_req(common.Version.V3, 4531, inform_req)
    msg_bytes = encoder.encode(msg)
    sender.send(msg_bytes)

    msg_bytes, addr = await sender.receive()
    version, req_id, error = trap._decode_inform_res(msg_bytes)
    assert version == common.Version.V3
    assert req_id == 4531
    assert error is None

    await sender.async_close()
    await listener.async_close()
