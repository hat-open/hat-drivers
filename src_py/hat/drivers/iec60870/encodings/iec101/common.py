from hat.drivers.iec60870.encodings.common import *  # NOQA

import enum
import typing

from hat import util

from hat.drivers.iec60870.encodings.common import Time


class AsduTypeError(Exception):
    pass


OriginatorAddress: typing.TypeAlias = int
"""Originator address in range [0, 255] - 0 if not available"""

AsduAddress: typing.TypeAlias = int
"""ASDU address in range [0, 255] or [0, 65535]"""

IoAddress: typing.TypeAlias = int
"""IO address in range [0, 255] or [0, 65535] or [0, 16777215]"""

OtherCauseType: typing.TypeAlias = int
"""Other cause type in range [0, 63]"""


class AsduType(enum.Enum):
    M_SP_NA = 1
    M_SP_TA = 2
    M_DP_NA = 3
    M_DP_TA = 4
    M_ST_NA = 5
    M_ST_TA = 6
    M_BO_NA = 7
    M_BO_TA = 8
    M_ME_NA = 9
    M_ME_TA = 10
    M_ME_NB = 11
    M_ME_TB = 12
    M_ME_NC = 13
    M_ME_TC = 14
    M_IT_NA = 15
    M_IT_TA = 16
    M_EP_TA = 17
    M_EP_TB = 18
    M_EP_TC = 19
    M_PS_NA = 20
    M_ME_ND = 21
    M_SP_TB = 30
    M_DP_TB = 31
    M_ST_TB = 32
    M_BO_TB = 33
    M_ME_TD = 34
    M_ME_TE = 35
    M_ME_TF = 36
    M_IT_TB = 37
    M_EP_TD = 38
    M_EP_TE = 39
    M_EP_TF = 40
    C_SC_NA = 45
    C_DC_NA = 46
    C_RC_NA = 47
    C_SE_NA = 48
    C_SE_NB = 49
    C_SE_NC = 50
    C_BO_NA = 51
    M_EI_NA = 70
    C_IC_NA = 100
    C_CI_NA = 101
    C_RD_NA = 102
    C_CS_NA = 103
    C_TS_NA = 104
    C_RP_NA = 105
    C_CD_NA = 106
    P_ME_NA = 110
    P_ME_NB = 111
    P_ME_NC = 112
    P_AC_NA = 113
    F_FR_NA = 120
    F_SR_NA = 121
    F_SC_NA = 122
    F_LS_NA = 123
    F_AF_NA = 124
    F_SG_NA = 125
    F_DR_TA = 126


class CauseType(enum.Enum):
    UNDEFINED = 0
    PERIODIC = 1
    BACKGROUND_SCAN = 2
    SPONTANEOUS = 3
    INITIALIZED = 4
    REQUEST = 5
    ACTIVATION = 6
    ACTIVATION_CONFIRMATION = 7
    DEACTIVATION = 8
    DEACTIVATION_CONFIRMATION = 9
    ACTIVATION_TERMINATION = 10
    REMOTE_COMMAND = 11
    LOCAL_COMMAND = 12
    FILE_TRANSFER = 13
    INTERROGATED_STATION = 20
    INTERROGATED_GROUP01 = 21
    INTERROGATED_GROUP02 = 22
    INTERROGATED_GROUP03 = 23
    INTERROGATED_GROUP04 = 24
    INTERROGATED_GROUP05 = 25
    INTERROGATED_GROUP06 = 26
    INTERROGATED_GROUP07 = 27
    INTERROGATED_GROUP08 = 28
    INTERROGATED_GROUP09 = 29
    INTERROGATED_GROUP10 = 30
    INTERROGATED_GROUP11 = 31
    INTERROGATED_GROUP12 = 32
    INTERROGATED_GROUP13 = 33
    INTERROGATED_GROUP14 = 34
    INTERROGATED_GROUP15 = 35
    INTERROGATED_GROUP16 = 36
    INTERROGATED_COUNTER = 37
    INTERROGATED_COUNTER01 = 38
    INTERROGATED_COUNTER02 = 39
    INTERROGATED_COUNTER03 = 40
    INTERROGATED_COUNTER04 = 41
    UNKNOWN_TYPE = 44
    UNKNOWN_CAUSE = 45
    UNKNOWN_ASDU_ADDRESS = 46
    UNKNOWN_IO_ADDRESS = 47


