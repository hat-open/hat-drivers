import itertools
import math

import pytest

from hat import aio
from hat.drivers import tcp
from hat.drivers.iec60870 import apci
from hat.drivers.iec60870 import app
from hat.drivers.iec60870 import iec104


class MockApciConnection(apci.Connection):

    def __init__(self):
        self._data_queue = aio.Queue()
        self._drain_queue = aio.Queue()
        self._async_group = aio.Group()

    @property
    def async_group(self):
        return self._async_group

    @property
    def info(self):
        return tcp.ConnectionInfo(
            local_addr=tcp.Address(host='abc', port=123),
            remote_addr=tcp.Address(host='def', port=456))

    def send(self, data):
        self._data_queue.put_nowait(data)

    async def drain(self):
        self._drain_queue.put_nowait(None)

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
            yield iec104.Time(**time_dict,
                              size=iec104.TimeSize.SEVEN)
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
    assert msg1.time == msg2.time
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


async def assert_send_receive(msgs, assert_msg=assert_msg_default):
    conn_apci = MockApciConnection()
    conn = iec104.Connection(conn_apci)

    conn.send(msgs)
    msgs_received = await conn.receive()
    for msg_sent, msg_rec in zip(msgs, msgs_received):
        assert_msg(msg_sent, msg_rec)


async def test_connection():
    conn_apci = MockApciConnection()
    conn = iec104.Connection(conn_apci)

    assert conn.is_open

    conn_apci.close()

    await conn.wait_closed()
    assert conn.is_closed

    conn_apci = MockApciConnection()
    conn = iec104.Connection(conn_apci)

    conn.close()

    await conn.wait_closed()
    assert conn_apci.is_closed


async def test_drain():
    conn_apci = MockApciConnection()
    conn = iec104.Connection(conn_apci)

    assert conn_apci._drain_queue.empty()

    await conn.drain()
    await conn_apci._drain_queue.get()

    assert conn_apci._drain_queue.empty()

    for _ in range(3):
        await conn.drain()
        await conn_apci._drain_queue.get()

    assert conn_apci._drain_queue.empty()

    conn.close()
    await conn.wait_closed()


@pytest.mark.parametrize("data", [
    *(iec104.SingleData(value=v, quality=q)
        for v, q in itertools.product(
            iec104.SingleValue,
            gen_qualities(2, iec104.IndicationQuality))),

    *(iec104.DoubleData(value=v, quality=q)
        for v, q in itertools.product(
            iec104.DoubleValue,
            gen_qualities(2, iec104.IndicationQuality))),

    *(iec104.StepPositionData(
            value=v,
            quality=q)
      for v, q in zip((iec104.StepPositionValue(value=-64, transient=True),
                       iec104.StepPositionValue(value=63, transient=False)),
                      gen_qualities(2, iec104.MeasurementQuality))),

    *(iec104.BitstringData(
            value=v,
            quality=q)
      for v, q in zip((iec104.BitstringValue(value=b'\xff' * 4),
                       iec104.BitstringValue(value=b'\x00' * 4)),
                      gen_qualities(2, iec104.MeasurementQuality))),

    *(iec104.NormalizedData(
            value=v,
            quality=q)
      for v, q in zip((iec104.NormalizedValue(value=-0.99876),
                       iec104.NormalizedValue(value=0.99876)),
                      gen_qualities(2, iec104.MeasurementQuality))),

    *(iec104.FloatingData(
            value=v,
            quality=q)
      for v, q in zip((iec104.FloatingValue(value=-12345.678),
                       iec104.FloatingValue(value=12345.678)),
                      gen_qualities(2, iec104.MeasurementQuality))),

    *(iec104.ScaledData(
            value=v,
            quality=q)
      for v, q in zip((iec104.ScaledValue(value=-2**15),
                       iec104.ScaledValue(value=2**14)),
                      gen_qualities(2, iec104.MeasurementQuality))),

    *(iec104.BinaryCounterData(
            value=v,
            quality=q)
      for v, q in zip((iec104.BinaryCounterValue(value=-2**31),
                       iec104.BinaryCounterValue(value=2**30)),
                      gen_qualities(2, iec104.CounterQuality))),

    *(iec104.StatusData(
            value=v,
            quality=q)
      for v, q in zip((iec104.StatusValue(value=[True] * 16,
                                          change=[True] * 16),
                       iec104.StatusValue(value=[False] * 16,
                                          change=[False] * 16)),
                      gen_qualities(2, iec104.MeasurementQuality))),
        ])
