import enum
import typing

from hat import util


SequenceNumber: typing.TypeAlias = int
"""sequence number in range [0, 0x7FFF]"""


class ApduFunction(enum.Enum):
    TESTFR_CON = 0x83
    TESTFR_ACT = 0x43
    STOPDT_CON = 0x23
    STOPDT_ACT = 0x13
    STARTDT_CON = 0x0B
    STARTDT_ACT = 0x07


class APDUI(typing.NamedTuple):
    ssn: SequenceNumber
    rsn: SequenceNumber
    data: util.Bytes


class APDUS(typing.NamedTuple):
    rsn: SequenceNumber


class APDUU(typing.NamedTuple):
    function: ApduFunction


APDU: typing.TypeAlias = APDUI | APDUS | APDUU
