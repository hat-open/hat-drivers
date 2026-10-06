from hat.drivers.common import *  # NOQA

import enum
import typing

from hat import util


Address: typing.TypeAlias = int
"""addres is 0 or in range [0, 255]"""


class Priority(enum.Enum):
    CLASS_1 = 0
    CLASS_2 = 1


class ReqFunction(enum.Enum):
    RESET_UNIT = 0
    RESET_COMMUNICATION = 1
    SEND_DATA = 3
    SEND_DATA_NO_RES = 4
    SEND_TEST = 7
    REQ_DATA_1_OR_2 = 8
    REQ_STATUS = 9
    REQ_DATA_1 = 10
    REQ_DATA_2 = 11
    REQ_TEST = 15


class ResFunction(enum.Enum):
    RESET_ACK = 0
    REJECT = 1
    RES_DATA = 8
    RES_ACK = 9
    RES_REJECT = 10
    RES_STATUS = 11
    RES_TEST = 15


class ReqMsg(typing.NamedTuple):
    frame_count: bool
    frame_count_valid: bool
    function: ReqFunction
    address: Address
    data: util.Bytes


class ResMsg(typing.NamedTuple):
    access_demand: bool
    data_flow_control: bool
    function: ResFunction
    address: Address
    data: util.Bytes


class ShortMsg(typing.NamedTuple):
    pass


Msg: typing.TypeAlias = ReqMsg | ResMsg | ShortMsg
