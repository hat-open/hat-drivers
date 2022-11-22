import enum
import typing

from hat.drivers.iec60870.msgs import iec101

from hat.drivers.iec60870.msgs.common import *  # NOQA
from hat.drivers.iec60870.msgs.common import Time


OriginatorAddress = int
"""Originator address in range [0, 255]"""

AsduAddress = int
"""ASDU address in range [0, 65535]"""

IoAddress = int
"""IO address in range [0, 16777215]"""


class AsduType(enum.Enum):
    M_SP_NA = iec101.common.AsduType.M_SP_NA.value
    M_DP_NA = iec101.common.AsduType.M_DP_NA.value
    M_ST_NA = iec101.common.AsduType.M_ST_NA.value
    M_BO_NA = iec101.common.AsduType.M_BO_NA.value
    M_ME_NA = iec101.common.AsduType.M_ME_NA.value
    M_ME_NB = iec101.common.AsduType.M_ME_NB.value
    M_ME_NC = iec101.common.AsduType.M_ME_NC.value
    M_IT_NA = iec101.common.AsduType.M_IT_NA.value
    M_PS_NA = iec101.common.AsduType.M_PS_NA.value
    M_ME_ND = iec101.common.AsduType.M_ME_ND.value
    M_SP_TB = iec101.common.AsduType.M_SP_TB.value
    M_DP_TB = iec101.common.AsduType.M_DP_TB.value
    M_ST_TB = iec101.common.AsduType.M_ST_TB.value
    M_BO_TB = iec101.common.AsduType.M_BO_TB.value
    M_ME_TD = iec101.common.AsduType.M_ME_TD.value
    M_ME_TE = iec101.common.AsduType.M_ME_TE.value
    M_ME_TF = iec101.common.AsduType.M_ME_TF.value
    M_IT_TB = iec101.common.AsduType.M_IT_TB.value
    M_EP_TD = iec101.common.AsduType.M_EP_TD.value
    M_EP_TE = iec101.common.AsduType.M_EP_TE.value
    M_EP_TF = iec101.common.AsduType.M_EP_TF.value
    C_SC_NA = iec101.common.AsduType.C_SC_NA.value
    C_DC_NA = iec101.common.AsduType.C_DC_NA.value
    C_RC_NA = iec101.common.AsduType.C_RC_NA.value
    C_SE_NA = iec101.common.AsduType.C_SE_NA.value
    C_SE_NB = iec101.common.AsduType.C_SE_NB.value
    C_SE_NC = iec101.common.AsduType.C_SE_NC.value
    C_BO_NA = iec101.common.AsduType.C_BO_NA.value
    C_SC_TA = 58
    C_DC_TA = 59
    C_RC_TA = 60
    C_SE_TA = 61
    C_SE_TB = 62
    C_SE_TC = 63
    C_BO_TA = 64
    M_EI_NA = iec101.common.AsduType.M_EI_NA.value
    C_IC_NA = iec101.common.AsduType.C_IC_NA.value
    C_CI_NA = iec101.common.AsduType.C_CI_NA.value
    C_RD_NA = iec101.common.AsduType.C_RD_NA.value
    C_CS_NA = iec101.common.AsduType.C_CS_NA.value
    C_RP_NA = iec101.common.AsduType.C_RP_NA.value
    C_TS_TA = 107
    P_ME_NA = iec101.common.AsduType.P_ME_NA.value
    P_ME_NB = iec101.common.AsduType.P_ME_NB.value
    P_ME_NC = iec101.common.AsduType.P_ME_NC.value
    P_AC_NA = iec101.common.AsduType.P_AC_NA.value
    F_FR_NA = iec101.common.AsduType.F_FR_NA.value
    F_SR_NA = iec101.common.AsduType.F_SR_NA.value
    F_SC_NA = iec101.common.AsduType.F_SC_NA.value
    F_LS_NA = iec101.common.AsduType.F_LS_NA.value
    F_AF_NA = iec101.common.AsduType.F_AF_NA.value
    F_SG_NA = iec101.common.AsduType.F_SG_NA.value
    F_DR_TA = iec101.common.AsduType.F_DR_TA.value


CauseType = iec101.common.CauseType
OtherCauseType = iec101.common.OtherCauseType
Cause = iec101.common.Cause

QualityType = iec101.common.QualityType
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

