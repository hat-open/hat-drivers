import enum
import typing

from hat.drivers.iec60870 import app


Bytes = app.iec101.common.Bytes
CauseSize = app.iec101.common.CauseSize
AsduAddressSize = app.iec101.common.AsduAddressSize
IoAddressSize = app.iec101.common.IoAddressSize
TimeSize = app.iec101.common.TimeSize
Time = app.iec101.common.Time

OriginatorAddress = app.iec101.common.OriginatorAddress
AsduAddress = app.iec101.common.AsduAddress
IoAddress = app.iec101.common.IoAddress

IndicationQuality = app.iec101.common.IndicationQuality
MeasurementQuality = app.iec101.common.MeasurementQuality
CounterQuality = app.iec101.common.CounterQuality
ProtectionQuality = app.iec101.common.ProtectionQuality
Quality = app.iec101.common.Quality

FreezeCode = app.iec101.common.FreezeCode

SingleValue = app.iec101.common.SingleValue
DoubleValue = app.iec101.common.DoubleValue
RegulatingValue = app.iec101.common.RegulatingValue
StepPositionValue = app.iec101.common.StepPositionValue
BitstringValue = app.iec101.common.BitstringValue
NormalizedValue = app.iec101.common.NormalizedValue
ScaledValue = app.iec101.common.ScaledValue
FloatingValue = app.iec101.common.FloatingValue
BinaryCounterValue = app.iec101.common.BinaryCounterValue
ProtectionValue = app.iec101.common.ProtectionValue
ProtectionStartValue = app.iec101.common.ProtectionStartValue
ProtectionCommandValue = app.iec101.common.ProtectionCommandValue
StatusValue = app.iec101.common.StatusValue


class DataResCause(enum.Enum):
    PERIODIC = app.iec101.common.CauseType.PERIODIC
    BACKGROUND_SCAN = app.iec101.common.CauseType.BACKGROUND_SCAN
    SPONTANEOUS = app.iec101.common.CauseType.SPONTANEOUS
    REQUEST = app.iec101.common.CauseType.REQUEST
    REMOTE_COMMAND = app.iec101.common.CauseType.REMOTE_COMMAND
    LOCAL_COMMAND = app.iec101.common.CauseType.LOCAL_COMMAND
    INTERROGATED_STATION = app.iec101.common.CauseType.INTERROGATED_STATION
    INTERROGATED_GROUP01 = app.iec101.common.CauseType.INTERROGATED_GROUP01
    INTERROGATED_GROUP02 = app.iec101.common.CauseType.INTERROGATED_GROUP02
    INTERROGATED_GROUP03 = app.iec101.common.CauseType.INTERROGATED_GROUP03
    INTERROGATED_GROUP04 = app.iec101.common.CauseType.INTERROGATED_GROUP04
    INTERROGATED_GROUP05 = app.iec101.common.CauseType.INTERROGATED_GROUP05
    INTERROGATED_GROUP06 = app.iec101.common.CauseType.INTERROGATED_GROUP06
    INTERROGATED_GROUP07 = app.iec101.common.CauseType.INTERROGATED_GROUP07
    INTERROGATED_GROUP08 = app.iec101.common.CauseType.INTERROGATED_GROUP08
    INTERROGATED_GROUP09 = app.iec101.common.CauseType.INTERROGATED_GROUP09
    INTERROGATED_GROUP10 = app.iec101.common.CauseType.INTERROGATED_GROUP10
    INTERROGATED_GROUP11 = app.iec101.common.CauseType.INTERROGATED_GROUP11
    INTERROGATED_GROUP12 = app.iec101.common.CauseType.INTERROGATED_GROUP12
    INTERROGATED_GROUP13 = app.iec101.common.CauseType.INTERROGATED_GROUP13
    INTERROGATED_GROUP14 = app.iec101.common.CauseType.INTERROGATED_GROUP14
    INTERROGATED_GROUP15 = app.iec101.common.CauseType.INTERROGATED_GROUP15
    INTERROGATED_GROUP16 = app.iec101.common.CauseType.INTERROGATED_GROUP16
    INTERROGATED_COUNTER = app.iec101.common.CauseType.INTERROGATED_COUNTER
    INTERROGATED_COUNTER01 = app.iec101.common.CauseType.INTERROGATED_COUNTER01
    INTERROGATED_COUNTER02 = app.iec101.common.CauseType.INTERROGATED_COUNTER02
    INTERROGATED_COUNTER03 = app.iec101.common.CauseType.INTERROGATED_COUNTER03
    INTERROGATED_COUNTER04 = app.iec101.common.CauseType.INTERROGATED_COUNTER04


