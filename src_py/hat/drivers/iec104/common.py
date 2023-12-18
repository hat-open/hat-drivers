import abc
import enum
import typing

from hat import aio
from hat import util

from hat.drivers import iec101
from hat.drivers import tcp
from hat.drivers.iec60870 import apci


AsduTypeError: typing.TypeAlias = iec101.AsduTypeError


TimeSize: typing.TypeAlias = iec101.TimeSize
Time: typing.TypeAlias = iec101.Time

OriginatorAddress: typing.TypeAlias = iec101.OriginatorAddress
"""Originator address in range [0, 255] - 0 if not available"""
AsduAddress: typing.TypeAlias = iec101.AsduAddress
"""ASDU address in range [0, 65535]"""
IoAddress: typing.TypeAlias = iec101.IoAddress
"""IO address in range [0, 16777215]"""

IndicationQuality: typing.TypeAlias = iec101.IndicationQuality
MeasurementQuality: typing.TypeAlias = iec101.MeasurementQuality
CounterQuality: typing.TypeAlias = iec101.CounterQuality
ProtectionQuality: typing.TypeAlias = iec101.ProtectionQuality
Quality: typing.TypeAlias = iec101.Quality

FreezeCode: typing.TypeAlias = iec101.FreezeCode

SingleValue: typing.TypeAlias = iec101.SingleValue
DoubleValue: typing.TypeAlias = iec101.DoubleValue
RegulatingValue: typing.TypeAlias = iec101.RegulatingValue
StepPositionValue: typing.TypeAlias = iec101.StepPositionValue
BitstringValue: typing.TypeAlias = iec101.BitstringValue
NormalizedValue: typing.TypeAlias = iec101.NormalizedValue
ScaledValue: typing.TypeAlias = iec101.ScaledValue
FloatingValue: typing.TypeAlias = iec101.FloatingValue
BinaryCounterValue: typing.TypeAlias = iec101.BinaryCounterValue
ProtectionValue: typing.TypeAlias = iec101.ProtectionValue
ProtectionStartValue: typing.TypeAlias = iec101.ProtectionStartValue
ProtectionCommandValue: typing.TypeAlias = iec101.ProtectionCommandValue
StatusValue: typing.TypeAlias = iec101.StatusValue

OtherCause: typing.TypeAlias = int
"""Other cause in range [0, 63]"""

DataResCause: typing.TypeAlias = iec101.DataResCause
DataCause: typing.TypeAlias = iec101.DataCause

CommandReqCause: typing.TypeAlias = iec101.CommandReqCause
CommandResCause: typing.TypeAlias = iec101.CommandResCause
CommandCause: typing.TypeAlias = iec101.CommandCause

InitializationResCause: typing.TypeAlias = iec101.InitializationResCause
InitializationCause: typing.TypeAlias = iec101.InitializationCause

ReadReqCause: typing.TypeAlias = iec101.ReadReqCause
ReadResCause: typing.TypeAlias = iec101.ReadResCause
ReadCause: typing.TypeAlias = iec101.ReadCause

ClockSyncReqCause: typing.TypeAlias = iec101.ClockSyncReqCause
ClockSyncResCause: typing.TypeAlias = iec101.ClockSyncResCause
ClockSyncCause: typing.TypeAlias = iec101.ClockSyncCause

ActivationReqCause: typing.TypeAlias = iec101.ActivationReqCause
ActivationResCause: typing.TypeAlias = iec101.ActivationResCause
ActivationCause: typing.TypeAlias = iec101.ActivationCause

DelayReqCause: typing.TypeAlias = iec101.DelayReqCause
DelayResCause: typing.TypeAlias = iec101.DelayResCause
DelayCause: typing.TypeAlias = iec101.DelayCause

ParameterReqCause: typing.TypeAlias = iec101.ParameterReqCause
ParameterResCause: typing.TypeAlias = iec101.ParameterResCause
ParameterCause: typing.TypeAlias = iec101.ParameterCause

ParameterActivationReqCause: typing.TypeAlias = iec101.ParameterActivationReqCause  # NOQA
ParameterActivationResCause: typing.TypeAlias = iec101.ParameterActivationResCause  # NOQA
ParameterActivationCause: typing.TypeAlias = iec101.ParameterActivationCause

