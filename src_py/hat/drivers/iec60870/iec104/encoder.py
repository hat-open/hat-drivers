import contextlib
import enum
import typing

from hat.drivers.iec60870 import app
from hat.drivers.iec60870.iec104 import common


class Encoder:

    def __init__(self):
        self._encoder = app.iec104.encoder.Encoder()

    def encode(self,
               msgs: typing.List[common.Msg]
               ) -> typing.Iterable[common.Bytes]:
        for asdu in _encode_msgs(msgs):
            yield self._encoder.encode_asdu(asdu)

    def decode(self,
               data: common.Bytes
               ) -> typing.Iterable[common.Msg]:
        asdu = self._encoder.decode_asdu(data)
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

    if asdu.type in {app.iec104.common.AsduType.M_SP_NA,
                     app.iec104.common.AsduType.M_DP_NA,
                     app.iec104.common.AsduType.M_ST_NA,
                     app.iec104.common.AsduType.M_BO_NA,
                     app.iec104.common.AsduType.M_ME_NA,
                     app.iec104.common.AsduType.M_ME_NB,
                     app.iec104.common.AsduType.M_ME_NC,
                     app.iec104.common.AsduType.M_IT_NA,
                     app.iec104.common.AsduType.M_PS_NA,
                     app.iec104.common.AsduType.M_ME_ND,
                     app.iec104.common.AsduType.M_SP_TB,
                     app.iec104.common.AsduType.M_DP_TB,
                     app.iec104.common.AsduType.M_ST_TB,
                     app.iec104.common.AsduType.M_BO_TB,
                     app.iec104.common.AsduType.M_ME_TD,
                     app.iec104.common.AsduType.M_ME_TE,
                     app.iec104.common.AsduType.M_ME_TF,
                     app.iec104.common.AsduType.M_IT_TB,
                     app.iec104.common.AsduType.M_EP_TD,
                     app.iec104.common.AsduType.M_EP_TE,
                     app.iec104.common.AsduType.M_EP_TF}:
        return common.DataMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            data=_decode_data_io_element(io_element, asdu.type),
            time=io.time,
            cause=_decode_cause(asdu.cause.type.value,
                                common.DataResCause))

    elif asdu.type in {app.iec104.common.AsduType.C_SC_NA,
                       app.iec104.common.AsduType.C_DC_NA,
                       app.iec104.common.AsduType.C_RC_NA,
                       app.iec104.common.AsduType.C_SE_NA,
                       app.iec104.common.AsduType.C_SE_NB,
                       app.iec104.common.AsduType.C_SE_NC,
                       app.iec104.common.AsduType.C_BO_NA,
                       app.iec104.common.AsduType.C_SC_TA,
                       app.iec104.common.AsduType.C_DC_TA,
                       app.iec104.common.AsduType.C_RC_TA,
                       app.iec104.common.AsduType.C_SE_TA,
                       app.iec104.common.AsduType.C_SE_TB,
                       app.iec104.common.AsduType.C_SE_TC,
                       app.iec104.common.AsduType.C_BO_TA}:
        return common.CommandMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            command=_decode_command_io_element(io_element, asdu.type),
            is_negative_confirm=asdu.cause.is_negative_confirm,
            time=io.time,
            cause=_decode_cause(asdu.cause.type.value,
                                common.CommandReqCause,
                                common.CommandResCause))

    elif asdu.type == app.iec104.common.AsduType.M_EI_NA:
        return common.InitializationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            param_change=io_element.param_change,
            cause=_decode_cause(io_element.cause,
                                common.InitializationResCause))

    elif asdu.type == app.iec104.common.AsduType.C_IC_NA:
        return common.InterrogationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            request=io_element.qualifier,
            is_negative_confirm=asdu.cause.is_negative_confirm,
            cause=_decode_cause(asdu.cause.type.value,
                                common.CommandReqCause,
                                common.CommandResCause))

    elif asdu.type == app.iec104.common.AsduType.C_CI_NA:
        return common.CounterInterrogationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            request=io_element.request,
            freeze=io_element.freeze,
            is_negative_confirm=asdu.cause.is_negative_confirm,
            cause=_decode_cause(asdu.cause.type.value,
                                common.CommandReqCause,
                                common.CommandResCause))

    elif asdu.type == app.iec104.common.AsduType.C_RD_NA:
        return common.ReadMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            cause=_decode_cause(asdu.cause.type.value,
                                common.ReadReqCause,
                                common.ReadResCause))

    elif asdu.type == app.iec104.common.AsduType.C_CS_NA:
        return common.ClockSyncMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            time=io_element.time,
            cause=_decode_cause(asdu.cause.type.value,
                                common.ActivationReqCause,
                                common.ActivationResCause))

    elif asdu.type == app.iec104.common.AsduType.C_RP_NA:
        return common.ResetMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            qualifier=io_element.qualifier,
            cause=_decode_cause(asdu.cause.type.value,
                                common.ActivationReqCause,
                                common.ActivationResCause))

    elif asdu.type == app.iec104.common.AsduType.C_TS_TA:
        return common.TestMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            counter=io_element.counter,
            time=io.time,
            cause=_decode_cause(asdu.cause.type.value,
                                common.ActivationReqCause,
                                common.ActivationResCause))

    elif asdu.type in {app.iec104.common.AsduType.P_ME_NA,
                       app.iec104.common.AsduType.P_ME_NB,
                       app.iec104.common.AsduType.P_ME_NC}:
        return common.ParameterMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            parameter=_decode_parameter_io_element(io_element, asdu.type),
            cause=_decode_cause(asdu.cause.type.value,
                                common.ParameterReqCause,
                                common.ParameterResCause))

    elif asdu.type == app.iec104.common.AsduType.P_AC_NA:
        return common.ParameterActivationMsg(
            is_test=asdu.cause.is_test,
            originator_address=asdu.cause.originator_address,
            asdu_address=asdu.address,
            io_address=io_address,
            qualifier=io_element.qualifier,
            cause=_decode_cause(asdu.cause.type.value,
                                common.ParameterActivationReqCause,
                                common.ParameterActivationResCause))

    raise ValueError('unsupported asdu type')


