import contextlib
import enum
import typing

from hat import util

from hat.drivers.iec104 import common
from hat.drivers.iec60870.encodings import iec104


class Encoder:

    def __init__(self):
        self._encoder = iec104.encoder.Encoder()

    def encode(self,
               msgs: list[common.Msg]
               ) -> typing.Iterable[util.Bytes]:
        for asdu in _encode_msgs(msgs):
            yield self._encoder.encode_asdu(asdu)

    def decode(self,
               data: util.Bytes
               ) -> typing.Iterable[common.Msg]:
        asdu, _ = self._encoder.decode_asdu(data)
        yield from _decode_asdu(asdu)


def _encode_msgs(msgs):
    # TODO: group messages and io elements

    for msg in msgs:
        yield _encode_msg(msg)


def _decode_asdu(asdu):
    for io in asdu.ios:
        for ioe_i, io_element in enumerate(io.elements):
            yield _decode_io_element(asdu, io, io_element, ioe_i)


def _decode_io_element(asdu, io, io_element, io_element_index):
    io_address = io.address + io_element_index

    if asdu.type in {iec104.common.AsduType.M_SP_NA,
                     iec104.common.AsduType.M_DP_NA,
                     iec104.common.AsduType.M_ST_NA,
                     iec104.common.AsduType.M_BO_NA,
                     iec104.common.AsduType.M_ME_NA,
                     iec104.common.AsduType.M_ME_NB,
                     iec104.common.AsduType.M_ME_NC,
                     iec104.common.AsduType.M_IT_NA,
                     iec104.common.AsduType.M_PS_NA,
                     iec104.common.AsduType.M_ME_ND,
                     iec104.common.AsduType.M_SP_TB,
                     iec104.common.AsduType.M_DP_TB,
                     iec104.common.AsduType.M_ST_TB,
                     iec104.common.AsduType.M_BO_TB,
                     iec104.common.AsduType.M_ME_TD,
                     iec104.common.AsduType.M_ME_TE,
                     iec104.common.AsduType.M_ME_TF,
                     iec104.common.AsduType.M_IT_TB,
                     iec104.common.AsduType.M_EP_TD,
                     iec104.common.AsduType.M_EP_TE,
                     iec104.common.AsduType.M_EP_TF}:
        return common.DataMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            data=_decode_data_io_element(io_element, asdu.type),
            time=io.time,
            cause=_decode_cause(asdu.cause.type,
                                common.DataResCause))

    elif asdu.type in {iec104.common.AsduType.C_SC_NA,
                       iec104.common.AsduType.C_DC_NA,
                       iec104.common.AsduType.C_RC_NA,
                       iec104.common.AsduType.C_SE_NA,
                       iec104.common.AsduType.C_SE_NB,
                       iec104.common.AsduType.C_SE_NC,
                       iec104.common.AsduType.C_BO_NA,
                       iec104.common.AsduType.C_SC_TA,
                       iec104.common.AsduType.C_DC_TA,
                       iec104.common.AsduType.C_RC_TA,
                       iec104.common.AsduType.C_SE_TA,
                       iec104.common.AsduType.C_SE_TB,
                       iec104.common.AsduType.C_SE_TC,
                       iec104.common.AsduType.C_BO_TA}:
        return common.CommandMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            command=_decode_command_io_element(io_element, asdu.type),
            is_negative_confirm=asdu.cause.is_negative_confirm,
            time=io.time,
            cause=_decode_cause(asdu.cause.type,
                                common.CommandReqCause,
                                common.CommandResCause))

    elif asdu.type == iec104.common.AsduType.M_EI_NA:
        return common.InitializationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            param_change=io_element.param_change,
            cause=_decode_cause(io_element.cause,
                                common.InitializationResCause))

    elif asdu.type == iec104.common.AsduType.C_IC_NA:
        return common.InterrogationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            request=io_element.qualifier,
            is_negative_confirm=asdu.cause.is_negative_confirm,
            cause=_decode_cause(asdu.cause.type,
                                common.CommandReqCause,
                                common.CommandResCause))

    elif asdu.type == iec104.common.AsduType.C_CI_NA:
        return common.CounterInterrogationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            request=io_element.request,
            freeze=io_element.freeze,
            is_negative_confirm=asdu.cause.is_negative_confirm,
            cause=_decode_cause(asdu.cause.type,
                                common.CommandReqCause,
                                common.CommandResCause))

    elif asdu.type == iec104.common.AsduType.C_RD_NA:
        return common.ReadMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            cause=_decode_cause(asdu.cause.type,
                                common.ReadReqCause,
                                common.ReadResCause))

    elif asdu.type == iec104.common.AsduType.C_CS_NA:
        return common.ClockSyncMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            time=io_element.time,
            is_negative_confirm=asdu.cause.is_negative_confirm,
            cause=_decode_cause(asdu.cause.type,
                                common.ClockSyncReqCause,
                                common.ClockSyncResCause))

    elif asdu.type == iec104.common.AsduType.C_RP_NA:
        return common.ResetMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            qualifier=io_element.qualifier,
            cause=_decode_cause(asdu.cause.type,
                                common.ActivationReqCause,
                                common.ActivationResCause))

    elif asdu.type == iec104.common.AsduType.C_TS_TA:
        return common.TestMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            counter=io_element.counter,
            time=io.time,
            cause=_decode_cause(asdu.cause.type,
                                common.ActivationReqCause,
                                common.ActivationResCause))

    elif asdu.type in {iec104.common.AsduType.P_ME_NA,
                       iec104.common.AsduType.P_ME_NB,
                       iec104.common.AsduType.P_ME_NC}:
        return common.ParameterMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            parameter=_decode_parameter_io_element(io_element, asdu.type),
            cause=_decode_cause(asdu.cause.type,
                                common.ParameterReqCause,
                                common.ParameterResCause))

    elif asdu.type == iec104.common.AsduType.P_AC_NA:
        return common.ParameterActivationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            qualifier=io_element.qualifier,
            cause=_decode_cause(asdu.cause.type,
                                common.ParameterActivationReqCause,
                                common.ParameterActivationResCause))

    raise ValueError('unsupported asdu type')


