from hat.drivers.iec60870.encodings.common import *  # NOQA

import enum
import typing

from hat import util

from hat.drivers.iec60870.encodings import iec101
from hat.drivers.iec60870.encodings import iec104
from hat.drivers.iec60870.encodings.common import Time


OriginatorAddress: typing.TypeAlias = iec101.OriginatorAddress

# different sizes for iec101 and iec104
AsduAddress: typing.TypeAlias = iec101.AsduAddress | iec104.AsduAddress

# different sizes for iec101 and iec104
IoAddress: typing.TypeAlias = iec101.IoAddress | iec104.IoAddress

OtherCauseType: typing.TypeAlias = iec101.OriginatorAddress

BinaryCounterValue: typing.TypeAlias = iec101.BinaryCounterValue


AssociationId: typing.TypeAlias = int
"""Association ID in range [0, 65535]"""

SequenceNumber: typing.TypeAlias = int
"""Sequnce number in range [0, 4294967295]"""

UserNumber: typing.TypeAlias = int
"""User number in range [0, 65535]"""


class AsduType(enum.Enum):
    S_IT_TC = 41
    S_CH_NA = 81
    S_RP_NA = 82
    S_AR_NA = 83
    S_KR_NA = 84
    S_KS_NA = 85
    S_KC_NA = 86
    S_ER_NA = 87
    S_UC_NA_X = 88
    S_US_NA = 90
    S_UQ_NA = 91
    S_UR_NA = 92
    S_UK_NA = 93
    S_UA_NA = 94
    S_UC_NA = 95


class MacAlgorithm(enum.Enum):
    NO_MAC = 0
    HMAC_SHA_256_8 = 3
    HMAC_SHA_256_16 = 4
    AES_GMAC = 6


class KeyWrapAlgorithm(enum.Enum):
    AES_128 = 1
    AES_256 = 2


class KeyStatus(enum.Enum):
    OK = 1
    NOT_INIT = 2
    COMM_FAIL = 3
    AUTH_FAIL = 4


class ErrorCode(enum.Enum):
    AUTHENTICATION_FAILED = 1
    AGGRESSIVE_NOT_PERMITTED = 4
    MAC_ALGORITHM_NOT_PERMITTED = 5
    KEY_WRAP_ALGORITHM_NOT_PERMITTED = 6
    AUTHORIZATION_FAILED = 7
    UPDATE_KEY_NOT_PERMITTED = 8
    INVALID_SIGNATURE = 9
    INVALID_CERTIFICATION = 10
    UNKNOWN_USER = 11


class KeyChangeMethod(enum.Enum):
    SYMMETRIC_AES_128_HMAC_SHA_1 = 3
    SYMMETRIC_AES_256_HMAC_SHA_256 = 4
    SYMMETRIC_AES_256_AES_GMAC = 5
    ASYMMETRIC_RSE_2048_DSA_SHA_1_HMAC_SHA_1 = 67
    ASYMMETRIC_RSE_2048_DSA_SHA_256_HMAC_SHA_256 = 68
    ASYMMETRIC_RSE_3072_DSA_SHA_256_HMAC_SHA_256 = 69
    ASYMMETRIC_RSE_2048_DSA_SHA_256_AES_GMAC = 70
    ASYMMETRIC_RSE_3072_DSA_SHA_256_AES_GMAC = 71


class Operation(enum.Enum):
    ADD = 1
    DELETE = 2
    CHANGE = 3


class UserRole(enum.Enum):
    VIEWER = 0
    OPERATOR = 1
    ENGINEER = 2
    INSTALLER = 3
    SECADM = 4
    SECAUD = 5
    RBACMNT = 6


CauseType = enum.Enum('CauseType', [
    *((cause.name, cause.value) for cause in iec101.CauseType),
    ('AUTHENTICATION', 14),
    ('SESSION_KEY_MAINTENANCE', 15),
    ('UPDATE_KEY_MAINTENANCE', 16)])


class Cause(typing.NamedTuple):
    type: CauseType | OtherCauseType
    is_negative_confirm: bool
    is_test: bool
    originator_address: OriginatorAddress


class IoElement_S_IT_TC(typing.NamedTuple):
    association_id: AssociationId
    value: BinaryCounterValue


