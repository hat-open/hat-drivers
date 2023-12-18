import enum
import typing

from hat.drivers.iec60870 import link
from hat.drivers.iec60870.encodings import iec101


AsduTypeError: typing.TypeAlias = iec101.AsduTypeError

Address: typing.TypeAlias = link.Address
AddressSize: typing.TypeAlias = link.AddressSize

CauseSize: typing.TypeAlias = iec101.CauseSize
AsduAddressSize: typing.TypeAlias = iec101.AsduAddressSize
IoAddressSize: typing.TypeAlias = iec101.IoAddressSize
TimeSize: typing.TypeAlias = iec101.TimeSize
Time: typing.TypeAlias = iec101.Time

OriginatorAddress: typing.TypeAlias = iec101.OriginatorAddress
AsduAddress: typing.TypeAlias = iec101.AsduAddress
IoAddress: typing.TypeAlias = iec101.IoAddress

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


class DataResCause(enum.Enum):
    PERIODIC = iec101.CauseType.PERIODIC.value
    BACKGROUND_SCAN = iec101.CauseType.BACKGROUND_SCAN.value
    SPONTANEOUS = iec101.CauseType.SPONTANEOUS.value
    REQUEST = iec101.CauseType.REQUEST.value
    REMOTE_COMMAND = iec101.CauseType.REMOTE_COMMAND.value
    LOCAL_COMMAND = iec101.CauseType.LOCAL_COMMAND.value
    INTERROGATED_STATION = iec101.CauseType.INTERROGATED_STATION.value
    INTERROGATED_GROUP01 = iec101.CauseType.INTERROGATED_GROUP01.value
    INTERROGATED_GROUP02 = iec101.CauseType.INTERROGATED_GROUP02.value
    INTERROGATED_GROUP03 = iec101.CauseType.INTERROGATED_GROUP03.value
    INTERROGATED_GROUP04 = iec101.CauseType.INTERROGATED_GROUP04.value
    INTERROGATED_GROUP05 = iec101.CauseType.INTERROGATED_GROUP05.value
    INTERROGATED_GROUP06 = iec101.CauseType.INTERROGATED_GROUP06.value
    INTERROGATED_GROUP07 = iec101.CauseType.INTERROGATED_GROUP07.value
    INTERROGATED_GROUP08 = iec101.CauseType.INTERROGATED_GROUP08.value
    INTERROGATED_GROUP09 = iec101.CauseType.INTERROGATED_GROUP09.value
    INTERROGATED_GROUP10 = iec101.CauseType.INTERROGATED_GROUP10.value
    INTERROGATED_GROUP11 = iec101.CauseType.INTERROGATED_GROUP11.value
    INTERROGATED_GROUP12 = iec101.CauseType.INTERROGATED_GROUP12.value
    INTERROGATED_GROUP13 = iec101.CauseType.INTERROGATED_GROUP13.value
    INTERROGATED_GROUP14 = iec101.CauseType.INTERROGATED_GROUP14.value
    INTERROGATED_GROUP15 = iec101.CauseType.INTERROGATED_GROUP15.value
    INTERROGATED_GROUP16 = iec101.CauseType.INTERROGATED_GROUP16.value
    INTERROGATED_COUNTER = iec101.CauseType.INTERROGATED_COUNTER.value
    INTERROGATED_COUNTER01 = iec101.CauseType.INTERROGATED_COUNTER01.value
    INTERROGATED_COUNTER02 = iec101.CauseType.INTERROGATED_COUNTER02.value
    INTERROGATED_COUNTER03 = iec101.CauseType.INTERROGATED_COUNTER03.value
    INTERROGATED_COUNTER04 = iec101.CauseType.INTERROGATED_COUNTER04.value


DataCause: typing.TypeAlias = DataResCause | OtherCause


class CommandReqCause(enum.Enum):
    ACTIVATION = iec101.CauseType.ACTIVATION.value
    DEACTIVATION = iec101.CauseType.DEACTIVATION.value


class CommandResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.CauseType.ACTIVATION_CONFIRMATION.value
    DEACTIVATION_CONFIRMATION = iec101.CauseType.DEACTIVATION_CONFIRMATION.value  # NOQA
    ACTIVATION_TERMINATION = iec101.CauseType.ACTIVATION_TERMINATION.value
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


CommandCause: typing.TypeAlias = CommandReqCause | CommandResCause | OtherCause


class InitializationResCause(enum.Enum):
    LOCAL_POWER = 0
    LOCAL_RESET = 1
    REMOTE_RESET = 2


InitializationCause: typing.TypeAlias = InitializationResCause | OtherCause


