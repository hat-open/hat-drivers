import enum
import typing

from hat import util


class SpduType(enum.Enum):
    CN = 13
    AC = 14
    RF = 12
    FN = 9
    DN = 10
    NF = 8
    AB = 25
    DT = 1


class Spdu(typing.NamedTuple):
    type: SpduType
    extended_spdus: bool | None = None
    version_number: int | None = None
    transport_disconnect: bool | None = None
    requirements: util.Bytes | None = None
    beginning: bool | None = None
    end: bool | None = None
    calling_ssel: int | None = None
    called_ssel: int | None = None
    user_data: util.Bytes | None = None
    data: util.Bytes = b''


give_tokens_spdu_bytes: util.Bytes = b'\x01\x00'
