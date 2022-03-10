import itertools
import math

import pytest

from hat.drivers.iec60870.app.iec104 import encoder, common


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


def assert_encode_decode(asdu_type, value, quality, cause, asdu,  io, time,
                         ioe_kwargs={}, assert_asdu=assert_asdu_default):
    _encoder = encoder.Encoder()

    io_element_class = getattr(common, f"IoElement_{asdu_type.name}")
    ioe_dict = {**ioe_kwargs}
    if asdu_type.name[:-1].endswith('_N'):
        time = None
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
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_SP_NA,
                                       common.AsduType.M_SP_TB])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.IndicationQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_sp(asdu_type, value, quality, cause, asdu, io, time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu, io, time)


@pytest.mark.parametrize("value", common.DoubleValue)
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_DP_NA,
                                       common.AsduType.M_DP_TB])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.IndicationQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_dp(asdu_type, value, quality, cause, asdu, io, time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time)


@pytest.mark.parametrize("value", [-64, -13, 0, 17, 63])
@pytest.mark.parametrize("transient", [True, False])
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_ST_NA,
                                       common.AsduType.M_ST_TB])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_st(asdu_type, value, quality, cause, asdu,
              io, time, transient):
    value = common.StepPositionValue(value=value,
                                     transient=transient)
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time)


@pytest.mark.parametrize("value", [
    b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00'])
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_BO_NA,
                                       common.AsduType.M_BO_TB])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_bo(asdu_type, value, quality, cause, asdu, io, time):
    value = common.BitstringValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time)


@pytest.mark.parametrize("value", (-1.0, 0.9999, -0.123, 0.456, 0))
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_ME_NA,
                                       common.AsduType.M_ME_ND,
                                       common.AsduType.M_ME_TD])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_me_normalized(asdu_type, value, quality, cause, asdu,
                         io, time):
    if asdu_type == common.AsduType.M_ME_ND:
        quality = None
    value = common.BitstringValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time,
                         assert_asdu=assert_asdu_float)


@pytest.mark.parametrize("value", (-2**15, -123, 0, 456, 2**15-1))
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_ME_NB,
                                       common.AsduType.M_ME_TE])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_me_scaled(asdu_type, value, quality, cause, asdu,
                     io, time):
    value = common.ScaledValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time)


@pytest.mark.parametrize("value", (-16777216.1234,
                                   -12345.678,
                                   0,
                                   12345.678,
                                   16777216.1234))
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_ME_NC,
                                       common.AsduType.M_ME_TF])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_me_floating(asdu_type, value, quality, cause, asdu, io,
                       time):
    value = common.FloatingValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time,
                         assert_asdu=assert_asdu_float)


@pytest.mark.parametrize("value", [-2**31, -123, 0, 456, 2**31-1])
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_IT_NA,
                                       common.AsduType.M_IT_TB])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.CounterQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_m_it(asdu_type, value, quality, cause, asdu,
              io, time):
    value = common.BinaryCounterValue(value=value)
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time)


@pytest.mark.parametrize("value", common.ProtectionValue)
@pytest.mark.parametrize("elapsed_time", [0, 123, 65535])
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_EP_TD])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.ProtectionQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_protect_value(asdu_type, value, quality, cause, asdu,
                       io, time, elapsed_time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time,
                         ioe_kwargs={'elapsed_time': elapsed_time})


@pytest.mark.parametrize("value", [
    common.ProtectionStartValue(*([True] * 6)),
    common.ProtectionStartValue(*([False] * 6)),
    common.ProtectionStartValue(*([True, False] * 3))])
@pytest.mark.parametrize("duration_time", [0, 123, 65535])
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_EP_TE])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.ProtectionQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_protect_start(asdu_type, value, quality, cause, asdu,
                       io, time,
                       duration_time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time,
                         ioe_kwargs={'duration_time': duration_time})


@pytest.mark.parametrize("value", [
    common.ProtectionCommandValue(*([True] * 4)),
    common.ProtectionCommandValue(*([False] * 4)),
    common.ProtectionCommandValue(*([True, False] * 2))])