def _decode_data_io_element(io_element, asdu_type):
    if asdu_type in {iec104.common.AsduType.M_SP_NA,
                     iec104.common.AsduType.M_SP_TB}:
        return common.SingleData(value=io_element.value,
                                 quality=io_element.quality)

    elif asdu_type in {iec104.common.AsduType.M_DP_NA,
                       iec104.common.AsduType.M_DP_TB}:
        return common.DoubleData(value=io_element.value,
                                 quality=io_element.quality)

    elif asdu_type in {iec104.common.AsduType.M_ST_NA,
                       iec104.common.AsduType.M_ST_TB}:
        return common.StepPositionData(value=io_element.value,
                                       quality=io_element.quality)

    elif asdu_type in {iec104.common.AsduType.M_BO_NA,
                       iec104.common.AsduType.M_BO_TB}:
        return common.BitstringData(value=io_element.value,
                                    quality=io_element.quality)

    elif asdu_type in {iec104.common.AsduType.M_ME_NA,
                       iec104.common.AsduType.M_ME_ND,
                       iec104.common.AsduType.M_ME_TD}:
        quality = (None if asdu_type == iec104.common.AsduType.M_ME_ND
                   else io_element.quality)
        return common.NormalizedData(value=io_element.value,
                                     quality=quality)

    elif asdu_type in {iec104.common.AsduType.M_ME_NB,
                       iec104.common.AsduType.M_ME_TE}:
        return common.ScaledData(value=io_element.value,
                                 quality=io_element.quality)

    elif asdu_type in {iec104.common.AsduType.M_ME_NC,
                       iec104.common.AsduType.M_ME_TF}:
        return common.FloatingData(value=io_element.value,
                                   quality=io_element.quality)

    elif asdu_type in {iec104.common.AsduType.M_IT_NA,
                       iec104.common.AsduType.M_IT_TB}:
        return common.BinaryCounterData(value=io_element.value,
                                        quality=io_element.quality)

    elif asdu_type == iec104.common.AsduType.M_EP_TD:
        return common.ProtectionData(
            value=io_element.value,
            quality=io_element.quality,
            elapsed_time=io_element.elapsed_time)

    elif asdu_type == iec104.common.AsduType.M_EP_TE:
        return common.ProtectionStartData(
            value=io_element.value,
            quality=io_element.quality,
            duration_time=io_element.duration_time)

    elif asdu_type == iec104.common.AsduType.M_EP_TF:
        return common.ProtectionCommandData(
            value=io_element.value,
            quality=io_element.quality,
            operating_time=io_element.operating_time)

    elif asdu_type == iec104.common.AsduType.M_PS_NA:
        return common.StatusData(value=io_element.value,
                                 quality=io_element.quality)

    raise ValueError('unsupported asdu type')


