import math
import random

import pytest

from hat import aio
from hat import util
from hat.drivers.iec60870 import iec101
from hat.drivers.iec60870 import link
from hat.drivers.iec60870 import app
from hat.drivers.iec60870.iec101.encoder import _encode_msg

rndm = random.Random(1)


class MockLinkConnection(link.Connection):

    def __init__(self):
        self._data_queue = aio.Queue()
        self._data_queue = aio.Queue()
        self._async_group = aio.Group()

    @property
    def async_group(self):
        return self._async_group

    async def send(self, data):
        self._data_queue.put_nowait(data)

    async def receive(self):
        return await self._data_queue.get()


def gen_quality(value):
    if type(value) in [iec101.SingleValue,
                       iec101.DoubleValue]:
        return iec101.IndicationQuality(
            invalid=gen_random_bool(),
            not_topical=gen_random_bool(),
            substituted=gen_random_bool(),
            blocked=gen_random_bool())
    if type(value) in [iec101.StepPositionValue,
                       iec101.BitstringValue,
                       iec101.NormalizedValue,
                       iec101.ScaledValue,
                       iec101.FloatingValue,
                       iec101.StatusValue]:
        return iec101.MeasurementQuality(
            invalid=gen_random_bool(),
            not_topical=gen_random_bool(),
            substituted=gen_random_bool(),
            blocked=gen_random_bool(),
            overflow=gen_random_bool())
    if type(value) is iec101.BinaryCounterValue:
        return iec101.CounterQuality(
            invalid=gen_random_bool(),
            adjusted=gen_random_bool(),
            overflow=gen_random_bool(),
            sequence=rndm.randint(0, 31))
    if type(value) in [iec101.ProtectionValue,
                       iec101.ProtectionStartValue,
                       iec101.ProtectionCommandValue]:
        return iec101.ProtectionQuality(
            invalid=gen_random_bool(),
            not_topical=gen_random_bool(),
            substituted=gen_random_bool(),
            blocked=gen_random_bool(),
            time_invalid=gen_random_bool())


def gen_random_bool():
    return bool(rndm.randint(0, 1))


def gen_asdu_address(size):
    if size == iec101.AsduAddressSize.ONE:
        return rndm.randint(0, 255)
    elif size == iec101.AsduAddressSize.TWO:
        return rndm.randint(256, 65535)


def gen_io_address(size):
    if iec101.IoAddressSize.ONE:
        return rndm.randint(0, 255)
    elif iec101.IoAddressSize.TWO:
        return rndm.randint(256, 65535)
    elif iec101.IoAddressSize.THREE:
        return rndm.randint(65536, 16777215)


def remove_msg_value(msg):
    key = {iec101.DataMsg: 'data',
           iec101.CommandMsg: 'command',
           iec101.ParameterMsg: 'parameter'}[type(msg)]
    new_value = getattr(msg, key).value._replace(value=None)
    return msg._replace(**{key: getattr(msg, key)._replace(value=new_value)})


