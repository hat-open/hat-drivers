from hat.drivers.iec60870.encodings.common import *  # NOQA

import enum
import typing

from hat.drivers.iec60870.encodings import iec101
from hat.drivers.iec60870.encodings.common import Time


AsduTypeError: typing.TypeAlias = iec101.AsduTypeError


OriginatorAddress: typing.TypeAlias = int
"""Originator address in range [0, 255] - 0 if not available"""

AsduAddress: typing.TypeAlias = int
"""ASDU address in range [0, 65535]"""

IoAddress: typing.TypeAlias = int
"""IO address in range [0, 16777215]"""


class AsduType(enum.Enum):
    M_SP_NA = iec101.AsduType.M_SP_NA.value
    M_DP_NA = iec101.AsduType.M_DP_NA.value
    M_ST_NA = iec101.AsduType.M_ST_NA.value
    M_BO_NA = iec101.AsduType.M_BO_NA.value
    M_ME_NA = iec101.AsduType.M_ME_NA.value
    M_ME_NB = iec101.AsduType.M_ME_NB.value
    M_ME_NC = iec101.AsduType.M_ME_NC.value
    M_IT_NA = iec101.AsduType.M_IT_NA.value
    M_PS_NA = iec101.AsduType.M_PS_NA.value
    M_ME_ND = iec101.AsduType.M_ME_ND.value
    M_SP_TB = iec101.AsduType.M_SP_TB.value
    M_DP_TB = iec101.AsduType.M_DP_TB.value
    M_ST_TB = iec101.AsduType.M_ST_TB.value
    M_BO_TB = iec101.AsduType.M_BO_TB.value
    M_ME_TD = iec101.AsduType.M_ME_TD.value
    M_ME_TE = iec101.AsduType.M_ME_TE.value
    M_ME_TF = iec101.AsduType.M_ME_TF.value
    M_IT_TB = iec101.AsduType.M_IT_TB.value
    M_EP_TD = iec101.AsduType.M_EP_TD.value
    M_EP_TE = iec101.AsduType.M_EP_TE.value
    M_EP_TF = iec101.AsduType.M_EP_TF.value
    C_SC_NA = iec101.AsduType.C_SC_NA.value
    C_DC_NA = iec101.AsduType.C_DC_NA.value
    C_RC_NA = iec101.AsduType.C_RC_NA.value
    C_SE_NA = iec101.AsduType.C_SE_NA.value
    C_SE_NB = iec101.AsduType.C_SE_NB.value
    C_SE_NC = iec101.AsduType.C_SE_NC.value
    C_BO_NA = iec101.AsduType.C_BO_NA.value
    C_SC_TA = 58
    C_DC_TA = 59
    C_RC_TA = 60
    C_SE_TA = 61
    C_SE_TB = 62
    C_SE_TC = 63
    C_BO_TA = 64
    M_EI_NA = iec101.AsduType.M_EI_NA.value
    C_IC_NA = iec101.AsduType.C_IC_NA.value
    C_CI_NA = iec101.AsduType.C_CI_NA.value
    C_RD_NA = iec101.AsduType.C_RD_NA.value
    C_CS_NA = iec101.AsduType.C_CS_NA.value
    C_RP_NA = iec101.AsduType.C_RP_NA.value
    C_TS_TA = 107
    P_ME_NA = iec101.AsduType.P_ME_NA.value
    P_ME_NB = iec101.AsduType.P_ME_NB.value
    P_ME_NC = iec101.AsduType.P_ME_NC.value
    P_AC_NA = iec101.AsduType.P_AC_NA.value
    F_FR_NA = iec101.AsduType.F_FR_NA.value
    F_SR_NA = iec101.AsduType.F_SR_NA.value
    F_SC_NA = iec101.AsduType.F_SC_NA.value
    F_LS_NA = iec101.AsduType.F_LS_NA.value
    F_AF_NA = iec101.AsduType.F_AF_NA.value
    F_SG_NA = iec101.AsduType.F_SG_NA.value
    F_DR_TA = iec101.AsduType.F_DR_TA.value


CauseType: typing.TypeAlias = iec101.CauseType
OtherCauseType: typing.TypeAlias = iec101.OtherCauseType
Cause: typing.TypeAlias = iec101.Cause

QualityType: typing.TypeAlias = iec101.QualityType
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

