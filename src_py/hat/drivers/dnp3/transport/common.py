import enum
import typing

from hat import util


Address: typing.TypeAlias = int
"""address in range [0, 0xffff]"""


class Direction(enum.Enum):
    OUTSTATION_TO_MASTER = 0
    MASTER_TO_OUTSTATION = 1


class PrimaryFunctionCode(enum.Enum):
    RESET_LINK_STATES = 0
    TEST_LINK_STATES = 2
    CONFIRMED_USER_DATA = 3
    UNCONFIRMED_USER_DATA = 4
    REQUEST_LINK_STATUS = 9


class SecondaryFunctionCode(enum.Enum):
    ACK = 0
    NACK = 1
    LINK_STATUS = 11
    NOT_SUPPORTED = 15


class PrimaryFrame(typing.NamedTuple):
    direction: Direction
    frame_count: bool
    function_code: PrimaryFunctionCode
    source: Address
    destination: Address
    data: util.Bytes


class SecondaryFrame(typing.NamedTuple):
    direction: Direction
    data_flow_control: bool
    function_code: SecondaryFunctionCode
    source: Address
    destination: Address
    data: util.Bytes


Frame: typing.TypeAlias = PrimaryFrame | SecondaryFrame
