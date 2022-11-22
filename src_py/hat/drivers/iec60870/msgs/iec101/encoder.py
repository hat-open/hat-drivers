import contextlib
import struct
import typing

from hat import util
from hat.drivers.iec60870.msgs import encoder
from hat.drivers.iec60870.msgs.iec101 import common


class Encoder:

    def __init__(self,
                 cause_size: common.CauseSize,
                 asdu_address_size: common.AsduAddressSize,
                 io_address_size: common.IoAddressSize):
        self._cause_size = cause_size
        self._encoder = encoder.Encoder(
            cause_size=cause_size,
            asdu_address_size=asdu_address_size,
            io_address_size=io_address_size,
            asdu_type_time_sizes=asdu_type_time_sizes,
            inverted_sequence_bit=False,
            decode_io_element_cb=decode_io_element,
            encode_io_element_cb=encode_io_element)

    def decode_asdu(self, asdu_bytes: common.Bytes) -> common.ASDU:
        asdu = self._encoder.decode_asdu(asdu_bytes)

        asdu_type = common.AsduType(asdu.type)
        cause = decode_cause(asdu.cause, self._cause_size)
        address = asdu.address
        ios = [common.IO(address=io.address,
                         elements=io.elements,
                         time=io.time)
               for io in asdu.ios]

        return common.ASDU(type=asdu_type,
                           cause=cause,
                           address=address,
                           ios=ios)

    def encode_asdu(self, asdu: common.ASDU) -> common.Bytes:
        asdu_type = asdu.type.value
        cause = encode_cause(asdu.cause, self._cause_size)
        address = asdu.address
        ios = [encoder.common.IO(address=io.address,
                                 elements=io.elements,
                                 time=io.time)
               for io in asdu.ios]

        asdu = encoder.common.ASDU(type=asdu_type,
                                   cause=cause,
                                   address=address,
                                   ios=ios)

        return self._encoder.encode_asdu(asdu)


asdu_type_time_sizes = {common.AsduType.M_SP_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_DP_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_ST_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_BO_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_ME_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_ME_TB.value: common.TimeSize.THREE,
                        common.AsduType.M_ME_TC.value: common.TimeSize.THREE,
                        common.AsduType.M_IT_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_EP_TA.value: common.TimeSize.THREE,
                        common.AsduType.M_EP_TB.value: common.TimeSize.THREE,
                        common.AsduType.M_EP_TC.value: common.TimeSize.THREE,
                        common.AsduType.M_SP_TB.value: common.TimeSize.SEVEN,
                        common.AsduType.M_DP_TB.value: common.TimeSize.SEVEN,
                        common.AsduType.M_ST_TB.value: common.TimeSize.SEVEN,
                        common.AsduType.M_BO_TB.value: common.TimeSize.SEVEN,
                        common.AsduType.M_ME_TD.value: common.TimeSize.SEVEN,
                        common.AsduType.M_ME_TE.value: common.TimeSize.SEVEN,
                        common.AsduType.M_ME_TF.value: common.TimeSize.SEVEN,
                        common.AsduType.M_IT_TB.value: common.TimeSize.SEVEN,
                        common.AsduType.M_EP_TD.value: common.TimeSize.SEVEN,
                        common.AsduType.M_EP_TE.value: common.TimeSize.SEVEN,
                        common.AsduType.M_EP_TF.value: common.TimeSize.SEVEN}


def decode_cause(cause: int,
                 cause_size: common.CauseSize
                 ) -> common.Cause:
    cause_type = decode_cause_type(cause & 0x3F)
    is_negative_confirm = bool(cause & 0x40)
    is_test = bool(cause & 0x80)

    if cause_size == common.CauseSize.ONE:
        originator_address = 0

    elif cause_size == common.CauseSize.TWO:
        originator_address = cause >> 8

    else:
        raise ValueError('unsupported cause size')

    return common.Cause(type=cause_type,
                        is_negative_confirm=is_negative_confirm,
                        is_test=is_test,
                        originator_address=originator_address)


