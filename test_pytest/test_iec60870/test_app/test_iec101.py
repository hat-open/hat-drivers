import itertools
import math

import pytest

from hat.drivers.iec60870.app.iec101 import encoder, common


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
            yield common.Time(**time_dict,
                              size=common.TimeSize.SEVEN)
            cnt += 1
            if cnt == amount:
                return


def time_seven_to_size(time_seven, size):
    if size is None:
        return
    if size is common.TimeSize.SEVEN:
        return time_seven
    if size is common.TimeSize.THREE:
        return common.Time(**dict(
                time_seven._asdict(),
                size=size,
                summer_time=None,
                hours=None,
                day_of_week=None,
                day_of_month=None,
                months=None,
                years=None))


def gen_causes(amount):
    cnt = 0
    while True:
        for (cause_type, is_negative_confirm, is_test, orig_addr) in zip(
                (common.CauseType.SPONTANEOUS,
                 common.CauseType.INTERROGATED_STATION,
                 common.CauseType.ACTIVATION,
                 common.CauseType.REMOTE_COMMAND,
                 common.CauseType.UNKNOWN_CAUSE),
                (True, False, True, False, True),
                (False, True, False, True, False),
                (0, 255, 123, 13, 1)):
            yield common.Cause(
                type=cause_type,
                is_negative_confirm=is_negative_confirm,
                is_test=is_test,
                originator_address=orig_addr)
            cnt += 1
            if cnt == amount:
                return


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


def assert_asdu_default(msg1, msg2):
    assert msg1 == msg2


def assert_asdu_float(asdu1, asdu2):
    assert asdu1.type == asdu2.type
    assert asdu1.cause == asdu2.cause
    assert asdu1.address == asdu2.address
    for io1, io2 in zip(asdu1.ios, asdu2.ios):
        assert io1.address == io2.address
        assert io1.time == io2.time
        for ioe1, ioe2 in zip(io1.elements, io2.elements):
            assert math.isclose(ioe1.value.value,
                                ioe2.value.value,
                                rel_tol=1e-3)
            for ioe_attr in ['quality',
                             'select',
                             'qualifier']:
                if hasattr(ioe1, ioe_attr):
                    assert getattr(ioe1, ioe_attr) == getattr(ioe2, ioe_attr)


def assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         ioe_kwargs={}, assert_asdu=assert_asdu_default):
    if cause_size == common.CauseSize.ONE:
        cause = cause._replace(originator_address=0)
    time = time_seven_to_size(time, time_size)
    _encoder = encoder.Encoder(
        cause_size=cause_size,
        asdu_address_size=asdu_size,
        io_address_size=io_size)

    io_element_class = getattr(common, f"IoElement_{asdu_type.name}")
    ioe_dict = {**ioe_kwargs}
    if value is not None:
        ioe_dict['value'] = value
    if quality:
        ioe_dict['quality'] = quality
    io_element = io_element_class(**ioe_dict)
    ios = [common.IO(
                address=io,
                elements=[io_element],
                time=time)]
    asdu = common.ASDU(
        type=asdu_type,
        cause=cause,
        address=asdu,
        ios=ios)
    asdu_encoded = _encoder.encode_asdu(asdu)
    asdu_decoded = _encoder.decode_asdu(asdu_encoded)

    assert_asdu(asdu_decoded, asdu)


@pytest.mark.parametrize("value", common.SingleValue)
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_SP_NA, None),
    (common.AsduType.M_SP_TA, common.TimeSize.THREE),
    (common.AsduType.M_SP_TB, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.IndicationQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_sp(asdu_type, value, quality, cause, asdu, asdu_size,
              io, io_size, cause_size, time, time_size):
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size)


@pytest.mark.parametrize("value", common.DoubleValue)
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_DP_NA, None),
    (common.AsduType.M_DP_TA, common.TimeSize.THREE),
    (common.AsduType.M_DP_TB, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.IndicationQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_dp(asdu_type, value, quality, cause, asdu, asdu_size,
              io, io_size, cause_size, time, time_size):
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size)


@pytest.mark.parametrize("value", [-64, -13, 0, 17, 63])
@pytest.mark.parametrize("transient", [True, False])
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_ST_NA, None),
    (common.AsduType.M_ST_TA, common.TimeSize.THREE),
    (common.AsduType.M_ST_TB, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_st(asdu_type, value, quality, cause, asdu, asdu_size,
              io, io_size, cause_size, time, time_size, transient):
    value = common.StepPositionValue(value=value,
                                     transient=transient)
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size)


