import math

import pytest

from hat.drivers.iec60870.app.iec104 import common, encoder


def asdu_type_ioe():
    for asdu_type in [common.AsduType.M_SP_NA,
                      common.AsduType.M_SP_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in single_values:
            yield asdu_type, io_element(value=value,
                                        quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_DP_NA,
                      common.AsduType.M_DP_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in [common.DoubleValue.ON,
                      common.DoubleValue.OFF,
                      common.DoubleValue.INTERMEDIATE,
                      common.DoubleValue.FAULT]:
            yield asdu_type, io_element(value=value,
                                        quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_ST_NA,
                      common.AsduType.M_ST_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in [-64, -13, 0, 17, 63]:
            for transient in [True, False]:
                yield asdu_type, io_element(
                                    value=common.StepPositionValue(
                                        value=value,
                                        transient=transient),
                                    quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_BO_NA,
                      common.AsduType.M_BO_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in bitstring_values:
            yield asdu_type, io_element(value=common.BitstringValue(
                                            value=value),
                                        quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_ME_NA,
                      common.AsduType.M_ME_ND,
                      common.AsduType.M_ME_TD]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in normalized_values:
            if asdu_type == common.AsduType.M_ME_ND:
                yield asdu_type, io_element(value=common.NormalizedValue(
                                                value=value))
            else:
                yield asdu_type, io_element(
                                    value=common.NormalizedValue(
                                        value=value),
                                    quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_ME_NB,
                      common.AsduType.M_ME_TE]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in scaled_values:
            yield asdu_type, io_element(value=common.ScaledValue(
                                            value=value),
                                        quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_ME_NC,
                      common.AsduType.M_ME_TF]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in floating_values:
            yield asdu_type, io_element(value=common.FloatingValue(
                                            value=value),
                                        quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_IT_NA,
                      common.AsduType.M_IT_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in [-2**31, -123, 0, 456, 2**31-1]:
            yield asdu_type, io_element(value=common.BinaryCounterValue(
                                            value=value),
                                        quality=next(quality_gen))

    for asdu_type in [common.AsduType.M_EP_TD]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for value in [common.ProtectionValue.OFF,
                      common.ProtectionValue.ON]:
            yield asdu_type, io_element(value=value,
                                        quality=next(quality_gen),
                                        elapsed_time=123)

    for asdu_type in [common.AsduType.M_EP_TE]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for bool_values in [[True] * 6, [False] * 6]:
            value = common.ProtectionStartValue(*bool_values)
            yield asdu_type, io_element(value=value,
                                        quality=next(quality_gen),
                                        duration_time=123)

    for asdu_type in [common.AsduType.M_EP_TF]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        quality_gen = get_quality_gen(asdu_type)
        for bool_values in [[True] * 4, [False] * 4]:
            value = common.ProtectionCommandValue(*bool_values)
            yield asdu_type, io_element(value=value,
                                        quality=next(quality_gen),
                                        operating_time=123)

    asdu_type = common.AsduType.M_PS_NA
    quality_gen = get_quality_gen(asdu_type)
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for v, change in [([True] * 16, [True] * 16),
                      ([False] * 16, [False] * 16),
                      ([False, True] * 8, [True, False] * 8)]:
        value = common.StatusValue(
            value=v,
            change=change)
        yield asdu_type, io_element(value=value,
                                    quality=next(quality_gen))

    qualifier_gen = get_int_gen(31)
    for asdu_type in [common.AsduType.C_SC_NA,
                      common.AsduType.C_SC_TA,
                      common.AsduType.C_DC_NA,
                      common.AsduType.C_DC_TA,
                      common.AsduType.C_RC_NA,
                      common.AsduType.C_RC_TA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        if 'SC' in asdu_type.name:
            values = single_values
        elif 'DC' in asdu_type.name:
            values = double_values
        elif 'RC' in asdu_type.name:
            values = [common.RegulatingValue.LOWER,
                      common.RegulatingValue.HIGHER]
        for value in values:
            for select in [True, False]:
                yield asdu_type, io_element(value=value,
                                            select=select,
                                            qualifier=next(qualifier_gen))

    for asdu_type in [common.AsduType.C_SE_NA,
                      common.AsduType.C_SE_TA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in normalized_values:
            for select in [True, False]:
                yield asdu_type, io_element(
                    value=common.NormalizedValue(value=value),
                    select=select)

    for asdu_type in [common.AsduType.C_SE_NB,
                      common.AsduType.C_SE_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in scaled_values:
            for select in [True, False]:
                yield asdu_type, io_element(
                    value=common.ScaledValue(value=value),
                    select=select)

    for asdu_type in [common.AsduType.C_SE_NC,
                      common.AsduType.C_SE_TC]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in floating_values:
            for select in [True, False]:
                yield asdu_type, io_element(
                    value=common.FloatingValue(value=value),
                    select=select)

    if asdu_type in [common.AsduType.C_BO_NA,
                     common.AsduType.C_BO_TA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in bitstring_values:
            yield asdu_type, io_element(
                value=common.BitstringValue(value=value))

    if asdu_type in [common.AsduType.C_TS_TA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for counter in [0, 65535, 1234]:
            yield asdu_type, io_element(counter=counter)

    for asdu_type in [common.AsduType.M_EI_NA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for param_change, cause in [(True, 0), (False, 0), (True, 127)]:
            yield asdu_type, io_element(
                param_change=param_change,
                cause=cause)

    asdu_type = common.AsduType.C_IC_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for qualifier in [0, 255, 123]:
        yield asdu_type, io_element(qualifier=qualifier)

    asdu_type = common.AsduType.C_CI_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for request in [0, 63, 13]:
        for freeze in [common.FreezeCode.READ,
                       common.FreezeCode.FREEZE,
                       common.FreezeCode.FREEZE_AND_RESET,
                       common.FreezeCode.RESET]:
            yield asdu_type, io_element(request=request,
                                        freeze=freeze)

    asdu_type = common.AsduType.C_CS_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    yield asdu_type, io_element(time=next(time_seven_gen))

    asdu_type = common.AsduType.C_RP_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for qualifier in [0, 255, 123]:
        yield asdu_type, io_element(qualifier=qualifier)

    qualifier_gen = get_int_gen(255)

    asdu_type = common.AsduType.P_ME_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for value in normalized_values:
        yield asdu_type, io_element(
            value=common.NormalizedValue(value=value),
            qualifier=next(qualifier_gen))

    asdu_type = common.AsduType.P_ME_NB
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for value in scaled_values:
        yield asdu_type, io_element(value=common.ScaledValue(value=value),
                                    qualifier=next(qualifier_gen))

    asdu_type = common.AsduType.P_ME_NC
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for value in floating_values:
        yield asdu_type, io_element(value=common.FloatingValue(value=value),
                                    qualifier=next(qualifier_gen))

    asdu_type = common.AsduType.P_AC_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(3):
        yield asdu_type, io_element(qualifier=next(qualifier_gen))

    asdu_type = common.AsduType.F_FR_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name, file_length, ready) in zip(
            [0, 65535, 1234],
            [0, 16777215, 123456],
            [True, False, True]):
        yield asdu_type, io_element(file_name=file_name,
                                    file_length=file_length,
                                    ready=ready)

    asdu_type = common.AsduType.F_SR_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name, section_name, section_length, ready) in zip(
            [0, 65535, 1234],
            [0, 255, 123],
            [0, 16777215, 4567],
            [True, False, True]):
        yield asdu_type, io_element(file_name=file_name,
                                    section_name=section_name,
                                    section_length=section_length,
                                    ready=ready)

    asdu_type = common.AsduType.F_SC_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name, section_name, qualifier) in zip(
            [0, 65535, 4567],
            [0, 255, 123],
            [0, 255, 123]):
        yield asdu_type, io_element(file_name=file_name,
                                    section_name=section_name,
                                    qualifier=qualifier)

    asdu_type = common.AsduType.F_LS_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name, section_name, last_qualifier, checksum) in zip(
            [0, 65535, 1234],
            [0, 255, 123],
            [0, 255, 123],
            [0, 255, 123]):
        yield asdu_type, io_element(file_name=file_name,
                                    section_name=section_name,
                                    last_qualifier=last_qualifier,
                                    checksum=checksum)

    asdu_type = common.AsduType.F_AF_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name, section_name, qualifier) in zip(
            [0, 65535, 456],
            [0, 255, 123],
            [0, 255, 123]):
        yield asdu_type, io_element(file_name=file_name,
                                    section_name=section_name,
                                    qualifier=qualifier)

    asdu_type = common.AsduType.F_SG_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name, section_name, segment) in zip(
            [0, 65535, 456],
            [0, 255, 123],
            [b'\xab\x12', b'\x00', b'\xff\xff\xcc']):
        yield asdu_type, io_element(file_name=file_name,
                                    section_name=section_name,
                                    segment=segment)

    asdu_type = common.AsduType.F_DR_TA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for (file_name,
         file_length,
         more_follows,
         is_directory,
         transfer_active,
         creation_time) in zip(
            [0, 65535],
            [0, 16777215],
            [False, True],
            [True, False],
            [False, True],
            [next(time_seven_gen), next(time_seven_gen)]):
        yield asdu_type, io_element(file_name=file_name,
                                    file_length=file_length,
                                    more_follows=more_follows,
                                    is_directory=is_directory,
                                    transfer_active=transfer_active,
                                    creation_time=creation_time)


def remove_ioe_value(asdu):
    ios_new = []
    for io in asdu.ios:
        ioes_new = []
        for ioe in io.elements:
            ioe_value_new = ioe.value._replace(value=None)
            ioes_new.append(ioe._replace(value=ioe_value_new))
        ios_new.append(io._replace(elements=ioes_new))
    return asdu._replace(ios=ios_new)


def get_quality_gen(asdu_type):
    samples = dict(
        invalid=[True, False, True],
        not_topical=[True, False, False],
        substituted=[True, False, True],
        blocked=[True, False, False],
        adjusted=[True, False, True],
        overflow=[True, False, False],
        time_invalid=[True, False, True],
        sequence=[0, 31, 13])
    dicts = [dict(zip(samples.keys(), values))
             for values in zip(*samples.values())]
    while True:
        for quality_dict in dicts:
            if asdu_type in [common.AsduType.M_SP_NA,
                             common.AsduType.M_SP_TB,
                             common.AsduType.M_DP_NA,
                             common.AsduType.M_DP_TB]:
                yield common.IndicationQuality(
                    **{k: v for k, v in quality_dict.items()
                       if hasattr(common.IndicationQuality, k)})
            elif asdu_type in [common.AsduType.M_IT_NA,
                               common.AsduType.M_IT_TB]:
                yield common.CounterQuality(
                    **{k: v for k, v in quality_dict.items()
                       if hasattr(common.CounterQuality, k)})
            elif asdu_type in [common.AsduType.M_EP_TD,
                               common.AsduType.M_EP_TE,
                               common.AsduType.M_EP_TF]:
                yield common.ProtectionQuality(
                    **{k: v for k, v in quality_dict.items()
                       if hasattr(common.ProtectionQuality, k)})
            else:
                yield common.MeasurementQuality(
                    **{k: v for k, v in quality_dict.items()
                       if hasattr(common.MeasurementQuality, k)})


single_values = [common.SingleValue.OFF,
                 common.SingleValue.ON]

double_values = [common.DoubleValue.FAULT,
                 common.DoubleValue.OFF,
                 common.DoubleValue.ON,
                 common.DoubleValue.INTERMEDIATE]

bitstring_values = [b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00']


normalized_values = [-1.0, 0.9999, -0.123, 0.456, 0]


scaled_values = [-2**15, -123, 0, 456, 2**15-1]


floating_values = [-16777216.1234, -12345.678, 0, 12345.678, 16777216.1234]


def get_int_gen(up_lim):
    while True:
        yield from (0, up_lim, up_lim // 2)


asdu_address_gen = get_int_gen(65535)
io_address_gen = get_int_gen(16777215)


def get_cause_gen():
    while True:
        for cause_type in common.CauseType:
            for (is_negative_confirm, is_test, originator_address) in [
                    (False, False, 0),
                    (True, True, 255),
                    (True, False, 123),
                    (False, True, 13)]:
                yield common.Cause(
                    type=cause_type,
                    is_negative_confirm=is_negative_confirm,
                    is_test=is_test,
                    originator_address=originator_address)


cause_gen = get_cause_gen()


def get_time_gen(size=common.TimeSize.SEVEN):
    samples = dict(
        milliseconds=(0, 59999, 1234),
        invalid=[True, False, True],
        minutes=(0, 59, 30),
        summer_time=[True, False, True],
        hours=(0, 23, 12),
        day_of_week=(1, 7, 3),
        day_of_month=(1, 31, 13),
        months=(1, 12, 6),
        years=(0, 99, 50))
    while True:
        for values in zip(*samples.values()):
            time_dict = dict(zip(samples.keys(), values))
            if size == common.TimeSize.THREE:
                time_dict = dict(
                    time_dict,
                    summer_time=None,
                    hours=None,
                    day_of_week=None,
                    day_of_month=None,
                    months=None,
                    years=None)
            yield common.Time(**time_dict,
                              size=size)


time_seven_gen = get_time_gen(size=common.TimeSize.SEVEN)
time_three_gen = get_time_gen(size=common.TimeSize.THREE)


def gen_time_for_asdu(asdu_type):
    global time_seven_gen
    global time_seven_gen
    if asdu_type.name[-2:] in ['NA', 'NB', 'NC', 'ND']:
        return
    if asdu_type == common.AsduType.F_DR_TA:
        return
    if asdu_type in [common.AsduType.C_SC_TA,
                     common.AsduType.C_DC_TA,
                     common.AsduType.C_RC_TA,
                     common.AsduType.C_SE_TA,
                     common.AsduType.C_SE_TB,
                     common.AsduType.C_SE_TC,
                     common.AsduType.C_BO_TA,
                     common.AsduType.C_TS_TA]:
        return next(time_seven_gen)
    if asdu_type.name.endswith('TA') or asdu_type.name in [
            'M_EP_TB', 'M_EP_TC', 'M_ME_TB', 'M_ME_TC']:
        return next(time_three_gen)
    return next(time_seven_gen)


@pytest.mark.parametrize("asdu_type, io_element", asdu_type_ioe())
def test_encode_decode(asdu_type, io_element):
    _encoder = encoder.Encoder()

    ioes = [io_element]
    ios = [common.IO(
                address=next(io_address_gen),
                elements=ioes,
                time=gen_time_for_asdu(asdu_type))]
    asdu = common.ASDU(
        type=asdu_type,
        cause=next(cause_gen),
        address=next(asdu_address_gen),
        ios=ios)

    asdu_encoded = _encoder.encode_asdu(asdu)
    asdu_decoded = _encoder.decode_asdu(asdu_encoded)

    # asserting float values with isclose
    if (hasattr(io_element, 'value') and
            (isinstance(io_element.value, common.NormalizedValue) or
             isinstance(io_element.value, common.FloatingValue))):
        for io, io_decoded in zip(asdu.ios, asdu_decoded.ios):
            for ioe, ioe_decoded in zip(io.elements, io_decoded.elements):
                assert math.isclose(ioe.value.value,
                                    ioe_decoded.value.value,
                                    rel_tol=1e-3)
        assert remove_ioe_value(asdu_decoded) == remove_ioe_value(asdu)
    else:
        assert asdu == asdu_decoded