def create_message(msg_type, asdu, io, originator, value=None):
    if msg_type == iec101.DataMsg:
        return iec101.DataMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            io_address=io,
            data=data_from_value(value),
            time=gen_time(value),
            cause=rndm.choice([*list(iec101.DataResCause)]))
    if msg_type == iec101.CommandMsg:
        return iec101.CommandMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            io_address=io,
            command=command_from_value(value),
            is_negative_confirm=gen_random_bool(),
            cause=gen_command_cause())
    if msg_type == iec101.InitializationMsg:
        return iec101.InitializationMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            param_change=gen_random_bool(),
            cause=rndm.choice([*list(iec101.InitializationResCause)]))
    if msg_type == iec101.InterrogationMsg:
        return iec101.InterrogationMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            request=rndm.randint(0, 255),
            cause=gen_command_cause())
    if msg_type == iec101.CounterInterrogationMsg:
        return iec101.CounterInterrogationMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            request=rndm.randint(0, 63),
            freeze=rndm.choice(list(iec101.FreezeCode)),
            cause=gen_command_cause())
    if msg_type == iec101.ReadMsg:
        return iec101.ReadMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            io_address=io,
            cause=rndm.choice([*list(iec101.ReadReqCause),
                               *list(iec101.ReadResCause)]))
    if msg_type == iec101.ClockSyncMsg:
        return iec101.ClockSyncMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            time=gen_time_of_size(),
            cause=gen_activation_cause())
    if msg_type == iec101.TestMsg:
        return iec101.TestMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            cause=gen_activation_cause())
    if msg_type == iec101.ResetMsg:
        return iec101.ResetMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            qualifier=rndm.randint(0, 255),
            cause=gen_activation_cause())
    if msg_type == iec101.ResetMsg:
        return iec101.ResetMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            qualifier=rndm.randint(0, 255),
            cause=gen_activation_cause())
    if msg_type == iec101.DelayMsg:
        return iec101.DelayMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            time=rndm.randint(0, 65535),
            cause=rndm.choice([*list(iec101.DelayReqCause),
                               *list(iec101.DelayResCause)]))
    if msg_type == iec101.ParameterMsg:
        return iec101.ParameterMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            io_address=io,
            parameter=paramter_from_value(value),
            cause=rndm.choice([*list(iec101.ParameterReqCause),
                               *list(iec101.ParameterResCause)]))
    if msg_type == iec101.ParameterActivationMsg:
        return iec101.ParameterActivationMsg(
            is_test=gen_random_bool(),
            originator_address=originator,
            asdu_address=asdu,
            io_address=io,
            qualifier=rndm.randint(0, 255),
            cause=rndm.choice([*list(iec101.ParameterActivationReqCause),
                               *list(iec101.ParameterActivationResCause)]))


def data_from_value(value):
    data_class = {
        iec101.SingleValue: iec101.SingleData,
        iec101.DoubleValue: iec101.DoubleData,
        iec101.StepPositionValue: iec101.StepPositionData,
        iec101.BitstringValue: iec101.BitstringData,
        iec101.NormalizedValue: iec101.NormalizedData,
        iec101.ScaledValue: iec101.ScaledData,
        iec101.FloatingValue: iec101.FloatingData,
        iec101.BinaryCounterValue: iec101.BinaryCounterData,
        iec101.ProtectionValue: iec101.ProtectionData,
        iec101.ProtectionStartValue: iec101.ProtectionStartData,
        iec101.ProtectionCommandValue: iec101.ProtectionCommandData,
        iec101.StatusValue: iec101.StatusData,
        }[type(value)]
    if data_class == iec101.ProtectionData:
        return data_class(
            value=value,
            quality=gen_quality(value),
            elapsed_time=rndm.randint(0, 65535))
    if data_class == iec101.ProtectionStartData:
        return data_class(
            value=value,
            quality=gen_quality(value),
            duration_time=rndm.randint(0, 65535))
    if data_class == iec101.ProtectionCommandData:
        return data_class(
            value=value,
            quality=gen_quality(value),
            operating_time=rndm.randint(0, 65535))
    return data_class(
            value=value,
            quality=gen_quality(value))


def command_from_value(value):
    command_class = {
        iec101.SingleValue: iec101.SingleCommand,
        iec101.DoubleValue: iec101.DoubleCommand,
        iec101.RegulatingValue: iec101.RegulatingCommand,
        iec101.NormalizedValue: iec101.NormalizedCommand,
        iec101.ScaledValue: iec101.ScaledCommand,
        iec101.FloatingValue: iec101.FloatingCommand,
        iec101.BitstringValue: iec101.BitstringCommand,
        }[type(value)]
    if command_class == iec101.BitstringCommand:
        return command_class(value=value)
    elif command_class in [iec101.NormalizedCommand,
                           iec101.ScaledCommand,
                           iec101.FloatingCommand]:
        return command_class(
            value=value,
            select=gen_random_bool())
    return command_class(
        value=value,
        select=gen_random_bool(),
        qualifier=rndm.randint(0, 31))