@pytest.mark.parametrize(
    "is_test, time, asdu, io, orig, cause",
    zip((True, False, True, False),
        (*gen_times(3), None),
        (0, 255, 65535, 123),
        (255, 65535, 16777215, 123),
        (1, 123, 255, 13),
        (iec104.DataResCause.SPONTANEOUS,
         iec104.DataResCause.INTERROGATED_STATION,
         iec104.DataResCause.REMOTE_COMMAND,
         iec104.DataResCause.LOCAL_COMMAND)))
async def test_send_receive_data(is_test, time, asdu, io, orig, cause, data):
    if isinstance(data, iec104.StatusData):
        time = None
    msg = iec104.DataMsg(
            is_test=is_test,
            originator_address=orig,
            asdu_address=asdu,
            io_address=io,
            data=data,
            time=time,
            cause=cause)
    if isinstance(data.value.value, float):
        await assert_send_receive([msg], assert_msg_data_float)
    else:
        await assert_send_receive([msg])


@pytest.mark.parametrize("data", [
    *(iec104.ProtectionData(value=iec104.ProtectionValue.ON,
                            quality=q,
                            elapsed_time=0)
      for q in gen_qualities(2, iec104.ProtectionQuality)),

    *(iec104.ProtectionData(value=iec104.ProtectionValue.OFF,
                            quality=q,
                            elapsed_time=65535)
      for q in gen_qualities(2, iec104.ProtectionQuality)),

    *(iec104.ProtectionStartData(
        value=v,
        quality=q,
        duration_time=dur_t)
      for v, q, dur_t in zip(
        (iec104.ProtectionStartValue(general=False,
                                     l1=False,
                                     l2=False,
                                     l3=False,
                                     ie=False,
                                     reverse=False),
         iec104.ProtectionStartValue(general=True,
                                     l1=True,
                                     l2=True,
                                     l3=True,
                                     ie=True,
                                     reverse=True)),
        gen_qualities(2, iec104.ProtectionQuality),
        (65535, 0))),

    *(iec104.ProtectionCommandData(
        value=v,
        quality=q,
        operating_time=oper_t)
      for v, q, oper_t in zip(
        (iec104.ProtectionCommandValue(general=True,
                                       l1=True,
                                       l2=True,
                                       l3=True),
         iec104.ProtectionCommandValue(general=False,
                                       l1=False,
                                       l2=False,
                                       l3=False)),
        gen_qualities(2, iec104.ProtectionQuality),
        (65535, 0))),
        ])