def _decode_command_io_element(io_element, asdu_type):
    if asdu_type in {iec104.common.AsduType.C_SC_NA,
                     iec104.common.AsduType.C_SC_TA}:
        return common.SingleCommand(value=io_element.value,
                                    select=io_element.select,
                                    qualifier=io_element.qualifier)

    elif asdu_type in {iec104.common.AsduType.C_DC_NA,
                       iec104.common.AsduType.C_DC_TA}:
        return common.DoubleCommand(value=io_element.value,
                                    select=io_element.select,
                                    qualifier=io_element.qualifier)

    elif asdu_type in {iec104.common.AsduType.C_RC_NA,
                       iec104.common.AsduType.C_RC_TA}:
        return common.RegulatingCommand(value=io_element.value,
                                        select=io_element.select,
                                        qualifier=io_element.qualifier)

    elif asdu_type in {iec104.common.AsduType.C_SE_NA,
                       iec104.common.AsduType.C_SE_TA}:
        return common.NormalizedCommand(value=io_element.value,
                                        select=io_element.select)

    elif asdu_type in {iec104.common.AsduType.C_SE_NB,
                       iec104.common.AsduType.C_SE_TB}:
        return common.ScaledCommand(value=io_element.value,
                                    select=io_element.select)

    elif asdu_type in {iec104.common.AsduType.C_SE_NC,
                       iec104.common.AsduType.C_SE_TC}:
        return common.FloatingCommand(value=io_element.value,
                                      select=io_element.select)

    elif asdu_type in {iec104.common.AsduType.C_BO_NA,
                       iec104.common.AsduType.C_BO_TA}:
        return common.BitstringCommand(value=io_element.value)

    raise ValueError('unsupported asdu type')


def _decode_parameter_io_element(io_element, asdu_type):
    if asdu_type == iec104.common.AsduType.P_ME_NA:
        return common.NormalizedParameter(value=io_element.value,
                                          qualifier=io_element.qualifier)

    elif asdu_type == iec104.common.AsduType.P_ME_NB:
        return common.ScaledParameter(value=io_element.value,
                                      qualifier=io_element.qualifier)

    elif asdu_type == iec104.common.AsduType.P_ME_NC:
        return common.FloatingParameter(value=io_element.value,
                                        qualifier=io_element.qualifier)

    raise ValueError('unsupported asdu type')


def _decode_cause(cause_type, *cause_classes):
    value = (cause_type.value if isinstance(cause_type, enum.Enum)
             else cause_type)
    for cause_class in cause_classes:
        with contextlib.suppress(ValueError):
            return cause_class(value)
    return value


def _encode_cause(cause):
    value = cause.value if isinstance(cause, enum.Enum) else cause
    with contextlib.suppress(ValueError):
        return iec104.common.CauseType(value)
    return value