class IoElement_S_CH_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    mac_algorithm: MacAlgorithm | int
    """MAC algorithm can be value in range [0, 255]"""
    reason: int
    """reason in range [0, 255] - only valid value is 1"""
    data: util.Bytes
    """data length in range [4, 65535]"""


class IoElement_S_RP_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    mac: util.Bytes


class IoElement_S_AR_NA(typing.NamedTuple):
    asdu: util.Bytes
    sequence: SequenceNumber
    user: UserNumber
    mac: util.Bytes


class IoElement_S_KR_NA(typing.NamedTuple):
    user: UserNumber


class IoElement_S_KS_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    key_wrap_algorithm: KeyWrapAlgorithm | int
    """Key wrap algorithm can be value in range [0, 255]"""
    key_status: KeyStatus | int
    """Key status can be value in range [0, 255]"""
    mac_algorithm: MacAlgorithm | int
    """MAC algorithm can be value in range [0, 255]"""
    data: util.Bytes
    """data length in range [8, 65535]"""
    mac: util.Bytes


class IoElement_S_KC_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    wrapped_key: util.Bytes
    """wrapped key length in range [8, 65535]"""


class IoElement_S_ER_NA(typing.NamedTuple):
    challenge_sequence: SequenceNumber
    key_change_sequence: SequenceNumber
    user: UserNumber
    association_id: AssociationId
    code: ErrorCode | int
    """Code can be value in range [0, 255]"""
    time: Time
    """Time size SEVEN"""
    text: util.Bytes
    """Text length in range [0, 65535]"""


class IoElement_S_UC_NA_X(typing.NamedTuple):
    key_change_method: KeyChangeMethod | int
    """Key change method can be value in range [0, 255]"""
    data: util.Bytes
    """Data length in range [0, 65535]"""


class IoElement_S_US_NA(typing.NamedTuple):
    key_change_method: KeyChangeMethod | int
    """Key change method can be value in range [0, 255]"""
    operation: Operation | int
    """Operation can be value in range [0, 255]"""
    sequence: SequenceNumber
    role: UserRole | int
    """Role can be value in range [0, 65535]"""
    role_expiry: int
    """Role expiry in range [0, 65535]"""
    name: util.Bytes
    """Name length in range [0, 65535]"""
    public_key: util.Bytes
    """Public key length in range [0, 65535]"""
    certification: util.Bytes
    """Certification length in range [0, 65535]"""


class IoElement_S_UQ_NA(typing.NamedTuple):
    key_change_method: KeyChangeMethod | int
    """Key change method can be value in range [0, 255]"""
    name: util.Bytes
    """Name length in range [0, 65535]"""
    data: util.Bytes
    """Data length in range [4, 65535]"""


class IoElement_S_UR_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    data: util.Bytes
    """Data length in range [4, 65535]"""


class IoElement_S_UK_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    encrypted_update_key: util.Bytes
    """Encrypted update key length in range [16, 65535]"""
    mac: util.Bytes


class IoElement_S_UA_NA(typing.NamedTuple):
    sequence: SequenceNumber
    user: UserNumber
    encrypted_update_key: util.Bytes
    """Encrypted update key length in range [16, 65535]"""
    signature: util.Bytes


class IoElement_S_UC_NA(typing.NamedTuple):
    mac: util.Bytes


IoElement: typing.TypeAlias = (IoElement_S_IT_TC |
                               IoElement_S_CH_NA |
                               IoElement_S_RP_NA |
                               IoElement_S_AR_NA |
                               IoElement_S_KR_NA |
                               IoElement_S_KS_NA |
                               IoElement_S_KC_NA |
                               IoElement_S_ER_NA |
                               IoElement_S_UC_NA_X |
                               IoElement_S_US_NA |
                               IoElement_S_UQ_NA |
                               IoElement_S_UR_NA |
                               IoElement_S_UK_NA |
                               IoElement_S_UA_NA |
                               IoElement_S_UC_NA)


class IO(typing.NamedTuple):
    address: IoAddress | None
    element: IoElement
    time: Time | None
    """Time size SEVEN"""


class ASDU(typing.NamedTuple):
    type: AsduType
    cause: Cause
    address: AsduAddress
    ios: list[IO]
