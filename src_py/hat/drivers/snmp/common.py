import enum
import typing

from hat import asn1


Bytes = asn1.Bytes

ObjectIdentifier = asn1.ObjectIdentifier


class Version(enum.Enum):
    V1 = 0
    V2C = 1
    V3 = 3


class ErrorType(enum.Enum):
    NO_ERROR = 0
    TOO_BIG = 1
    NO_SUCH_NAME = 2
    BAD_VALUE = 3
    READ_ONLY = 4
    GEN_ERR = 5
    NO_ACCESS = 6
    WRONG_TYPE = 7
    WRONG_LENGTH = 8
    WRONG_ENCODING = 9
    WRONG_VALUE = 10
    NO_CREATION = 11
    INCONSISTENT_VALUE = 12
    RESOURCE_UNAVAILABLE = 13
    COMMIT_FAILED = 14
    UNDO_FAILED = 15
    AUTHORIZATION_ERROR = 16
    NOT_WRITABLE = 17
    INCONSISTENT_NAME = 18


class CauseType(enum.Enum):
    COLD_START = 0
    WARM_START = 1
    LINK_DOWN = 2
    LINK_UP = 3
    AUTHENICATION_FAILURE = 4
    EGP_NEIGHBOR_LOSS = 5
    ENTERPRISE_SPECIFIC = 6


class DataType(enum.Enum):
    INTEGER = 0
    UNSIGNED = 1
    COUNTER = 2
    BIG_COUNTER = 3
    STRING = 4
    OBJECT_ID = 5
    IP_ADDRESS = 6
    TIME_TICKS = 7
    ARBITRARY = 8
    EMPTY = 9
    UNSPECIFIED = 10
    NO_SUCH_OBJECT = 11
    NO_SUCH_INSTANCE = 12
    END_OF_MIB_VIEW = 13


class MsgType(enum.Enum):
    GET_REQUEST = 'get-request'
    GET_NEXT_REQUEST = 'get-next-request'
    GET_BULK_REQUEST = 'get-bulk-request'
    RESPONSE = 'response'
    SET_REQUEST = 'set-request'
    TRAP = 'trap'
    INFORM_REQUEST = 'inform-request'
    SNMPV2_TRAP = 'snmpV2-trap'
    REPORT = 'report'


class Error(typing.NamedTuple):
    type: ErrorType
    index: int


class Cause(typing.NamedTuple):
    type: CauseType
    value: int


class Data(typing.NamedTuple):
    """Data

    Type of value is determined by value of data type:

        +------------------+------------------------+
        | type             | value                  |
        +==================+========================+
        | INTEGER          | int                    |
        +------------------+------------------------+
        | UNSIGNED         | int                    |
        +------------------+------------------------+
        | COUNTER          | int                    |
        +------------------+------------------------+
        | BIG_COUNTER      | int                    |
        +------------------+------------------------+
        | STRING           | str                    |
        +------------------+------------------------+
        | OBJECT_ID        | ObjectIdentifier       |
        +------------------+------------------------+
        | IP_ADDRESS       | Tuple[int,int,int,int] |
        +------------------+------------------------+
        | TIME_TICKS       | int                    |
        +------------------+------------------------+
        | ARBITRARY        | Bytes                  |
        +------------------+------------------------+
        | EMPTY            | NoneType               |
        +------------------+------------------------+
        | UNSPECIFIED      | NoneType               |
        +------------------+------------------------+
        | NO_SUCH_OBJECT   | NoneType               |
        +------------------+------------------------+
        | NO_SUCH_INSTANCE | NoneType               |
        +------------------+------------------------+
        | END_OF_MIB_VIEW  | NoneType               |
        +------------------+------------------------+

    """
    type: DataType
    name: ObjectIdentifier
    value: typing.Any


class Trap(typing.NamedTuple):
    oid: ObjectIdentifier
    timestamp: int
    data: typing.List[Data]


class Context(typing.NamedTuple):
    engine_id: str
    name: str


class BasicPdu(typing.NamedTuple):
    request_id: int
    error: Error
    data: typing.List[Data]


class TrapPdu(typing.NamedTuple):
    enterprise: ObjectIdentifier
    addr: typing.Tuple[int, int, int, int]
    cause: Cause
    timestamp: int
    data: typing.List[Data]


class BulkPdu(typing.NamedTuple):
    request_id: int
    non_repeaters: int
    max_repetitions: int
    data: typing.List[Data]


Pdu = typing.Union[BasicPdu, TrapPdu, BulkPdu]


class MsgV1(typing.NamedTuple):
    type: MsgType
    community: str
    pdu: Pdu


class MsgV2C(typing.NamedTuple):
    type: MsgType
    community: str
    pdu: Pdu


class MsgV3(typing.NamedTuple):
    type: MsgType
    id: int
    reportable: bool
    context: Context
    pdu: Pdu


Msg = typing.Union[MsgV1, MsgV2C, MsgV3]