def _encode_msg(msg):
    # TODO: group messages and io elements

    is_negative_confirm = False
    io_address = 0
    time = None

    if isinstance(msg, common.DataMsg):
        asdu_type = _get_data_asdu_type(msg.data, msg.time)
        cause_type = _encode_cause(msg.cause)
        io_address = msg.io_address
        io_element = _get_data_io_element(msg.data, asdu_type)
        time = msg.time

    elif isinstance(msg, common.CommandMsg):
        asdu_type = _get_command_asdu_type(msg.command, msg.time)
        cause_type = _encode_cause(msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_address = msg.io_address
        io_element = _get_command_io_element(msg.command, asdu_type)
        time = msg.time

    elif isinstance(msg, common.InitializationMsg):
        asdu_type = iec104.common.AsduType.M_EI_NA
        cause_type = iec104.common.CauseType.INITIALIZED
        io_element = iec104.common.IoElement_M_EI_NA(
            param_change=msg.param_change,
            cause=(msg.cause.value if isinstance(msg.cause, enum.Enum)
                   else msg.cause))

    elif isinstance(msg, common.InterrogationMsg):
        asdu_type = iec104.common.AsduType.C_IC_NA
        cause_type = _encode_cause(msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_element = iec104.common.IoElement_C_IC_NA(
            qualifier=msg.request)

    elif isinstance(msg, common.CounterInterrogationMsg):
        asdu_type = iec104.common.AsduType.C_CI_NA
        cause_type = _encode_cause(msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_element = iec104.common.IoElement_C_CI_NA(
            request=msg.request,
            freeze=msg.freeze)

    elif isinstance(msg, common.ReadMsg):
        asdu_type = iec104.common.AsduType.C_RD_NA
        cause_type = _encode_cause(msg.cause)
        io_address = msg.io_address
        io_element = iec104.common.IoElement_C_RD_NA()

    elif isinstance(msg, common.ClockSyncMsg):
        asdu_type = iec104.common.AsduType.C_CS_NA
        cause_type = _encode_cause(msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_element = iec104.common.IoElement_C_CS_NA(
            time=msg.time)

    elif isinstance(msg, common.TestMsg):
        asdu_type = iec104.common.AsduType.C_TS_TA
        cause_type = _encode_cause(msg.cause)
        io_element = iec104.common.IoElement_C_TS_TA(
            counter=msg.counter)
        time = msg.time

    elif isinstance(msg, common.ResetMsg):
        asdu_type = iec104.common.AsduType.C_RP_NA
        cause_type = _encode_cause(msg.cause)
        io_element = iec104.common.IoElement_C_RP_NA(
            qualifier=msg.qualifier)

    elif isinstance(msg, common.ParameterMsg):
        asdu_type = _get_parameter_asdu_type(msg.parameter)
        cause_type = _encode_cause(msg.cause)
        io_address = msg.io_address
        io_element = _get_parameter_io_element(msg.parameter, asdu_type)

    elif isinstance(msg, common.ParameterActivationMsg):
        asdu_type = iec104.common.AsduType.P_AC_NA
        cause_type = _encode_cause(msg.cause)
        io_address = msg.io_address
        io_element = iec104.common.IoElement_P_AC_NA(
            qualifier=msg.qualifier)

    else:
        raise ValueError('unsupported message')

    cause = iec104.common.Cause(type=cause_type,
                                is_negative_confirm=is_negative_confirm,
                                is_test=msg.is_test,
                                originator_address=msg.originator_address)

    io = iec104.common.IO(address=io_address,
                          elements=[io_element],
                          time=time)

    asdu = iec104.common.ASDU(type=asdu_type,
                              cause=cause,
                              address=msg.asdu_address,
                              ios=[io])

    return asdu


def _get_data_asdu_type(data, time):
    if isinstance(data, common.SingleData):
        if time is None:
            return iec104.common.AsduType.M_SP_NA

        else:
            return iec104.common.AsduType.M_SP_TB

    elif isinstance(data, common.DoubleData):
        if time is None:
            return iec104.common.AsduType.M_DP_NA

        else:
            return iec104.common.AsduType.M_DP_TB

    elif isinstance(data, common.StepPositionData):
        if time is None:
            return iec104.common.AsduType.M_ST_NA

        else:
            return iec104.common.AsduType.M_ST_TB

    elif isinstance(data, common.BitstringData):
        if time is None:
            return iec104.common.AsduType.M_BO_NA

        else:
            return iec104.common.AsduType.M_BO_TB

    elif isinstance(data, common.NormalizedData):
        if time is None:
            if data.quality is not None:
                return iec104.common.AsduType.M_ME_NA

            else:
                return iec104.common.AsduType.M_ME_ND

        else:
            if data.quality is not None:
                return iec104.common.AsduType.M_ME_TD

    elif isinstance(data, common.ScaledData):
        if time is None:
            return iec104.common.AsduType.M_ME_NB

        else:
            return iec104.common.AsduType.M_ME_TE

    elif isinstance(data, common.FloatingData):
        if time is None:
            return iec104.common.AsduType.M_ME_NC

        else:
            return iec104.common.AsduType.M_ME_TF

    elif isinstance(data, common.BinaryCounterData):
        if time is None:
            return iec104.common.AsduType.M_IT_NA

        else:
            return iec104.common.AsduType.M_IT_TB

    elif isinstance(data, common.ProtectionData):
        if time is not None:
            return iec104.common.AsduType.M_EP_TD

    elif isinstance(data, common.ProtectionStartData):
        if time is not None:
            return iec104.common.AsduType.M_EP_TE

    elif isinstance(data, common.ProtectionCommandData):
        if time is not None:
            return iec104.common.AsduType.M_EP_TF

    elif isinstance(data, common.StatusData):
        if time is None:
            return iec104.common.AsduType.M_PS_NA

    raise ValueError('unsupported data')


def _get_command_asdu_type(command, time):
    if isinstance(command, common.SingleCommand):
        if time is None:
            return iec104.common.AsduType.C_SC_NA

        else:
            return iec104.common.AsduType.C_SC_TA

    elif isinstance(command, common.DoubleCommand):
        if time is None:
            return iec104.common.AsduType.C_DC_NA

        else:
            return iec104.common.AsduType.C_DC_TA

    elif isinstance(command, common.RegulatingCommand):
        if time is None:
            return iec104.common.AsduType.C_RC_NA

        else:
            return iec104.common.AsduType.C_RC_TA

    elif isinstance(command, common.NormalizedCommand):
        if time is None:
            return iec104.common.AsduType.C_SE_NA

        else:
            return iec104.common.AsduType.C_SE_TA

    elif isinstance(command, common.ScaledCommand):
        if time is None:
            return iec104.common.AsduType.C_SE_NB

        else:
            return iec104.common.AsduType.C_SE_TB

    elif isinstance(command, common.FloatingCommand):
        if time is None:
            return iec104.common.AsduType.C_SE_NC

        else:
            return iec104.common.AsduType.C_SE_TC

    elif isinstance(command, common.BitstringCommand):
        if time is None:
            return iec104.common.AsduType.C_BO_NA

        else:
            return iec104.common.AsduType.C_BO_TA

    raise ValueError('unsupported command')


def _get_parameter_asdu_type(parameter):
    if isinstance(parameter, common.NormalizedParameter):
        return iec104.common.AsduType.P_ME_NA

    elif isinstance(parameter, common.ScaledParameter):
        return iec104.common.AsduType.P_ME_NB

    elif isinstance(parameter, common.FloatingParameter):
        return iec104.common.AsduType.P_ME_NC

    raise ValueError('unsupported parameter')


def _get_data_io_element(data, asdu_type):
    if asdu_type == iec104.common.AsduType.M_SP_NA:
        return iec104.common.IoElement_M_SP_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_DP_NA:
        return iec104.common.IoElement_M_DP_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ST_NA:
        return iec104.common.IoElement_M_ST_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_BO_NA:
        return iec104.common.IoElement_M_BO_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_NA:
        return iec104.common.IoElement_M_ME_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_NB:
        return iec104.common.IoElement_M_ME_NB(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_NC:
        return iec104.common.IoElement_M_ME_NC(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_IT_NA:
        return iec104.common.IoElement_M_IT_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_PS_NA:
        return iec104.common.IoElement_M_PS_NA(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_ND:
        return iec104.common.IoElement_M_ME_ND(value=data.value)

    if asdu_type == iec104.common.AsduType.M_SP_TB:
        return iec104.common.IoElement_M_SP_TB(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_DP_TB:
        return iec104.common.IoElement_M_DP_TB(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ST_TB:
        return iec104.common.IoElement_M_ST_TB(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_BO_TB:
        return iec104.common.IoElement_M_BO_TB(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_TD:
        return iec104.common.IoElement_M_ME_TD(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_TE:
        return iec104.common.IoElement_M_ME_TE(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_ME_TF:
        return iec104.common.IoElement_M_ME_TF(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_IT_TB:
        return iec104.common.IoElement_M_IT_TB(value=data.value,
                                               quality=data.quality)

    if asdu_type == iec104.common.AsduType.M_EP_TD:
        return iec104.common.IoElement_M_EP_TD(
            value=data.value,
            quality=data.quality,
            elapsed_time=data.elapsed_time)

    if asdu_type == iec104.common.AsduType.M_EP_TE:
        return iec104.common.IoElement_M_EP_TE(
            value=data.value,
            quality=data.quality,
            duration_time=data.duration_time)

    if asdu_type == iec104.common.AsduType.M_EP_TF:
        return iec104.common.IoElement_M_EP_TF(
            value=data.value,
            quality=data.quality,
            operating_time=data.operating_time)

    raise ValueError('unsupported asdu type')


def _get_command_io_element(command, asdu_type):
    if asdu_type == iec104.common.AsduType.C_SC_NA:
        return iec104.common.IoElement_C_SC_NA(value=command.value,
                                               select=command.select,
                                               qualifier=command.qualifier)

    if asdu_type == iec104.common.AsduType.C_SC_TA:
        return iec104.common.IoElement_C_SC_TA(value=command.value,
                                               select=command.select,
                                               qualifier=command.qualifier)

    if asdu_type == iec104.common.AsduType.C_DC_NA:
        return iec104.common.IoElement_C_DC_NA(value=command.value,
                                               select=command.select,
                                               qualifier=command.qualifier)

    if asdu_type == iec104.common.AsduType.C_DC_TA:
        return iec104.common.IoElement_C_DC_TA(value=command.value,
                                               select=command.select,
                                               qualifier=command.qualifier)

    if asdu_type == iec104.common.AsduType.C_RC_NA:
        return iec104.common.IoElement_C_RC_NA(value=command.value,
                                               select=command.select,
                                               qualifier=command.qualifier)

    if asdu_type == iec104.common.AsduType.C_RC_TA:
        return iec104.common.IoElement_C_RC_TA(value=command.value,
                                               select=command.select,
                                               qualifier=command.qualifier)

    if asdu_type == iec104.common.AsduType.C_SE_NA:
        return iec104.common.IoElement_C_SE_NA(value=command.value,
                                               select=command.select)

    if asdu_type == iec104.common.AsduType.C_SE_TA:
        return iec104.common.IoElement_C_SE_TA(value=command.value,
                                               select=command.select)

    if asdu_type == iec104.common.AsduType.C_SE_NB:
        return iec104.common.IoElement_C_SE_NB(value=command.value,
                                               select=command.select)

    if asdu_type == iec104.common.AsduType.C_SE_TB:
        return iec104.common.IoElement_C_SE_TB(value=command.value,
                                               select=command.select)

    if asdu_type == iec104.common.AsduType.C_SE_NC:
        return iec104.common.IoElement_C_SE_NC(value=command.value,
                                               select=command.select)

    if asdu_type == iec104.common.AsduType.C_SE_TC:
        return iec104.common.IoElement_C_SE_TC(value=command.value,
                                               select=command.select)

    if asdu_type == iec104.common.AsduType.C_BO_NA:
        return iec104.common.IoElement_C_BO_NA(value=command.value)

    if asdu_type == iec104.common.AsduType.C_BO_TA:
        return iec104.common.IoElement_C_BO_TA(value=command.value)

    raise ValueError('unsupported asdu type')


def _get_parameter_io_element(parameter, asdu_type):
    if asdu_type == iec104.common.AsduType.P_ME_NA:
        return iec104.common.IoElement_P_ME_NA(
            value=parameter.value,
            qualifier=parameter.qualifier)

    if asdu_type == iec104.common.AsduType.P_ME_NB:
        return iec104.common.IoElement_P_ME_NB(
            value=parameter.value,
            qualifier=parameter.qualifier)

    if asdu_type == iec104.common.AsduType.P_ME_NC:
        return iec104.common.IoElement_P_ME_NC(
            value=parameter.value,
            qualifier=parameter.qualifier)

    raise ValueError('unsupported asdu type')
