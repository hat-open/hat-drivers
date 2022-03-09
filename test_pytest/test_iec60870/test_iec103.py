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

    return (MockLinkConnection(), MockSlave())


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


@pytest.mark.timeout(3)
@pytest.mark.parametrize('value, supplementary, time', [
    (common.DoubleValue.OFF, 1, default_time_four),
    (common.DoubleValue.ON, 5, default_time_four)])
async def test_time_tagged_message(value, supplementary, time):
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn,
                                          data_cb=receive_queue.put_nowait)
    slave_asdu = common.ASDU(
        type=common.AsduType.TIME_TAGGED_MESSAGE,
        cause=common.Cause.SPONTANEOUS,
        address=1,
        ios=[common.IO(
            address=common.IoAddress(function_type=1,
                                     information_number=1),
            elements=[common.IoElement_TIME_TAGGED_MESSAGE(
                common.DoubleWithTimeValue(
                    value=value,
                    time=time,
                    supplementary=supplementary))])])
    await slave.send(slave_asdu)
    master_data = await receive_queue.get()

    assert master_data.asdu_address == slave_asdu.address
    assert master_data.io_address == common.IoAddress(function_type=1,
                                                      information_number=1)
    assert master_data.cause.value == common.Cause.SPONTANEOUS.value
    assert master_data.value == common.DoubleWithTimeValue(
            value=value,
            time=time,
            supplementary=supplementary)

    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.skip(reason='test not implemented')
async def test_time_tagged_message_with_relative_time():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_measurands_1():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_time_tagged_measurands_with_relative_time():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_identification():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_time_synchronization():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_general_interrogation():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_general_interrogation_termination():
    pass


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