def paramter_from_value(value):
    parameter_class = {
        iec101.NormalizedValue: iec101.NormalizedParameter,
        iec101.ScaledValue: iec101.ScaledParameter,
        iec101.FloatingValue: iec101.FloatingParameter
    }[type(value)]
    return parameter_class(
        value=value,
        qualifier=rndm.randint(0, 255))


def gen_time_of_size(size=iec101.TimeSize.SEVEN):
    milliseconds = rndm.randint(0, 59999)
    invalid = gen_random_bool()
    minutes = rndm.randint(0, 59)
    summer_time = gen_random_bool()
    hours = rndm.randint(0, 23)
    day_of_week = rndm.randint(1, 7)
    day_of_month = rndm.randint(1, 31)
    months = rndm.randint(1, 12)
    years = rndm.randint(0, 99)
    if size == iec101.TimeSize.THREE:
        return iec101.Time(
                    size=iec101.TimeSize.THREE,
                    milliseconds=milliseconds,
                    invalid=invalid,
                    minutes=minutes,
                    summer_time=None,
                    hours=None,
                    day_of_week=None,
                    day_of_month=None,
                    months=None,
                    years=None)
    if size == iec101.TimeSize.SEVEN:
        return iec101.Time(
                        size=iec101.TimeSize.SEVEN,
                        milliseconds=milliseconds,
                        invalid=invalid,
                        minutes=minutes,
                        summer_time=summer_time,
                        hours=hours,
                        day_of_week=day_of_week,
                        day_of_month=day_of_month,
                        months=months,
                        years=years)


def gen_time(value):
    if type(value) in [iec101.ProtectionValue,
                       iec101.ProtectionStartValue,
                       iec101.ProtectionCommandValue]:
        return gen_time_of_size(size=iec101.TimeSize.SEVEN)
    elif type(value) == iec101.StatusValue:
        return
    time_size = rndm.choice([iec101.TimeSize.SEVEN,
                             iec101.TimeSize.THREE,
                             None])
    if time_size is None:
        return
    return gen_time_of_size(size=time_size)


async def test_connection():
    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=iec101.CauseSize.TWO,
                             asdu_address_size=iec101.AsduAddressSize.TWO,
                             io_address_size=iec101.IoAddressSize.THREE)
    assert conn.is_open

    await conn_link.async_close()

    await conn.wait_closed()
    assert conn.is_closed


def gen_command_cause():
    return rndm.choice([*list(iec101.CommandReqCause),
                        *list(iec101.CommandResCause)])


def gen_activation_cause():
    return rndm.choice([*list(iec101.ActivationReqCause),
                        *list(iec101.ActivationResCause)])


def get_data_from_msg(msg):
    if isinstance(msg, iec101.DataMsg):
        return msg.data
    elif isinstance(msg, iec101.CommandMsg):
        return msg.command
    elif isinstance(msg, iec101.ParameterMsg):
        return msg.parameter