def encode_cause(cause: common.Cause,
                 cause_size: common.CauseSize
                 ) -> int:
    result = ((0x80 if cause.is_test else 0) |
              (0x40 if cause.is_negative_confirm else 0) |
              encode_cause_type(cause.type))

    if cause_size == common.CauseSize.ONE:
        return result

    if cause_size == common.CauseSize.TWO:
        return result | (cause.originator_address << 8)

    raise ValueError('unsupported cause size')


def decode_cause_type(value: int
                      ) -> typing.Union[common.CauseType,
                                        common.OtherCauseType]:
    with contextlib.suppress(ValueError):
        return common.CauseType(value)
    return value


def encode_cause_type(cause_type: typing.Union[common.CauseType,
                                               common.OtherCauseType]
                      ) -> int:
    return (cause_type.value if isinstance(cause_type, common.CauseType)
            else cause_type)


def decode_io_element(io_bytes: common.Bytes,
                      asdu_type: int
                      ) -> typing.Tuple[common.IoElement, common.Bytes]:
    asdu_type = common.AsduType(asdu_type)

    if asdu_type == common.AsduType.M_SP_NA:
        value = common.SingleValue(io_bytes[0] & 1)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.INDICATION)

        element = common.IoElement_M_SP_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_SP_TA:
        value = common.SingleValue(io_bytes[0] & 1)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.INDICATION)

        element = common.IoElement_M_SP_TA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_DP_NA:
        value = common.DoubleValue(io_bytes[0] & 3)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.INDICATION)

        element = common.IoElement_M_DP_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_DP_TA:
        value = common.DoubleValue(io_bytes[0] & 3)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.INDICATION)

        element = common.IoElement_M_DP_TA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ST_NA:
        value, io_bytes = decode_step_position_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ST_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ST_TA:
        value, io_bytes = decode_step_position_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ST_TA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_BO_NA:
        value, io_bytes = decode_bitstring_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_BO_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_BO_TA:
        value, io_bytes = decode_bitstring_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_BO_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_NA:
        value, io_bytes = decode_normalized_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_TA:
        value, io_bytes = decode_normalized_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_TA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_NB:
        value, io_bytes = decode_scaled_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_NB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_TB:
        value, io_bytes = decode_scaled_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_TB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_NC:
        value, io_bytes = decode_floating_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_NC(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_TC:
        value, io_bytes = decode_floating_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_TC(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_IT_NA:
        value, io_bytes = decode_binary_counter_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.COUNTER)

        element = common.IoElement_M_IT_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_IT_TA:
        value, io_bytes = decode_binary_counter_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.COUNTER)

        element = common.IoElement_M_IT_TA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EP_TA:
        value = common.ProtectionValue(io_bytes[0] & 0x03)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.PROTECTION)
        elapsed_time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_M_EP_TA(value=value,
                                           quality=quality,
                                           elapsed_time=elapsed_time)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EP_TB:
        value, io_bytes = decode_protection_start_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.PROTECTION)
        duration_time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_M_EP_TB(value=value,
                                           quality=quality,
                                           duration_time=duration_time)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EP_TC:
        value, io_bytes = decode_protection_command_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.PROTECTION)
        operating_time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_M_EP_TC(value=value,
                                           quality=quality,
                                           operating_time=operating_time)
        return element, io_bytes

    if asdu_type == common.AsduType.M_PS_NA:
        value, io_bytes = decode_status_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_PS_NA(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_ND:
        value, io_bytes = decode_normalized_value(io_bytes)

        element = common.IoElement_M_ME_ND(value=value)
        return element, io_bytes

    if asdu_type == common.AsduType.M_SP_TB:
        value = common.SingleValue(io_bytes[0] & 1)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.INDICATION)

        element = common.IoElement_M_SP_TB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_DP_TB:
        value = common.DoubleValue(io_bytes[0] & 3)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.INDICATION)

        element = common.IoElement_M_DP_TB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ST_TB:
        value, io_bytes = decode_step_position_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ST_TB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_BO_TB:
        value, io_bytes = decode_bitstring_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_BO_TB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_TD:
        value, io_bytes = decode_normalized_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_TD(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_TE:
        value, io_bytes = decode_scaled_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_TE(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_ME_TF:
        value, io_bytes = decode_floating_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.MEASUREMENT)

        element = common.IoElement_M_ME_TF(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_IT_TB:
        value, io_bytes = decode_binary_counter_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.COUNTER)

        element = common.IoElement_M_IT_TB(value=value,
                                           quality=quality)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EP_TD:
        value = common.ProtectionValue(io_bytes[0] & 0x03)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.PROTECTION)
        elapsed_time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_M_EP_TD(value=value,
                                           quality=quality,
                                           elapsed_time=elapsed_time)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EP_TE:
        value, io_bytes = decode_protection_start_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.PROTECTION)
        duration_time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_M_EP_TE(value=value,
                                           quality=quality,
                                           duration_time=duration_time)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EP_TF:
        value, io_bytes = decode_protection_command_value(io_bytes)
        quality, io_bytes = decode_quality(io_bytes,
                                           common.QualityType.PROTECTION)
        operating_time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_M_EP_TF(value=value,
                                           quality=quality,
                                           operating_time=operating_time)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SC_NA:
        value = common.SingleValue(io_bytes[0] & 1)
        select = bool(io_bytes[0] & 0x80)
        qualifier = (io_bytes[0] >> 2) & 0x1F
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SC_NA(value=value,
                                           select=select,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_DC_NA:
        value = common.DoubleValue(io_bytes[0] & 3)
        select = bool(io_bytes[0] & 0x80)
        qualifier = (io_bytes[0] >> 2) & 0x1F
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_DC_NA(value=value,
                                           select=select,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_RC_NA:
        value = common.RegulatingValue(io_bytes[0] & 3)
        select = bool(io_bytes[0] & 0x80)
        qualifier = (io_bytes[0] >> 2) & 0x1F
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_RC_NA(value=value,
                                           select=select,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SE_NA:
        value, io_bytes = decode_normalized_value(io_bytes)
        select = bool(io_bytes[0] & 0x80)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SE_NA(value=value,
                                           select=select)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SE_NB:
        value, io_bytes = decode_scaled_value(io_bytes)
        select = bool(io_bytes[0] & 0x80)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SE_NB(value=value,
                                           select=select)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SE_NC:
        value, io_bytes = decode_floating_value(io_bytes)
        select = bool(io_bytes[0] & 0x80)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SE_NC(value=value,
                                           select=select)
        return element, io_bytes

    if asdu_type == common.AsduType.C_BO_NA:
        value, io_bytes = decode_bitstring_value(io_bytes)

        element = common.IoElement_C_BO_NA(value=value)
        return element, io_bytes

    if asdu_type == common.AsduType.M_EI_NA:
        param_change = bool(io_bytes[0] & 0x80)
        cause = io_bytes[0] & 0x7F
        io_bytes = io_bytes[1:]

        element = common.IoElement_M_EI_NA(param_change=param_change,
                                           cause=cause)
        return element, io_bytes

    if asdu_type == common.AsduType.C_IC_NA:
        qualifier, io_bytes = io_bytes[0], io_bytes[1:]

        element = common.IoElement_C_IC_NA(qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_CI_NA:
        request = io_bytes[0] & 0x3F
        freeze = common.FreezeCode(io_bytes[0] >> 6)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_CI_NA(request=request,
                                           freeze=freeze)
        return element, io_bytes

    if asdu_type == common.AsduType.C_RD_NA:
        element = common.IoElement_C_RD_NA()
        return element, io_bytes

    if asdu_type == common.AsduType.C_CS_NA:
        time = encoder.decode_time(io_bytes[:7], common.TimeSize.SEVEN)
        io_bytes = io_bytes[7:]

        element = common.IoElement_C_CS_NA(time=time)
        return element, io_bytes

    if asdu_type == common.AsduType.C_TS_NA:
        io_bytes = io_bytes[2:]

        element = common.IoElement_C_TS_NA()
        return element, io_bytes

    if asdu_type == common.AsduType.C_RP_NA:
        qualifier, io_bytes = io_bytes[0], io_bytes[1:]

        element = common.IoElement_C_RP_NA(qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_CD_NA:
        time = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_C_CD_NA(time=time)
        return element, io_bytes

    if asdu_type == common.AsduType.P_ME_NA:
        value, io_bytes = decode_normalized_value(io_bytes)
        qualifier, io_bytes = io_bytes[0], io_bytes[1:]

        element = common.IoElement_P_ME_NA(value=value,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.P_ME_NB:
        value, io_bytes = decode_scaled_value(io_bytes)
        qualifier, io_bytes = io_bytes[0], io_bytes[1:]

        element = common.IoElement_P_ME_NB(value=value,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.P_ME_NC:
        value, io_bytes = decode_floating_value(io_bytes)
        qualifier, io_bytes = io_bytes[0], io_bytes[1:]

        element = common.IoElement_P_ME_NC(value=value,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.P_AC_NA:
        qualifier, io_bytes = io_bytes[0], io_bytes[1:]

        element = common.IoElement_P_AC_NA(qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.F_FR_NA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        file_length = int.from_bytes(io_bytes[2:5], 'little')
        ready = bool(io_bytes[5] & 0x80)
        io_bytes = io_bytes[6:]

        element = common.IoElement_F_FR_NA(file_name=file_name,
                                           file_length=file_length,
                                           ready=ready)
        return element, io_bytes

    if asdu_type == common.AsduType.F_SR_NA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        section_name = io_bytes[2]
        section_length = int.from_bytes(io_bytes[3:6], 'little')
        ready = bool(io_bytes[6] & 0x80)
        io_bytes = io_bytes[7:]

        element = common.IoElement_F_SR_NA(file_name=file_name,
                                           section_name=section_name,
                                           section_length=section_length,
                                           ready=ready)
        return element, io_bytes

    if asdu_type == common.AsduType.F_SC_NA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        section_name = io_bytes[2]
        qualifier = io_bytes[3]
        io_bytes = io_bytes[4:]

        element = common.IoElement_F_SC_NA(file_name=file_name,
                                           section_name=section_name,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.F_LS_NA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        section_name = io_bytes[2]
        last_qualifier = io_bytes[3]
        checksum = io_bytes[4]
        io_bytes = io_bytes[5:]

        element = common.IoElement_F_LS_NA(file_name=file_name,
                                           section_name=section_name,
                                           last_qualifier=last_qualifier,
                                           checksum=checksum)
        return element, io_bytes

    if asdu_type == common.AsduType.F_AF_NA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        section_name = io_bytes[2]
        qualifier = io_bytes[3]
        io_bytes = io_bytes[4:]

        element = common.IoElement_F_AF_NA(file_name=file_name,
                                           section_name=section_name,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.F_SG_NA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        section_name = io_bytes[2]
        length = io_bytes[3]
        segment = io_bytes[4:4+length]
        io_bytes = io_bytes[4+length:]

        element = common.IoElement_F_SG_NA(file_name=file_name,
                                           section_name=section_name,
                                           segment=segment)
        return element, io_bytes

    if asdu_type == common.AsduType.F_DR_TA:
        file_name = int.from_bytes(io_bytes[:2], 'little')
        file_length = int.from_bytes(io_bytes[2:5], 'little')
        more_follows = bool(io_bytes[5] & 0x20)
        is_directory = bool(io_bytes[5] & 0x40)
        transfer_active = bool(io_bytes[5] & 0x80)
        creation_time = encoder.decode_time(io_bytes[6:13],
                                            common.TimeSize.SEVEN)
        io_bytes = io_bytes[13:]

        element = common.IoElement_F_DR_TA(file_name=file_name,
                                           file_length=file_length,
                                           more_follows=more_follows,
                                           is_directory=is_directory,
                                           transfer_active=transfer_active,
                                           creation_time=creation_time)
        return element, io_bytes

    raise ValueError('unsupported ASDU type')


def encode_io_element(element: common.IoElement,
                      asdu_type: int
                      ) -> typing.Iterable[int]:
    asdu_type = common.AsduType(asdu_type)

    if isinstance(element, common.IoElement_M_SP_NA):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality

    elif isinstance(element, common.IoElement_M_SP_TA):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality

    elif isinstance(element, common.IoElement_M_DP_NA):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality

    elif isinstance(element, common.IoElement_M_DP_TA):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality

    elif isinstance(element, common.IoElement_M_ST_NA):
        yield from encode_step_position_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ST_TA):
        yield from encode_step_position_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_BO_NA):
        yield from encode_bitstring_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_BO_TA):
        yield from encode_bitstring_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_NA):
        yield from encode_normalized_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_TA):
        yield from encode_normalized_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_NB):
        yield from encode_scaled_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_TB):
        yield from encode_scaled_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_NC):
        yield from encode_floating_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_TC):
        yield from encode_floating_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_IT_NA):
        yield from encode_binary_counter_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_IT_TA):
        yield from encode_binary_counter_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_EP_TA):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality
        yield from element.elapsed_time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_M_EP_TB):
        yield from encode_protection_start_value(element.value)
        yield from encode_quality(element.quality)
        yield from element.duration_time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_M_EP_TC):
        yield from encode_protection_command_value(element.value)
        yield from encode_quality(element.quality)
        yield from element.operating_time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_M_PS_NA):
        yield from encode_status_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_ND):
        yield from encode_normalized_value(element.value)

    elif isinstance(element, common.IoElement_M_SP_TB):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality

    elif isinstance(element, common.IoElement_M_DP_TB):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality

    elif isinstance(element, common.IoElement_M_ST_TB):
        yield from encode_step_position_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_BO_TB):
        yield from encode_bitstring_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_TD):
        yield from encode_normalized_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_TE):
        yield from encode_scaled_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_ME_TF):
        yield from encode_floating_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_IT_TB):
        yield from encode_binary_counter_value(element.value)
        yield from encode_quality(element.quality)

    elif isinstance(element, common.IoElement_M_EP_TD):
        quality = util.first(encode_quality(element.quality))
        yield element.value.value | quality
        yield from element.elapsed_time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_M_EP_TE):
        yield from encode_protection_start_value(element.value)
        yield from encode_quality(element.quality)
        yield from element.duration_time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_M_EP_TF):
        yield from encode_protection_command_value(element.value)
        yield from encode_quality(element.quality)
        yield from element.operating_time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_C_SC_NA):
        yield (element.value.value |
               (0x80 if element.select else 0) |
               ((element.qualifier & 0x1F) << 2))

    elif isinstance(element, common.IoElement_C_DC_NA):
        yield (element.value.value |
               (0x80 if element.select else 0) |
               ((element.qualifier & 0x1F) << 2))

    elif isinstance(element, common.IoElement_C_RC_NA):
        yield (element.value.value |
               (0x80 if element.select else 0) |
               ((element.qualifier & 0x1F) << 2))

    elif isinstance(element, common.IoElement_C_SE_NA):
        yield from encode_normalized_value(element.value)
        yield (0x80 if element.select else 0)

    elif isinstance(element, common.IoElement_C_SE_NB):
        yield from encode_scaled_value(element.value)
        yield (0x80 if element.select else 0)

    elif isinstance(element, common.IoElement_C_SE_NC):
        yield from encode_floating_value(element.value)
        yield (0x80 if element.select else 0)

    elif isinstance(element, common.IoElement_C_BO_NA):
        yield from encode_bitstring_value(element.value)

    elif isinstance(element, common.IoElement_M_EI_NA):
        yield ((0x80 if element.param_change else 0x00) |
               (element.cause & 0x7F))

    elif isinstance(element, common.IoElement_C_IC_NA):
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_C_CI_NA):
        yield ((element.freeze.value << 6) |
               (element.request & 0x3F))

    elif isinstance(element, common.IoElement_C_RD_NA):
        pass

    elif isinstance(element, common.IoElement_C_CS_NA):
        yield from encoder.encode_time(element.time, common.TimeSize.SEVEN)

    elif isinstance(element, common.IoElement_C_TS_NA):
        yield 0xAA
        yield 0x55

    elif isinstance(element, common.IoElement_C_RP_NA):
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_C_CD_NA):
        yield from element.time.to_bytes(2, 'little')

    elif isinstance(element, common.IoElement_P_ME_NA):
        yield from encode_normalized_value(element.value)
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_P_ME_NB):
        yield from encode_scaled_value(element.value)
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_P_ME_NC):
        yield from encode_floating_value(element.value)
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_P_AC_NA):
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_F_FR_NA):
        yield from element.file_name.to_bytes(2, 'little')
        yield from element.file_length.to_bytes(3, 'little')
        yield (0x80 if element.ready else 0x00)

    elif isinstance(element, common.IoElement_F_SR_NA):
        yield from element.file_name.to_bytes(2, 'little')
        yield element.section_name & 0xFF
        yield from element.section_length.to_bytes(3, 'little')
        yield (0x80 if element.ready else 0x00)

    elif isinstance(element, common.IoElement_F_SC_NA):
        yield from element.file_name.to_bytes(2, 'little')
        yield element.section_name & 0xFF
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_F_LS_NA):
        yield from element.file_name.to_bytes(2, 'little')
        yield element.section_name & 0xFF
        yield element.last_qualifier & 0xFF
        yield element.checksum & 0xFF

    elif isinstance(element, common.IoElement_F_AF_NA):
        yield from element.file_name.to_bytes(2, 'little')
        yield element.section_name & 0xFF
        yield element.qualifier & 0xFF

    elif isinstance(element, common.IoElement_F_SG_NA):
        yield from element.file_name.to_bytes(2, 'little')
        yield element.section_name & 0xFF
        yield len(element.segment)
        yield from element.segment

    elif isinstance(element, common.IoElement_F_DR_TA):
        yield from element.file_name.to_bytes(2, 'little')
        yield from element.file_length.to_bytes(3, 'little')
        yield ((0x20 if element.more_follows else 0x00) |
               (0x40 if element.is_directory else 0x00) |
               (0x80 if element.transfer_active else 0x00))
        yield from encoder.encode_time(element.creation_time,
                                       common.TimeSize.SEVEN)

    else:
        raise ValueError('unsupported IO element')