class ReadReqCause(enum.Enum):
    REQUEST = iec101.CauseType.REQUEST.value


class ReadResCause(enum.Enum):
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


ReadCause: typing.TypeAlias = ReadReqCause | ReadResCause | OtherCause


class ClockSyncReqCause(enum.Enum):
    ACTIVATION = iec101.CauseType.ACTIVATION.value


class ClockSyncResCause(enum.Enum):
    SPONTANEOUS = iec101.CauseType.SPONTANEOUS.value
    ACTIVATION_CONFIRMATION = iec101.CauseType.ACTIVATION_CONFIRMATION.value
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


ClockSyncCause: typing.TypeAlias = (ClockSyncReqCause |
                                    ClockSyncResCause |
                                    OtherCause)


class ActivationReqCause(enum.Enum):
    ACTIVATION = iec101.CauseType.ACTIVATION.value


class ActivationResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.CauseType.ACTIVATION_CONFIRMATION.value
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


ActivationCause: typing.TypeAlias = (ActivationReqCause |
                                     ActivationResCause |
                                     OtherCause)


class DelayReqCause(enum.Enum):
    SPONTANEOUS = iec101.CauseType.SPONTANEOUS.value
    ACTIVATION = iec101.CauseType.ACTIVATION.value


class DelayResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.CauseType.ACTIVATION_CONFIRMATION.value
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


DelayCause: typing.TypeAlias = DelayReqCause | DelayResCause | OtherCause


class ParameterReqCause(enum.Enum):
    SPONTANEOUS = iec101.CauseType.SPONTANEOUS.value
    ACTIVATION = iec101.CauseType.ACTIVATION.value


class ParameterResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.CauseType.ACTIVATION_CONFIRMATION.value
    INTERROGATED_STATION = iec101.CauseType.INTERROGATED_STATION.value
    INTERROGATED_GROUP01 = iec101.CauseType.INTERROGATED_GROUP01.value
    INTERROGATED_GROUP02 = iec101.CauseType.INTERROGATED_GROUP02.value
    INTERROGATED_GROUP03 = iec101.CauseType.INTERROGATED_GROUP03.value
    INTERROGATED_GROUP04 = iec101.CauseType.INTERROGATED_GROUP04.value
    INTERROGATED_GROUP05 = iec101.CauseType.INTERROGATED_GROUP05.value
    INTERROGATED_GROUP06 = iec101.CauseType.INTERROGATED_GROUP06.value
    INTERROGATED_GROUP07 = iec101.CauseType.INTERROGATED_GROUP07.value
    INTERROGATED_GROUP08 = iec101.CauseType.INTERROGATED_GROUP08.value
    INTERROGATED_GROUP09 = iec101.CauseType.INTERROGATED_GROUP09.value
    INTERROGATED_GROUP10 = iec101.CauseType.INTERROGATED_GROUP10.value
    INTERROGATED_GROUP11 = iec101.CauseType.INTERROGATED_GROUP11.value
    INTERROGATED_GROUP12 = iec101.CauseType.INTERROGATED_GROUP12.value
    INTERROGATED_GROUP13 = iec101.CauseType.INTERROGATED_GROUP13.value
    INTERROGATED_GROUP14 = iec101.CauseType.INTERROGATED_GROUP14.value
    INTERROGATED_GROUP15 = iec101.CauseType.INTERROGATED_GROUP15.value
    INTERROGATED_GROUP16 = iec101.CauseType.INTERROGATED_GROUP16.value
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


ParameterCause: typing.TypeAlias = (ParameterReqCause |
                                    ParameterResCause |
                                    OtherCause)


class ParameterActivationReqCause(enum.Enum):
    ACTIVATION = iec101.CauseType.ACTIVATION.value
    DEACTIVATION = iec101.CauseType.DEACTIVATION.value


class ParameterActivationResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.CauseType.ACTIVATION_CONFIRMATION.value
    DEACTIVATION_CONFIRMATION = iec101.CauseType.DEACTIVATION_CONFIRMATION.value  # NOQA
    UNKNOWN_TYPE = iec101.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.CauseType.UNKNOWN_ASDU_ADDRESS.value
    UNKNOWN_IO_ADDRESS = iec101.CauseType.UNKNOWN_IO_ADDRESS.value


ParameterActivationCause: typing.TypeAlias = (ParameterActivationReqCause |
                                              ParameterActivationResCause |
                                              OtherCause)


class SingleData(typing.NamedTuple):
    value: SingleValue
    quality: IndicationQuality


