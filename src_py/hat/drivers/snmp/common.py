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
    NO_ERROR = 0                 # v1, v2c, v3
    TOO_BIG = 1                  # v1, v2c, v3
    NO_SUCH_NAME = 2             # v1, v2c, v3
    BAD_VALUE = 3                # v1, v2c, v3
    READ_ONLY = 4                # v1, v2c, v3
    GEN_ERR = 5                  # v1, v2c, v3
    NO_ACCESS = 6                # v2c, v3
    WRONG_TYPE = 7               # v2c, v3
    WRONG_LENGTH = 8             # v2c, v3
    WRONG_ENCODING = 9           # v2c, v3
    WRONG_VALUE = 10             # v2c, v3
    NO_CREATION = 11             # v2c, v3
    INCONSISTENT_VALUE = 12      # v2c, v3
    RESOURCE_UNAVAILABLE = 13    # v2c, v3
    COMMIT_FAILED = 14           # v2c, v3
    UNDO_FAILED = 15             # v2c, v3
    AUTHORIZATION_ERROR = 16     # v2c, v3
    NOT_WRITABLE = 17            # v2c, v3
    INCONSISTENT_NAME = 18       # v2c, v3


class CauseType(enum.Enum):
    COLD_START = 0
    WARM_START = 1
    LINK_DOWN = 2
    LINK_UP = 3
    AUTHENICATION_FAILURE = 4
    EGP_NEIGHBOR_LOSS = 5
    ENTERPRISE_SPECIFIC = 6


class DataType(enum.Enum):
    INTEGER = 0               # v1, v2c, v3
    UNSIGNED = 1              # v1, v2c, v3
    COUNTER = 2               # v1, v2c, v3
    BIG_COUNTER = 3           # v2c, v3
    STRING = 4                # v1, v2c, v3
    OBJECT_ID = 5             # v1, v2c, v3
    IP_ADDRESS = 6            # v1, v2c, v3
    TIME_TICKS = 7            # v1, v2c, v3
    ARBITRARY = 8             # v1, v2c, v3
    EMPTY = 9                 # v1
    UNSPECIFIED = 10          # v2c, v3
    NO_SUCH_OBJECT = 11       # v2c, v3
    NO_SUCH_INSTANCE = 12     # v2c, v3
    END_OF_MIB_VIEW = 13      # v2c, v3


class Error(typing.NamedTuple):
    type: ErrorType
    index: int


class Cause(typing.NamedTuple):
    type: CauseType
    value: int


class Data(typing.NamedTuple):
    """Data

    Type of value is determined by value of data type:

        +------------------+---------------------------+
        | type             | value                     |
        +==================+===========================+
        | INTEGER          | int                       |
        +------------------+---------------------------+
        | UNSIGNED         | int                       |
        +------------------+---------------------------+
        | COUNTER          | int                       |
        +------------------+---------------------------+
        | BIG_COUNTER      | int                       |
        +------------------+---------------------------+
        | STRING           | str                       |
        +------------------+---------------------------+
        | OBJECT_ID        | ObjectIdentifier          |
        +------------------+---------------------------+
        | IP_ADDRESS       | Tuple[int, int, int, int] |
        +------------------+---------------------------+
        | TIME_TICKS       | int                       |
        +------------------+---------------------------+
        | ARBITRARY        | Bytes                     |
        +------------------+---------------------------+
        | EMPTY            | NoneType                  |
        +------------------+---------------------------+
        | UNSPECIFIED      | NoneType                  |
        +------------------+---------------------------+
        | NO_SUCH_OBJECT   | NoneType                  |
        +------------------+---------------------------+
        | NO_SUCH_INSTANCE | NoneType                  |
        +------------------+---------------------------+
        | END_OF_MIB_VIEW  | NoneType                  |
        +------------------+---------------------------+

    """
    type: DataType
    name: ObjectIdentifier
    value: typing.Any


class Context(typing.NamedTuple):
    engine_id: typing.Optional[str]
    """engine id is not available in case of v1 and v2c"""
    name: str
    """name is used as community name in case of v1 and v2c"""


class Trap(typing.NamedTuple):
    context: Context
    cause: typing.Optional[Cause]
    """cause is available in case of v1"""
    oid: ObjectIdentifier
    timestamp: int
    data: typing.List[Data]


class Inform(typing.NamedTuple):
    context: Context
    data: typing.List[Data]


class GetDataReq(typing.NamedTuple):
    names: typing.List[ObjectIdentifier]


class GetNextDataReq(typing.NamedTuple):
    names: typing.List[ObjectIdentifier]


class GetBulkDataReq(typing.NamedTuple):
    names: typing.List[ObjectIdentifier]


class SetDataReq(typing.NamedTuple):
    data: typing.List[Data]


Request = typing.Union[GetDataReq,
                       GetNextDataReq,
                       GetBulkDataReq,
                       SetDataReq]

Response = typing.Union[Error, typing.List[Data]]
