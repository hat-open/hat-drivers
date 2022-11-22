import enum
import typing

from hat.drivers.iec60870.msgs import iec101


Bytes = iec101.common.Bytes
CauseSize = iec101.common.CauseSize
AsduAddressSize = iec101.common.AsduAddressSize
IoAddressSize = iec101.common.IoAddressSize
TimeSize = iec101.common.TimeSize
Time = iec101.common.Time

OriginatorAddress = iec101.common.OriginatorAddress
AsduAddress = iec101.common.AsduAddress
IoAddress = iec101.common.IoAddress

IndicationQuality = iec101.common.IndicationQuality
MeasurementQuality = iec101.common.MeasurementQuality
CounterQuality = iec101.common.CounterQuality
ProtectionQuality = iec101.common.ProtectionQuality
Quality = iec101.common.Quality

FreezeCode = iec101.common.FreezeCode

SingleValue = iec101.common.SingleValue
DoubleValue = iec101.common.DoubleValue
RegulatingValue = iec101.common.RegulatingValue
StepPositionValue = iec101.common.StepPositionValue
BitstringValue = iec101.common.BitstringValue
NormalizedValue = iec101.common.NormalizedValue
ScaledValue = iec101.common.ScaledValue
FloatingValue = iec101.common.FloatingValue
BinaryCounterValue = iec101.common.BinaryCounterValue
ProtectionValue = iec101.common.ProtectionValue
ProtectionStartValue = iec101.common.ProtectionStartValue
ProtectionCommandValue = iec101.common.ProtectionCommandValue
StatusValue = iec101.common.StatusValue

OtherCause = int
"""Other cause in range [0, 63]"""


class DataResCause(enum.Enum):
    PERIODIC = iec101.common.CauseType.PERIODIC.value
    BACKGROUND_SCAN = iec101.common.CauseType.BACKGROUND_SCAN.value
    SPONTANEOUS = iec101.common.CauseType.SPONTANEOUS.value
    REQUEST = iec101.common.CauseType.REQUEST.value
    REMOTE_COMMAND = iec101.common.CauseType.REMOTE_COMMAND.value
    LOCAL_COMMAND = iec101.common.CauseType.LOCAL_COMMAND.value
    INTERROGATED_STATION = iec101.common.CauseType.INTERROGATED_STATION.value  # NOQA
    INTERROGATED_GROUP01 = iec101.common.CauseType.INTERROGATED_GROUP01.value  # NOQA
    INTERROGATED_GROUP02 = iec101.common.CauseType.INTERROGATED_GROUP02.value  # NOQA
    INTERROGATED_GROUP03 = iec101.common.CauseType.INTERROGATED_GROUP03.value  # NOQA
    INTERROGATED_GROUP04 = iec101.common.CauseType.INTERROGATED_GROUP04.value  # NOQA
    INTERROGATED_GROUP05 = iec101.common.CauseType.INTERROGATED_GROUP05.value  # NOQA
    INTERROGATED_GROUP06 = iec101.common.CauseType.INTERROGATED_GROUP06.value  # NOQA
    INTERROGATED_GROUP07 = iec101.common.CauseType.INTERROGATED_GROUP07.value  # NOQA
    INTERROGATED_GROUP08 = iec101.common.CauseType.INTERROGATED_GROUP08.value  # NOQA
    INTERROGATED_GROUP09 = iec101.common.CauseType.INTERROGATED_GROUP09.value  # NOQA
    INTERROGATED_GROUP10 = iec101.common.CauseType.INTERROGATED_GROUP10.value  # NOQA
    INTERROGATED_GROUP11 = iec101.common.CauseType.INTERROGATED_GROUP11.value  # NOQA
    INTERROGATED_GROUP12 = iec101.common.CauseType.INTERROGATED_GROUP12.value  # NOQA
    INTERROGATED_GROUP13 = iec101.common.CauseType.INTERROGATED_GROUP13.value  # NOQA
    INTERROGATED_GROUP14 = iec101.common.CauseType.INTERROGATED_GROUP14.value  # NOQA
    INTERROGATED_GROUP15 = iec101.common.CauseType.INTERROGATED_GROUP15.value  # NOQA
    INTERROGATED_GROUP16 = iec101.common.CauseType.INTERROGATED_GROUP16.value  # NOQA
    INTERROGATED_COUNTER = iec101.common.CauseType.INTERROGATED_COUNTER.value  # NOQA
    INTERROGATED_COUNTER01 = iec101.common.CauseType.INTERROGATED_COUNTER01.value  # NOQA
    INTERROGATED_COUNTER02 = iec101.common.CauseType.INTERROGATED_COUNTER02.value  # NOQA
    INTERROGATED_COUNTER03 = iec101.common.CauseType.INTERROGATED_COUNTER03.value  # NOQA
    INTERROGATED_COUNTER04 = iec101.common.CauseType.INTERROGATED_COUNTER04.value  # NOQA


DataCause = typing.Union[DataResCause, OtherCause]


class CommandReqCause(enum.Enum):
    ACTIVATION = iec101.common.CauseType.ACTIVATION.value
    DEACTIVATION = iec101.common.CauseType.DEACTIVATION.value


class CommandResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.common.CauseType.ACTIVATION_CONFIRMATION.value  # NOQA
    DEACTIVATION_CONFIRMATION = iec101.common.CauseType.DEACTIVATION_CONFIRMATION.value  # NOQA
    ACTIVATION_TERMINATION = iec101.common.CauseType.ACTIVATION_TERMINATION.value  # NOQA
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


