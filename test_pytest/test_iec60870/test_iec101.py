import itertools
import math

import pytest

from hat import aio
from hat.drivers.iec60870 import app
from hat.drivers.iec60870 import iec101
from hat.drivers.iec60870 import link


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


def gen_qualities(amount, quality_class):
    samples = {
        'invalid': [True, False, True],
        'not_topical': [True, False, False],
        'substituted': [True, False, True],
        'blocked': [True, False, False],
        'adjusted': [True, False, True],
        'overflow': [True, False, False],
        'time_invalid': [True, False, True],
        'sequence': [0, 31, 13]}
    cnt = 0
    while True:
        for q_dict in [dict(zip(samples.keys(), values))
                       for values in zip(*samples.values())]:
            yield quality_class(**{k: v for k, v in q_dict.items()
                                if hasattr(quality_class, k)})
            cnt += 1
            if cnt == amount:
                return


def gen_times(amount):
    samples = {
        'milliseconds': (0, 59999, 1234),
        'invalid': [True, False, True],
        'minutes': (0, 59, 30),
        'summer_time': [True, False, True],
        'hours': (0, 23, 12),
        'day_of_week': (1, 7, 3),
        'day_of_month': (1, 31, 13),
        'months': (1, 12, 6),
        'years': (0, 99, 50)}
    cnt = 0
    while True:
        for values in zip(*samples.values()):
            time_dict = dict(zip(samples.keys(), values))
            yield iec101.Time(**time_dict,
                              size=iec101.TimeSize.SEVEN)
            cnt += 1
            if cnt == amount:
                return


def assert_msg_default(msg1, msg2):
    assert msg1 == msg2


def assert_msg_data_float(msg1, msg2):
    assert msg1.is_test == msg2.is_test
    assert msg1.originator_address == msg2.originator_address
    assert msg1.asdu_address == msg2.asdu_address
    assert msg1.io_address == msg2.io_address
    assert msg1.time == msg2.time
    assert msg1.cause == msg2.cause
    assert msg1.data.quality == msg2.data.quality
    assert math.isclose(msg1.data.value.value,
                        msg2.data.value.value,
                        rel_tol=1e-3)


def assert_msg_cmd_float(msg1, msg2):
    assert msg1.is_test == msg2.is_test
    assert msg1.originator_address == msg2.originator_address
    assert msg1.asdu_address == msg2.asdu_address
    assert msg1.io_address == msg2.io_address
    assert msg1.cause == msg2.cause
    if hasattr(msg1.command, 'select'):
        assert msg1.command.select == msg2.command.select
    if hasattr(msg1.command, 'qualifier'):
        assert msg1.command.qualifier == msg2.command.qualifier
    assert math.isclose(msg1.command.value.value,
                        msg2.command.value.value,
                        rel_tol=1e-3)


def assert_msg_param_float(msg1, msg2):
    assert msg1.is_test == msg2.is_test
    assert msg1.originator_address == msg2.originator_address
    assert msg1.asdu_address == msg2.asdu_address
    assert msg1.io_address == msg2.io_address
    assert msg1.cause == msg2.cause
    assert msg1.parameter.qualifier == msg2.parameter.qualifier
    assert math.isclose(msg1.parameter.value.value,
                        msg2.parameter.value.value,
                        rel_tol=1e-3)


async def assert_send_receive(msgs, cause_size, asdu_size, io_size,
                              assert_msg=assert_msg_default):
    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=cause_size,
                             asdu_address_size=asdu_size,
                             io_address_size=io_size)

    res = await conn.send(msgs)
    assert res is None
    msgs_received = await conn.receive()
    for msg_sent, msg_rec in zip(msgs, msgs_received):
        assert_msg(msg_sent, msg_rec)


async def test_connection():
    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=iec101.CauseSize.TWO,
                             asdu_address_size=iec101.AsduAddressSize.TWO,
                             io_address_size=iec101.IoAddressSize.THREE)
    assert conn.is_open

    conn_link.close()

    await conn.wait_closed()
    assert conn.is_closed

    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=iec101.CauseSize.TWO,
                             asdu_address_size=iec101.AsduAddressSize.TWO,
                             io_address_size=iec101.IoAddressSize.THREE)

    conn.close()

    await conn.wait_closed()
    assert conn_link.is_closed