@pytest.mark.parametrize("value", [
    b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00'])
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_BO_NA, None),
    (common.AsduType.M_BO_TA, common.TimeSize.THREE),
    (common.AsduType.M_BO_TB, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_bo(asdu_type, value, quality, cause, asdu, asdu_size,
              io, io_size, cause_size, time, time_size):
    value = common.BitstringValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size)


@pytest.mark.parametrize("value", (-1.0, 0.9999, -0.123, 0.456, 0))
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_ME_NA, None),
    (common.AsduType.M_ME_TA, common.TimeSize.THREE),
    (common.AsduType.M_ME_ND, None),
    (common.AsduType.M_ME_TD, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_me_normalized(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size):
    if asdu_type == common.AsduType.M_ME_ND:
        quality = None
    value = common.BitstringValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         assert_asdu=assert_asdu_float)


@pytest.mark.parametrize("value", (-2**15, -123, 0, 456, 2**15-1))
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_ME_NB, None),
    (common.AsduType.M_ME_TB, common.TimeSize.THREE),
    (common.AsduType.M_ME_TE, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_me_scaled(asdu_type, value, quality, cause, asdu, asdu_size,
                     io, io_size, cause_size, time, time_size):
    value = common.ScaledValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size)


@pytest.mark.parametrize("value", (-16777216.1234,
                                   -12345.678,
                                   0,
                                   12345.678,
                                   16777216.1234))
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_ME_NC, None),
    (common.AsduType.M_ME_TC, common.TimeSize.THREE),
    (common.AsduType.M_ME_TF, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_me_floating(asdu_type, value, quality, cause, asdu, asdu_size,
                       io, io_size, cause_size, time, time_size):
    value = common.FloatingValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         assert_asdu=assert_asdu_float)


@pytest.mark.parametrize("value", [-2**31, -123, 0, 456, 2**31-1])
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_IT_NA, None),
    (common.AsduType.M_IT_TA, common.TimeSize.THREE),
    (common.AsduType.M_IT_TB, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.CounterQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_m_it(asdu_type, value, quality, cause, asdu, asdu_size,
              io, io_size, cause_size, time, time_size):
    value = common.BinaryCounterValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size)


@pytest.mark.parametrize("value", common.ProtectionValue)
@pytest.mark.parametrize("elapsed_time", [0, 123, 65535])
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_EP_TA, common.TimeSize.THREE),
    (common.AsduType.M_EP_TD, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.ProtectionQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_protect_value(asdu_type, value, quality, cause, asdu, asdu_size,
                       io, io_size, cause_size, time, time_size, elapsed_time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         ioe_kwargs={'elapsed_time': elapsed_time})


@pytest.mark.parametrize("value", [
    common.ProtectionStartValue(*([True] * 6)),
    common.ProtectionStartValue(*([False] * 6)),
    common.ProtectionStartValue(*([True, False] * 3))])
@pytest.mark.parametrize("duration_time", [0, 123, 65535])
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_EP_TB, common.TimeSize.THREE),
    (common.AsduType.M_EP_TE, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.ProtectionQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_protect_start(asdu_type, value, quality, cause, asdu, asdu_size,
                       io, io_size, cause_size, time, time_size,
                       duration_time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         ioe_kwargs={'duration_time': duration_time})


@pytest.mark.parametrize("value", [
    common.ProtectionCommandValue(*([True] * 4)),
    common.ProtectionCommandValue(*([False] * 4)),
    common.ProtectionCommandValue(*([True, False] * 2))])
@pytest.mark.parametrize("operating_time", [0, 123, 65535])
@pytest.mark.parametrize("asdu_type, time_size", [
    (common.AsduType.M_EP_TC, common.TimeSize.THREE),
    (common.AsduType.M_EP_TF, common.TimeSize.SEVEN)])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size, time",
    zip(gen_qualities(3, common.ProtectionQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO),
        gen_times(3)))
def test_protect_command(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         operating_time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu, asdu_size,
                         io, io_size, cause_size, time, time_size,
                         ioe_kwargs={'operating_time': operating_time})


@pytest.mark.parametrize("value", [[True] * 16,
                                   [False] * 16,
                                   [False, True] * 8])
@pytest.mark.parametrize("change", [[True] * 16,
                                    [False] * 16,
                                    [False, True] * 8])
@pytest.mark.parametrize(
    "quality, cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_status_value(value, quality, cause, asdu, asdu_size,
                      io, io_size, cause_size, change):
    value = common.StatusValue(
        value=value,
        change=change)
    assert_encode_decode(common.AsduType.M_PS_NA, value, quality, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None)


