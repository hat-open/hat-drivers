from hat.drivers.iec61850.manager.common import *  # NOQA

from collections.abc import Collection
import enum
import typing

from hat.drivers.iec61850.manager.common import (DatasetRef,
                                                 ControlModel)


class Cdc(enum.Enum):
    SPS = 'SPS'
    DPS = 'DPS'
    INS = 'INS'
    ENS = 'ENS'
    ACT = 'ACT'
    ACD = 'ACD'
    SEC = 'SEC'
    BCR = 'BCR'
    HST = 'HST'
    VSS = 'VSS'
    MV = 'MV'
    CMV = 'CMV'
    SAV = 'SAV'
    WYE = 'WYE'
    DEL = 'DEL'
    SEQ = 'SEQ'
    HMV = 'HMV'
    HWYE = 'HWYE'
    HDEL = 'HDEL'
    SPC = 'SPC'
    DPC = 'DPC'
    INC = 'INC'
    ENC = 'ENC'
    BSC = 'BSC'
    ISC = 'ISC'
    APC = 'APC'
    BAC = 'BAC'
    SPG = 'SPG'
    ING = 'ING'
    ENG = 'ENG'
    ORG = 'ORG'
    TSG = 'TSG'
    CUG = 'CUG'
    VSG = 'VSG'
    ASG = 'ASG'
    CURVE = 'CURVE'
    CSG = 'CSG'
    DPL = 'DPL'
    LPL = 'LPL'
    CSD = 'CSD'


class CdcDataRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    names: tuple[str | int, ...]


class CdcDataValue(typing.NamedTuple):
    path: tuple[str | int, ...]
    writable: bool


class CdcData(typing.NamedTuple):
    cdc: Cdc
    datasets: Collection[DatasetRef]
    values: Collection[CdcDataValue]


class CdcCommand(typing.NamedTuple):
    cdc: Cdc
    model: ControlModel
    with_operate_time: bool