@pytest.mark.parametrize("data", [
    *(iec101.SingleData(value=v, quality=q)
        for v, q in itertools.product(
            iec101.SingleValue,
            gen_qualities(2, iec101.IndicationQuality))),

    *(iec101.DoubleData(value=v, quality=q)
        for v, q in itertools.product(
            iec101.DoubleValue,
            gen_qualities(2, iec101.IndicationQuality))),

    *(iec101.StepPositionData(
            value=v,
            quality=q)
      for v, q in zip((iec101.StepPositionValue(value=-64, transient=True),
                       iec101.StepPositionValue(value=63, transient=False)),
                      gen_qualities(2, iec101.MeasurementQuality))),

    *(iec101.BitstringData(
            value=v,
            quality=q)
      for v, q in zip((iec101.BitstringValue(value=b'\xff' * 4),
                       iec101.BitstringValue(value=b'\x00' * 4)),
                      gen_qualities(2, iec101.MeasurementQuality))),

    *(iec101.NormalizedData(
            value=v,
            quality=q)
      for v, q in zip((iec101.NormalizedValue(value=-0.99876),
                       iec101.NormalizedValue(value=0.99876)),
                      gen_qualities(2, iec101.MeasurementQuality))),

    *(iec101.FloatingData(
            value=v,
            quality=q)
      for v, q in zip((iec101.FloatingValue(value=-12345.678),
                       iec101.FloatingValue(value=12345.678)),
                      gen_qualities(2, iec101.MeasurementQuality))),

    *(iec101.ScaledData(
            value=v,
            quality=q)
      for v, q in zip((iec101.ScaledValue(value=-2**15),
                       iec101.ScaledValue(value=2**14)),
                      gen_qualities(2, iec101.MeasurementQuality))),

    *(iec101.BinaryCounterData(
            value=v,
            quality=q)
      for v, q in zip((iec101.BinaryCounterValue(value=-2**31),
                       iec101.BinaryCounterValue(value=2**30)),
                      gen_qualities(2, iec101.CounterQuality))),

    *(iec101.StatusData(
            value=v,
            quality=q)
      for v, q in zip((iec101.StatusValue(value=[True] * 16,
                                          change=[True] * 16),
                       iec101.StatusValue(value=[False] * 16,
                                          change=[False] * 16)),
                      gen_qualities(2, iec101.MeasurementQuality))),
        ])
@pytest.mark.parametrize(
    "is_test, time, asdu, asdu_size, io, io_size, orig, cause, cause_size",
    zip((True, False, True, False),
        (*gen_times(3), None),
        (0, 255, 65535, 123),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215, 123),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE,
         iec101.IoAddressSize.TWO),
        (0, 0, 255, 13),
        (iec101.DataResCause.SPONTANEOUS,
         iec101.DataResCause.INTERROGATED_STATION,
         iec101.DataResCause.REMOTE_COMMAND,
         iec101.DataResCause.LOCAL_COMMAND),
        (iec101.CauseSize.ONE, iec101.CauseSize.ONE,
         iec101.CauseSize.TWO, iec101.CauseSize.TWO)))
async def test_send_receive_data2(is_test, time, asdu, asdu_size,
                                  io, io_size, orig, cause, cause_size, data):
    if isinstance(data, iec101.StatusData):
        time = None
    msg = iec101.DataMsg(
            is_test=is_test,
            originator_address=orig,
            asdu_address=asdu,
            io_address=io,
            data=data,
            time=time,
            cause=cause)
    if isinstance(data.value.value, float):
        await assert_send_receive([msg], cause_size, asdu_size,
                                  io_size, assert_msg_data_float)
    else:
        await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("data", [
    *(iec101.ProtectionData(value=iec101.ProtectionValue.ON,
                            quality=q,
                            elapsed_time=0)
      for q in gen_qualities(2, iec101.ProtectionQuality)),

    *(iec101.ProtectionData(value=iec101.ProtectionValue.OFF,
                            quality=q,
                            elapsed_time=65535)
      for q in gen_qualities(2, iec101.ProtectionQuality)),

    *(iec101.ProtectionStartData(
        value=v,
        quality=q,
        duration_time=dur_t)
      for v, q, dur_t in zip(
        (iec101.ProtectionStartValue(general=False,
                                     l1=False,
                                     l2=False,
                                     l3=False,
                                     ie=False,
                                     reverse=False),
         iec101.ProtectionStartValue(general=True,
                                     l1=True,
                                     l2=True,
                                     l3=True,
                                     ie=True,
                                     reverse=True)),
        gen_qualities(2, iec101.ProtectionQuality),
        (65535, 0))),

    *(iec101.ProtectionCommandData(
        value=v,
        quality=q,
        operating_time=oper_t)
      for v, q, oper_t in zip(
        (iec101.ProtectionCommandValue(general=True,
                                       l1=True,
                                       l2=True,
                                       l3=True),
         iec101.ProtectionCommandValue(general=False,
                                       l1=False,
                                       l2=False,
                                       l3=False)),
        gen_qualities(2, iec101.ProtectionQuality),
        (65535, 0))),
        ])