class Cause(typing.NamedTuple):
    type: CauseType | OtherCauseType
    is_negative_confirm: bool
    is_test: bool
    originator_address: OriginatorAddress


class QualityType(enum.Enum):
    INDICATION = 0
    MEASUREMENT = 1
    COUNTER = 2
    PROTECTION = 3


class IndicationQuality(typing.NamedTuple):
    invalid: bool
    not_topical: bool
    substituted: bool
    blocked: bool


class MeasurementQuality(typing.NamedTuple):
    invalid: bool
    not_topical: bool
    substituted: bool
    blocked: bool
    overflow: bool


class CounterQuality(typing.NamedTuple):
    invalid: bool
    adjusted: bool
    overflow: bool
    sequence: int
    """sequence in range [0, 31]"""


class ProtectionQuality(typing.NamedTuple):
    invalid: bool
    not_topical: bool
    substituted: bool
    blocked: bool
    time_invalid: bool


Quality: typing.TypeAlias = (IndicationQuality |
                             MeasurementQuality |
                             CounterQuality |
                             ProtectionQuality)


class FreezeCode(enum.Enum):
    READ = 0
    FREEZE = 1
    FREEZE_AND_RESET = 2
    RESET = 3


class SingleValue(enum.Enum):
    OFF = 0
    ON = 1


class DoubleValue(enum.Enum):
    """DoubleDataValue

    `FAULT` stands for value 3, defined in the protocol as *INDETERMINATE*.
    This is in order to make it more distinguishable from ``INTERMEDIATE``.

    """
    INTERMEDIATE = 0
    OFF = 1
    ON = 2
    FAULT = 3


class RegulatingValue(enum.Enum):
    LOWER = 1
    HIGHER = 2


class StepPositionValue(typing.NamedTuple):
    value: int
    """value in range [-64, 63]"""
    transient: bool


class BitstringValue(typing.NamedTuple):
    value: util.Bytes
    """bitstring encoded as 4 bytes"""


class NormalizedValue(typing.NamedTuple):
    value: float
    """value in range [-1.0, 1.0)"""


class ScaledValue(typing.NamedTuple):
    value: int
    """value in range [-2^15, 2^15-1]"""


class FloatingValue(typing.NamedTuple):
    value: float


class BinaryCounterValue(typing.NamedTuple):
    value: int
    """value in range [-2^31, 2^31-1]"""


class ProtectionValue(enum.Enum):
    OFF = 1
    ON = 2


class ProtectionStartValue(typing.NamedTuple):
    general: bool
    l1: bool
    l2: bool
    l3: bool
    ie: bool
    reverse: bool


class ProtectionCommandValue(typing.NamedTuple):
    general: bool
    l1: bool
    l2: bool
    l3: bool


class StatusValue(typing.NamedTuple):
    value: list[bool]
    """value length is 16"""
    change: list[bool]
    """change length is 16"""


class IoElement_M_SP_NA(typing.NamedTuple):
    value: SingleValue
    quality: IndicationQuality


class IoElement_M_SP_TA(typing.NamedTuple):
    value: SingleValue
    quality: IndicationQuality


class IoElement_M_DP_NA(typing.NamedTuple):
    value: DoubleValue
    quality: IndicationQuality


class IoElement_M_DP_TA(typing.NamedTuple):
    value: DoubleValue
    quality: IndicationQuality


class IoElement_M_ST_NA(typing.NamedTuple):
    value: StepPositionValue
    quality: MeasurementQuality


class IoElement_M_ST_TA(typing.NamedTuple):
    value: StepPositionValue
    quality: MeasurementQuality


class IoElement_M_BO_NA(typing.NamedTuple):
    value: BitstringValue
    quality: MeasurementQuality


class IoElement_M_BO_TA(typing.NamedTuple):
    value: BitstringValue
    quality: MeasurementQuality


class IoElement_M_ME_NA(typing.NamedTuple):
    value: NormalizedValue
    quality: MeasurementQuality


class IoElement_M_ME_TA(typing.NamedTuple):
    value: NormalizedValue
    quality: MeasurementQuality