def _decode_data_io_element(io_element, asdu_type):
    if asdu_type in {app.iec104.common.AsduType.M_SP_NA,
                     app.iec104.common.AsduType.M_SP_TB}:
        return common.SingleData(value=io_element.value,
                                 quality=io_element.quality)

    elif asdu_type in {app.iec104.common.AsduType.M_DP_NA,
                       app.iec104.common.AsduType.M_DP_TB}:
        return common.DoubleData(value=io_element.value,
                                 quality=io_element.quality)

    elif asdu_type in {app.iec104.common.AsduType.M_ST_NA,
                       app.iec104.common.AsduType.M_ST_TB}:
        return common.StepPositionData(value=io_element.value,
                                       quality=io_element.quality)

    elif asdu_type in {app.iec104.common.AsduType.M_BO_NA,
                       app.iec104.common.AsduType.M_BO_TB}:
        return common.BitstringData(value=io_element.value,
                                    quality=io_element.quality)

    elif asdu_type in {app.iec104.common.AsduType.M_ME_NA,
                       app.iec104.common.AsduType.M_ME_ND,
                       app.iec104.common.AsduType.M_ME_TD}:
        quality = (None if asdu_type == app.iec104.common.AsduType.M_ME_ND
                   else io_element.quality)
        return common.NormalizedData(value=io_element.value,
                                     quality=quality)

    elif asdu_type in {app.iec104.common.AsduType.M_ME_NB,
                       app.iec104.common.AsduType.M_ME_TE}:
        return common.ScaledData(value=io_element.value,
                                 quality=io_element.quality)

    elif asdu_type in {app.iec104.common.AsduType.M_ME_NC,
                       app.iec104.common.AsduType.M_ME_TF}:
        return common.FloatingData(value=io_element.value,
                                   quality=io_element.quality)

    elif asdu_type in {app.iec104.common.AsduType.M_IT_NA,
                       app.iec104.common.AsduType.M_IT_TB}:
        return common.BinaryCounterData(value=io_element.value,
                                        quality=io_element.quality)

    elif asdu_type == app.iec104.common.AsduType.M_EP_TD:
        return common.ProtectionData(
            value=io_element.value,
            quality=io_element.quality,
            elapsed_time=io_element.elapsed_time)

    elif asdu_type == app.iec104.common.AsduType.M_EP_TE:
        return common.ProtectionStartData(
            value=io_element.value,
            quality=io_element.quality,
            duration_time=io_element.duration_time)

    elif asdu_type == app.iec104.common.AsduType.M_EP_TF:
        return common.ProtectionCommandData(
            value=io_element.value,
            quality=io_element.quality,
            operating_time=io_element.operating_time)

    elif asdu_type == app.iec104.common.AsduType.M_PS_NA:
        return common.StatusData(value=io_element.value,
                                 quality=io_element.quality)

    raise ValueError('unsupported asdu type')