@pytest.mark.parametrize(
    "is_test, time, asdu, asdu_size, io, io_size, orig, cause, cause_size",
    zip((True, False, True),
        gen_times(3),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.DataResCause.SPONTANEOUS,
         iec101.DataResCause.INTERROGATED_STATION,
         iec101.DataResCause.REMOTE_COMMAND),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_protection_data(is_test, time, asdu, asdu_size, io,
                                            io_size, orig, cause, cause_size,
                                            data):
    msg = iec101.DataMsg(
            is_test=is_test,
            originator_address=orig,
            asdu_address=asdu,
            io_address=io,
            data=data,
            time=time,
            cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("command", [
    *(iec101.SingleCommand(value=v, select=s, qualifier=q)
        for v, s, q in itertools.product(iec101.SingleValue,
                                         (True, False),
                                         (0, 31))),
    *(iec101.DoubleCommand(value=v, select=s, qualifier=q)
        for v, s, q in itertools.product(iec101.DoubleValue,
                                         (True, False),
                                         (0, 31))),
    *(iec101.RegulatingCommand(value=v, select=s, qualifier=q)
        for v, s, q in itertools.product(iec101.RegulatingValue,
                                         (True, False),
                                         (0, 31))),
    *(iec101.NormalizedCommand(value=v, select=s)
        for v, s in itertools.product(
            (iec101.NormalizedValue(value=-0.9987),),
            (True, False))),
    *(iec101.ScaledCommand(value=v, select=s)
        for v, s in itertools.product(
            (iec101.ScaledValue(value=-2**15),),
            (True, False))),
    *(iec101.FloatingCommand(value=v, select=s)
        for v, s in itertools.product(
            (iec101.FloatingValue(value=-12345.678),),
            (True, False))),
    iec101.BitstringCommand(value=iec101.BitstringValue(value=b'\xff' * 4)),
        ])
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io, io_size, orig, cause, cause_size, "
    "is_neg_conf",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CommandReqCause.ACTIVATION,
         iec101.CommandReqCause.DEACTIVATION,
         iec101.CommandResCause.ACTIVATION_CONFIRMATION),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO),
        (True, False, True)))
async def test_send_receive_cmd(is_test, asdu, asdu_size, io, io_size,
                                orig, cause, cause_size, is_neg_conf, command):
    msg = iec101.CommandMsg(
            is_test=is_test,
            originator_address=orig,
            asdu_address=asdu,
            io_address=io,
            command=command,
            is_negative_confirm=is_neg_conf,
            cause=cause)

    if isinstance(command.value.value, float):
        await assert_send_receive([msg], cause_size, asdu_size, io_size,
                                  assert_msg_cmd_float)
    else:
        await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("param_change", (True,
                                          False))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io_size, orig, cause, cause_size",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.InitializationResCause.LOCAL_POWER,
         iec101.InitializationResCause.LOCAL_RESET,
         iec101.InitializationResCause.REMOTE_RESET),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_init(is_test, asdu, asdu_size, io_size,
                                 orig, cause, cause_size, param_change):
    msg = iec101.InitializationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        param_change=param_change,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("req", (0,
                                 255))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io_size, orig, is_negative_confirm, "
    "cause, cause_size",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (False, True, False),
        (iec101.CommandReqCause.ACTIVATION,
         iec101.CommandReqCause.DEACTIVATION,
         iec101.CommandResCause.ACTIVATION_TERMINATION),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_interrogate(is_test, asdu, asdu_size, io_size,
                                        orig, is_negative_confirm,
                                        cause, cause_size, req):
    msg = iec101.InterrogationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        request=req,
        is_negative_confirm=is_negative_confirm,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("req", (0, 63))
