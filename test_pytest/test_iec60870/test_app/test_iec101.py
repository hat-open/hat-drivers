import math
import random

import pytest

from hat.drivers.iec60870.app.iec101 import encoder, common


rndm = random.Random(1)


def asdu_type_ioe():
    for asdu_type in [common.AsduType.M_SP_NA,
                      common.AsduType.M_SP_TA,
                      common.AsduType.M_SP_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in [common.SingleValue.ON, common.SingleValue.OFF]:
            yield asdu_type, io_element(value=value,
                                        quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_DP_NA,
                      common.AsduType.M_DP_TA,
                      common.AsduType.M_DP_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in [common.DoubleValue.ON,
                      common.DoubleValue.OFF,
                      common.DoubleValue.INTERMEDIATE,
                      common.DoubleValue.FAULT]:
            yield asdu_type, io_element(value=value,
                                        quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_ST_NA,
                      common.AsduType.M_ST_TA,
                      common.AsduType.M_ST_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in step_position_values:
            for transient in [True, False]:
                yield asdu_type, io_element(value=common.StepPositionValue(
                                                value=value,
                                                transient=transient),
                                            quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_BO_NA,
                      common.AsduType.M_BO_TA,
                      common.AsduType.M_BO_TB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in bitstring_values:
            yield asdu_type, io_element(value=common.BitstringValue(
                                            value=value),
                                        quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_ME_NA,
                      common.AsduType.M_ME_TA,
                      common.AsduType.M_ME_ND,
                      common.AsduType.M_ME_TD]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in normalized_values:
            if asdu_type == common.AsduType.M_ME_ND:
                yield asdu_type, io_element(value=common.NormalizedValue(
                                                value=value))
            else:
                yield asdu_type, io_element(value=common.NormalizedValue(
                                                value=value),
                                            quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_ME_NB,
                      common.AsduType.M_ME_TB,
                      common.AsduType.M_ME_TE,
                      ]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in scaled_values:
            yield asdu_type, io_element(value=common.ScaledValue(
                                            value=value),
                                        quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_ME_NC,
                      common.AsduType.M_ME_TC,
                      common.AsduType.M_ME_TF,
                      ]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in floating_values:
            yield asdu_type, io_element(value=common.FloatingValue(
                                            value=value),
                                        quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_IT_NA,
                      common.AsduType.M_IT_TA,
                      common.AsduType.M_IT_TB,
                      ]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in binary_counter_values:
            yield asdu_type, io_element(value=common.BinaryCounterValue(
                                            value=value),
                                        quality=get_quality(asdu_type))

    for asdu_type in [common.AsduType.M_EP_TA,
                      common.AsduType.M_EP_TD]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in [common.ProtectionValue.OFF,
                      common.ProtectionValue.ON]:
            yield asdu_type, io_element(value=value,
                                        quality=get_quality(asdu_type),
                                        elapsed_time=123)

    for asdu_type in [common.AsduType.M_EP_TB,
                      common.AsduType.M_EP_TE]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in range(3):
            value = common.ProtectionStartValue(
                general=get_random_bool(),
                l1=get_random_bool(),
                l2=get_random_bool(),
                l3=get_random_bool(),
                ie=get_random_bool(),
                reverse=get_random_bool())
            yield asdu_type, io_element(value=value,
                                        quality=get_quality(asdu_type),
                                        duration_time=123)

    for asdu_type in [common.AsduType.M_EP_TC,
                      common.AsduType.M_EP_TF]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in range(3):
            value = common.ProtectionCommandValue(
                general=get_random_bool(),
                l1=get_random_bool(),
                l2=get_random_bool(),
                l3=get_random_bool())
            yield asdu_type, io_element(value=value,
                                        quality=get_quality(asdu_type),
                                        operating_time=123)

    for asdu_type in [common.AsduType.C_SC_NA,
                      common.AsduType.C_DC_NA,
                      common.AsduType.C_RC_NA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        values = {
            common.AsduType.C_SC_NA: [common.SingleValue.OFF,
                                      common.SingleValue.ON],
            common.AsduType.C_DC_NA: [common.DoubleValue.FAULT,
                                      common.DoubleValue.OFF,
                                      common.DoubleValue.ON,
                                      common.DoubleValue.INTERMEDIATE],
            common.AsduType.C_RC_NA: [common.RegulatingValue.LOWER,
                                      common.RegulatingValue.HIGHER]
                }[asdu_type]
        for value in values:
            for select in [True, False]:
                yield asdu_type, io_element(value=value,
                                            select=select,
                                            qualifier=rndm.randint(0, 31))

    for asdu_type in [common.AsduType.C_SE_NA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in normalized_values:
            for select in [True, False]:
                yield asdu_type, io_element(
                    value=common.NormalizedValue(value=value),
                    select=select)

    for asdu_type in [common.AsduType.C_SE_NB]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in scaled_values:
            for select in [True, False]:
                yield asdu_type, io_element(
                    value=common.ScaledValue(value=value),
                    select=select)

    for asdu_type in [common.AsduType.C_SE_NC]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in floating_values:
            for select in [True, False]:
                yield asdu_type, io_element(
                    value=common.FloatingValue(value=value),
                    select=select)

    for asdu_type in [common.AsduType.C_BO_NA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for value in bitstring_values:
            yield asdu_type, io_element(
                value=common.BitstringValue(value=value))

    for asdu_type in [common.AsduType.M_EI_NA]:
        io_element = getattr(common, f"IoElement_{asdu_type.name}")
        for _ in range(3):
            cause = rndm.randint(0, 127)
            yield asdu_type, io_element(
                param_change=get_random_bool(),
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
    yield asdu_type, io_element(time=get_time(size=common.TimeSize.SEVEN))

    asdu_type = common.AsduType.C_RP_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for qualifier in [0, 255, 123]:
        yield asdu_type, io_element(qualifier=qualifier)

    asdu_type = common.AsduType.C_CD_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for time in [0, 65535, 123]:
        yield asdu_type, io_element(time=time)

    asdu_type = common.AsduType.P_ME_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for value in normalized_values:
        yield asdu_type, io_element(
            value=common.NormalizedValue(value=value),
            qualifier=rndm.randint(0, 255))

    asdu_type = common.AsduType.P_ME_NB
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for value in scaled_values:
        yield asdu_type, io_element(value=common.ScaledValue(value=value),
                                    qualifier=rndm.randint(0, 255))

    asdu_type = common.AsduType.P_ME_NC
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for value in floating_values:
        yield asdu_type, io_element(value=common.FloatingValue(value=value),
                                    qualifier=rndm.randint(0, 255))

    asdu_type = common.AsduType.F_FR_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    file_length=rndm.randint(0, 16777215),
                                    ready=get_random_bool())

    asdu_type = common.AsduType.F_SR_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    section_name=rndm.randint(0, 255),
                                    section_length=rndm.randint(0, 16777215),
                                    ready=get_random_bool())

    asdu_type = common.AsduType.F_SC_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    section_name=rndm.randint(0, 255),
                                    qualifier=rndm.randint(0, 255))

    asdu_type = common.AsduType.F_LS_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    section_name=rndm.randint(0, 255),
                                    last_qualifier=rndm.randint(0, 255),
                                    checksum=rndm.randint(0, 255))

    asdu_type = common.AsduType.F_AF_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    section_name=rndm.randint(0, 255),
                                    qualifier=rndm.randint(0, 255))

    asdu_type = common.AsduType.F_SG_NA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    section_name=rndm.randint(0, 255),
                                    segment=b'\xab\x12')

    asdu_type = common.AsduType.F_DR_TA
    io_element = getattr(common, f"IoElement_{asdu_type.name}")
    for _ in range(5):
        yield asdu_type, io_element(file_name=rndm.randint(0, 65535),
                                    file_length=rndm.randint(0, 16777215),
                                    more_follows=get_random_bool(),
                                    is_directory=get_random_bool(),
                                    transfer_active=get_random_bool(),
                                    creation_time=get_time(
                                        size=common.TimeSize.SEVEN))
    # TODO: C_RD_NA,  C_TS_NA


step_position_values = [-64, -13, 0, 17, 63]


bitstring_values = [b'\xff' * 4, b'\x00' * 4, b'\x12\xab\xff\x00']


normalized_values = [-1.0, 0.9999, -0.123, 0.456, 0]


scaled_values = [-2**15, -123, 0, 456, 2**15-1]


floating_values = [-16777216.1234, -12345.678, 0, 12345.678, 16777216.1234]


binary_counter_values = [-2**31, -123, 0, 456, 2**31-1]


def remove_ioe_value(asdu):
    ios_new = []
    for io in asdu.ios:
        ioes_new = []
        for ioe in io.elements:
            ioe_value_new = ioe.value._replace(value=None)
            ioes_new.append(ioe._replace(value=ioe_value_new))
        ios_new.append(io._replace(elements=ioes_new))
    return asdu._replace(ios=ios_new)


def get_time_from_asdu(asdu_type):
    if asdu_type.name[-2:] in ['NA', 'NB', 'NC', 'ND']:
        return
    if asdu_type == common.AsduType.F_DR_TA:
        return
    if asdu_type.name.endswith('TA') or asdu_type.name in [
            'M_EP_TB', 'M_EP_TC', 'M_ME_TB', 'M_ME_TC']:
        return get_time(size=common.TimeSize.THREE)
    return get_time(size=common.TimeSize.SEVEN)


time_cnt = 0


def get_time(size=common.TimeSize.SEVEN):
    global time_cnt
    time_cnt += 1
    milliseconds = time_cnt % 60000
    invalid = bool(time_cnt % 2)
    minutes = time_cnt % 60
    summer_time = bool(time_cnt % 2)
    hours = time_cnt % 24
    day_of_week = time_cnt % 7 + 1
    day_of_month = time_cnt % 31 + 1
    months = time_cnt % 12 + 1
    years = time_cnt % 100
    if size == common.TimeSize.THREE:
        return common.Time(
                    size=common.TimeSize.THREE,
                    milliseconds=time_cnt % 59999,
                    invalid=invalid,
                    minutes=minutes,
                    summer_time=None,
                    hours=None,
                    day_of_week=None,
                    day_of_month=None,
                    months=None,
                    years=None)
    if size == common.TimeSize.SEVEN:
        return common.Time(
                        size=common.TimeSize.SEVEN,
                        milliseconds=milliseconds,
                        invalid=invalid,
                        minutes=minutes,
                        summer_time=summer_time,
                        hours=hours,
                        day_of_week=day_of_week,
                        day_of_month=day_of_month,
                        months=months,
                        years=years)


def get_random_bool():
    return bool(rndm.randint(0, 1))


def get_quality(asdu_type):
    if asdu_type in [common.AsduType.M_SP_NA,
                     common.AsduType.M_SP_TA,
                     common.AsduType.M_SP_TB,
                     common.AsduType.M_DP_NA,
                     common.AsduType.M_DP_TA,
                     common.AsduType.M_DP_TB]:
        return common.IndicationQuality(
            invalid=get_random_bool(),
            not_topical=get_random_bool(),
            substituted=get_random_bool(),
            blocked=get_random_bool())
    if asdu_type in [common.AsduType.M_IT_NA,
                     common.AsduType.M_IT_TA,
                     common.AsduType.M_IT_TB]:
        return common.CounterQuality(
            invalid=get_random_bool(),
            adjusted=get_random_bool(),
            overflow=get_random_bool(),
            sequence=rndm.randint(0, 31))
    if asdu_type in [common.AsduType.M_EP_TA,
                     common.AsduType.M_EP_TD,
                     common.AsduType.M_EP_TB,
                     common.AsduType.M_EP_TE,
                     common.AsduType.M_EP_TC,
                     common.AsduType.M_EP_TF]:
        return common.ProtectionQuality(
            invalid=get_random_bool(),
            not_topical=get_random_bool(),
            substituted=get_random_bool(),
            blocked=get_random_bool(),
            time_invalid=get_random_bool())
    return common.MeasurementQuality(
        invalid=get_random_bool(),
        not_topical=get_random_bool(),
        substituted=get_random_bool(),
        blocked=get_random_bool(),
        overflow=get_random_bool())


def get_cause_size():
    return common.CauseSize(rndm.randint(1, 2))


def get_asdu_address_size():
    return common.AsduAddressSize(rndm.randint(1, 2))


def get_io_address_size():
    return common.IoAddressSize(rndm.randint(1, 3))


def get_asdu_address(size):
    if size == common.AsduAddressSize.ONE:
        return rndm.randint(0, 255)
    if size == common.AsduAddressSize.TWO:
        return rndm.randint(256, 65535)


def get_io_address(size):
    if common.IoAddressSize.ONE:
        return rndm.randint(0, 255)
    if common.IoAddressSize.TWO:
        return rndm.randint(256, 65535)
    if common.IoAddressSize.THREE:
        return rndm.randint(65536, 16777215)


@pytest.mark.parametrize("asdu_type, io_element", asdu_type_ioe())
def test_encoder(asdu_type, io_element):
    time = get_time_from_asdu(asdu_type)
    cause_size = get_cause_size()
    originator_address = (0 if cause_size == common.CauseSize.ONE
                          else rndm.randint(0, 255))
    asdu_address_size = get_asdu_address_size()
    asdu_address = get_asdu_address(asdu_address_size)
    io_address_size = get_io_address_size()
    _encoder = encoder.Encoder(
        cause_size=cause_size,
        asdu_address_size=asdu_address_size,
        io_address_size=io_address_size)

    ioes = [io_element]
    ios_no = rndm.randint(1, 3)
    ios = [common.IO(
                address=get_io_address(io_address_size),
                elements=ioes,
                time=time)
           for i in range(ios_no)]

    asdu = common.ASDU(
        type=asdu_type,
        cause=common.Cause(
            type=common.CauseType.SPONTANEOUS,
            is_negative_confirm=False,
            is_test=False,
            originator_address=originator_address),
        address=asdu_address,
        ios=ios)
    asdu_encoded = _encoder.encode_asdu(asdu)
    asdu_decoded = _encoder.decode_asdu(asdu_encoded)

    io_element = asdu.ios[0].elements[0]
    if (hasattr(io_element, 'value') and
            (isinstance(io_element.value, common.NormalizedValue) or
             isinstance(io_element.value, common.FloatingValue))):
        for io, io_decoded in zip(asdu.ios, asdu_decoded.ios):
            for ioe, ioe_decoded in zip(io.elements, io_decoded.elements):
                assert math.isclose(ioe.value.value,
                                    ioe_decoded.value.value,
                                    rel_tol=1e-3)
        assert remove_ioe_value(asdu_decoded) == remove_ioe_value(asdu)
        return
    assert asdu_decoded == asdu