def decode_quality(io_bytes: common.Bytes,
                   quality_type: common.QualityType
                   ) -> typing.Tuple[common.Quality, common.Bytes]:
    if quality_type == common.QualityType.INDICATION:
        invalid = bool(io_bytes[0] & 0x80)
        not_topical = bool(io_bytes[0] & 0x40)
        substituted = bool(io_bytes[0] & 0x20)
        blocked = bool(io_bytes[0] & 0x10)
        quality = common.IndicationQuality(invalid=invalid,
                                           not_topical=not_topical,
                                           substituted=substituted,
                                           blocked=blocked)

    elif quality_type == common.QualityType.MEASUREMENT:
        invalid = bool(io_bytes[0] & 0x80)
        not_topical = bool(io_bytes[0] & 0x40)
        substituted = bool(io_bytes[0] & 0x20)
        blocked = bool(io_bytes[0] & 0x10)
        overflow = bool(io_bytes[0] & 0x01)
        quality = common.MeasurementQuality(invalid=invalid,
                                            not_topical=not_topical,
                                            substituted=substituted,
                                            blocked=blocked,
                                            overflow=overflow)

    elif quality_type == common.QualityType.COUNTER:
        invalid = bool(io_bytes[0] & 0x80)
        adjusted = bool(io_bytes[0] & 0x40)
        overflow = bool(io_bytes[0] & 0x20)
        sequence = io_bytes[0] & 0x1F
        quality = common.CounterQuality(invalid=invalid,
                                        adjusted=adjusted,
                                        overflow=overflow,
                                        sequence=sequence)

    elif quality_type == common.QualityType.PROTECTION:
        invalid = bool(io_bytes[0] & 0x80)
        not_topical = bool(io_bytes[0] & 0x40)
        substituted = bool(io_bytes[0] & 0x20)
        blocked = bool(io_bytes[0] & 0x10)
        time_invalid = bool(io_bytes[0] & 0x08)
        quality = common.ProtectionQuality(invalid=invalid,
                                           not_topical=not_topical,
                                           substituted=substituted,
                                           blocked=blocked,
                                           time_invalid=time_invalid)

    else:
        raise ValueError('unsupported quality type')

    return quality, io_bytes[1:]