@pytest.mark.parametrize("asdu_type, value", [
    *itertools.product((common.AsduType.C_SC_NA,), common.SingleValue),
    *itertools.product((common.AsduType.C_DC_NA,), common.DoubleValue),
    *itertools.product((common.AsduType.C_RC_NA,), common.RegulatingValue),
    ])
@pytest.mark.parametrize("select, qualifier", [(True, 0),
                                               (False, 31)])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_cmd_ind(asdu_type, value, cause, asdu, asdu_size, io, io_size,
                 cause_size, select, qualifier):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'select': select,
                                     'qualifier': qualifier})


@pytest.mark.parametrize("asdu_type, value", [
    *itertools.product((common.AsduType.C_SE_NA,),
                       [common.NormalizedValue(value=i)
                        for i in (-1.0, 0.9999, -0.123, 0.456, 0)]),
    *itertools.product((common.AsduType.C_SE_NC,),
                       [common.FloatingValue(value=i)
                        for i in (-16777216.1234, 0, 16777216.1234)])
    ])
@pytest.mark.parametrize("select", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_cmd_float(asdu_type, value, cause, asdu, asdu_size, io, io_size,
                   cause_size, select):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'select': select},
                         assert_asdu=assert_asdu_float)


@pytest.mark.parametrize("value", (-2**15, -123, 0, 456, 2**15-1))
@pytest.mark.parametrize("select", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_cmd_scale(value, cause, asdu, asdu_size, io, io_size,
                   cause_size, select):
    value = common.ScaledValue(value=value)
    assert_encode_decode(common.AsduType.C_SE_NB, value, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'select': select})


@pytest.mark.parametrize("value", (
    b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00'))
@pytest.mark.parametrize("select", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_cmd_bitstring(value, cause, asdu, asdu_size, io, io_size,
                       cause_size, select):
    value = common.BitstringValue(value=value)
    assert_encode_decode(common.AsduType.C_BO_NA, value, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None)


@pytest.mark.parametrize("param_change", [True, False])
@pytest.mark.parametrize("cause_ioe", [0, 127])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_m_ei_na(cause, asdu, asdu_size, io, io_size,
                 cause_size, param_change, cause_ioe):
    assert_encode_decode(common.AsduType.M_EI_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'param_change': param_change,
                                     'cause': cause_ioe})


@pytest.mark.parametrize("asdu_type", [common.AsduType.C_IC_NA,
                                       common.AsduType.C_RP_NA,
                                       common.AsduType.P_AC_NA])
@pytest.mark.parametrize("qualifier", [0, 123, 255])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_c_ic_rp_ac(asdu_type, cause, asdu, asdu_size, io, io_size, cause_size,
                    qualifier):
    assert_encode_decode(asdu_type, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'qualifier': qualifier})


@pytest.mark.parametrize("request_ioe", [0, 63, 13])
@pytest.mark.parametrize("freeze", common.FreezeCode)
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_c_ci_na(cause, asdu, asdu_size, io, io_size,
                 cause_size, request_ioe, freeze):
    assert_encode_decode(common.AsduType.C_CI_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'request': request_ioe,
                                     'freeze': freeze})


@pytest.mark.parametrize("time_ioe", gen_times(3))
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_c_cs_na(cause, asdu, asdu_size, io, io_size, cause_size, time_ioe):
    assert_encode_decode(common.AsduType.C_CS_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'time': time_ioe})


@pytest.mark.parametrize("time_ioe", [0, 65535, 123])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_c_cd_na(cause, asdu, asdu_size, io, io_size, cause_size, time_ioe):
    assert_encode_decode(common.AsduType.C_CD_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'time': time_ioe})


@pytest.mark.parametrize("asdu_type, value", [
    *itertools.product((common.AsduType.P_ME_NA,),
                       [common.NormalizedValue(value=1)
                        for i in (-1.0, 0.9999, -0.123, 0.456, 0)]),
    *itertools.product((common.AsduType.P_ME_NC,),
                       [common.FloatingValue(value=1)
                        for i in (-16777216.1234, 0, 16777216.1234)]),
    ])
@pytest.mark.parametrize("qualifier", [0, 123, 255])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_p_me_na_nc(asdu_type, value, cause, asdu, asdu_size, io, io_size,
                    cause_size, qualifier):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'qualifier': qualifier})