DataCause = typing.Union[DataResCause, None]


class CommandReqCause(enum.Enum):
    ACTIVATION = app.iec101.common.CauseType.ACTIVATION
    DEACTIVATION = app.iec101.common.CauseType.DEACTIVATION


class CommandResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = app.iec101.common.CauseType.ACTIVATION_CONFIRMATION  # NOQA
    DEACTIVATION_CONFIRMATION = app.iec101.common.CauseType.DEACTIVATION_CONFIRMATION  # NOQA
    ACTIVATION_TERMINATION = app.iec101.common.CauseType.ACTIVATION_TERMINATION
    UNKNOWN_TYPE = app.iec101.common.CauseType.UNKNOWN_TYPE
    UNKNOWN_CAUSE = app.iec101.common.CauseType.UNKNOWN_CAUSE
    UNKNOWN_ASDU_ADDRESS = app.iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS
    UNKNOWN_IO_ADDRESS = app.iec101.common.CauseType.UNKNOWN_IO_ADDRESS


CommandCause = typing.Union[CommandReqCause, CommandResCause, None]


class InitializationResCause(enum.Enum):
    LOCAL_POWER = 0
    LOCAL_RESET = 1
    REMOTE_RESET = 2


InitializationCause = typing.Union[InitializationResCause, None]


class ReadReqCause(enum.Enum):
    REQUEST = app.iec101.common.CauseType.REQUEST


class ReadResCause(enum.Enum):
    UNKNOWN_TYPE = app.iec101.common.CauseType.UNKNOWN_TYPE
    UNKNOWN_CAUSE = app.iec101.common.CauseType.UNKNOWN_CAUSE
    UNKNOWN_ASDU_ADDRESS = app.iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS
    UNKNOWN_IO_ADDRESS = app.iec101.common.CauseType.UNKNOWN_IO_ADDRESS


ReadCause = typing.Union[ReadReqCause, ReadResCause, None]


class ActivationReqCause(enum.Enum):
    ACTIVATION = app.iec101.common.CauseType.ACTIVATION


class ActivationResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = app.iec101.common.CauseType.ACTIVATION_CONFIRMATION  # NOQA
    UNKNOWN_TYPE = app.iec101.common.CauseType.UNKNOWN_TYPE
    UNKNOWN_CAUSE = app.iec101.common.CauseType.UNKNOWN_CAUSE
    UNKNOWN_ASDU_ADDRESS = app.iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS
    UNKNOWN_IO_ADDRESS = app.iec101.common.CauseType.UNKNOWN_IO_ADDRESS


ActivationCause = typing.Union[ActivationReqCause, ActivationResCause, None]


class DelayReqCause(enum.Enum):
    SPONTANEOUS = app.iec101.common.CauseType.SPONTANEOUS
    ACTIVATION = app.iec101.common.CauseType.ACTIVATION


class DelayResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = app.iec101.common.CauseType.ACTIVATION_CONFIRMATION  # NOQA
    UNKNOWN_TYPE = app.iec101.common.CauseType.UNKNOWN_TYPE
    UNKNOWN_CAUSE = app.iec101.common.CauseType.UNKNOWN_CAUSE
    UNKNOWN_ASDU_ADDRESS = app.iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS
    UNKNOWN_IO_ADDRESS = app.iec101.common.CauseType.UNKNOWN_IO_ADDRESS


DelayCause = typing.Union[DelayReqCause, DelayResCause, None]


class ParameterReqCause(enum.Enum):
    SPONTANEOUS = app.iec101.common.CauseType.SPONTANEOUS
    ACTIVATION = app.iec101.common.CauseType.ACTIVATION


class ParameterResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = app.iec101.common.CauseType.ACTIVATION_CONFIRMATION  # NOQA
    INTERROGATED_STATION = app.iec101.common.CauseType.INTERROGATED_STATION
    INTERROGATED_GROUP01 = app.iec101.common.CauseType.INTERROGATED_GROUP01
    INTERROGATED_GROUP02 = app.iec101.common.CauseType.INTERROGATED_GROUP02
    INTERROGATED_GROUP03 = app.iec101.common.CauseType.INTERROGATED_GROUP03
    INTERROGATED_GROUP04 = app.iec101.common.CauseType.INTERROGATED_GROUP04
    INTERROGATED_GROUP05 = app.iec101.common.CauseType.INTERROGATED_GROUP05
    INTERROGATED_GROUP06 = app.iec101.common.CauseType.INTERROGATED_GROUP06
    INTERROGATED_GROUP07 = app.iec101.common.CauseType.INTERROGATED_GROUP07
    INTERROGATED_GROUP08 = app.iec101.common.CauseType.INTERROGATED_GROUP08
    INTERROGATED_GROUP09 = app.iec101.common.CauseType.INTERROGATED_GROUP09
    INTERROGATED_GROUP10 = app.iec101.common.CauseType.INTERROGATED_GROUP10
    INTERROGATED_GROUP11 = app.iec101.common.CauseType.INTERROGATED_GROUP11
    INTERROGATED_GROUP12 = app.iec101.common.CauseType.INTERROGATED_GROUP12
    INTERROGATED_GROUP13 = app.iec101.common.CauseType.INTERROGATED_GROUP13
    INTERROGATED_GROUP14 = app.iec101.common.CauseType.INTERROGATED_GROUP14
    INTERROGATED_GROUP15 = app.iec101.common.CauseType.INTERROGATED_GROUP15
    INTERROGATED_GROUP16 = app.iec101.common.CauseType.INTERROGATED_GROUP16
    UNKNOWN_TYPE = app.iec101.common.CauseType.UNKNOWN_TYPE
    UNKNOWN_CAUSE = app.iec101.common.CauseType.UNKNOWN_CAUSE
    UNKNOWN_ASDU_ADDRESS = app.iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS
    UNKNOWN_IO_ADDRESS = app.iec101.common.CauseType.UNKNOWN_IO_ADDRESS


ParameterCause = typing.Union[ParameterReqCause, ParameterResCause, None]


class ParameterActivationReqCause(enum.Enum):
    ACTIVATION = app.iec101.common.CauseType.ACTIVATION
    DEACTIVATION = app.iec101.common.CauseType.DEACTIVATION


class ParameterActivationResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = app.iec101.common.CauseType.ACTIVATION_CONFIRMATION  # NOQA
    DEACTIVATION_CONFIRMATION = app.iec101.common.CauseType.DEACTIVATION_CONFIRMATION  # NOQA
    UNKNOWN_TYPE = app.iec101.common.CauseType.UNKNOWN_TYPE
    UNKNOWN_CAUSE = app.iec101.common.CauseType.UNKNOWN_CAUSE
    UNKNOWN_ASDU_ADDRESS = app.iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS
    UNKNOWN_IO_ADDRESS = app.iec101.common.CauseType.UNKNOWN_IO_ADDRESS


ParameterActivationCause = typing.Union[ParameterActivationReqCause,
                                        ParameterActivationResCause,
                                        None]


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
    quality: typing.Optional[MeasurementQuality]


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


Data = typing.Union[SingleData,
                    DoubleData,
                    StepPositionData,
                    BitstringData,
                    NormalizedData,
                    ScaledData,
                    FloatingData,
                    BinaryCounterData,
                    ProtectionData,
                    ProtectionStartData,
                    ProtectionCommandData,
                    StatusData]


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


Command = typing.Union[SingleCommand,
                       DoubleCommand,
                       RegulatingCommand,
                       NormalizedCommand,
                       ScaledCommand,
                       FloatingCommand,
                       BitstringCommand]


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


Parameter = typing.Union[NormalizedParameter,
                         ScaledParameter,
                         FloatingParameter]


class DataMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    io_address: IoAddress
    data: Data
    time: typing.Optional[Time]
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
    cause: CommandCause


class CounterInterrogationMsg(typing.NamedTuple):
    is_test: bool
    originator_address: OriginatorAddress
    asdu_address: AsduAddress
    request: int
    """request in range [0, 63]"""
    freeze: FreezeCode
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
    cause: ActivationCause


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


Msg = typing.Union[DataMsg,
                   CommandMsg,
                   InitializationMsg,
                   InterrogationMsg,
                   CounterInterrogationMsg,
                   ReadMsg,
                   ClockSyncMsg,
                   TestMsg,
                   ResetMsg,
                   DelayMsg,
                   ParameterMsg,
                   ParameterActivationMsg]


time_from_datetime = app.iec101.common.time_from_datetime
time_to_datetime = app.iec101.common.time_to_datetime
