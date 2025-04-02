from collections.abc import Collection
import datetime
import enum
import typing

from hat import util


EntryTime: typing.TypeAlias = datetime.datetime

ReportId: typing.TypeAlias = str


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
    names: tuple[str | int, ...]


class CommandRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    name: str


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
    BIT_STRING = 'BIT_STRING'  # Collection[bool]
    OCTET_STRING = 'OCTET_STRING'  # util.Bytes
    VISIBLE_STRING = 'VISIBLE_STRING'  # str
    MMS_STRING = 'MMS_STRING'  # str


class AcsiValueType(enum.Enum):
    QUALITY = 'QUALITY'
    TIMESTAMP = 'TIMESTAMP'
    DOUBLE_POINT = 'DOUBLE_POINT'
    DIRECTION = 'DIRECTION'
    SEVERITY = 'SEVERITY'
    ANALOGUE = 'ANALOGUE'
    VECTOR = 'VECTOR'
    STEP_POSITION = 'STEP_POSITION'
    BINARY_CONTROL = 'BINARY_CONTROL'


class ArrayValueType(typing.NamedTuple):
    type: 'ValueType'


class StructValueType(typing.NamedTuple):
    elements: Collection[typing.Tuple[str, 'ValueType']]


ValueType: typing.TypeAlias = (BasicValueType |
                               AcsiValueType |
                               ArrayValueType |
                               StructValueType)


# values ######################################################################

class Timestamp(typing.NamedTuple):
    value: datetime.datetime
    leap_second: bool
    clock_failure: bool
    not_synchronized: bool
    accuracy: int | None
    """accurate fraction bits [0,24]"""


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


class DoublePoint(enum.Enum):
    INTERMEDIATE = 0
    OFF = 1
    ON = 2
    BAD = 3


class Direction(enum.Enum):
    UNKNOWN = 0
    FORWARD = 1
    BACKWARD = 2
    BOTH = 3


class Severity(enum.Enum):
    UNKNOWN = 0
    CRITICAL = 1
    MAJOR = 2
    MINOR = 3
    WARNING = 4


class Analogue(typing.NamedTuple):
    i: int | None = None
    f: float | None = None


class Vector(typing.NamedTuple):
    magnitude: Analogue
    angle: Analogue | None


class StepPosition(typing.NamedTuple):
    value: int
    """value in range [-64, 63]"""
    transient: bool | None


class BinaryControl(enum.Enum):
    STOP = 0
    LOWER = 1
    HIGHER = 2
    RESERVED = 3


BasicValue: typing.NamedTuple = (bool | int | float | str | util.Bytes |
                                 Collection[bool])

AcsiValue = (Quality | Timestamp | DoublePoint | Direction | Severity |
             Analogue | Vector | StepPosition | BinaryControl)

ArrayValue: typing.NamedTuple = Collection['Value']

StructValue: typing.NamedTuple = typing.Dict[str, 'Value']

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
    FAILED_DUE_TO_SERVER_CONSTRAINT = 12


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


class TestError(enum.Enum):
    NO_ERROR = 0
    UNKNOWN = 1
    TIMEOUT_TEST_NOT_OK = 2
    OPERATOR_TEST_NOT_OK = 3


class CommandError(typing.NamedTuple):
    service_error: ServiceError | None
    additional_cause: AdditionalCause | None
    test_error: TestError | None


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


class RcbAttrType(enum.Enum):
    REPORT_ID = 'RptID'
    REPORT_ENABLE = 'RptEna'
    DATASET = 'DatSet'
    CONF_REVISION = 'ConfRev'
    OPTIONAL_FIELDS = 'OptFlds'
    BUFFER_TIME = 'BufTm'
    SEQUENCE_NUMBER = 'SqNum'
    TRIGGER_OPTIONS = 'TrgOps'
    INTEGRITY_PERIOD = 'IntgPd'
    GI = 'GI'
    PURGE_BUFFER = 'PurgeBuf'  # brcb
    ENTRY_ID = 'EntryID'  # brcb
    TIME_OF_ENTRY = 'TimeOfEntry'  # brcb
    RESERVATION_TIME = 'ResvTms'  # brcb
    RESERVE = 'Resv'  # urcb