@pytest.mark.parametrize("value", (-2**15, -123, 0, 456, 2**15-1))
@pytest.mark.parametrize("qualifier", [0, 123, 255])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_p_me_nb(value, cause, asdu, asdu_size, io, io_size,
                 cause_size, qualifier):
    value = common.ScaledValue(value=value)
    assert_encode_decode(common.AsduType.P_ME_NB, value, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'qualifier': qualifier})


@pytest.mark.parametrize("file_name", [0, 65535])
@pytest.mark.parametrize("file_length", [0, 16777215])
@pytest.mark.parametrize("ready", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_f_fr_na(cause, asdu, asdu_size, io, io_size,
                 cause_size, file_name, file_length, ready):
    assert_encode_decode(common.AsduType.F_FR_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'file_name': file_name,
                                     'file_length': file_length,
                                     'ready': ready})


@pytest.mark.parametrize("file_name", [0, 65535])
@pytest.mark.parametrize("section_name", [0, 255])
@pytest.mark.parametrize("section_length", [0, 16777215])
@pytest.mark.parametrize("ready", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_f_sr_na(cause, asdu, asdu_size, io, io_size,
                 cause_size, file_name, section_name, section_length, ready):
    assert_encode_decode(common.AsduType.F_SR_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'file_name': file_name,
                                     'section_name': section_name,
                                     'section_length': section_length,
                                     'ready': ready})


@pytest.mark.parametrize("asdu_type", (common.AsduType.F_SC_NA,
                                       common.AsduType.F_AF_NA))
@pytest.mark.parametrize("file_name", (0, 65535))
@pytest.mark.parametrize("section_name", (0, 255))
@pytest.mark.parametrize("qualifier", (0, 255))
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_f_sc_af_na(asdu_type, cause, asdu, asdu_size, io, io_size,
                    cause_size, file_name, section_name, qualifier):
    assert_encode_decode(asdu_type, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'file_name': file_name,
                                     'section_name': section_name,
                                     'qualifier': qualifier})


@pytest.mark.parametrize("file_name", (0, 65535))
@pytest.mark.parametrize("section_name", (0, 255))
@pytest.mark.parametrize("last_qualifier", (0, 255))
@pytest.mark.parametrize("checksum", (0, 255))
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_f_ls_na(cause, asdu, asdu_size, io, io_size, cause_size,
                 file_name, section_name, last_qualifier, checksum):
    assert_encode_decode(common.AsduType.F_LS_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'file_name': file_name,
                                     'section_name': section_name,
                                     'last_qualifier': last_qualifier,
                                     'checksum': checksum})


@pytest.mark.parametrize("file_name", (0, 65535))
@pytest.mark.parametrize("section_name", (0, 255))
@pytest.mark.parametrize("segment", (b'\xab\x12', b''))
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_f_sg_na(cause, asdu, asdu_size, io, io_size, cause_size,
                 file_name, section_name, segment):
    assert_encode_decode(common.AsduType.F_SG_NA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'file_name': file_name,
                                     'section_name': section_name,
                                     'segment': segment})


@pytest.mark.parametrize("file_name", (0, 65535))
@pytest.mark.parametrize("file_length", (0, 16777215))
@pytest.mark.parametrize("more_follows, is_directory, transfer_active", [
    (True, True, True),
    (False, False, False)])
@pytest.mark.parametrize("creation_time", gen_times(3))
@pytest.mark.parametrize(
    "cause, asdu, asdu_size, io, io_size, cause_size",
    zip(gen_causes(3),
        (0, 255, 65535),
        (common.AsduAddressSize.ONE,
         common.AsduAddressSize.ONE,
         common.AsduAddressSize.TWO),
        (255, 65535, 16777215),
        (common.IoAddressSize.ONE,
         common.IoAddressSize.TWO,
         common.IoAddressSize.THREE),
        (common.CauseSize.ONE,
         common.CauseSize.ONE,
         common.CauseSize.TWO)))
def test_f_dr_ta(cause, asdu, asdu_size, io, io_size, cause_size,
                 file_name, file_length, more_follows, is_directory,
                 transfer_active, creation_time):
    assert_encode_decode(common.AsduType.F_DR_TA, None, None, cause, asdu,
                         asdu_size, io, io_size, cause_size, None, None,
                         ioe_kwargs={'file_name': file_name,
                                     'file_length': file_length,
                                     'more_follows': more_follows,
                                     'is_directory': is_directory,
                                     'transfer_active': transfer_active,
                                     'creation_time': creation_time})


# TODO: C_RD_NA,  C_TS_NA,