SingleData: typing.TypeAlias = iec101.SingleData
DoubleData: typing.TypeAlias = iec101.DoubleData
StepPositionData: typing.TypeAlias = iec101.StepPositionData
BitstringData: typing.TypeAlias = iec101.BitstringData
NormalizedData: typing.TypeAlias = iec101.NormalizedData
ScaledData: typing.TypeAlias = iec101.ScaledData
FloatingData: typing.TypeAlias = iec101.FloatingData
BinaryCounterData: typing.TypeAlias = iec101.BinaryCounterData
ProtectionData: typing.TypeAlias = iec101.ProtectionData
ProtectionStartData: typing.TypeAlias = iec101.ProtectionStartData
ProtectionCommandData: typing.TypeAlias = iec101.ProtectionCommandData
StatusData: typing.TypeAlias = iec101.StatusData
Data: typing.TypeAlias = iec101.Data

SingleCommand: typing.TypeAlias = iec101.SingleCommand
DoubleCommand: typing.TypeAlias = iec101.DoubleCommand
RegulatingCommand: typing.TypeAlias = iec101.RegulatingCommand
NormalizedCommand: typing.TypeAlias = iec101.NormalizedCommand
ScaledCommand: typing.TypeAlias = iec101.ScaledCommand
FloatingCommand: typing.TypeAlias = iec101.FloatingCommand
BitstringCommand: typing.TypeAlias = iec101.BitstringCommand
Command: typing.TypeAlias = iec101.Command

NormalizedParameter: typing.TypeAlias = iec101.NormalizedParameter
ScaledParameter: typing.TypeAlias = iec101.ScaledParameter
FloatingParameter: typing.TypeAlias = iec101.FloatingParameter
Parameter: typing.TypeAlias = iec101.Parameter

DataMsg: typing.TypeAlias = iec101.DataMsg
InitializationMsg: typing.TypeAlias = iec101.InitializationMsg
InterrogationMsg: typing.TypeAlias = iec101.InterrogationMsg
CounterInterrogationMsg: typing.TypeAlias = iec101.CounterInterrogationMsg
ReadMsg: typing.TypeAlias = iec101.ReadMsg
ClockSyncMsg: typing.TypeAlias = iec101.ClockSyncMsg
ResetMsg: typing.TypeAlias = iec101.ResetMsg
ParameterMsg: typing.TypeAlias = iec101.ParameterMsg
ParameterActivationMsg: typing.TypeAlias = iec101.ParameterActivationMsg


class CommandMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    command: Command
    is_negative_confirm: bool
    time: Time | None
    cause: CommandCause


class TestMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    counter: int
    """counter in range [0, 65535]"""
    time: Time
    cause: ActivationCause


Msg: typing.TypeAlias = (DataMsg |
                         CommandMsg |
                         InitializationMsg |
                         InterrogationMsg |
                         CounterInterrogationMsg |
                         ReadMsg |
                         ClockSyncMsg |
                         TestMsg |
                         ResetMsg |
                         ParameterMsg |
                         ParameterActivationMsg)


time_from_datetime = iec101.time_from_datetime
time_to_datetime = iec101.time_to_datetime


class Connection(aio.Resource):

    @property
    @abc.abstractmethod
    def conn(self) -> apci.Connection:
        pass

    @property
    def async_group(self) -> aio.Group:
        return self.conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        return self.conn.info

    @property
    def is_enabled(self) -> bool:
        return self.conn.is_enabled

    def register_enabled_cb(self,
                            cb: typing.Callable[[bool], None]
                            ) -> util.RegisterCallbackHandle:
        return self.conn.register_enabled_cb(cb)

    @abc.abstractmethod
    async def send(self, msgs: list[Msg], wait_ack: bool = False):
        pass

    @abc.abstractmethod
    async def drain(self, wait_ack: bool = False):
        pass

    @abc.abstractmethod
    async def receive(self) -> list[Msg]:
        pass


class Function(enum.Enum):
    DATA = 'data'
    COMMAND = 'command'
    INITIALIZATION = 'initialization'
    INTERROGATION = 'interrogation'
    COUNTER_INTERROGATION = 'counter_interrogation'
    READ = 'read'
    CLOCK_SYNC = 'clock_sync'
    TEST = 'test'
    RESET = 'reset'
    PARAMETER = 'parameter'
    PARAMETER_ACTIVATION = 'parameter_activation'