def get_values(value_type):
    if value_type == iec101.SingleValue:
        yield from iec101.SingleValue
    elif value_type == iec101.DoubleValue:
        yield from iec101.DoubleValue
    elif value_type == iec101.RegulatingValue:
        yield from iec101.RegulatingValue
    elif value_type == iec101.StepPositionValue:
        for i in range(-64, 64):
            for tr in [True, False]:
                yield iec101.StepPositionValue(value=i, transient=tr)
    elif value_type == iec101.BitstringValue:
        yield iec101.BitstringValue(value=b'\xff' * 4)
    elif value_type == iec101.NormalizedValue:
        yield iec101.NormalizedValue(value=-0.9987)
    elif value_type == iec101.ScaledValue:
        for i in [-2**15, 2**14, 0, 123]:
            yield iec101.ScaledValue(value=i)
    elif value_type == iec101.FloatingValue:
        for i in [-12345.678, 12345.678, 0.123]:
            yield iec101.FloatingValue(value=i)
    elif value_type == iec101.BinaryCounterValue:
        for i in [-2**31, 2**30, 123]:
            yield iec101.BinaryCounterValue(value=i)
    elif value_type == iec101.ProtectionValue:
        yield from iec101.ProtectionValue
    elif value_type == iec101.ProtectionStartValue:
        for i in range(10):
            yield iec101.ProtectionStartValue(
                        general=gen_random_bool(),
                        l1=gen_random_bool(),
                        l2=gen_random_bool(),
                        l3=gen_random_bool(),
                        ie=gen_random_bool(),
                        reverse=gen_random_bool())
    elif value_type == iec101.ProtectionCommandValue:
        for i in range(10):
            yield iec101.ProtectionCommandValue(
                        general=gen_random_bool(),
                        l1=gen_random_bool(),
                        l2=gen_random_bool(),
                        l3=gen_random_bool())
    elif value_type == iec101.StatusValue:
        yield iec101.StatusValue(
                value=[True] * 16,
                change=[True] * 16)
        for i in range(10):
            yield iec101.StatusValue(
                value=[gen_random_bool() for _ in range(16)],
                change=[gen_random_bool() for _ in range(16)])
    else:
        yield None


@pytest.mark.parametrize("msg_type, value_type, repetitions", [
    (iec101.DataMsg, iec101.SingleValue, 5),
    (iec101.DataMsg, iec101.DoubleValue, 5),
    (iec101.DataMsg, iec101.StepPositionValue, 5),
    (iec101.DataMsg, iec101.BitstringValue, 5),
    (iec101.DataMsg, iec101.NormalizedValue, 5),
    (iec101.DataMsg, iec101.ScaledValue, 5),
    (iec101.DataMsg, iec101.FloatingValue, 5),
    (iec101.DataMsg, iec101.BinaryCounterValue, 5),
    (iec101.DataMsg, iec101.ProtectionValue, 5),
    (iec101.DataMsg, iec101.ProtectionStartValue, 5),
    (iec101.DataMsg, iec101.ProtectionCommandValue, 5),
    (iec101.DataMsg, iec101.StatusValue, 5),
    (iec101.CommandMsg, iec101.SingleValue, 5),
    (iec101.CommandMsg, iec101.DoubleValue, 5),
    (iec101.CommandMsg, iec101.RegulatingValue, 5),
    (iec101.CommandMsg, iec101.NormalizedValue, 5),
    (iec101.CommandMsg, iec101.ScaledValue, 5),
    (iec101.CommandMsg, iec101.FloatingValue, 5),
    (iec101.CommandMsg, iec101.BitstringValue, 5),
    (iec101.InitializationMsg, None, 5),
    (iec101.InterrogationMsg, None, 5),
    (iec101.CounterInterrogationMsg, None, 5),
    (iec101.ReadMsg, None, 5),
    (iec101.ClockSyncMsg, None, 5),
    (iec101.TestMsg, None, 5),
    (iec101.ResetMsg, None, 5),
    (iec101.DelayMsg, None, 5),
    (iec101.ParameterMsg, iec101.NormalizedValue, 5),
    (iec101.ParameterMsg, iec101.ScaledValue, 5),
    (iec101.ParameterMsg, iec101.FloatingValue, 5),
    (iec101.ParameterActivationMsg, None, 5),
    ])
