from hat import util

from hat.drivers.iec60870.encodings import encoder
from hat.drivers.iec60870.encodings import iec101
from hat.drivers.iec60870.encodings.iec104 import common


iec101_asdu_types = {common.AsduType.M_SP_NA.value,
                     common.AsduType.M_DP_NA.value,
                     common.AsduType.M_ST_NA.value,
                     common.AsduType.M_BO_NA.value,
                     common.AsduType.M_ME_NA.value,
                     common.AsduType.M_ME_NB.value,
                     common.AsduType.M_ME_NC.value,
                     common.AsduType.M_IT_NA.value,
                     common.AsduType.M_PS_NA.value,
                     common.AsduType.M_ME_ND.value,
                     common.AsduType.M_SP_TB.value,
                     common.AsduType.M_DP_TB.value,
                     common.AsduType.M_ST_TB.value,
                     common.AsduType.M_BO_TB.value,
                     common.AsduType.M_ME_TD.value,
                     common.AsduType.M_ME_TE.value,
                     common.AsduType.M_ME_TF.value,
                     common.AsduType.M_IT_TB.value,
                     common.AsduType.M_EP_TD.value,
                     common.AsduType.M_EP_TE.value,
                     common.AsduType.M_EP_TF.value,
                     common.AsduType.C_SC_NA.value,
                     common.AsduType.C_DC_NA.value,
                     common.AsduType.C_RC_NA.value,
                     common.AsduType.C_SE_NA.value,
                     common.AsduType.C_SE_NB.value,
                     common.AsduType.C_SE_NC.value,
                     common.AsduType.C_BO_NA.value,
                     common.AsduType.M_EI_NA.value,
                     common.AsduType.C_IC_NA.value,
                     common.AsduType.C_CI_NA.value,
                     common.AsduType.C_RD_NA.value,
                     common.AsduType.C_CS_NA.value,
                     common.AsduType.C_RP_NA.value,
                     common.AsduType.P_ME_NA.value,
                     common.AsduType.P_ME_NB.value,
                     common.AsduType.P_ME_NC.value,
                     common.AsduType.P_AC_NA.value,
                     common.AsduType.F_FR_NA.value,
                     common.AsduType.F_SR_NA.value,
                     common.AsduType.F_SC_NA.value,
                     common.AsduType.F_LS_NA.value,
                     common.AsduType.F_AF_NA.value,
                     common.AsduType.F_SG_NA.value,
                     common.AsduType.F_DR_TA.value}


class Encoder:

    def __init__(self, max_asdu_size: int = 249):
        self._max_asdu_size = max_asdu_size
        self._encoder = encoder.Encoder(
            cause_size=common.CauseSize.TWO,
            asdu_address_size=common.AsduAddressSize.TWO,
            io_address_size=common.IoAddressSize.THREE,
            asdu_type_time_sizes=_asdu_type_time_sizes,
            inverted_sequence_bit=False,
            decode_io_element_cb=_decode_io_element,
            encode_io_element_cb=_encode_io_element)

    @property
    def max_asdu_size(self) -> int:
        return self._max_asdu_size

    @property
    def cause_size(self) -> common.CauseSize:
        return self._encoder.cause_size

    @property
    def asdu_address_size(self) -> common.AsduAddressSize:
        return self._encoder.asdu_address_size

    @property
    def io_address_size(self) -> common.IoAddressSize:
        return self._encoder.io_address_size

    def decode_asdu(self,
                    asdu_bytes: util.Bytes
                    ) -> tuple[common.ASDU, util.Bytes]:
        asdu, rest = self._encoder.decode_asdu(asdu_bytes)

        asdu_type = _decode_asdu_type(asdu.type)

        cause = iec101.decode_cause(asdu.cause, common.CauseSize.TWO)
        address = asdu.address
        ios = [common.IO(address=io.address,
                         elements=io.elements,
                         time=io.time)
               for io in asdu.ios]

        asdu = common.ASDU(type=asdu_type,
                           cause=cause,
                           address=address,
                           ios=ios)
        return asdu, rest

    def encode_asdu(self, asdu: common.ASDU) -> util.Bytes:
        asdu_type = asdu.type.value
        cause = iec101.encode_cause(asdu.cause, common.CauseSize.TWO)
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