class IoElement_M_ME_NB(typing.NamedTuple):
    value: ScaledValue
    quality: MeasurementQuality


class IoElement_M_ME_TB(typing.NamedTuple):
    value: ScaledValue
    quality: MeasurementQuality


class IoElement_M_ME_NC(typing.NamedTuple):
    value: FloatingValue
    quality: MeasurementQuality


class IoElement_M_ME_TC(typing.NamedTuple):
    value: FloatingValue
    quality: MeasurementQuality


class IoElement_M_IT_NA(typing.NamedTuple):
    value: BinaryCounterValue
    quality: CounterQuality


class IoElement_M_IT_TA(typing.NamedTuple):
    value: BinaryCounterValue
    quality: CounterQuality


class IoElement_M_EP_TA(typing.NamedTuple):
    value: ProtectionValue
    quality: ProtectionQuality
    elapsed_time: int
    """elapsed_time in range [0, 65535]"""


class IoElement_M_EP_TB(typing.NamedTuple):
    value: ProtectionStartValue
    quality: ProtectionQuality
    duration_time: int
    """duration_time in range [0, 65535]"""


class IoElement_M_EP_TC(typing.NamedTuple):
    value: ProtectionCommandValue
    quality: ProtectionQuality
    operating_time: int
    """operating_time in range [0, 65535]"""


class IoElement_M_PS_NA(typing.NamedTuple):
    value: StatusValue
    quality: MeasurementQuality


class IoElement_M_ME_ND(typing.NamedTuple):
    value: NormalizedValue


class IoElement_M_SP_TB(typing.NamedTuple):
    value: SingleValue
    quality: IndicationQuality


class IoElement_M_DP_TB(typing.NamedTuple):
    value: DoubleValue
    quality: IndicationQuality


class IoElement_M_ST_TB(typing.NamedTuple):
    value: StepPositionValue
    quality: MeasurementQuality


class IoElement_M_BO_TB(typing.NamedTuple):
    value: BitstringValue
    quality: MeasurementQuality


class IoElement_M_ME_TD(typing.NamedTuple):
    value: NormalizedValue
    quality: MeasurementQuality


class IoElement_M_ME_TE(typing.NamedTuple):
    value: ScaledValue
    quality: MeasurementQuality


class IoElement_M_ME_TF(typing.NamedTuple):
    value: FloatingValue
    quality: MeasurementQuality


class IoElement_M_IT_TB(typing.NamedTuple):
    value: BinaryCounterValue
    quality: CounterQuality


class IoElement_M_EP_TD(typing.NamedTuple):
    value: ProtectionValue
    quality: ProtectionQuality
    elapsed_time: int
    """elapsed_time in range [0, 65535]"""


class IoElement_M_EP_TE(typing.NamedTuple):
    value: ProtectionStartValue
    quality: ProtectionQuality
    duration_time: int
    """duration_time in range [0, 65535]"""


class IoElement_M_EP_TF(typing.NamedTuple):
    value: ProtectionCommandValue
    quality: ProtectionQuality
    operating_time: int
    """operating_time in range [0, 65535]"""


class IoElement_C_SC_NA(typing.NamedTuple):
    value: SingleValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class IoElement_C_DC_NA(typing.NamedTuple):
    value: DoubleValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class IoElement_C_RC_NA(typing.NamedTuple):
    value: RegulatingValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class IoElement_C_SE_NA(typing.NamedTuple):
    value: NormalizedValue
    select: bool


class IoElement_C_SE_NB(typing.NamedTuple):
    value: ScaledValue
    select: bool


class IoElement_C_SE_NC(typing.NamedTuple):
    value: FloatingValue
    select: bool


class IoElement_C_BO_NA(typing.NamedTuple):
    value: BitstringValue


class IoElement_M_EI_NA(typing.NamedTuple):
    param_change: bool
    cause: int
    """cause in range [0, 127]"""


class IoElement_C_IC_NA(typing.NamedTuple):
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_C_CI_NA(typing.NamedTuple):
    request: int
    """request in range [0, 63]"""
    freeze: FreezeCode


class IoElement_C_RD_NA(typing.NamedTuple):
    pass


class IoElement_C_CS_NA(typing.NamedTuple):
    time: Time
    """time size is SEVEN"""


class IoElement_C_TS_NA(typing.NamedTuple):
    pass