def _decode_command_io_element(io_element, asdu_type):
    if asdu_type in {app.iec104.common.AsduType.C_SC_NA,
                     app.iec104.common.AsduType.C_SC_TA}:
        return common.SingleCommand(value=io_element.value,
                                    select=io_element.select,
                                    qualifier=io_element.qualifier)

    elif asdu_type in {app.iec104.common.AsduType.C_DC_NA,
                       app.iec104.common.AsduType.C_DC_TA}:
        return common.DoubleCommand(value=io_element.value,
                                    select=io_element.select,
                                    qualifier=io_element.qualifier)

    elif asdu_type in {app.iec104.common.AsduType.C_RC_NA,
                       app.iec104.common.AsduType.C_RC_TA}:
        return common.RegulatingCommand(value=io_element.value,
                                        select=io_element.select,
                                        qualifier=io_element.qualifier)

    elif asdu_type in {app.iec104.common.AsduType.C_SE_NA,
                       app.iec104.common.AsduType.C_SE_TA}:
        return common.NormalizedCommand(value=io_element.value,
                                        select=io_element.select)

    elif asdu_type in {app.iec104.common.AsduType.C_SE_NB,
                       app.iec104.common.AsduType.C_SE_TB}:
        return common.ScaledCommand(value=io_element.value,
                                    select=io_element.select)

    elif asdu_type in {app.iec104.common.AsduType.C_SE_NC,
                       app.iec104.common.AsduType.C_SE_TC}:
        return common.FloatingCommand(value=io_element.value,
                                      select=io_element.select)

    elif asdu_type in {app.iec104.common.AsduType.C_BO_NA,
                       app.iec104.common.AsduType.C_BO_TA}:
        return common.BitstringCommand(value=io_element.value)

    raise ValueError('unsupported asdu type')


def _decode_parameter_io_element(io_element, asdu_type):
    if asdu_type == app.iec104.common.AsduType.P_ME_NA:
        return common.NormalizedParameter(value=io_element.value,
                                          qualifier=io_element.qualifier)

    elif asdu_type == app.iec104.common.AsduType.P_ME_NB:
        return common.ScaledParameter(value=io_element.value,
                                      qualifier=io_element.qualifier)

    elif asdu_type == app.iec104.common.AsduType.P_ME_NC:
        return common.FloatingParameter(value=io_element.value,
                                        qualifier=io_element.qualifier)

    raise ValueError('unsupported asdu type')


def _decode_cause(value, *cause_classes):
    for cause_class in cause_classes:
        with contextlib.suppress(ValueError):
            return cause_class(value)
    return value


