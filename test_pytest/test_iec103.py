import asyncio
import math

import pytest

from hat import aio

from hat.drivers import iec103
from hat.drivers.iec60870 import link
from hat.drivers.iec60870.encodings import iec103 as encoding


default_time_seven = iec103.Time(
    size=iec103.TimeSize.SEVEN,
    milliseconds=0,
    invalid=False,
    substituted=False,
    minutes=0,
    summer_time=False,
    hours=12,
    day_of_week=1,
    day_of_month=1,
    months=1,
    years=99)

default_time_four = encoding.Time(
    size=encoding.TimeSize.FOUR,
    milliseconds=1,
    invalid=False,
    substituted=False,
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
    enc = encoding.Encoder()

    class MockLinkConnection(aio.Resource):

        def __init__(self):
            self._async_group = aio.Group()

        @property
        def async_group(self):
            return self._async_group

        @property
        def info(self):
            return link.ConnectionInfo(name=None,
                                       port='',
                                       address=0)

        async def send(self, data, sent_cb=None):
            send_queue.put_nowait(data)
            if sent_cb:
                await aio.call(sent_cb)

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
            asdu, _ = enc.decode_asdu(await send_queue.get())
            return asdu

    return MockLinkConnection(), MockSlave()


@pytest.mark.parametrize('asdu_address, time', [(0xFF, default_time_seven),
                                                (0x01, default_time_seven)])
async def test_time_sync(asdu_address, time):
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn)

    await master_conn.time_sync(time=time, asdu_address=asdu_address)
    sent = await slave.receive()

    assert sent.type == encoding.AsduType.TIME_SYNCHRONIZATION
    assert sent.cause == encoding.Cause.TIME_SYNCHRONIZATION
    assert sent.address == asdu_address
    assert len(sent.ios) == 1
    assert sent.ios[0].address.function_type == 255
    assert sent.ios[0].address.information_number == 0
    assert len(sent.ios[0].elements) == 1
    assert sent.ios[0].elements[0].time == time

    if asdu_address != 0xFF:
        await slave.send(encoding.ASDU(
            type=encoding.AsduType.TIME_SYNCHRONIZATION,
            cause=encoding.Cause.TIME_SYNCHRONIZATION,
            address=asdu_address,
            ios=[encoding.IO(
                address=encoding.IoAddress(function_type=255,
                                           information_number=0),
                elements=[
                    encoding.IoElement_TIME_SYNCHRONIZATION(time=time)])]))

    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.parametrize('data_causes', [
    ['gi'],
    ['gi', 'spontaneous', 'gi'],
    ['gi', 'spontaneous', 'gi', 'gi', 'spontaneous']])
async def test_interrogate(data_causes):
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn,
                                          data_cb=receive_queue.put_nowait)

    interrogate_future = asyncio.ensure_future(
        master_conn.interrogate(asdu_address=0x01))
    gi_initiation_asdu = await slave.receive()

    assert gi_initiation_asdu.type == encoding.AsduType.GENERAL_INTERROGATION
    assert gi_initiation_asdu.cause == encoding.Cause.GENERAL_INTERROGATION
    assert gi_initiation_asdu.address == 0x01
    assert len(gi_initiation_asdu.ios) == 1
    assert gi_initiation_asdu.ios[0].address.function_type == 255
    assert gi_initiation_asdu.ios[0].address.information_number == 0
    assert len(gi_initiation_asdu.ios[0].elements) == 1
    scan_number = gi_initiation_asdu.ios[0].elements[0].scan_number

    value = encoding.DoubleValue.OFF
    for data_cause, information_number in zip(
            data_causes, range(len(data_causes))):
        cause = (encoding.Cause.GENERAL_INTERROGATION if data_cause == 'gi'
                 else encoding.Cause.SPONTANEOUS)
        value = (encoding.DoubleValue.ON if value == encoding.DoubleValue.OFF
                 else encoding.DoubleValue.OFF)
        slave_asdu = encoding.ASDU(
            type=encoding.AsduType.TIME_TAGGED_MESSAGE,
            cause=cause,
            address=0x01,
            ios=[encoding.IO(
                address=encoding.IoAddress(
                    function_type=1, information_number=information_number),
                elements=[encoding.IoElement_TIME_TAGGED_MESSAGE(
                    encoding.DoubleWithTimeValue(
                        value=value,
                        time=default_time_four,
                        supplementary=1))])])
        await slave.send(slave_asdu)
        master_data = await receive_queue.get()

        assert master_data.asdu_address == slave_asdu.address
        assert master_data.io_address == encoding.IoAddress(
                function_type=1, information_number=information_number)
        assert master_data.cause.value == cause.value
        assert master_data.value == encoding.DoubleWithTimeValue(
                value=value,
                time=default_time_four,
                supplementary=1)

    assert not interrogate_future.done()

    await slave.send(encoding.ASDU(
        type=encoding.AsduType.GENERAL_INTERROGATION_TERMINATION,
        cause=encoding.Cause.TERMINATION_OF_GENERAL_INTERROGATION,
        address=0x01,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=255,
                                       information_number=0),
            elements=[
                encoding.IoElement_GENERAL_INTERROGATION_TERMINATION(
                    scan_number=scan_number)])]))

    await interrogate_future
    assert interrogate_future.done()
    await slave.async_close()
    await master_conn.async_close()