class DoubleData(typing.NamedTuple):
    value: DoubleValue
    quality: IndicationQuality


class StepPositionData(typing.NamedTuple):
    value: StepPositionValue
    quality: MeasurementQuality


class BitstringData(typing.NamedTuple):
    value: BitstringValue
    quality: MeasurementQuality


class NormalizedData(typing.NamedTuple):
    value: NormalizedValue
    quality: MeasurementQuality | None


class ScaledData(typing.NamedTuple):
    value: ScaledValue
    quality: MeasurementQuality


class FloatingData(typing.NamedTuple):
    value: FloatingValue
    quality: MeasurementQuality


class BinaryCounterData(typing.NamedTuple):
    value: BinaryCounterValue
    quality: CounterQuality


class ProtectionData(typing.NamedTuple):
    value: ProtectionValue
    quality: ProtectionQuality
    elapsed_time: int
    """elapsed_time in range [0, 65535]"""


class ProtectionStartData(typing.NamedTuple):
    value: ProtectionStartValue
    quality: ProtectionQuality
    duration_time: int
    """duration_time in range [0, 65535]"""


class ProtectionCommandData(typing.NamedTuple):
    value: ProtectionCommandValue
    quality: ProtectionQuality
    operating_time: int
    """operating_time in range [0, 65535]"""


class StatusData(typing.NamedTuple):
    value: StatusValue
    quality: MeasurementQuality


Data: typing.TypeAlias = (SingleData |
                          DoubleData |
                          StepPositionData |
                          BitstringData |
                          NormalizedData |
                          ScaledData |
                          FloatingData |
                          BinaryCounterData |
                          ProtectionData |
                          ProtectionStartData |
                          ProtectionCommandData |
                          StatusData)


class SingleCommand(typing.NamedTuple):
    value: SingleValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class DoubleCommand(typing.NamedTuple):
    value: DoubleValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class RegulatingCommand(typing.NamedTuple):
    value: RegulatingValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class NormalizedCommand(typing.NamedTuple):
    value: NormalizedValue
    select: bool


class ScaledCommand(typing.NamedTuple):
    value: ScaledValue
    select: bool


class FloatingCommand(typing.NamedTuple):
    value: FloatingValue
    select: bool


class BitstringCommand(typing.NamedTuple):
    value: BitstringValue


Command: typing.TypeAlias = (SingleCommand |
                             DoubleCommand |
                             RegulatingCommand |
                             NormalizedCommand |
                             ScaledCommand |
                             FloatingCommand |
                             BitstringCommand)


class NormalizedParameter(typing.NamedTuple):
    value: NormalizedValue
    qualifier: int
    """qualifier in range [0, 255]"""


class ScaledParameter(typing.NamedTuple):
    value: ScaledValue
    qualifier: int
    """qualifier in range [0, 255]"""


class FloatingParameter(typing.NamedTuple):
    value: FloatingValue
    qualifier: int
    """qualifier in range [0, 255]"""


Parameter: typing.TypeAlias = (NormalizedParameter |
                               ScaledParameter |
                               FloatingParameter)


class DataMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    data: Data
    time: Time | None
    cause: DataCause


class CommandMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    command: Command
    is_negative_confirm: bool
    cause: CommandCause


class InitializationMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    param_change: bool
    cause: InitializationCause


class InterrogationMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    request: int
    """request in range [0, 255]"""
    is_negative_confirm: bool
    cause: CommandCause


class CounterInterrogationMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    request: int
    """request in range [0, 63]"""
    freeze: FreezeCode
    is_negative_confirm: bool
    cause: CommandCause


class ReadMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    cause: ReadCause


class ClockSyncMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    time: Time
    is_negative_confirm: bool
    cause: ClockSyncCause


class TestMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    cause: ActivationCause


class ResetMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    qualifier: int
    """qualifier in range [0, 255]"""
    cause: ActivationCause


class DelayMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    time: int
    """time in range [0, 65535]"""
    cause: DelayCause


class ParameterMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    parameter: Parameter
    cause: ParameterCause


class ParameterActivationMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    qualifier: int
    """qualifier in range [0, 255]"""
    cause: ParameterActivationCause


Msg: typing.TypeAlias = (DataMsg |
                         CommandMsg |
                         InitializationMsg |
                         InterrogationMsg |
                         CounterInterrogationMsg |
                         ReadMsg |
                         ClockSyncMsg |
                         TestMsg |
                         ResetMsg |
                         DelayMsg |
                         ParameterMsg |
                         ParameterActivationMsg)


time_from_datetime = iec101.time_from_datetime
time_to_datetime = iec101.time_to_datetime