CommandCause = typing.Union[CommandReqCause, CommandResCause, OtherCause]


class InitializationResCause(enum.Enum):
    LOCAL_POWER = 0
    LOCAL_RESET = 1
    REMOTE_RESET = 2


InitializationCause = typing.Union[InitializationResCause, OtherCause]


class ReadReqCause(enum.Enum):
    REQUEST = iec101.common.CauseType.REQUEST.value


class ReadResCause(enum.Enum):
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


ReadCause = typing.Union[ReadReqCause, ReadResCause, OtherCause]


class ClockSyncReqCause(enum.Enum):
    ACTIVATION = iec101.common.CauseType.ACTIVATION.value


class ClockSyncResCause(enum.Enum):
    SPONTANEOUS = iec101.common.CauseType.SPONTANEOUS.value
    ACTIVATION_CONFIRMATION = iec101.common.CauseType.ACTIVATION_CONFIRMATION.value  # NOQA
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


ClockSyncCause = typing.Union[ClockSyncReqCause,
                              ClockSyncResCause,
                              OtherCause]


class ActivationReqCause(enum.Enum):
    ACTIVATION = iec101.common.CauseType.ACTIVATION.value


class ActivationResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.common.CauseType.ACTIVATION_CONFIRMATION.value  # NOQA
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


ActivationCause = typing.Union[ActivationReqCause,
                               ActivationResCause,
                               OtherCause]


class DelayReqCause(enum.Enum):
    SPONTANEOUS = iec101.common.CauseType.SPONTANEOUS.value
    ACTIVATION = iec101.common.CauseType.ACTIVATION.value


class DelayResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.common.CauseType.ACTIVATION_CONFIRMATION.value  # NOQA
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


DelayCause = typing.Union[DelayReqCause, DelayResCause, OtherCause]


class ParameterReqCause(enum.Enum):
    SPONTANEOUS = iec101.common.CauseType.SPONTANEOUS.value
    ACTIVATION = iec101.common.CauseType.ACTIVATION.value


class ParameterResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.common.CauseType.ACTIVATION_CONFIRMATION.value  # NOQA
    INTERROGATED_STATION = iec101.common.CauseType.INTERROGATED_STATION.value  # NOQA
    INTERROGATED_GROUP01 = iec101.common.CauseType.INTERROGATED_GROUP01.value  # NOQA
    INTERROGATED_GROUP02 = iec101.common.CauseType.INTERROGATED_GROUP02.value  # NOQA
    INTERROGATED_GROUP03 = iec101.common.CauseType.INTERROGATED_GROUP03.value  # NOQA
    INTERROGATED_GROUP04 = iec101.common.CauseType.INTERROGATED_GROUP04.value  # NOQA
    INTERROGATED_GROUP05 = iec101.common.CauseType.INTERROGATED_GROUP05.value  # NOQA
    INTERROGATED_GROUP06 = iec101.common.CauseType.INTERROGATED_GROUP06.value  # NOQA
    INTERROGATED_GROUP07 = iec101.common.CauseType.INTERROGATED_GROUP07.value  # NOQA
    INTERROGATED_GROUP08 = iec101.common.CauseType.INTERROGATED_GROUP08.value  # NOQA
    INTERROGATED_GROUP09 = iec101.common.CauseType.INTERROGATED_GROUP09.value  # NOQA
    INTERROGATED_GROUP10 = iec101.common.CauseType.INTERROGATED_GROUP10.value  # NOQA
    INTERROGATED_GROUP11 = iec101.common.CauseType.INTERROGATED_GROUP11.value  # NOQA
    INTERROGATED_GROUP12 = iec101.common.CauseType.INTERROGATED_GROUP12.value  # NOQA
    INTERROGATED_GROUP13 = iec101.common.CauseType.INTERROGATED_GROUP13.value  # NOQA
    INTERROGATED_GROUP14 = iec101.common.CauseType.INTERROGATED_GROUP14.value  # NOQA
    INTERROGATED_GROUP15 = iec101.common.CauseType.INTERROGATED_GROUP15.value  # NOQA
    INTERROGATED_GROUP16 = iec101.common.CauseType.INTERROGATED_GROUP16.value  # NOQA
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


ParameterCause = typing.Union[ParameterReqCause, ParameterResCause, OtherCause]


class ParameterActivationReqCause(enum.Enum):
    ACTIVATION = iec101.common.CauseType.ACTIVATION.value
    DEACTIVATION = iec101.common.CauseType.DEACTIVATION.value


class ParameterActivationResCause(enum.Enum):
    ACTIVATION_CONFIRMATION = iec101.common.CauseType.ACTIVATION_CONFIRMATION.value  # NOQA
    DEACTIVATION_CONFIRMATION = iec101.common.CauseType.DEACTIVATION_CONFIRMATION.value  # NOQA
    UNKNOWN_TYPE = iec101.common.CauseType.UNKNOWN_TYPE.value
    UNKNOWN_CAUSE = iec101.common.CauseType.UNKNOWN_CAUSE.value
    UNKNOWN_ASDU_ADDRESS = iec101.common.CauseType.UNKNOWN_ASDU_ADDRESS.value  # NOQA
    UNKNOWN_IO_ADDRESS = iec101.common.CauseType.UNKNOWN_IO_ADDRESS.value


ParameterActivationCause = typing.Union[ParameterActivationReqCause,
                                        ParameterActivationResCause,
                                        OtherCause]


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


time_from_datetime = iec101.common.time_from_datetime
time_to_datetime = iec101.common.time_to_datetime