async def test_interrogate_different_scan_number():

    def termination_asdu(scan_number):
        return encoding.ASDU(
            type=encoding.AsduType.GENERAL_INTERROGATION_TERMINATION,
            cause=encoding.Cause.TERMINATION_OF_GENERAL_INTERROGATION,
            address=0x01,
            ios=[encoding.IO(
                address=encoding.IoAddress(function_type=255,
                                           information_number=0),
                elements=[
                    encoding.IoElement_GENERAL_INTERROGATION_TERMINATION(
                        scan_number=scan_number)])])

    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn)

    interrogate_future = asyncio.ensure_future(
        master_conn.interrogate(asdu_address=0x01))
    gi_initiation_asdu = await slave.receive()

    assert len(gi_initiation_asdu.ios) == 1
    assert len(gi_initiation_asdu.ios[0].elements) == 1
    scan_number = gi_initiation_asdu.ios[0].elements[0].scan_number

    await slave.send(termination_asdu((scan_number + 1) % 0x100))
    assert not interrogate_future.done()
    await slave.send(termination_asdu(scan_number))
    await interrogate_future
    assert interrogate_future.done()

    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.parametrize('cause', [
    encoding.Cause.GENERAL_COMMAND,
    encoding.Cause.GENERAL_COMMAND_NACK
])
async def test_send_command(cause):
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn,
                                          data_cb=receive_queue.put_nowait)

    io_address = encoding.IoAddress(function_type=33, information_number=44)

    send_command_future = asyncio.ensure_future(
        master_conn.send_command(asdu_address=11,
                                 io_address=io_address,
                                 value=encoding.DoubleValue.ON))
    ab = await slave.receive()
    assert ab.type == encoding.AsduType.GENERAL_COMMAND
    assert ab.cause == encoding.Cause.GENERAL_COMMAND
    assert ab.address == 11
    assert len(ab.ios) == 1
    assert ab.ios[0].address == io_address
    assert len(ab.ios[0].elements) == 1
    assert ab.ios[0].elements[0].value == encoding.DoubleValue.ON

    assert not send_command_future.done()

    slave_asdu = encoding.ASDU(
        type=encoding.AsduType.TIME_TAGGED_MESSAGE,
        cause=cause,
        address=0x01,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=1, information_number=11),
            elements=[encoding.IoElement_TIME_TAGGED_MESSAGE(
                encoding.DoubleWithTimeValue(
                    value=encoding.DoubleValue.ON,
                    time=default_time_four,
                    supplementary=0))])])
    await slave.send(slave_asdu)
    await send_command_future

    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.parametrize(
    'counter, io_more_follows, data_count, value_type, value, values_count, '
    'av_more_follows', [
        (False, False, 5,
         encoding.ValueType.INT, encoding.IntValue(13), 1, False),
        (False, False, 1,
         encoding.ValueType.INT, encoding.IntValue(13), 10, False),
        (False, False, 2,
         encoding.ValueType.INT, encoding.IntValue(13), 5, False)])
