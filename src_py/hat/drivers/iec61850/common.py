from collections.abc import Collection
import datetime
import enum
import typing

from hat import util


EntryTime: typing.TypeAlias = datetime.datetime


# references ##################################################################

class PersistedDatasetRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    name: str


class NonPersistedDatasetRef(typing.NamedTuple):
    name: str


DatasetRef: typing.TypeAlias = PersistedDatasetRef | NonPersistedDatasetRef


class DataRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    fc: str
    names: Collection[str | int]


class CommandRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    names: Collection[str]


class RcbType(enum.Enum):
    BUFFERED = 'BR'
    UNBUFFERED = 'RP'


class RcbRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    type: RcbType
    name: str


# value types #################################################################

class BasicValueType(enum.Enum):
    BOOLEAN = 'BOOLEAN'  # bool
    INTEGER = 'INTEGER'  # int
    UNSIGNED = 'UNSIGNED'  # int
    FLOAT = 'FLOAT'  # float
    BIT_STRING = 'BIT_STRING'  # list[bool]
    OCTET_STRING = 'OCTET_STRING'  # util.Bytes
    VISIBLE_STRING = 'VISIBLE_STRING'  # str
    MMS_STRING = 'MMS_STRING'  # str


class AcsiValueType(enum.Enum):
    QUALITY = 'QUALITY'
    TIMESTAMP = 'TIMESTAMP'


class ArrayValueType(typing.NamedTuple):
    type: 'ValueType'


class StructValueType(typing.NamedTuple):
    elements: Collection['ValueType']


ValueType: typing.TypeAlias = (BasicValueType |
                               AcsiValueType |
                               ArrayValueType |
                               StructValueType)


# values ######################################################################

class Timestamp(typing.NamedTuple):
    t: datetime.datetime
    leap_seconds_known: bool
    clock_failure: bool
    clock_not_synchronized: bool
    time_accuracy: typing.Optional[int]
    """number of bits of accuracy in regard to fraction of seconds [0, 24]"""


class QualityValidity(enum.Enum):
    GOOD = 0
    INVALID = 1
    RESERVED = 2
    QUESTIONABLE = 3


class QualityDetail(enum.Enum):
    OVERFLOW = 2
    OUT_OF_RANGE = 3
    BAD_REFERENCE = 4
    OSCILLATORY = 5
    FAILURE = 6
    OLD_DATA = 7
    INCONSISTENT = 8
    INACCURATE = 9


class QualitySource(enum.Enum):
    PROCESS = 0
    SUBSTITUTED = 1


class Quality(typing.NamedTuple):
    validity: QualityValidity
    details: set[QualityDetail]
    source: QualitySource
    test: bool
    operator_blocked: bool


BasicValue: typing.NamedTuple = (bool | int | float | str | util.Bytes |
                                 list[bool])

AcsiValue = Quality | Timestamp

ArrayValue: typing.NamedTuple = Collection['Value']

StructValue: typing.NamedTuple = Collection['Value']

Value: typing.NamedTuple = BasicValue | AcsiValue | ArrayValue | StructValue


# errors ######################################################################

class ServiceError(enum.Enum):
    NO_ERROR = 0
    INSTANCE_NOT_AVAILABLE = 1
    INSTANCE_IN_USE = 2
    ACCESS_VIOLATION = 3
    ACCESS_NOT_ALLOWED_IN_CURRENT_STATE = 4
    PARAMETER_VALUE_INAPPROPRIATE = 5
    PARAMETER_VALUE_INCONSISTENT = 6
    CLASS_NOT_SUPPORTED = 7
    INSTANCE_LOCKED_BY_OTHER_CLIENT = 8
    CONTROL_MUST_BE_SELECTED = 9
    TYPE_CONFLICT = 10
    FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT = 11
    FAILED_DUE_TO_SERVER_CONTRAINT = 12