def _encode_msg(msg):
    # TODO: group messages and io elements

    is_negative_confirm = False
    io_address = 0
    time = None

    if isinstance(msg, common.DataMsg):
        asdu_type = _get_data_asdu_type(msg.data, msg.time)
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_address = msg.io_address
        io_element = _get_data_io_element(msg.data, asdu_type)
        time = msg.time

    elif isinstance(msg, common.CommandMsg):
        asdu_type = _get_command_asdu_type(msg.command, msg.time)
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_address = msg.io_address
        io_element = _get_command_io_element(msg.command, asdu_type)
        time = msg.time

    elif isinstance(msg, common.InitializationMsg):
        asdu_type = app.iec104.common.AsduType.M_EI_NA
        cause_type = app.iec104.common.CauseType.INITIALIZED
        io_element = app.iec104.common.IoElement_M_EI_NA(
            param_change=msg.param_change,
            cause=(msg.cause.value if isinstance(msg.cause, enum.Enum)
                   else msg.cause))

    elif isinstance(msg, common.InterrogationMsg):
        asdu_type = app.iec104.common.AsduType.C_IC_NA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_element = app.iec104.common.IoElement_C_IC_NA(
            qualifier=msg.request)

    elif isinstance(msg, common.CounterInterrogationMsg):
        asdu_type = app.iec104.common.AsduType.C_CI_NA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        is_negative_confirm = msg.is_negative_confirm
        io_element = app.iec104.common.IoElement_C_CI_NA(
            request=msg.request,
            freeze=msg.freeze)

    elif isinstance(msg, common.ReadMsg):
        asdu_type = app.iec104.common.AsduType.C_RD_NA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_address = msg.io_address
        io_element = app.iec104.common.IoElement_C_RD_NA()

    elif isinstance(msg, common.ClockSyncMsg):
        asdu_type = app.iec104.common.AsduType.C_CS_NA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_element = app.iec104.common.IoElement_C_CS_NA(
            time=msg.time)

    elif isinstance(msg, common.TestMsg):
        asdu_type = app.iec104.common.AsduType.C_TS_TA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_element = app.iec104.common.IoElement_C_TS_TA(
            counter=msg.counter)
        time = msg.time

    elif isinstance(msg, common.ResetMsg):
        asdu_type = app.iec104.common.AsduType.C_RP_NA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_element = app.iec104.common.IoElement_C_RP_NA(
            qualifier=msg.qualifier)

    elif isinstance(msg, common.ParameterMsg):
        asdu_type = _get_parameter_asdu_type(msg.parameter)
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_address = msg.io_address
        io_element = _get_parameter_io_element(msg.parameter, asdu_type)

    elif isinstance(msg, common.ParameterActivationMsg):
        asdu_type = app.iec104.common.AsduType.P_AC_NA
        cause_type = app.iec104.common.CauseType(
            msg.cause.value if isinstance(msg.cause, enum.Enum)
            else msg.cause)
        io_address = msg.io_address
        io_element = app.iec104.common.IoElement_P_AC_NA(
            qualifier=msg.qualifier)

    else:
        raise ValueError('unsupported message')

    cause = app.iec104.common.Cause(type=cause_type,
                                    is_negative_confirm=is_negative_confirm,
                                    is_test=msg.is_test,
                                    originator_address=msg.originator_address)

    io = app.iec104.common.IO(address=io_address,
                              elements=[io_element],
                              time=time)

    asdu = app.iec104.common.ASDU(type=asdu_type,
                                  cause=cause,
                                  address=msg.asdu_address,
                                  ios=[io])

    return asdu


def _get_data_asdu_type(data, time):
    if isinstance(data, common.SingleData):
        if time is None:
            return app.iec104.common.AsduType.M_SP_NA

        else:
            return app.iec104.common.AsduType.M_SP_TB

    elif isinstance(data, common.DoubleData):
        if time is None:
            return app.iec104.common.AsduType.M_DP_NA

        else:
            return app.iec104.common.AsduType.M_DP_TB

    elif isinstance(data, common.StepPositionData):
        if time is None:
            return app.iec104.common.AsduType.M_ST_NA

        else:
            return app.iec104.common.AsduType.M_ST_TB

    elif isinstance(data, common.BitstringData):
        if time is None:
            return app.iec104.common.AsduType.M_BO_NA

        else:
            return app.iec104.common.AsduType.M_BO_TB

    elif isinstance(data, common.NormalizedData):
        if time is None:
            if data.quality is not None:
                return app.iec104.common.AsduType.M_ME_NA

            else:
                return app.iec104.common.AsduType.M_ME_ND

        else:
            if data.quality is not None:
                return app.iec104.common.AsduType.M_ME_TD

    elif isinstance(data, common.ScaledData):
        if time is None:
            return app.iec104.common.AsduType.M_ME_NB

        else:
            return app.iec104.common.AsduType.M_ME_TE

    elif isinstance(data, common.FloatingData):
        if time is None:
            return app.iec104.common.AsduType.M_ME_NC

        else:
            return app.iec104.common.AsduType.M_ME_TF

    elif isinstance(data, common.BinaryCounterData):
        if time is None:
            return app.iec104.common.AsduType.M_IT_NA

        else:
            return app.iec104.common.AsduType.M_IT_TB

    elif isinstance(data, common.ProtectionData):
        if time is not None:
            return app.iec104.common.AsduType.M_EP_TD

    elif isinstance(data, common.ProtectionStartData):
        if time is not None:
            return app.iec104.common.AsduType.M_EP_TE

    elif isinstance(data, common.ProtectionCommandData):
        if time is not None:
            return app.iec104.common.AsduType.M_EP_TF

    elif isinstance(data, common.StatusData):
        if time is None:
            return app.iec104.common.AsduType.M_PS_NA

    raise ValueError('unsupported data')


