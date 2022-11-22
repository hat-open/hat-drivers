import typing

from hat.drivers import iec101


Bytes = iec101.Bytes
TimeSize = iec101.TimeSize
Time = iec101.Time

OriginatorAddress = iec101.OriginatorAddress
"""Originator address in range [0, 255] - 0 if not available"""
AsduAddress = iec101.AsduAddress
"""ASDU address in range [0, 65535]"""
IoAddress = iec101.IoAddress
"""IO address in range [0, 16777215]"""

IndicationQuality = iec101.IndicationQuality
MeasurementQuality = iec101.MeasurementQuality
CounterQuality = iec101.CounterQuality
ProtectionQuality = iec101.ProtectionQuality
Quality = iec101.Quality

FreezeCode = iec101.FreezeCode

SingleValue = iec101.SingleValue
DoubleValue = iec101.DoubleValue
RegulatingValue = iec101.RegulatingValue
StepPositionValue = iec101.StepPositionValue
BitstringValue = iec101.BitstringValue
NormalizedValue = iec101.NormalizedValue
ScaledValue = iec101.ScaledValue
FloatingValue = iec101.FloatingValue
BinaryCounterValue = iec101.BinaryCounterValue
ProtectionValue = iec101.ProtectionValue
ProtectionStartValue = iec101.ProtectionStartValue
ProtectionCommandValue = iec101.ProtectionCommandValue
StatusValue = iec101.StatusValue

OtherCause = int
"""Other cause in range [0, 63]"""

DataResCause = iec101.DataResCause
DataCause = iec101.DataCause

CommandReqCause = iec101.CommandReqCause
CommandResCause = iec101.CommandResCause
CommandCause = iec101.CommandCause

InitializationResCause = iec101.InitializationResCause
InitializationCause = iec101.InitializationCause

ReadReqCause = iec101.ReadReqCause
ReadResCause = iec101.ReadResCause
ReadCause = iec101.ReadCause

ClockSyncReqCause = iec101.ClockSyncReqCause
ClockSyncResCause = iec101.ClockSyncResCause
ClockSyncCause = iec101.ClockSyncCause

ActivationReqCause = iec101.ActivationReqCause
ActivationResCause = iec101.ActivationResCause
ActivationCause = iec101.ActivationCause

DelayReqCause = iec101.DelayReqCause
DelayResCause = iec101.DelayResCause
DelayCause = iec101.DelayCause

ParameterReqCause = iec101.ParameterReqCause
ParameterResCause = iec101.ParameterResCause
ParameterCause = iec101.ParameterCause

ParameterActivationReqCause = iec101.ParameterActivationReqCause
ParameterActivationResCause = iec101.ParameterActivationResCause
ParameterActivationCause = iec101.ParameterActivationCause

SingleData = iec101.SingleData
DoubleData = iec101.DoubleData
StepPositionData = iec101.StepPositionData
BitstringData = iec101.BitstringData
NormalizedData = iec101.NormalizedData
ScaledData = iec101.ScaledData
FloatingData = iec101.FloatingData
BinaryCounterData = iec101.BinaryCounterData
ProtectionData = iec101.ProtectionData
ProtectionStartData = iec101.ProtectionStartData
ProtectionCommandData = iec101.ProtectionCommandData
StatusData = iec101.StatusData
Data = iec101.Data

SingleCommand = iec101.SingleCommand
DoubleCommand = iec101.DoubleCommand
RegulatingCommand = iec101.RegulatingCommand
NormalizedCommand = iec101.NormalizedCommand
ScaledCommand = iec101.ScaledCommand
FloatingCommand = iec101.FloatingCommand
BitstringCommand = iec101.BitstringCommand
Command = iec101.Command

NormalizedParameter = iec101.NormalizedParameter
ScaledParameter = iec101.ScaledParameter
FloatingParameter = iec101.FloatingParameter
Parameter = iec101.Parameter

DataMsg = iec101.DataMsg
InitializationMsg = iec101.InitializationMsg
InterrogationMsg = iec101.InterrogationMsg
CounterInterrogationMsg = iec101.CounterInterrogationMsg
ReadMsg = iec101.ReadMsg
ClockSyncMsg = iec101.ClockSyncMsg
ResetMsg = iec101.ResetMsg
ParameterMsg = iec101.ParameterMsg
ParameterActivationMsg = iec101.ParameterActivationMsg


class CommandMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    command: Command
    is_negative_confirm: bool
    time: typing.Optional[Time]
    cause: CommandCause


class TestMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    counter: int
    """counter in range [0, 65535]"""
    time: Time
    cause: ActivationCause


Msg = typing.Union[DataMsg,
                   CommandMsg,
                   InitializationMsg,
                   InterrogationMsg,
                   CounterInterrogationMsg,
                   ReadMsg,
                   ClockSyncMsg,
                   TestMsg,
                   ResetMsg,
                   ParameterMsg,
                   ParameterActivationMsg]


time_from_datetime = iec101.time_from_datetime
time_to_datetime = iec101.time_to_datetime
