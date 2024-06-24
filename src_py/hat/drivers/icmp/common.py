import typing

from hat import util


class EchoMsg(typing.NamedTuple):
    is_reply: bool
    identifier: int
    sequence_number: int
    data: util.Bytes


Msg: typing.TypeAlias = EchoMsg