async def test_send_receive(msg_type, value_type, repetitions):
    cause_size = rndm.choice(list(iec101.CauseSize))
    asdu_size = rndm.choice(list(iec101.AsduAddressSize))
    io_size = rndm.choice(list(iec101.IoAddressSize))

    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=cause_size,
                             asdu_address_size=asdu_size,
                             io_address_size=io_size)

    for value in get_values(value_type):
        for _ in range(repetitions):
            originator = (0 if cause_size == iec101.CauseSize.ONE
                          else rndm.randint(0, 255))
            asdu = gen_asdu_address(asdu_size)
            io = gen_io_address(io_size)
            msg_sent = create_message(msg_type, asdu, io, originator, value)
            res = await conn.send([msg_sent])
            assert res is None
            msgs = await conn.receive()
            assert len(msgs) == 1
            msg_received = msgs[0]

            if type(value) in [iec101.NormalizedValue,
                               iec101.FloatingValue]:
                data_sent = get_data_from_msg(msg_sent)
                data_received = get_data_from_msg(msg_received)
                assert math.isclose(data_sent.value.value,
                                    data_received.value.value,
                                    rel_tol=1e-3)
                msg_sent = remove_msg_value(msg_sent)
                msg_received = remove_msg_value(msg_received)

            assert msg_sent == msg_received


def msg_type_causes_unexp():
    # generates message type with all causes unexpected for that type
    causes_all = set(i.name for i in app.iec101.common.CauseType)

    causes = set(i.name for i in iec101.DataResCause)
    yield from ((iec101.DataMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    causes = set(i.name for i in [*list(iec101.CommandReqCause),
                                  *list(iec101.CommandResCause)])
    yield from ((iec101.CommandMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    yield from ((iec101.InterrogationMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    yield from ((iec101.CounterInterrogationMsg,
                 app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    causes = set(i.name for i in [*list(iec101.ReadReqCause),
                                  *list(iec101.ReadResCause)])
    yield from ((iec101.ReadMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    causes = set(i.name for i in [*list(iec101.ActivationReqCause),
                                  *list(iec101.ActivationResCause)])
    yield from ((iec101.ClockSyncMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    yield from ((iec101.TestMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    yield from ((iec101.ResetMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    causes = set(i.name for i in [*list(iec101.DelayReqCause),
                                  *list(iec101.DelayResCause)])
    yield from ((iec101.DelayMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    causes = set(i.name for i in [*list(iec101.ParameterReqCause),
                                  *list(iec101.ParameterResCause)])
    yield from ((iec101.ParameterMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))

    causes = set(i.name for i in [*list(iec101.ParameterActivationReqCause),
                                  *list(iec101.ParameterActivationResCause)])
    yield from ((iec101.ParameterActivationMsg, app.iec101.common.CauseType[c])
                for c in causes_all.difference(causes))


@pytest.mark.parametrize("msg_type, cause_unexp", msg_type_causes_unexp())
async def test_cause_unexpected(msg_type, cause_unexp):
    cause_size = iec101.CauseSize.TWO
    asdu_size = iec101.AsduAddressSize.TWO
    io_size = iec101.IoAddressSize.TWO

    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=cause_size,
                             asdu_address_size=asdu_size,
                             io_address_size=io_size)

    value_type = {
        iec101.DataMsg: iec101.SingleValue,
        iec101.CommandMsg: iec101.SingleValue,
        iec101.ParameterMsg: iec101.NormalizedValue}.get(msg_type)
    value = util.first(get_values(value_type)) if value_type else None
    msg = create_message(msg_type, 1, 2, 123, value)

    # message is first encoded to app.iec101.common.ASDU
    asdu = _encode_msg(msg)
    # asdu's cause type is replaced with cause unexepcted for this message type
    asdu_cause_unexp = asdu._replace(
        cause=asdu.cause._replace(type=cause_unexp))
    # asdu is encoded with app.iec101.encoder.Encoder to bytes
    asdu_bytes = conn._encoder._encoder.encode_asdu(asdu_cause_unexp)

    # bytes are set to queue to be received from connection
    conn_link._data_queue.put_nowait(asdu_bytes)
    msgs_received = await conn.receive()
    msg_no_cause = msgs_received[0]

    assert isinstance(msg_no_cause.cause, int)
    assert msg_no_cause.cause == cause_unexp.value
