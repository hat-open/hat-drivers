from hat.drivers.common import *  # NOQA

from collections.abc import Collection
import enum
import typing

from hat import util


class ReqIdentifier(enum.Enum):
    STATUS_MESSAGE = 2
    PARAMETER_ASSIGNMENT = 3
    COMMAND = 5
    RETRIEVAL_ERROR_MESSAGE = 17
    RETRIEVAL_STATUS_MESSAGE = 18
    RETRIEVAL_PARAMETER = 19
    RETRIEVAL_RESULT_MESSAGE = 20
    RETRIEVAL_COMMAND_STATUS = 21


class ResIdentifier(enum.Enum):
    ERROR_MESSAGE = 1
    STATUS_MESSAGE = 2
    PARAMETER_MESSAGE = 3
    RESULT_MESSAGE = 4
    COMMAND_RESPONSE = 5
    ERROR_MESSAGE_FROM_BUFFER = 33
    STATUS_MESSAGE_FROM_BUFFER = 34
    RESULT_MESSAGE_FROM_BUFFER = 36
    COMMAND_RESPONSE_FROM_BUFFER = 37


OtherIdentifier: typing.TypeAlias = int
"""Other identifier in range [0, 127]"""


class DT(typing.NamedTuple):
    channel: int
    type: int
    data: util.Bytes


class ReqMsg(typing.NamedTuple):
    function_group: int
    identifier: ReqIdentifier | OtherIdentifier
    job_number: int
    dts: Collection[DT]


class ResMsg(typing.NamedTuple):
    function_group: int
    identifier: ResIdentifier | OtherIdentifier
    job_number: int
    dts: Collection[DT]


Msg: typing.TypeAlias = ReqMsg | ResMsg


class GeneralMsg(typing.NamedTuple):
    node: int
    msgs: Collection[Msg]


class BufferIdentifier(enum.Enum):
    ERROR = 1
    STATUS = 2
    PARAMETER = 3
    RESULT = 4
    COMMAND = 5


class BufferKey(typing.NamedTuple):
    identifier: BufferIdentifier
    function_group: int
    channel: int
    dt_type: int


Buffer = dict[BufferKey, util.Bytes]