IoElement_M_SP_NA: typing.TypeAlias = iec101.IoElement_M_SP_NA
IoElement_M_DP_NA: typing.TypeAlias = iec101.IoElement_M_DP_NA
IoElement_M_ST_NA: typing.TypeAlias = iec101.IoElement_M_ST_NA
IoElement_M_BO_NA: typing.TypeAlias = iec101.IoElement_M_BO_NA
IoElement_M_ME_NA: typing.TypeAlias = iec101.IoElement_M_ME_NA
IoElement_M_ME_NB: typing.TypeAlias = iec101.IoElement_M_ME_NB
IoElement_M_ME_NC: typing.TypeAlias = iec101.IoElement_M_ME_NC
IoElement_M_IT_NA: typing.TypeAlias = iec101.IoElement_M_IT_NA
IoElement_M_PS_NA: typing.TypeAlias = iec101.IoElement_M_PS_NA
IoElement_M_ME_ND: typing.TypeAlias = iec101.IoElement_M_ME_ND
IoElement_M_SP_TB: typing.TypeAlias = iec101.IoElement_M_SP_TB
IoElement_M_DP_TB: typing.TypeAlias = iec101.IoElement_M_DP_TB
IoElement_M_ST_TB: typing.TypeAlias = iec101.IoElement_M_ST_TB
IoElement_M_BO_TB: typing.TypeAlias = iec101.IoElement_M_BO_TB
IoElement_M_ME_TD: typing.TypeAlias = iec101.IoElement_M_ME_TD
IoElement_M_ME_TE: typing.TypeAlias = iec101.IoElement_M_ME_TE
IoElement_M_ME_TF: typing.TypeAlias = iec101.IoElement_M_ME_TF
IoElement_M_IT_TB: typing.TypeAlias = iec101.IoElement_M_IT_TB
IoElement_M_EP_TD: typing.TypeAlias = iec101.IoElement_M_EP_TD
IoElement_M_EP_TE: typing.TypeAlias = iec101.IoElement_M_EP_TE
IoElement_M_EP_TF: typing.TypeAlias = iec101.IoElement_M_EP_TF
IoElement_C_SC_NA: typing.TypeAlias = iec101.IoElement_C_SC_NA
IoElement_C_DC_NA: typing.TypeAlias = iec101.IoElement_C_DC_NA
IoElement_C_RC_NA: typing.TypeAlias = iec101.IoElement_C_RC_NA
IoElement_C_SE_NA: typing.TypeAlias = iec101.IoElement_C_SE_NA
IoElement_C_SE_NB: typing.TypeAlias = iec101.IoElement_C_SE_NB
IoElement_C_SE_NC: typing.TypeAlias = iec101.IoElement_C_SE_NC
IoElement_C_BO_NA: typing.TypeAlias = iec101.IoElement_C_BO_NA
IoElement_M_EI_NA: typing.TypeAlias = iec101.IoElement_M_EI_NA
IoElement_C_IC_NA: typing.TypeAlias = iec101.IoElement_C_IC_NA
IoElement_C_CI_NA: typing.TypeAlias = iec101.IoElement_C_CI_NA
IoElement_C_RD_NA: typing.TypeAlias = iec101.IoElement_C_RD_NA
IoElement_C_CS_NA: typing.TypeAlias = iec101.IoElement_C_CS_NA
IoElement_C_RP_NA: typing.TypeAlias = iec101.IoElement_C_RP_NA
IoElement_P_ME_NA: typing.TypeAlias = iec101.IoElement_P_ME_NA
IoElement_P_ME_NB: typing.TypeAlias = iec101.IoElement_P_ME_NB
IoElement_P_ME_NC: typing.TypeAlias = iec101.IoElement_P_ME_NC
IoElement_P_AC_NA: typing.TypeAlias = iec101.IoElement_P_AC_NA
IoElement_F_FR_NA: typing.TypeAlias = iec101.IoElement_F_FR_NA
IoElement_F_SR_NA: typing.TypeAlias = iec101.IoElement_F_SR_NA
IoElement_F_SC_NA: typing.TypeAlias = iec101.IoElement_F_SC_NA
IoElement_F_LS_NA: typing.TypeAlias = iec101.IoElement_F_LS_NA
IoElement_F_AF_NA: typing.TypeAlias = iec101.IoElement_F_AF_NA
IoElement_F_SG_NA: typing.TypeAlias = iec101.IoElement_F_SG_NA
IoElement_F_DR_TA: typing.TypeAlias = iec101.IoElement_F_DR_TA


class IoElement_C_SC_TA(typing.NamedTuple):
    value: SingleValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class IoElement_C_DC_TA(typing.NamedTuple):
    value: DoubleValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class IoElement_C_RC_TA(typing.NamedTuple):
    value: RegulatingValue
    select: bool
    qualifier: int
    """qualifier in range [0, 31]"""


class IoElement_C_SE_TA(typing.NamedTuple):
    value: NormalizedValue
    select: bool


class IoElement_C_SE_TB(typing.NamedTuple):
    value: ScaledValue
    select: bool


class IoElement_C_SE_TC(typing.NamedTuple):
    value: FloatingValue
    select: bool


class IoElement_C_BO_TA(typing.NamedTuple):
    value: BitstringValue


class IoElement_C_TS_TA(typing.NamedTuple):
    counter: int
    """counter in range [0, 65535]"""


IoElement: typing.TypeAlias = (IoElement_M_SP_NA |
                               IoElement_M_DP_NA |
                               IoElement_M_ST_NA |
                               IoElement_M_BO_NA |
                               IoElement_M_ME_NA |
                               IoElement_M_ME_NB |
                               IoElement_M_ME_NC |
                               IoElement_M_IT_NA |
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
                               IoElement_C_SC_TA |
                               IoElement_C_DC_TA |
                               IoElement_C_RC_TA |
                               IoElement_C_SE_TA |
                               IoElement_C_SE_TB |
                               IoElement_C_SE_TC |
                               IoElement_C_BO_TA |
                               IoElement_M_EI_NA |
                               IoElement_C_IC_NA |
                               IoElement_C_CI_NA |
                               IoElement_C_RD_NA |
                               IoElement_C_CS_NA |
                               IoElement_C_RP_NA |
                               IoElement_C_TS_TA |
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
