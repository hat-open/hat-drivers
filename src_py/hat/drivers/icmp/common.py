from hat.drivers.common import *  # NOQA

import typing

from hat import util


class EchoMsg(typing.NamedTuple):
    is_reply: bool
    identifier: int
    sequence_number: int
    data: util.Bytes


Msg: typing.TypeAlias = EchoMsg


class EndpointInfo(typing.NamedTuple):
    name: str | None
    local_host: str