@pytest.mark.parametrize("freeze", iec101.FreezeCode)
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io_size, orig, is_negative_confirm, "
    "cause, cause_size",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (False, True, False),
        (iec101.CommandReqCause.ACTIVATION,
         iec101.CommandReqCause.DEACTIVATION,
         iec101.CommandResCause.ACTIVATION_TERMINATION),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_cnt_interrogate(is_test, asdu, asdu_size, io_size,
                                            orig, is_negative_confirm, cause,
                                            cause_size, req, freeze):
    msg = iec101.CounterInterrogationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        request=req,
        freeze=freeze,
        is_negative_confirm=is_negative_confirm,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("cause", (*iec101.ReadReqCause,
                                   *iec101.ReadResCause))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io, io_size, orig, cause_size",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_read(is_test, asdu, asdu_size, io, io_size,
                                 orig, cause_size, cause):
    msg = iec101.ReadMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        io_address=io,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("cause", (*iec101.ActivationReqCause,
                                   *iec101.ActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io, io_size, orig, cause_size, time",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO),
        gen_times(3)))
async def test_send_receive_clock_sync(is_test, asdu, asdu_size, io, io_size,
                                       orig, cause_size, time, cause):
    msg = iec101.ClockSyncMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        time=time,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("cause", (*iec101.ActivationReqCause,
                                   *iec101.ActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io_size, orig, cause_size",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_test(is_test, asdu, asdu_size, io_size, orig,
                                 cause_size, cause):
    msg = iec101.TestMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("cause", (*iec101.ActivationReqCause,
                                   *iec101.ActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io_size, orig, cause_size, qualifier",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO),
        (0, 123, 255)))
async def test_send_receive_reset(is_test, asdu, asdu_size, io_size, orig,
                                  cause_size, qualifier, cause):
    msg = iec101.ResetMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        qualifier=qualifier,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("cause", (
    *iec101.ParameterReqCause,
    iec101.ParameterResCause.ACTIVATION_CONFIRMATION,
    iec101.ParameterResCause.INTERROGATED_STATION,
    iec101.ParameterResCause.UNKNOWN_CAUSE))
@pytest.mark.parametrize("parameter", (
    iec101.NormalizedParameter(value=iec101.NormalizedValue(value=-0.9987),
                               qualifier=255),
    iec101.NormalizedParameter(value=iec101.NormalizedValue(value=0.9987),
                               qualifier=0),
    iec101.ScaledParameter(value=iec101.ScaledValue(value=255),
                           qualifier=0),
    iec101.ScaledParameter(value=iec101.ScaledValue(value=0),
                           qualifier=255),
    iec101.FloatingParameter(value=iec101.FloatingValue(value=-1234.5678),
                             qualifier=0),
    iec101.FloatingParameter(value=iec101.FloatingValue(value=1234.5678),
                             qualifier=255),
    ))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io, io_size, orig, cause_size",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO)))
async def test_send_receive_prameter(is_test, asdu, asdu_size, io, io_size,
                                     orig, cause_size, parameter, cause):
    msg = iec101.ParameterMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        io_address=io,
        parameter=parameter,
        cause=cause)

    if isinstance(parameter.value.value, float):
        await assert_send_receive([msg], cause_size, asdu_size, io_size,
                                  assert_msg_param_float)
    else:
        await assert_send_receive([msg], cause_size, asdu_size, io_size)