def _get_command_asdu_type(command, time):
    if isinstance(command, common.SingleCommand):
        if time is None:
            return app.iec104.common.AsduType.C_SC_NA

        else:
            return app.iec104.common.AsduType.C_SC_TA

    elif isinstance(command, common.DoubleCommand):
        if time is None:
            return app.iec104.common.AsduType.C_DC_NA

        else:
            return app.iec104.common.AsduType.C_DC_TA

    elif isinstance(command, common.RegulatingCommand):
        if time is None:
            return app.iec104.common.AsduType.C_RC_NA

        else:
            return app.iec104.common.AsduType.C_RC_TA

    elif isinstance(command, common.NormalizedCommand):
        if time is None:
            return app.iec104.common.AsduType.C_SE_NA

        else:
            return app.iec104.common.AsduType.C_SE_TA

    elif isinstance(command, common.ScaledCommand):
        if time is None:
            return app.iec104.common.AsduType.C_SE_NB

        else:
            return app.iec104.common.AsduType.C_SE_TB

    elif isinstance(command, common.FloatingCommand):
        if time is None:
            return app.iec104.common.AsduType.C_SE_NC

        else:
            return app.iec104.common.AsduType.C_SE_TC

    elif isinstance(command, common.BitstringCommand):
        if time is None:
            return app.iec104.common.AsduType.C_BO_NA

        else:
            return app.iec104.common.AsduType.C_BO_TA

    raise ValueError('unsupported command')


def _get_parameter_asdu_type(parameter):
    if isinstance(parameter, common.NormalizedParameter):
        return app.iec104.common.AsduType.P_ME_NA

    elif isinstance(parameter, common.ScaledParameter):
        return app.iec104.common.AsduType.P_ME_NB

    elif isinstance(parameter, common.FloatingParameter):
        return app.iec104.common.AsduType.P_ME_NC

    raise ValueError('unsupported parameter')