def encode_quality(quality: common.Quality
                   ) -> typing.Iterable[int]:
    if isinstance(quality, common.IndicationQuality):
        yield ((0x80 if quality.invalid else 0) |
               (0x40 if quality.not_topical else 0) |
               (0x20 if quality.substituted else 0) |
               (0x10 if quality.blocked else 0))

    elif isinstance(quality, common.MeasurementQuality):
        yield ((0x80 if quality.invalid else 0) |
               (0x40 if quality.not_topical else 0) |
               (0x20 if quality.substituted else 0) |
               (0x10 if quality.blocked else 0) |
               (0x01 if quality.overflow else 0))

    elif isinstance(quality, common.CounterQuality):
        yield ((0x80 if quality.invalid else 0) |
               (0x40 if quality.adjusted else 0) |
               (0x20 if quality.overflow else 0) |
               (quality.sequence & 0x1F))

    elif isinstance(quality, common.ProtectionQuality):
        yield ((0x80 if quality.invalid else 0) |
               (0x40 if quality.not_topical else 0) |
               (0x20 if quality.substituted else 0) |
               (0x10 if quality.blocked else 0) |
               (0x08 if quality.time_invalid else 0))

    else:
        raise ValueError('unsupported quality')


def decode_step_position_value(io_bytes: common.Bytes
                               ) -> typing.Tuple[common.StepPositionValue,
                                                 common.Bytes]:
    value = (((-1 << 7) if io_bytes[0] & 0x40 else 0) |
             (io_bytes[0] & 0x7F))
    transient = bool(io_bytes[0] & 0x80)
    step_position_value = common.StepPositionValue(value=value,
                                                   transient=transient)
    return step_position_value, io_bytes[1:]


