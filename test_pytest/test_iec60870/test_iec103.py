import math

import pytest

from hat import aio
from hat.drivers.iec60870 import iec103
from hat.drivers.iec60870 import link
from hat.drivers.iec60870.app.iec103 import common, encoder

default_time_seven = iec103.Time(
    size=iec103.TimeSize.SEVEN,
    milliseconds=0,
    invalid=False,
    minutes=0,
    summer_time=False,
    hours=12,
    day_of_week=1,
    day_of_month=1,
    months=1,
    years=99)

default_time_four = common.Time(
    size=common.TimeSize.FOUR,
    milliseconds=1,
    invalid=False,
    minutes=2,
    summer_time=False,
    hours=3,
    day_of_week=None,
    day_of_month=None,
    months=None,
    years=None)


def create_connection_slave_pair():
    send_queue = aio.Queue()
    receive_queue = aio.Queue()
    enc = encoder.Encoder()

    class MockLinkConnection(link.Connection):

        def __init__(self):
            self._async_group = aio.Group()

        @property
        def async_group(self):
            return self._async_group

        async def send(self, data):
            send_queue.put_nowait(data)

        async def receive(self):
            return await receive_queue.get()

    class MockSlave(aio.Resource):

        def __init__(self):
            self._async_group = aio.Group()

        @property
        def async_group(self):
            return self._async_group

        async def send(self, asdu):
            receive_queue.put_nowait(enc.encode_asdu(asdu))

        async def receive(self):
            return enc.decode_asdu(await send_queue.get())

    return MockLinkConnection(), MockSlave()


@pytest.mark.parametrize('asdu_address, time', [(0xFF, default_time_seven),
                                                (0x01, default_time_seven)])
async def test_time_sync(asdu_address, time):
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn)

    await master_conn.time_sync(time=time, asdu_address=asdu_address)
    sent = await slave.receive()

    assert sent.type == common.AsduType.TIME_SYNCHRONIZATION
    assert sent.cause == common.Cause.TIME_SYNCHRONIZATION
    assert sent.address == asdu_address
    assert len(sent.ios) == 1
    assert sent.ios[0].address.function_type == 255
    assert sent.ios[0].address.information_number == 0
    assert len(sent.ios[0].elements) == 1
    assert sent.ios[0].elements[0].time == time

    if asdu_address != 0xFF:
        await slave.send(common.ASDU(
            type=common.AsduType.TIME_SYNCHRONIZATION,
            cause=common.Cause.TIME_SYNCHRONIZATION,
            address=asdu_address,
            ios=[common.IO(
                address=common.IoAddress(function_type=255,
                                         information_number=0),
                elements=[
                    common.IoElement_TIME_SYNCHRONIZATION(time=time)])]))

    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.skip(reason='test not implemented')
async def test_interrogate():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_send_command():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_interrogate_generic():
    pass


@pytest.mark.parametrize('asdu_type, value, cmp_fn', [
    (common.AsduType.TIME_TAGGED_MESSAGE,
     common.DoubleWithTimeValue(value=common.DoubleValue.ON,
                                time=default_time_four,
                                supplementary=5),
     None),
    (common.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME,
     common.DoubleWithRelativeTimeValue(value=common.DoubleValue.ON,
                                        relative_time=123,
                                        fault_number=123,
                                        time=default_time_four,
                                        supplementary=1),
     None),
    (common.AsduType.MEASURANDS_1,
     common.MeasurandValue(overflow=False, invalid=False, value=0.14),
     lambda recv_val, sent_val: math.isclose(
         recv_val.value.values[iec103.common.MeasurandType.M1_I_L2].value,
         sent_val.value,
         rel_tol=1e-3)),
    (common.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME,
     common.MeasurandWithRelativeTimeValue(value=3.14,
                                           relative_time=123,
                                           fault_number=123,
                                           time=default_time_four),
     lambda recv_val, sent_val: math.isclose(recv_val.value.value,
                                             sent_val.value,
                                             rel_tol=1e-3))])
async def test_spontaneous(asdu_type, value, cmp_fn):
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn,
                                          data_cb=receive_queue.put_nowait)
    element = getattr(common, f'IoElement_{asdu_type.name}')
    io_addr = common.IoAddress(function_type=1, information_number=1)

    slave_asdu = common.ASDU(
        type=asdu_type,
        cause=common.Cause.SPONTANEOUS,
        address=1,
        ios=[common.IO(address=io_addr, elements=[element(value)])])
    await slave.send(slave_asdu)
    master_data = await receive_queue.get()

    assert master_data.asdu_address == slave_asdu.address
    assert master_data.io_address == io_addr
    assert master_data.cause.value == common.Cause.SPONTANEOUS.value

    if not cmp_fn:
        assert master_data.value == value
    else:
        assert cmp_fn(master_data, value)

    await slave.async_close()
    await master_conn.async_close()


async def test_identification():
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn,
                                          data_cb=receive_queue.put_nowait)
    io_addr = common.IoAddress(function_type=1, information_number=1)

    slave_asdu = common.ASDU(
        type=common.AsduType.IDENTIFICATION,
        cause=common.Cause.SPONTANEOUS,
        address=1,
        ios=[common.IO(address=io_addr,
                       elements=[common.IoElement_IDENTIFICATION(
                           compatibility=1,
                           value=b'10101010',
                           software=b'1010')])])
    await slave.send(slave_asdu)
    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.skip(reason='test not implemented')
async def test_measurands_2():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_generic_data():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_generic_identification():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_general_command():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_generic_command():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_list_of_recorded_disturbances():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_order_for_disturbance_data_transmission():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_acknowledgement_for_disturbance_data_transmission():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_ready_for_transmission_of_disturbance_data():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_ready_for_transmission_of_a_channel():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_ready_for_transmission_of_tags():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_transmission_of_tags():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_transmission_of_disturbance_values():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_end_of_transmission():
    pass
