import enum
import typing


Bytes = typing.Union[bytes, bytearray, memoryview]


class ApduFunction(enum.Enum):
    TESTFR_CON = 0x83
    TESTFR_ACT = 0x43
    STOPDT_CON = 0x23
    STOPDT_ACT = 0x13
    STARTDT_CON = 0x0B
    STARTDT_ACT = 0x07


class APDUI(typing.NamedTuple):
    ssn: int
    rsn: int
    data: Bytes


class APDUS(typing.NamedTuple):
    rsn: int


class APDUU(typing.NamedTuple):
    function: ApduFunction


APDU = typing.Union[APDUI, APDUS, APDUU]