def _get_data_io_element(data, asdu_type):
    if asdu_type == app.iec104.common.AsduType.M_SP_NA:
        return app.iec104.common.IoElement_M_SP_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_DP_NA:
        return app.iec104.common.IoElement_M_DP_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ST_NA:
        return app.iec104.common.IoElement_M_ST_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_BO_NA:
        return app.iec104.common.IoElement_M_BO_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_NA:
        return app.iec104.common.IoElement_M_ME_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_NB:
        return app.iec104.common.IoElement_M_ME_NB(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_NC:
        return app.iec104.common.IoElement_M_ME_NC(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_IT_NA:
        return app.iec104.common.IoElement_M_IT_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_PS_NA:
        return app.iec104.common.IoElement_M_PS_NA(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_ND:
        return app.iec104.common.IoElement_M_ME_ND(value=data.value)

    if asdu_type == app.iec104.common.AsduType.M_SP_TB:
        return app.iec104.common.IoElement_M_SP_TB(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_DP_TB:
        return app.iec104.common.IoElement_M_DP_TB(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ST_TB:
        return app.iec104.common.IoElement_M_ST_TB(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_BO_TB:
        return app.iec104.common.IoElement_M_BO_TB(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_TD:
        return app.iec104.common.IoElement_M_ME_TD(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_TE:
        return app.iec104.common.IoElement_M_ME_TE(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_ME_TF:
        return app.iec104.common.IoElement_M_ME_TF(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_IT_TB:
        return app.iec104.common.IoElement_M_IT_TB(value=data.value,
                                                   quality=data.quality)

    if asdu_type == app.iec104.common.AsduType.M_EP_TD:
        return app.iec104.common.IoElement_M_EP_TD(
            value=data.value,
            quality=data.quality,
            elapsed_time=data.elapsed_time)

    if asdu_type == app.iec104.common.AsduType.M_EP_TE:
        return app.iec104.common.IoElement_M_EP_TE(
            value=data.value,
            quality=data.quality,
            duration_time=data.duration_time)

    if asdu_type == app.iec104.common.AsduType.M_EP_TF:
        return app.iec104.common.IoElement_M_EP_TF(
            value=data.value,
            quality=data.quality,
            operating_time=data.operating_time)

    raise ValueError('unsupported asdu type')


def _get_command_io_element(command, asdu_type):
    if asdu_type == app.iec104.common.AsduType.C_SC_NA:
        return app.iec104.common.IoElement_C_SC_NA(value=command.value,
                                                   select=command.select,
                                                   qualifier=command.qualifier)

    if asdu_type == app.iec104.common.AsduType.C_SC_TA:
        return app.iec104.common.IoElement_C_SC_TA(value=command.value,
                                                   select=command.select,
                                                   qualifier=command.qualifier)

    if asdu_type == app.iec104.common.AsduType.C_DC_NA:
        return app.iec104.common.IoElement_C_DC_NA(value=command.value,
                                                   select=command.select,
                                                   qualifier=command.qualifier)

    if asdu_type == app.iec104.common.AsduType.C_DC_TA:
        return app.iec104.common.IoElement_C_DC_TA(value=command.value,
                                                   select=command.select,
                                                   qualifier=command.qualifier)

    if asdu_type == app.iec104.common.AsduType.C_RC_NA:
        return app.iec104.common.IoElement_C_RC_NA(value=command.value,
                                                   select=command.select,
                                                   qualifier=command.qualifier)

    if asdu_type == app.iec104.common.AsduType.C_RC_TA:
        return app.iec104.common.IoElement_C_RC_TA(value=command.value,
                                                   select=command.select,
                                                   qualifier=command.qualifier)

    if asdu_type == app.iec104.common.AsduType.C_SE_NA:
        return app.iec104.common.IoElement_C_SE_NA(value=command.value,
                                                   select=command.select)

    if asdu_type == app.iec104.common.AsduType.C_SE_TA:
        return app.iec104.common.IoElement_C_SE_TA(value=command.value,
                                                   select=command.select)

    if asdu_type == app.iec104.common.AsduType.C_SE_NB:
        return app.iec104.common.IoElement_C_SE_NB(value=command.value,
                                                   select=command.select)

    if asdu_type == app.iec104.common.AsduType.C_SE_TB:
        return app.iec104.common.IoElement_C_SE_TB(value=command.value,
                                                   select=command.select)

    if asdu_type == app.iec104.common.AsduType.C_SE_NC:
        return app.iec104.common.IoElement_C_SE_NC(value=command.value,
                                                   select=command.select)

    if asdu_type == app.iec104.common.AsduType.C_SE_TC:
        return app.iec104.common.IoElement_C_SE_TC(value=command.value,
                                                   select=command.select)

    if asdu_type == app.iec104.common.AsduType.C_BO_NA:
        return app.iec104.common.IoElement_C_BO_NA(value=command.value)

    if asdu_type == app.iec104.common.AsduType.C_BO_TA:
        return app.iec104.common.IoElement_C_BO_TA(value=command.value)

    raise ValueError('unsupported asdu type')


def _get_parameter_io_element(parameter, asdu_type):
    if asdu_type == app.iec104.common.AsduType.P_ME_NA:
        return app.iec104.common.IoElement_P_ME_NA(
            value=parameter.value,
            qualifier=parameter.qualifier)

    if asdu_type == app.iec104.common.AsduType.P_ME_NB:
        return app.iec104.common.IoElement_P_ME_NB(
            value=parameter.value,
            qualifier=parameter.qualifier)

    if asdu_type == app.iec104.common.AsduType.P_ME_NC:
        return app.iec104.common.IoElement_P_ME_NC(
            value=parameter.value,
            qualifier=parameter.qualifier)

    raise ValueError('unsupported asdu type')