@pytest.mark.parametrize("cause", (
    *iec101.ParameterActivationReqCause,
    *iec101.ParameterActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, asdu_size, io, io_size, orig, cause_size, qualifier",
    zip((True, False, True),
        (0, 255, 65535),
        (iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.ONE,
         iec101.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (iec101.IoAddressSize.ONE,
         iec101.IoAddressSize.TWO,
         iec101.IoAddressSize.THREE),
        (0, 123, 255),
        (iec101.CauseSize.ONE,
         iec101.CauseSize.TWO,
         iec101.CauseSize.TWO),
        (0, 123, 255)))
async def test_send_receive_prameter_act(is_test, asdu, asdu_size, io, io_size,
                                         orig, cause_size, qualifier, cause):
    msg = iec101.ParameterActivationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        io_address=io,
        qualifier=qualifier,
        cause=cause)

    await assert_send_receive([msg], cause_size, asdu_size, io_size)


def asdu_other_cause():
    # generates asdu with cause that correspond to OtherCause
    # for the corresponding message

    # DataMsg
    data_causes = {i.name for i in iec101.DataResCause}
    for cause in app.iec101.common.CauseType:
        if cause.name in data_causes:
            continue
        yield app.iec101.common.ASDU(
                type=app.iec101.common.AsduType.M_SP_NA,
                cause=app.iec101.common.Cause(type=cause,
                                              is_negative_confirm=False,
                                              is_test=False,
                                              originator_address=0),
                address=13,
                ios=[app.iec101.common.IO(
                        address=123,
                        elements=[app.iec101.common.IoElement_M_SP_NA(
                            value=iec101.SingleValue.ON,
                            quality=iec101.IndicationQuality(
                                invalid=False,
                                not_topical=False,
                                substituted=False,
                                blocked=False))],
                        time=None)])

    # CommandMsg
    cmd_causes = set(i.name for i in (*iec101.CommandReqCause,
                                      *iec101.CommandResCause))
    for cause in app.iec101.common.CauseType:
        if cause.name in cmd_causes:
            continue
        yield app.iec101.common.ASDU(
                type=app.iec101.common.AsduType.C_SC_NA,
                cause=app.iec101.common.Cause(type=cause,
                                              is_negative_confirm=False,
                                              is_test=False,
                                              originator_address=0),
                address=13,
                ios=[app.iec101.common.IO(
                        address=123,
                        elements=[app.iec101.common.IoElement_C_SC_NA(
                            value=iec101.SingleValue.ON,
                            select=True,
                            qualifier=1)],
                        time=None)])


@pytest.mark.parametrize("asdu", asdu_other_cause())
async def test_other_cause(asdu):
    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=iec101.CauseSize.TWO,
                             asdu_address_size=iec101.AsduAddressSize.TWO,
                             io_address_size=iec101.IoAddressSize.TWO)

    # asdu is encoded with app.iec101.encoder.Encoder to bytes
    asdu_bytes = conn._encoder._encoder.encode_asdu(asdu)

    # bytes are set to queue to be received from connection
    conn_link._data_queue.put_nowait(asdu_bytes)
    msgs = await conn.receive()
    assert len(msgs) == 1
    msg = msgs[0]

    assert isinstance(msg.cause, int)
    assert msg.cause == asdu.cause.type.value


async def test_sequence_of_ioes():
    conn_link = MockLinkConnection()
    conn = iec101.Connection(conn=conn_link,
                             cause_size=iec101.CauseSize.TWO,
                             asdu_address_size=iec101.AsduAddressSize.TWO,
                             io_address_size=iec101.IoAddressSize.TWO)

    ioes_number = 3

    # asdu is encoded with app.iec104.encoder.Encoder to bytes
    quality = app.iec104.common.MeasurementQuality(invalid=False,
                                                   not_topical=False,
                                                   substituted=False,
                                                   blocked=False,
                                                   overflow=False)
    io_address = 123
    asdu = app.iec104.common.ASDU(
                type=app.iec104.common.AsduType.M_ME_NB,
                cause=app.iec104.common.Cause(
                    type=app.iec104.common.CauseType.SPONTANEOUS,
                    is_negative_confirm=False,
                    is_test=False,
                    originator_address=0),
                address=13,
                ios=[app.iec104.common.IO(
                        address=io_address,
                        elements=[
                            app.iec104.common.IoElement_M_ME_NB(
                                value=iec101.ScaledValue(value=v),
                                quality=quality)
                            for v in range(ioes_number)],
                        time=None)])
    asdu_bytes = conn._encoder._encoder.encode_asdu(asdu)

    # bytes are set to queue to be received from connection
    conn_link._data_queue.put_nowait(asdu_bytes)
    msgs = await conn.receive()
    assert len(msgs) == ioes_number

    for i, msg in enumerate(msgs):
        assert msg.data.value.value == i
        assert msg.io_address == io_address + i