def encode_step_position_value(value: common.StepPositionValue
                               ) -> typing.Iterable[int]:
    yield ((0x80 if value.transient else 0) |
           (value.value & 0x7F))


def decode_bitstring_value(io_bytes: common.Bytes
                           ) -> typing.Tuple[common.BitstringValue,
                                             common.Bytes]:
    value = io_bytes[:4]
    bitstring_value = common.BitstringValue(value)
    return bitstring_value, io_bytes[4:]


def encode_bitstring_value(value: common.BitstringValue
                           ) -> typing.Iterable[int]:
    yield value.value[0]
    yield value.value[1]
    yield value.value[2]
    yield value.value[3]


def decode_normalized_value(io_bytes: common.Bytes
                            ) -> typing.Tuple[common.NormalizedValue,
                                              common.Bytes]:
    value = struct.unpack('<h', io_bytes[:2])[0] / 0x7fff
    normalized_value = common.NormalizedValue(value)
    return normalized_value, io_bytes[2:]


def encode_normalized_value(value: common.NormalizedValue
                            ) -> typing.Iterable[int]:
    yield from struct.pack('<h', round(value.value * 0x7fff))


def decode_scaled_value(io_bytes: common.Bytes
                        ) -> typing.Tuple[common.ScaledValue, common.Bytes]:
    value = struct.unpack('<h', io_bytes[:2])[0]
    scaled_value = common.ScaledValue(value)
    return scaled_value, io_bytes[2:]


