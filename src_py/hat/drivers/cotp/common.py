import enum
import typing

from hat import util


class TpduType(enum.Enum):
    DT = 0xF0
    CR = 0xE0
    CC = 0xD0
    DR = 0x80
    ER = 0x70


class DT(typing.NamedTuple):
    """Data TPDU"""
    eot: bool
    """end of transmition flag"""
    data: util.Bytes


class CR(typing.NamedTuple):
    """Connection request TPDU"""
    src: int
    """connection reference selectet by initiator of connection request"""
    cls: int
    """transport protocol class"""
    calling_tsel: int | None
    """calling transport selector"""
    called_tsel: int | None
    """responding transport selector"""
    max_tpdu: int
    """max tpdu size in octets"""
    pref_max_tpdu: int
    """preferred max tpdu size in octets"""


class CC(typing.NamedTuple):
    """Connection confirm TPDU"""
    dst: int
    """connection reference selected by initiator of connection request"""
    src: int
    """connection reference selected by initiator of connection confirm"""
    cls: int
    """transport protocol class"""
    calling_tsel: int | None
    """calling transport selector"""
    called_tsel: int | None
    """responding transport selector"""
    max_tpdu: int
    """max tpdu size in octets"""
    pref_max_tpdu: int
    """preferred max tpdu size in octets"""


class DR(typing.NamedTuple):
    """Disconnect request TPDU"""
    dst: int
    """connection reference selected by remote entity"""
    src: int
    """connection reference selected by initiator of disconnect request"""
    reason: int
    """reason for disconnection"""


class ER(typing.NamedTuple):
    """Error TPDU"""
    dst: int
    """connection reference selected by remote entity"""
    cause: int
    """reject cause"""


Tpdu: typing.TypeAlias = DT | CR | CC | DR | ER