class IoElement_C_RP_NA(typing.NamedTuple):
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_C_CD_NA(typing.NamedTuple):
    time: int
    """time in range [0, 65535]"""


class IoElement_P_ME_NA(typing.NamedTuple):
    value: NormalizedValue
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_P_ME_NB(typing.NamedTuple):
    value: ScaledValue
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_P_ME_NC(typing.NamedTuple):
    value: FloatingValue
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_P_AC_NA(typing.NamedTuple):
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_F_FR_NA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    file_length: int
    """file_length in range [0, 16777215]"""
    ready: bool


class IoElement_F_SR_NA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    section_name: int
    """section_name in range [0, 255]"""
    section_length: int
    """section_length in range [0, 16777215]"""
    ready: bool


class IoElement_F_SC_NA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    section_name: int
    """section_name in range [0, 255]"""
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_F_LS_NA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    section_name: int
    """section_name in range [0, 255]"""
    last_qualifier: int
    """last_qualifier in range [0, 255]"""
    checksum: int
    """checksum in range [0, 255]"""


class IoElement_F_AF_NA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    section_name: int
    """section_name in range [0, 255]"""
    qualifier: int
    """qualifier in range [0, 255]"""


class IoElement_F_SG_NA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    section_name: int
    """section_name in range [0, 255]"""
    segment: util.Bytes


class IoElement_F_DR_TA(typing.NamedTuple):
    file_name: int
    """file_name in range [0, 65535]"""
    file_length: int
    """file_length in range [0, 16777215]"""
    more_follows: bool
    is_directory: bool
    transfer_active: bool
    creation_time: Time


IoElement: typing.TypeAlias = (IoElement_M_SP_NA |
                               IoElement_M_SP_TA |
                               IoElement_M_DP_NA |
                               IoElement_M_DP_TA |
                               IoElement_M_ST_NA |
                               IoElement_M_ST_TA |
                               IoElement_M_BO_NA |
                               IoElement_M_BO_TA |
                               IoElement_M_ME_NA |
                               IoElement_M_ME_TA |
                               IoElement_M_ME_NB |
                               IoElement_M_ME_TB |
                               IoElement_M_ME_NC |
                               IoElement_M_ME_TC |
                               IoElement_M_IT_NA |
                               IoElement_M_IT_TA |
                               IoElement_M_EP_TA |
                               IoElement_M_EP_TB |
                               IoElement_M_EP_TC |
                               IoElement_M_PS_NA |
                               IoElement_M_ME_ND |
                               IoElement_M_SP_TB |
                               IoElement_M_DP_TB |
                               IoElement_M_ST_TB |
                               IoElement_M_BO_TB |
                               IoElement_M_ME_TD |
                               IoElement_M_ME_TE |
                               IoElement_M_ME_TF |
                               IoElement_M_IT_TB |
                               IoElement_M_EP_TD |
                               IoElement_M_EP_TE |
                               IoElement_M_EP_TF |
                               IoElement_C_SC_NA |
                               IoElement_C_DC_NA |
                               IoElement_C_RC_NA |
                               IoElement_C_SE_NA |
                               IoElement_C_SE_NB |
                               IoElement_C_SE_NC |
                               IoElement_C_BO_NA |
                               IoElement_M_EI_NA |
                               IoElement_C_IC_NA |
                               IoElement_C_CI_NA |
                               IoElement_C_RD_NA |
                               IoElement_C_CS_NA |
                               IoElement_C_TS_NA |
                               IoElement_C_RP_NA |
                               IoElement_C_CD_NA |
                               IoElement_P_ME_NA |
                               IoElement_P_ME_NB |
                               IoElement_P_ME_NC |
                               IoElement_P_AC_NA |
                               IoElement_F_FR_NA |
                               IoElement_F_SR_NA |
                               IoElement_F_SC_NA |
                               IoElement_F_LS_NA |
                               IoElement_F_AF_NA |
                               IoElement_F_SG_NA |
                               IoElement_F_DR_TA)


class IO(typing.NamedTuple):
    address: IoAddress
    elements: list[IoElement]
    time: Time | None


class ASDU(typing.NamedTuple):
    type: AsduType
    cause: Cause
    address: AsduAddress
    ios: list[IO]
