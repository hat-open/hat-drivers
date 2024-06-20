from collections.abc import Collection
import enum
import typing

from hat import asn1
from hat import util


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


class AuthType(enum.Enum):
    MD5 = 1
    SHA = 2


class PrivType(enum.Enum):
    DES = 1


class Error(typing.NamedTuple):
    type: ErrorType
    index: int


class Cause(typing.NamedTuple):
    type: CauseType
    value: int


# v1, v2c, v3
class IntegerData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: int


# v1, v2c, v3
class UnsignedData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: int


# v1, v2c, v3
class CounterData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: int


# v2c, v3
class BigCounterData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: int


# v1, v2c, v3
class StringData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: util.Bytes


# v1, v2c, v3
class ObjectIdData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: asn1.ObjectIdentifier


# v1, v2c, v3
class IpAddressData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: tuple[int, int, int, int]


# v1, v2c, v3
class TimeTicksData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: int


# v1, v2c, v3
class ArbitraryData(typing.NamedTuple):
    name: asn1.ObjectIdentifier
    value: util.Bytes


# v1
class EmptyData(typing.NamedTuple):
    name: asn1.ObjectIdentifier


# v2c, v3
class UnspecifiedData(typing.NamedTuple):
    name: asn1.ObjectIdentifier


# v2c, v3
class NoSuchObjectData(typing.NamedTuple):
    name: asn1.ObjectIdentifier


# v2c, v3
class NoSuchInstanceData(typing.NamedTuple):
    name: asn1.ObjectIdentifier


# v2c, v3
class EndOfMibViewData(typing.NamedTuple):
    name: asn1.ObjectIdentifier


Data: typing.TypeAlias = (IntegerData |
                          UnsignedData |
                          CounterData |
                          BigCounterData |
                          StringData |
                          ObjectIdData |
                          IpAddressData |
                          TimeTicksData |
                          ArbitraryData |
                          EmptyData |
                          UnspecifiedData |
                          NoSuchObjectData |
                          NoSuchInstanceData |
                          EndOfMibViewData)


CommunityName: typing.TypeAlias = str

UserName: typing.TypeAlias = str

Password: typing.TypeAlias = str

EngineId: typing.TypeAlias = util.Bytes


class User(typing.NamedTuple):
    name: UserName
    auth_type: AuthType | None
    auth_password: Password | None
    priv_type: PrivType | None
    priv_password: Password | None


class Context(typing.NamedTuple):
    engine_id: EngineId
    name: str


class Trap(typing.NamedTuple):
    cause: Cause | None
    """cause is available in case of v1"""
    oid: asn1.ObjectIdentifier
    timestamp: int
    data: Collection[Data]


class Inform(typing.NamedTuple):
    data: Collection[Data]


class GetDataReq(typing.NamedTuple):
    names: Collection[asn1.ObjectIdentifier]


class GetNextDataReq(typing.NamedTuple):
    names: Collection[asn1.ObjectIdentifier]


class GetBulkDataReq(typing.NamedTuple):
    names: Collection[asn1.ObjectIdentifier]


class SetDataReq(typing.NamedTuple):
    data: Collection[Data]


Request: typing.TypeAlias = (GetDataReq |
                             GetNextDataReq |
                             GetBulkDataReq |
                             SetDataReq)

Response: typing.TypeAlias = Error | Collection[Data]


def validate_user(user: User):
    if user.auth_type and not user.auth_password:
        raise Exception('invalid auth password')

    if user.priv_type and not user.priv_password:
        raise Exception('invalid priv password')

    if user.priv_type and not user.auth_type:
        raise Exception('invalid auth/priv pair')