async def test_interrogate_generic(counter, io_more_follows, data_count,
                                   value_type, value, values_count,
                                   av_more_follows):
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(
        conn=conn, generic_data_cb=receive_queue.put_nowait)

    ggi_future = asyncio.ensure_future(
        master_conn.interrogate_generic(asdu_address=1))
    ggi_asdu = await slave.receive()

    assert ggi_asdu.type == encoding.AsduType.GENERIC_COMMAND
    assert ggi_asdu.cause == encoding.Cause.GENERAL_INTERROGATION
    assert ggi_asdu.address == 1
    assert len(ggi_asdu.ios) == 1
    assert ggi_asdu.ios[0].address == encoding.IoAddress(
        function_type=254,
        information_number=245)
    assert len(ggi_asdu.ios[0].elements) == 1
    assert ggi_asdu.ios[0].elements[0].data == []
    return_identifier = ggi_asdu.ios[0].elements[0].return_identifier

    data = [(encoding.Identification(group_id=0, entry_id=1),
             encoding.DescriptiveData(
                description=encoding.Description.VALUE_ARRAY,
                value=encoding.ArrayValue(
                    value_type=value_type,
                    more_follows=av_more_follows,
                    values=[value] * values_count)))] * data_count

    ggi_response_asdu = encoding.ASDU(
        type=encoding.AsduType.GENERIC_DATA,
        cause=encoding.Cause.GENERAL_INTERROGATION,
        address=1,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=254,
                                       information_number=245),
            elements=[encoding.IoElement_GENERIC_DATA(
                return_identifier=return_identifier,
                counter=counter,
                more_follows=io_more_follows,
                data=data)])])
    await slave.send(ggi_response_asdu)

    for i in range(data_count):
        master_cb_generic_data = await receive_queue.get()
        assert master_cb_generic_data.asdu_address == 1
        assert master_cb_generic_data.io_address == encoding.IoAddress(
            function_type=254, information_number=245)
        assert master_cb_generic_data.cause == iec103.GenericDataCause.GENERAL_INTERROGATION  # NOQA
        assert master_cb_generic_data.identification == encoding.Identification(  # NOQA
            group_id=0, entry_id=1)
        assert master_cb_generic_data.description == encoding.Description.VALUE_ARRAY  # NOQA
        assert master_cb_generic_data.value == data[i][1].value

    spontaneus_generic_data_asdu = encoding.ASDU(
        type=encoding.AsduType.GENERIC_DATA,
        cause=encoding.Cause.SPONTANEOUS,
        address=1,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=254,
                                       information_number=244),
            elements=[encoding.IoElement_GENERIC_DATA(
                return_identifier=0,
                counter=counter,
                more_follows=io_more_follows,
                data=data)])])
    await slave.send(spontaneus_generic_data_asdu)

    for i in range(data_count):
        master_cb_generic_data = await receive_queue.get()
        assert master_cb_generic_data.asdu_address == 1
        assert master_cb_generic_data.io_address == encoding.IoAddress(
            function_type=254, information_number=244)
        assert master_cb_generic_data.cause == iec103.GenericDataCause.SPONTANEOUS  # NOQA
        assert master_cb_generic_data.identification == encoding.Identification(  # NOQA
            group_id=0, entry_id=1)
        assert master_cb_generic_data.description == encoding.Description.VALUE_ARRAY  # NOQA
        assert master_cb_generic_data.value == data[i][1].value

    assert not ggi_future.done()

    ggi_termination_wrong_rii = encoding.ASDU(
        type=encoding.AsduType.GENERIC_DATA,
        cause=encoding.Cause.TERMINATION_OF_GENERAL_INTERROGATION,
        address=1,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=254,
                                       information_number=245),
            elements=[encoding.IoElement_GENERIC_DATA(
                return_identifier=1,
                counter=counter,
                more_follows=io_more_follows,
                data=[])])])
    await slave.send(ggi_termination_wrong_rii)

    assert not ggi_future.done()

    ggi_termination = encoding.ASDU(
        type=encoding.AsduType.GENERIC_DATA,
        cause=encoding.Cause.TERMINATION_OF_GENERAL_INTERROGATION,
        address=1,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=254,
                                       information_number=245),
            elements=[encoding.IoElement_GENERIC_DATA(
                return_identifier=return_identifier,
                counter=counter,
                more_follows=io_more_follows,
                data=[])])])
    await slave.send(ggi_termination)

    await ggi_future
    assert ggi_future.done()

    await slave.async_close()
    await master_conn.async_close()


def compare_measurands_2_data(master_data, value):
    for i, v in enumerate(master_data.value.values.items()):
        measurand_type, measurand_value = v
        assert measurand_type == iec103.MeasurandType((
            encoding.AsduType.MEASURANDS_2.value, i))
        assert measurand_value.overflow == value[i].overflow
        assert measurand_value.invalid == value[i].invalid
        assert math.isclose(measurand_value.value,
                            value[i].value,
                            rel_tol=1e-2)
        return True