class AdditionalCause(enum.Enum):
    UNKNOWN = 0
    NOT_SUPPORTED = 1
    BLOCKED_BY_SWITCHING_HIERARCHY = 2
    SELECT_FAILED = 3
    INVALID_POSITION = 4
    POSITION_REACHED = 5
    PARAMETER_CHANGE_IN_EXECUTION = 6
    STEP_LIMIT = 7
    BLOCKED_BY_MODE = 8
    BLOCKED_BY_PROCESS = 9
    BLOCKED_BY_INTERLOCKING = 10
    BLOCKED_BY_SYNCHROCHECK = 11
    COMMAND_ALREADY_IN_EXECUTION = 12
    BLOCKED_BY_HEALTH = 13
    ONE_OF_N_CONTROL = 14
    ABORTION_BY_CANCEL = 15
    TIME_LIMIT_OVER = 16
    ABORTION_BY_TRIP = 17
    OBJECT_NOT_SELECTED = 18
    OBJECT_ALREADY_SELECTED = 19
    NO_ACCESS_AUTHORITY = 20
    ENDED_WITH_OVERSHOOT = 21
    ABORTION_DUE_TO_DEVIATION = 22
    ABORTION_BY_COMMUNICATION_LOSS = 23
    BLOCKED_BY_COMMAND = 24
    NONE = 25
    INCONSISTENT_PARAMETERS = 26
    LOCKED_BY_OTHER_CLIENT = 27


# rcb #########################################################################

class OptionalField(enum.Enum):
    SEQUENCE_NUMBER = 1
    REPORT_TIME_STAMP = 2
    REASON_FOR_INCLUSION = 3
    DATA_SET_NAME = 4
    DATA_REFERENCE = 5
    BUFFER_OVERFLOW = 6
    ENTRY_ID = 7
    CONF_REVISION = 8


class TriggerCondition(enum.Enum):
    DATA_CHANGE = 1
    QUALITY_CHANGE = 2
    DATA_UPDATE = 3
    INTEGRITY = 4
    GENERAL_INTERROGATION = 5


class Brcb(typing.NamedTuple):
    report_id: str | None = None
    report_enable: bool | None = None
    dataset: DatasetRef | None = None
    conf_revision: int | None = None
    optional_fields: set[OptionalField] | None = None
    buffer_time: int | None = None
    sequence_number: int | None = None
    trigger_options: set[TriggerCondition] | None = None
    integrity_period: int | None = None
    gi: bool | None = None
    purge_buffer: bool | None = None
    entry_id: bytes | None = None
    time_of_entry: EntryTime | None = None
    reservation_time: int | None = None


class Urcb(typing.NamedTuple):
    report_id: str | None = None
    report_enable: bool | None = None
    reserve: bool | None = None
    dataset: DatasetRef | None = None
    conf_revision: int | None = None
    optional_fields: set[OptionalField] | None = None
    buffer_time: int | None = None
    sequence_number: int | None = None
    trigger_options: set[TriggerCondition] | None = None
    integrity_period: int | None = None
    gi: bool | None = None


Rcb: typing.TypeAlias = Brcb | Urcb


# report ######################################################################

class ReportDef(typing.NamedTuple):
    report_id: str
    data: Collection[ValueType]


class ReasonCode(enum.Enum):
    DATA_CHANGE = 1
    QUALITY_CHANGE = 2
    DATA_UPDATE = 3
    INTEGRITY = 4
    GENERAL_INTERROGATION = 5
    APPLICATION_TRIGGER = 6


class ReportData(typing.NamedTuple):
    ref: DataRef | None
    value: Value
    reasons: set[ReasonCode] | None


class ReportEntry(typing.NamedTuple):
    time: EntryTime
    id: str
    data: Collection[ReportData]


class Report(typing.NamedTuple):
    report_id: str
    sequence_number: int | None
    subsequence_number: int | None
    more_segments_follow: bool | None
    dataset: DatasetRef | None
    buffer_overflow: bool | None
    conf_revision: int | None
    entries: Collection[ReportEntry]


# command #####################################################################

class ControlModel(enum.Enum):
    DIRECT_WITH_NORMAL_SECURITY = 1
    SBO_WITH_NORMAL_SECURITY = 2
    DIRECT_WITH_ENHANCED_SECURITY = 3
    SBO_WITH_ENHANCED_SECURITY = 4


class OriginatorCategory(enum.Enum):
    NOT_SUPPORTED = 0
    BAY_CONTROL = 1
    STATION_CONTROL = 2
    REMOTE_CONTROL = 3
    AUTOMATIC_BAY = 4
    AUTOMATIC_STATION = 5
    AUTOMATIC_REMOTE = 6
    MAINTENANCE = 7
    PROCESS = 8


class Originator(typing.NamedTuple):
    category: OriginatorCategory
    identification: util.Bytes


class Command(typing.NamedTuple):
    value: Value
    origin: Originator
    control_number: int
    """control number in range [0, 255]"""
    t: Timestamp
    test: bool
    check: list[bool] | None
    """not available in cancel action"""


class Termination(typing.NamedTuple):
    ref: CommandRef
    cmd: Command
    error: AdditionalCause | None