_asdu_type_time_sizes = {
    **{k: v for k, v in iec101.asdu_type_time_sizes.items()
       if k in iec101_asdu_types},
    **{common.AsduType.C_SC_TA.value: common.TimeSize.SEVEN,
       common.AsduType.C_DC_TA.value: common.TimeSize.SEVEN,
       common.AsduType.C_RC_TA.value: common.TimeSize.SEVEN,
       common.AsduType.C_SE_TA.value: common.TimeSize.SEVEN,
       common.AsduType.C_SE_TB.value: common.TimeSize.SEVEN,
       common.AsduType.C_SE_TC.value: common.TimeSize.SEVEN,
       common.AsduType.C_BO_TA.value: common.TimeSize.SEVEN,
       common.AsduType.C_TS_TA.value: common.TimeSize.SEVEN}}


def _decode_io_element(io_bytes, asdu_type):
    asdu_type = _decode_asdu_type(asdu_type)

    if asdu_type.value in iec101_asdu_types:
        return iec101.decode_io_element(io_bytes, asdu_type.value)

    if asdu_type == common.AsduType.C_SC_TA:
        value = common.SingleValue(io_bytes[0] & 1)
        select = bool(io_bytes[0] & 0x80)
        qualifier = (io_bytes[0] >> 2) & 0x1F
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SC_TA(value=value,
                                           select=select,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_DC_TA:
        value = common.DoubleValue(io_bytes[0] & 3)
        select = bool(io_bytes[0] & 0x80)
        qualifier = (io_bytes[0] >> 2) & 0x1F
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_DC_TA(value=value,
                                           select=select,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_RC_TA:
        value = common.RegulatingValue(io_bytes[0] & 3)
        select = bool(io_bytes[0] & 0x80)
        qualifier = (io_bytes[0] >> 2) & 0x1F
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_RC_TA(value=value,
                                           select=select,
                                           qualifier=qualifier)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SE_TA:
        value, io_bytes = iec101.decode_normalized_value(io_bytes)
        select = bool(io_bytes[0] & 0x80)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SE_TA(value=value,
                                           select=select)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SE_TB:
        value, io_bytes = iec101.decode_scaled_value(io_bytes)
        select = bool(io_bytes[0] & 0x80)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SE_TB(value=value,
                                           select=select)
        return element, io_bytes

    if asdu_type == common.AsduType.C_SE_TC:
        value, io_bytes = iec101.decode_floating_value(io_bytes)
        select = bool(io_bytes[0] & 0x80)
        io_bytes = io_bytes[1:]

        element = common.IoElement_C_SE_TC(value=value,
                                           select=select)
        return element, io_bytes

    if asdu_type == common.AsduType.C_BO_TA:
        value, io_bytes = iec101.decode_bitstring_value(io_bytes)

        element = common.IoElement_C_BO_TA(value=value)
        return element, io_bytes

    if asdu_type == common.AsduType.C_TS_TA:
        counter = int.from_bytes(io_bytes[:2], 'little')
        io_bytes = io_bytes[2:]

        element = common.IoElement_C_TS_TA(counter=counter)
        return element, io_bytes

    raise ValueError('unsupported ASDU type')


def _encode_io_element(element, asdu_type):
    asdu_type = _decode_asdu_type(asdu_type)

    if asdu_type.value in iec101_asdu_types:
        yield from iec101.encode_io_element(element, asdu_type.value)

    elif isinstance(element, common.IoElement_C_SC_TA):
        yield (element.value.value |
               (0x80 if element.select else 0) |
               ((element.qualifier & 0x1F) << 2))

    elif isinstance(element, common.IoElement_C_DC_TA):
        yield (element.value.value |
               (0x80 if element.select else 0) |
               ((element.qualifier & 0x1F) << 2))

    elif isinstance(element, common.IoElement_C_RC_TA):
        yield (element.value.value |
               (0x80 if element.select else 0) |
               ((element.qualifier & 0x1F) << 2))

    elif isinstance(element, common.IoElement_C_SE_TA):
        yield from iec101.encode_normalized_value(element.value)
        yield (0x80 if element.select else 0)

    elif isinstance(element, common.IoElement_C_SE_TB):
        yield from iec101.encode_scaled_value(element.value)
        yield (0x80 if element.select else 0)

    elif isinstance(element, common.IoElement_C_SE_TC):
        yield from iec101.encode_floating_value(element.value)
        yield (0x80 if element.select else 0)

    elif isinstance(element, common.IoElement_C_BO_TA):
        yield from iec101.encode_bitstring_value(element.value)

    elif isinstance(element, common.IoElement_C_TS_TA):
        yield from element.counter.to_bytes(2, 'little')

    else:
        raise ValueError('unsupported IO element')


def _decode_asdu_type(asdu_type):
    try:
        return common.AsduType(asdu_type)

    except ValueError:
        raise common.AsduTypeError(f"unsupported asdu type {asdu_type}")