@pytest.mark.parametrize("operating_time", [0, 123, 65535])
@pytest.mark.parametrize("asdu_type", [common.AsduType.M_EP_TF])
@pytest.mark.parametrize(
    "quality, cause, asdu, io, time",
    zip(gen_qualities(3, common.ProtectionQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_protect_command(asdu_type, value, quality, cause, asdu,
                         io, time,
                         operating_time):
    assert_encode_decode(asdu_type, value, quality, cause, asdu,
                         io, time,
                         ioe_kwargs={'operating_time': operating_time})


@pytest.mark.parametrize("value", [[True] * 16,
                                   [False] * 16,
                                   [False, True] * 8])
@pytest.mark.parametrize("change", [[True] * 16,
                                    [False] * 16,
                                    [False, True] * 8])
@pytest.mark.parametrize(
    "quality, cause, asdu, io",
    zip(gen_qualities(3, common.MeasurementQuality),
        gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_status_value(value, quality, cause, asdu, io, change):
    value = common.StatusValue(
        value=value,
        change=change)
    assert_encode_decode(common.AsduType.M_PS_NA, value, quality, cause, asdu,
                         io, None)


@pytest.mark.parametrize("asdu_type, value", [
    *itertools.product((common.AsduType.C_SC_NA,), common.SingleValue),
    *itertools.product((common.AsduType.C_DC_NA,), common.DoubleValue),
    *itertools.product((common.AsduType.C_RC_NA,), common.RegulatingValue),
    ])
@pytest.mark.parametrize("select, qualifier", [(True, 0),
                                               (False, 31)])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_cmd_ind(asdu_type, value, cause, asdu, io,
                 select, qualifier):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'select': select,
                                     'qualifier': qualifier})


@pytest.mark.parametrize("asdu_type, value", [
    *itertools.product((common.AsduType.C_SC_TA,), common.SingleValue),
    *itertools.product((common.AsduType.C_DC_TA,), common.DoubleValue),
    *itertools.product((common.AsduType.C_RC_TA,), common.RegulatingValue),
    ])
@pytest.mark.parametrize("select, qualifier", [(True, 0),
                                               (False, 31)])
@pytest.mark.parametrize(
    "cause, asdu, io, time",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_cmd_ind_with_time(asdu_type, value, cause, asdu, io,
                           select, qualifier, time):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         io, time,
                         ioe_kwargs={'select': select,
                                     'qualifier': qualifier})


@pytest.mark.parametrize("asdu_type, value, time", [
    *((common.AsduType.C_SE_NA, common.NormalizedValue(value=v), None)
      for v in (-1.0, 0.9999, -0.123, 0.456, 0)),

    *((common.AsduType.C_SE_TA, common.NormalizedValue(value=v), t)
      for v, t in zip((-1.0, 0.9999, -0.123, 0.456, 0), gen_times(5))),

    *((common.AsduType.C_SE_NC, common.NormalizedValue(value=v), None)
      for v in (-16777216.1234, 0, 16777216.1234)),

    *((common.AsduType.C_SE_TC, common.NormalizedValue(value=v), t)
      for v, t in zip((-16777216.1234, 0, 16777216.1234), gen_times(3))),
    ])
@pytest.mark.parametrize("select", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_cmd_float(asdu_type, value, cause, asdu, io, select, time):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         io, time,
                         ioe_kwargs={'select': select},
                         assert_asdu=assert_asdu_float)


@pytest.mark.parametrize("asdu_type, value, time", [
    *((common.AsduType.C_SE_NB, common.NormalizedValue(value=v), None)
      for v in (-2**15, -123, 0, 456, 2**15-1)),

    *((common.AsduType.C_SE_TB, common.NormalizedValue(value=v), t)
      for v, t in zip((-2**15, -123, 0, 456, 2**15-1), gen_times(5))),
    ])
@pytest.mark.parametrize("select", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_cmd_scale(asdu_type, value, time, cause, asdu, io, select):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         io, time,
                         ioe_kwargs={'select': select})


@pytest.mark.parametrize("asdu_type, value, time", [
    *((common.AsduType.C_BO_NA, common.BitstringValue(value=v), None)
      for v in (b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00')),

    *((common.AsduType.C_BO_TA, common.BitstringValue(value=v), t)
      for v, t in zip((b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00'),
                      gen_times(3))),
    ])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_cmd_bitstring(asdu_type, value, time, cause, asdu, io):
    assert_encode_decode(asdu_type, value, None, cause, asdu, io, time)


@pytest.mark.parametrize("counter", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, io, time",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215),
        gen_times(3)))
def test_c_ts_ta(cause, asdu, io, time, counter):
    assert_encode_decode(common.AsduType.C_TS_TA, None, None, cause, asdu,
                         io, time,
                         ioe_kwargs={'counter': counter})


@pytest.mark.parametrize("param_change", [True, False])
@pytest.mark.parametrize("cause_ioe", [0, 127])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_m_ei_na(cause, asdu, io, param_change, cause_ioe):
    assert_encode_decode(common.AsduType.M_EI_NA, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'param_change': param_change,
                                     'cause': cause_ioe})


@pytest.mark.parametrize("asdu_type", [common.AsduType.C_IC_NA,
                                       common.AsduType.C_RP_NA,
                                       common.AsduType.P_AC_NA])
@pytest.mark.parametrize("qualifier", [0, 123, 255])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_c_ic_rp_ac(asdu_type, cause, asdu, io,
                    qualifier):
    assert_encode_decode(asdu_type, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'qualifier': qualifier})


@pytest.mark.parametrize("request_ioe", [0, 63, 13])
@pytest.mark.parametrize("freeze", common.FreezeCode)
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_c_ci_na(cause, asdu, io, request_ioe, freeze):
    assert_encode_decode(common.AsduType.C_CI_NA, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'request': request_ioe,
                                     'freeze': freeze})


@pytest.mark.parametrize("time_ioe", gen_times(3))
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_c_cs_na(cause, asdu, io, time_ioe):
    assert_encode_decode(common.AsduType.C_CS_NA, None, None, cause, asdu,
                         io, None,
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
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_p_me_na_nc(asdu_type, value, cause, asdu, io,
                    qualifier):
    assert_encode_decode(asdu_type, value, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'qualifier': qualifier})


@pytest.mark.parametrize("value", (-2**15, -123, 0, 456, 2**15-1))
@pytest.mark.parametrize("qualifier", [0, 123, 255])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_p_me_nb(value, cause, asdu, io, qualifier):
    value = common.ScaledValue(value=value)
    assert_encode_decode(common.AsduType.P_ME_NB, value, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'qualifier': qualifier})


@pytest.mark.parametrize("file_name", [0, 65535])
@pytest.mark.parametrize("file_length", [0, 16777215])
@pytest.mark.parametrize("ready", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_f_fr_na(cause, asdu, io,
                 file_name, file_length, ready):
    assert_encode_decode(common.AsduType.F_FR_NA, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'file_name': file_name,
                                     'file_length': file_length,
                                     'ready': ready})


@pytest.mark.parametrize("file_name", [0, 65535])
@pytest.mark.parametrize("section_name", [0, 255])
@pytest.mark.parametrize("section_length", [0, 16777215])
@pytest.mark.parametrize("ready", [True, False])
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_f_sr_na(cause, asdu, io,
                 file_name, section_name, section_length, ready):
    assert_encode_decode(common.AsduType.F_SR_NA, None, None, cause, asdu,
                         io, None,
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
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_f_sc_af_na(asdu_type, cause, asdu, io,
                    file_name, section_name, qualifier):
    assert_encode_decode(asdu_type, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'file_name': file_name,
                                     'section_name': section_name,
                                     'qualifier': qualifier})


@pytest.mark.parametrize("file_name", (0, 65535))
@pytest.mark.parametrize("section_name", (0, 255))
@pytest.mark.parametrize("last_qualifier", (0, 255))
@pytest.mark.parametrize("checksum", (0, 255))
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_f_ls_na(cause, asdu, io,
                 file_name, section_name, last_qualifier, checksum):
    assert_encode_decode(common.AsduType.F_LS_NA, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'file_name': file_name,
                                     'section_name': section_name,
                                     'last_qualifier': last_qualifier,
                                     'checksum': checksum})


@pytest.mark.parametrize("file_name", (0, 65535))
@pytest.mark.parametrize("section_name", (0, 255))
@pytest.mark.parametrize("segment", (b'\xab\x12', b''))
@pytest.mark.parametrize(
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_f_sg_na(cause, asdu, io,
                 file_name, section_name, segment):
    assert_encode_decode(common.AsduType.F_SG_NA, None, None, cause, asdu,
                         io, None,
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
    "cause, asdu, io",
    zip(gen_causes(3),
        (0, 255, 65535),
        (255, 65535, 16777215)))
def test_f_dr_ta(cause, asdu, io,
                 file_name, file_length, more_follows, is_directory,
                 transfer_active, creation_time):
    assert_encode_decode(common.AsduType.F_DR_TA, None, None, cause, asdu,
                         io, None,
                         ioe_kwargs={'file_name': file_name,
                                     'file_length': file_length,
                                     'more_follows': more_follows,
                                     'is_directory': is_directory,
                                     'transfer_active': transfer_active,
                                     'creation_time': creation_time})


# TODO: C_RD_NA