@pytest.mark.parametrize('asdu_type, value, cmp_fn', [
    (encoding.AsduType.TIME_TAGGED_MESSAGE,
     encoding.DoubleWithTimeValue(value=encoding.DoubleValue.ON,
                                  time=default_time_four,
                                  supplementary=5),
     None),
    (encoding.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME,
     encoding.DoubleWithRelativeTimeValue(value=encoding.DoubleValue.ON,
                                          relative_time=123,
                                          fault_number=123,
                                          time=default_time_four,
                                          supplementary=1),
     None),
    (encoding.AsduType.MEASURANDS_1,
     encoding.MeasurandValue(overflow=False, invalid=False, value=0.14),
     lambda recv_val, sent_val: math.isclose(
         recv_val.value.values[iec103.MeasurandType.M1_I_L2].value,
         sent_val.value,
         rel_tol=1e-3)),
    (encoding.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME,
     encoding.MeasurandWithRelativeTimeValue(value=3.14,
                                             relative_time=123,
                                             fault_number=123,
                                             time=default_time_four),
     lambda recv_val, sent_val: math.isclose(recv_val.value.value,
                                             sent_val.value,
                                             rel_tol=1e-3)),
    (encoding.AsduType.MEASURANDS_2,
     [encoding.MeasurandValue(overflow=False, invalid=False, value=0.1)],
     compare_measurands_2_data),
    (encoding.AsduType.MEASURANDS_2,
     [encoding.MeasurandValue(overflow=False, invalid=False, value=-0.1),
      encoding.MeasurandValue(overflow=False, invalid=False, value=0.5),
      encoding.MeasurandValue(overflow=False, invalid=False, value=-0.5),
      encoding.MeasurandValue(overflow=False, invalid=False, value=0.9999),
      encoding.MeasurandValue(overflow=False, invalid=False, value=-0.9999),
      encoding.MeasurandValue(overflow=False, invalid=False, value=0.9999),
      encoding.MeasurandValue(overflow=False, invalid=False, value=-1.0),
      encoding.MeasurandValue(overflow=False, invalid=False, value=0.5936),
      encoding.MeasurandValue(overflow=False, invalid=False, value=-0.5936)],
     compare_measurands_2_data)])
async def test_spontaneous(asdu_type, value, cmp_fn):
    receive_queue = aio.Queue()
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn,
                                          data_cb=receive_queue.put_nowait)
    element = getattr(encoding, f'IoElement_{asdu_type.name}')
    io_addr = encoding.IoAddress(function_type=1, information_number=1)

    elements = []
    if isinstance(value, list):
        elements = [element(v) for v in value]
    else:
        elements = [element(value)]

    slave_asdu = encoding.ASDU(
        type=asdu_type,
        cause=encoding.Cause.SPONTANEOUS,
        address=1,
        ios=[encoding.IO(address=io_addr, elements=elements)])
    await slave.send(slave_asdu)

    master_data = await receive_queue.get()

    assert master_data.asdu_address == slave_asdu.address
    assert master_data.io_address == io_addr
    assert master_data.cause.value == encoding.Cause.SPONTANEOUS.value

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
    io_addr = encoding.IoAddress(function_type=1, information_number=1)

    slave_asdu = encoding.ASDU(
        type=encoding.AsduType.IDENTIFICATION,
        cause=encoding.Cause.SPONTANEOUS,
        address=1,
        ios=[encoding.IO(
            address=io_addr,
            elements=[encoding.IoElement_IDENTIFICATION(
                compatibility=1,
                value=b'10101010',
                software=b'1010')])])
    await slave.send(slave_asdu)
    await slave.async_close()
    await master_conn.async_close()


@pytest.mark.skip(reason='test not implemented')
async def test_generic_identification():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_general_command():
    pass


@pytest.mark.skip(reason='test not implemented')
async def test_generic_command():
    pass


async def test_transmission_of_disturbance_data():
    conn, slave = create_connection_slave_pair()
    master_conn = iec103.MasterConnection(conn=conn)
    slave_asdu = encoding.ASDU(
        type=encoding.AsduType.LIST_OF_RECORDED_DISTURBANCES,
        cause=encoding.Cause.TRANSMISSION_OF_DISTURBANCE_DATA,
        address=1,
        ios=[encoding.IO(
            address=encoding.IoAddress(function_type=1,
                                       information_number=1),
            elements=[encoding.IoElement_LIST_OF_RECORDED_DISTURBANCES(
                fault_number=3,
                trip=True,
                transmitted=False,
                test=False,
                other=False,
                time=default_time_seven)])])
    await slave.send(slave_asdu)
    # TODO: finish sequence when functionality implemented
    await slave.async_close()
    await master_conn.async_close()