IoElement_M_SP_NA = iec101.common.IoElement_M_SP_NA
IoElement_M_DP_NA = iec101.common.IoElement_M_DP_NA
IoElement_M_ST_NA = iec101.common.IoElement_M_ST_NA
IoElement_M_BO_NA = iec101.common.IoElement_M_BO_NA
IoElement_M_ME_NA = iec101.common.IoElement_M_ME_NA
IoElement_M_ME_NB = iec101.common.IoElement_M_ME_NB
IoElement_M_ME_NC = iec101.common.IoElement_M_ME_NC
IoElement_M_IT_NA = iec101.common.IoElement_M_IT_NA
IoElement_M_PS_NA = iec101.common.IoElement_M_PS_NA
IoElement_M_ME_ND = iec101.common.IoElement_M_ME_ND
IoElement_M_SP_TB = iec101.common.IoElement_M_SP_TB
IoElement_M_DP_TB = iec101.common.IoElement_M_DP_TB
IoElement_M_ST_TB = iec101.common.IoElement_M_ST_TB
IoElement_M_BO_TB = iec101.common.IoElement_M_BO_TB
IoElement_M_ME_TD = iec101.common.IoElement_M_ME_TD
IoElement_M_ME_TE = iec101.common.IoElement_M_ME_TE
IoElement_M_ME_TF = iec101.common.IoElement_M_ME_TF
IoElement_M_IT_TB = iec101.common.IoElement_M_IT_TB
IoElement_M_EP_TD = iec101.common.IoElement_M_EP_TD
IoElement_M_EP_TE = iec101.common.IoElement_M_EP_TE
IoElement_M_EP_TF = iec101.common.IoElement_M_EP_TF
IoElement_C_SC_NA = iec101.common.IoElement_C_SC_NA
IoElement_C_DC_NA = iec101.common.IoElement_C_DC_NA
IoElement_C_RC_NA = iec101.common.IoElement_C_RC_NA
IoElement_C_SE_NA = iec101.common.IoElement_C_SE_NA
IoElement_C_SE_NB = iec101.common.IoElement_C_SE_NB
IoElement_C_SE_NC = iec101.common.IoElement_C_SE_NC
IoElement_C_BO_NA = iec101.common.IoElement_C_BO_NA
IoElement_M_EI_NA = iec101.common.IoElement_M_EI_NA
IoElement_C_IC_NA = iec101.common.IoElement_C_IC_NA
IoElement_C_CI_NA = iec101.common.IoElement_C_CI_NA
IoElement_C_RD_NA = iec101.common.IoElement_C_RD_NA
IoElement_C_CS_NA = iec101.common.IoElement_C_CS_NA
IoElement_C_RP_NA = iec101.common.IoElement_C_RP_NA
IoElement_P_ME_NA = iec101.common.IoElement_P_ME_NA
IoElement_P_ME_NB = iec101.common.IoElement_P_ME_NB
IoElement_P_ME_NC = iec101.common.IoElement_P_ME_NC
IoElement_P_AC_NA = iec101.common.IoElement_P_AC_NA
IoElement_F_FR_NA = iec101.common.IoElement_F_FR_NA
IoElement_F_SR_NA = iec101.common.IoElement_F_SR_NA
IoElement_F_SC_NA = iec101.common.IoElement_F_SC_NA
IoElement_F_LS_NA = iec101.common.IoElement_F_LS_NA
IoElement_F_AF_NA = iec101.common.IoElement_F_AF_NA
IoElement_F_SG_NA = iec101.common.IoElement_F_SG_NA
IoElement_F_DR_TA = iec101.common.IoElement_F_DR_TA


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


IoElement = typing.Union[IoElement_M_SP_NA,
                         IoElement_M_DP_NA,
                         IoElement_M_ST_NA,
                         IoElement_M_BO_NA,
                         IoElement_M_ME_NA,
                         IoElement_M_ME_NB,
                         IoElement_M_ME_NC,
                         IoElement_M_IT_NA,
                         IoElement_M_PS_NA,
                         IoElement_M_ME_ND,
                         IoElement_M_SP_TB,
                         IoElement_M_DP_TB,
                         IoElement_M_ST_TB,
                         IoElement_M_BO_TB,
                         IoElement_M_ME_TD,
                         IoElement_M_ME_TE,
                         IoElement_M_ME_TF,
                         IoElement_M_IT_TB,
                         IoElement_M_EP_TD,
                         IoElement_M_EP_TE,
                         IoElement_M_EP_TF,
                         IoElement_C_SC_NA,
                         IoElement_C_DC_NA,
                         IoElement_C_RC_NA,
                         IoElement_C_SE_NA,
                         IoElement_C_SE_NB,
                         IoElement_C_SE_NC,
                         IoElement_C_BO_NA,
                         IoElement_C_SC_TA,
                         IoElement_C_DC_TA,
                         IoElement_C_RC_TA,
                         IoElement_C_SE_TA,
                         IoElement_C_SE_TB,
                         IoElement_C_SE_TC,
                         IoElement_C_BO_TA,
                         IoElement_M_EI_NA,
                         IoElement_C_IC_NA,
                         IoElement_C_CI_NA,
                         IoElement_C_RD_NA,
                         IoElement_C_CS_NA,
                         IoElement_C_RP_NA,
                         IoElement_C_TS_TA,
                         IoElement_P_ME_NA,
                         IoElement_P_ME_NB,
                         IoElement_P_ME_NC,
                         IoElement_P_AC_NA,
                         IoElement_F_FR_NA,
                         IoElement_F_SR_NA,
                         IoElement_F_SC_NA,
                         IoElement_F_LS_NA,
                         IoElement_F_AF_NA,
                         IoElement_F_SG_NA,
                         IoElement_F_DR_TA]


class IO(typing.NamedTuple):
    address: IoAddress
    elements: typing.List[IoElement]
    time: typing.Optional[Time]


class ASDU(typing.NamedTuple):
    type: AsduType
    cause: Cause
    address: AsduAddress
    ios: typing.List[IO]