def encode_scaled_value(value: common.ScaledValue
                        ) -> typing.Iterable[int]:
    yield from struct.pack('<h', value.value)


def decode_floating_value(io_bytes: common.Bytes
                          ) -> typing.Tuple[common.FloatingValue,
                                            common.Bytes]:
    value = struct.unpack('<f', io_bytes[:4])[0]
    floating_value = common.FloatingValue(value)
    return floating_value, io_bytes[4:]


def encode_floating_value(value: common.FloatingValue
                          ) -> typing.Iterable[int]:
    yield from struct.pack('<f', value.value)


def decode_binary_counter_value(io_bytes: common.Bytes
                                ) -> typing.Tuple[common.BinaryCounterValue,
                                                  common.Bytes]:
    value = struct.unpack('<i', io_bytes[:4])[0]
    binary_counter_value = common.BinaryCounterValue(value)
    return binary_counter_value, io_bytes[4:]


def encode_binary_counter_value(value: common.BinaryCounterValue
                                ) -> typing.Iterable[int]:
    yield from struct.pack('<i', value.value)


def decode_protection_start_value(io_bytes: common.Bytes
                                  ) -> typing.Tuple[common.ProtectionStartValue,  # NOQA
                                                    common.Bytes]:
    general = bool(io_bytes[0] & 0x01)
    l1 = bool(io_bytes[0] & 0x02)
    l2 = bool(io_bytes[0] & 0x04)
    l3 = bool(io_bytes[0] & 0x08)
    ie = bool(io_bytes[0] & 0x10)
    reverse = bool(io_bytes[0] & 0x20)
    protection_start_value = common.ProtectionStartValue(general=general,
                                                         l1=l1,
                                                         l2=l2,
                                                         l3=l3,
                                                         ie=ie,
                                                         reverse=reverse)
    return protection_start_value, io_bytes[1:]


