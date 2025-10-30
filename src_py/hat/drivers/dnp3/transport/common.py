import typing

from hat import util


class Segment(typing.NamedTuple):
    first: bool
    last: bool
    sequence: int
    data: util.Bytes