@pytest.mark.parametrize(
    "is_test, time, asdu, io, orig, cause",
    zip((True, False, True),
        gen_times(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        (1, 123, 255),
        (iec104.DataResCause.BACKGROUND_SCAN,
         iec104.DataResCause.REMOTE_COMMAND,
         iec104.DataResCause.INTERROGATED_COUNTER03)))
async def test_send_receive_protection_data(is_test, time, asdu, io, orig,
                                            cause, data):
    msg = iec104.DataMsg(
            is_test=is_test,
            originator_address=orig,
            asdu_address=asdu,
            io_address=io,
            data=data,
            time=time,
            cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("command", [
    *(iec104.SingleCommand(value=v, select=s, qualifier=q)
        for v, s, q in itertools.product(iec104.SingleValue,
                                         (True, False),
                                         (0, 31))),
    *(iec104.DoubleCommand(value=v, select=s, qualifier=q)
        for v, s, q in itertools.product(iec104.DoubleValue,
                                         (True, False),
                                         (0, 31))),
    *(iec104.RegulatingCommand(value=v, select=s, qualifier=q)
        for v, s, q in itertools.product(iec104.RegulatingValue,
                                         (True, False),
                                         (0, 31))),
    *(iec104.NormalizedCommand(value=v, select=s)
        for v, s in itertools.product(
            (iec104.NormalizedValue(value=-0.9987),),
            (True, False))),
    *(iec104.ScaledCommand(value=v, select=s)
        for v, s in itertools.product(
            (iec104.ScaledValue(value=-2**15),),
            (True, False))),
    *(iec104.FloatingCommand(value=v, select=s)
        for v, s in itertools.product(
            (iec104.FloatingValue(value=-12345.678),),
            (True, False))),
    iec104.BitstringCommand(value=iec104.BitstringValue(value=b'\xff' * 4)),
        ])
@pytest.mark.parametrize(
    "is_test, asdu, io, orig, is_neg_conf, time, cause",
    zip((True, False, True),
        (0, 255, 65535),
        (255, 65535, 16777215),
        (1, 123, 255),
        (True, False, True),
        (*gen_times(2), None),
        (iec104.CommandReqCause.ACTIVATION,
         iec104.CommandReqCause.DEACTIVATION,
         iec104.CommandResCause.ACTIVATION_CONFIRMATION)))
async def test_send_receive_cmd(is_test, asdu, io, orig,
                                is_neg_conf, time, command, cause):
    msg = iec104.CommandMsg(
            is_test=is_test,
            originator_address=orig,
            asdu_address=asdu,
            io_address=io,
            command=command,
            is_negative_confirm=is_neg_conf,
            time=time,
            cause=cause)

    if isinstance(command.value.value, float):
        await assert_send_receive([msg], assert_msg_cmd_float)
    else:
        await assert_send_receive([msg])


@pytest.mark.parametrize("param_change", (True,
                                          False))
@pytest.mark.parametrize(
    "is_test, asdu, orig, cause",
    zip((True, False, True),
        (0, 255, 65535),
        (1, 123, 255),
        (iec104.InitializationResCause.LOCAL_POWER,
         iec104.InitializationResCause.LOCAL_RESET,
         iec104.InitializationResCause.REMOTE_RESET)))
async def test_send_receive_init(is_test, asdu, orig, cause, param_change):
    msg = iec104.InitializationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        param_change=param_change,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("req", (0,
                                 255))
@pytest.mark.parametrize(
    "is_test, asdu, orig, is_negative_confirm, cause",
    zip((True, False, True),
        (0, 255, 65535),
        (1, 123, 255),
        (False, True, False),
        (iec104.CommandReqCause.ACTIVATION,
         iec104.CommandReqCause.DEACTIVATION,
         iec104.CommandResCause.ACTIVATION_TERMINATION)))
async def test_send_receive_interrogate(is_test, asdu, orig,
                                        is_negative_confirm, cause, req):
    msg = iec104.InterrogationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        request=req,
        is_negative_confirm=is_negative_confirm,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("req", (0, 63))
@pytest.mark.parametrize("freeze", iec104.FreezeCode)
@pytest.mark.parametrize(
    "is_test, asdu, orig, is_negative_confirm, cause",
    zip((True, False, True),
        (0, 255, 65535),
        (1, 123, 255),
        (False, True, False),
        (iec104.CommandReqCause.ACTIVATION,
         iec104.CommandResCause.UNKNOWN_TYPE,
         iec104.CommandResCause.UNKNOWN_ASDU_ADDRESS)))
async def test_send_receive_cnt_interrogate(is_test, asdu, orig,
                                            is_negative_confirm, cause, req,
                                            freeze):
    msg = iec104.CounterInterrogationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        request=req,
        freeze=freeze,
        is_negative_confirm=is_negative_confirm,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("cause", (*iec104.ReadReqCause,
                                   *iec104.ReadResCause))
@pytest.mark.parametrize(
    "is_test, asdu, io, orig",
    zip((True, False, True),
        (0, 255, 65535),
        (255, 65535, 16777215),
        (1, 123, 255)))
async def test_send_receive_read(is_test, asdu, io, orig, cause):
    msg = iec104.ReadMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        io_address=io,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("cause", (*iec104.ClockSyncReqCause,
                                   *iec104.ClockSyncResCause))
@pytest.mark.parametrize(
    "is_test, asdu, orig, time, is_neg_conf",
    zip((True, False, True),
        (0, 255, 65535),
        (1, 123, 255),
        gen_times(3),
        (True, False, True)))
async def test_send_receive_clock_sync(is_test, asdu, orig, time, cause,
                                       is_neg_conf):
    msg = iec104.ClockSyncMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        time=time,
        is_negative_confirm=is_neg_conf,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("cause", (*iec104.ActivationReqCause,
                                   *iec104.ActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, orig, counter, time",
    zip((True, False, True),
        (0, 255, 65535),
        (1, 123, 255),
        (0, 1234, 65535),
        gen_times(3)))
async def test_send_receive_test(is_test, asdu, orig, counter, time, cause):
    msg = iec104.TestMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        counter=counter,
        time=time,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("cause", (*iec104.ActivationReqCause,
                                   *iec104.ActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, orig, qualifier",
    zip((True, False, True),
        (0, 255, 65535),
        (1, 123, 255),
        (0, 123, 255)))
async def test_send_receive_reset(is_test, asdu, orig, qualifier, cause):
    msg = iec104.ResetMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        qualifier=qualifier,
        cause=cause)

    await assert_send_receive([msg])


@pytest.mark.parametrize("cause", (
    *iec104.ParameterReqCause,
    iec104.ParameterResCause.ACTIVATION_CONFIRMATION,
    iec104.ParameterResCause.INTERROGATED_STATION,
    iec104.ParameterResCause.UNKNOWN_CAUSE))
@pytest.mark.parametrize("parameter", (
    iec104.NormalizedParameter(value=iec104.NormalizedValue(value=-0.9987),
                               qualifier=255),
    iec104.NormalizedParameter(value=iec104.NormalizedValue(value=0.9987),
                               qualifier=0),
    iec104.ScaledParameter(value=iec104.ScaledValue(value=255),
                           qualifier=0),
    iec104.ScaledParameter(value=iec104.ScaledValue(value=0),
                           qualifier=255),
    iec104.FloatingParameter(value=iec104.FloatingValue(value=-1234.5678),
                             qualifier=0),
    iec104.FloatingParameter(value=iec104.FloatingValue(value=1234.5678),
                             qualifier=255),
    ))
@pytest.mark.parametrize(
    "is_test, asdu, io, orig",
    zip((True, False, True),
        (0, 255, 65535),
        (255, 65535, 16777215),
        (1, 123, 255)))
async def test_send_receive_prameter(is_test, asdu, io, orig, parameter,
                                     cause):
    msg = iec104.ParameterMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        io_address=io,
        parameter=parameter,
        cause=cause)

    if isinstance(parameter.value.value, float):
        await assert_send_receive([msg], assert_msg_param_float)
    else:
        await assert_send_receive([msg])


@pytest.mark.parametrize("cause", (
    *iec104.ParameterActivationReqCause,
    *iec104.ParameterActivationResCause))
@pytest.mark.parametrize(
    "is_test, asdu, io, orig, qualifier",
    zip((True, False, True),
        (0, 255, 65535),
        (255, 65535, 16777215),
        (1, 123, 255),
        (0, 123, 255)))
async def test_send_receive_prameter_act(is_test, asdu, io, orig, qualifier,
                                         cause):
    msg = iec104.ParameterActivationMsg(
        is_test=is_test,
        originator_address=orig,
        asdu_address=asdu,
        io_address=io,
        qualifier=qualifier,
        cause=cause)

    await assert_send_receive([msg])


def asdu_other_cause():
    # generates asdu with cause that correspond to OtherCause
    # for the corresponding message

    # DataMsg
    data_causes = {i.name for i in iec104.DataResCause}
    for cause in app.iec104.common.CauseType:
        if cause.name in data_causes:
            continue
        yield app.iec104.common.ASDU(
                type=app.iec104.common.AsduType.M_SP_NA,
                cause=app.iec104.common.Cause(type=cause,
                                              is_negative_confirm=False,
                                              is_test=False,
                                              originator_address=0),
                address=13,
                ios=[app.iec104.common.IO(
                        address=123,
                        elements=[app.iec104.common.IoElement_M_SP_NA(
                            value=iec104.SingleValue.ON,
                            quality=iec104.IndicationQuality(
                                invalid=False,
                                not_topical=False,
                                substituted=False,
                                blocked=False))],
                        time=None)])

    # CommandMsg
    cmd_causes = set(i.name for i in (*iec104.CommandReqCause,
                                      *iec104.CommandResCause))
    for cause in app.iec104.common.CauseType:
        if cause.name in cmd_causes:
            continue
        yield app.iec104.common.ASDU(
                type=app.iec104.common.AsduType.C_SC_NA,
                cause=app.iec104.common.Cause(type=cause,
                                              is_negative_confirm=False,
                                              is_test=False,
                                              originator_address=0),
                address=13,
                ios=[app.iec104.common.IO(
                        address=123,
                        elements=[app.iec104.common.IoElement_C_SC_NA(
                            value=iec104.SingleValue.ON,
                            select=True,
                            qualifier=1)],
                        time=None)])


@pytest.mark.parametrize("asdu", asdu_other_cause())
async def test_other_cause(asdu):
    conn_apci = MockApciConnection()
    conn = iec104.Connection(conn=conn_apci)

    # asdu is encoded with app.iec104.encoder.Encoder to bytes
    asdu_bytes = conn._encoder._encoder.encode_asdu(asdu)

    # bytes are set to queue to be received from connection
    conn_apci._data_queue.put_nowait(asdu_bytes)
    msgs = await conn.receive()
    assert len(msgs) == 1
    msg = msgs[0]

    assert isinstance(msg.cause, int)
    assert msg.cause == asdu.cause.type.value


async def test_sequence_of_ioes():
    conn_apci = MockApciConnection()
    conn = iec104.Connection(conn=conn_apci)

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
                                value=iec104.ScaledValue(value=v),
                                quality=quality)
                            for v in range(ioes_number)],
                        time=None)])
    asdu_bytes = conn._encoder._encoder.encode_asdu(asdu)

    # bytes are set to queue to be received from connection
    conn_apci._data_queue.put_nowait(asdu_bytes)
    msgs = await conn.receive()
    assert len(msgs) == ioes_number

    for i, msg in enumerate(msgs):
        assert msg.data.value.value == i
        assert msg.io_address == io_address + i