def encode_protection_start_value(value: common.ProtectionStartValue
                                  ) -> typing.Iterable[int]:
    yield ((0x01 if value.general else 0x00) |
           (0x02 if value.l1 else 0x00) |
           (0x04 if value.l2 else 0x00) |
           (0x08 if value.l3 else 0x00) |
           (0x10 if value.ie else 0x00) |
           (0x20 if value.reverse else 0x00))


def decode_protection_command_value(io_bytes: common.Bytes
                                    ) -> typing.Tuple[common.ProtectionCommandValue,  # NOQA
                                                      common.Bytes]:
    general = bool(io_bytes[0] & 0x01)
    l1 = bool(io_bytes[0] & 0x02)
    l2 = bool(io_bytes[0] & 0x04)
    l3 = bool(io_bytes[0] & 0x08)
    protection_command_value = common.ProtectionCommandValue(general=general,
                                                             l1=l1,
                                                             l2=l2,
                                                             l3=l3)
    return protection_command_value, io_bytes[1:]


def encode_protection_command_value(value: common.ProtectionCommandValue
                                    ) -> typing.Iterable[int]:
    yield ((0x01 if value.general else 0x00) |
           (0x02 if value.l1 else 0x00) |
           (0x04 if value.l2 else 0x00) |
           (0x08 if value.l3 else 0x00))


def decode_status_value(io_bytes: common.Bytes
                        ) -> typing.Tuple[common.StatusValue,
                                          common.Bytes]:
    value = [bool(io_bytes[i // 8] & (1 << (i % 8)))
             for i in range(16)]
    change = [bool(io_bytes[2 + i // 8] & (1 << (i % 8)))
              for i in range(16)]
    status_value = common.StatusValue(value=value,
                                      change=change)
    return status_value, io_bytes[4:]


def encode_status_value(value: common.StatusValue
                        ) -> typing.Iterable[int]:
    for i in [value.value, value.change]:
        for j in range(2):
            acc = 0
            for k in range(8):
                if i[j * 8 + k]:
                    acc = acc | (1 << k)
            yield acc