ReportIdRcbAttrValue: typing.TypeAlias = ReportId

ReportEnableRcbAttrValue: typing.TypeAlias = bool

DatasetRcbAttrValue: typing.TypeAlias = DatasetRef

ConfRevisionRcbAttrValue: typing.TypeAlias = int

OptionalFieldsRcbAttrValue: typing.TypeAlias = set[OptionalField]

BufferTimeRcbAttrValue: typing.TypeAlias = int

SequenceNumberRcbAttrValue: typing.TypeAlias = int

TriggerOptionsRcbAttrValue: typing.TypeAlias = set[TriggerCondition]

IntegrityPeriodRcbAttrValue: typing.TypeAlias = int

GiRcbAttrValue: typing.TypeAlias = bool

PurgeBufferRcbAttrValue: typing.TypeAlias = bool

EntryIdRcbAttrValue: typing.TypeAlias = util.Bytes

TimeOfEntryRcbAttrValue: typing.TypeAlias = EntryTime

ReservationTimeRcbAttrValue: typing.TypeAlias = int

ReserveRcbAttrValue: typing.TypeAlias = bool

RcbAttrValue: typing.TypeAlias = (ReportIdRcbAttrValue |
                                  ReportEnableRcbAttrValue |
                                  DatasetRcbAttrValue |
                                  ConfRevisionRcbAttrValue |
                                  OptionalFieldsRcbAttrValue |
                                  BufferTimeRcbAttrValue |
                                  SequenceNumberRcbAttrValue |
                                  TriggerOptionsRcbAttrValue |
                                  IntegrityPeriodRcbAttrValue |
                                  GiRcbAttrValue |
                                  PurgeBufferRcbAttrValue |
                                  EntryIdRcbAttrValue |
                                  TimeOfEntryRcbAttrValue |
                                  ReservationTimeRcbAttrValue |
                                  ReserveRcbAttrValue)


# report ######################################################################

class ReasonCode(enum.Enum):
    DATA_CHANGE = 1
    QUALITY_CHANGE = 2
    DATA_UPDATE = 3
    INTEGRITY = 4
    GENERAL_INTERROGATION = 5
    APPLICATION_TRIGGER = 6


class ReportData(typing.NamedTuple):
    ref: DataRef
    value: Value
    reasons: set[ReasonCode] | None


class Report(typing.NamedTuple):
    report_id: ReportId
    sequence_number: int | None
    subsequence_number: int | None
    more_segments_follow: bool | None
    dataset: DatasetRef | None
    buffer_overflow: bool | None
    conf_revision: int | None
    entry_time: EntryTime | None
    entry_id: util.Bytes | None
    data: Collection[ReportData]


# command #####################################################################

class ControlModel(enum.Enum):
    DIRECT_WITH_NORMAL_SECURITY = 1
    SBO_WITH_NORMAL_SECURITY = 2
    DIRECT_WITH_ENHANCED_SECURITY = 3
    SBO_WITH_ENHANCED_SECURITY = 4


class OriginCategory(enum.Enum):
    NOT_SUPPORTED = 0
    BAY_CONTROL = 1
    STATION_CONTROL = 2
    REMOTE_CONTROL = 3
    AUTOMATIC_BAY = 4
    AUTOMATIC_STATION = 5
    AUTOMATIC_REMOTE = 6
    MAINTENANCE = 7
    PROCESS = 8


class Origin(typing.NamedTuple):
    category: OriginCategory
    identification: util.Bytes


class Check(enum.Enum):
    SYNCHRO = 0
    INTERLOCK = 1


class Command(typing.NamedTuple):
    value: Value
    operate_time: Timestamp | None
    origin: Origin
    control_number: int
    """control number in range [0, 255]"""
    t: Timestamp
    test: bool
    checks: set[Check]
    """ignored in cancel action"""


class Termination(typing.NamedTuple):
    ref: CommandRef
    cmd: Command
    error: CommandError | None
