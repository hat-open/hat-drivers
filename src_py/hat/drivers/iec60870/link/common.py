import enum
import typing


Bytes = typing.Union[bytes, bytearray, memoryview]


class AddressSize(enum.Enum):
    ZERO = 0
    ONE = 1
    TWO = 2


class ReqFunction(enum.Enum):
    RESET_LINK = 0
    RESET_PROCESS = 1
    TEST = 2
    DATA = 3
    DATA_NO_RES = 4
    REQ_ACCESS_DEMAND = 8
    REQ_STATUS = 9
    REQ_DATA_1 = 10
    REQ_DATA_2 = 11


class ResFunction(enum.Enum):
    ACK = 0
    NACK = 1
    RES_DATA = 8
    RES_NACK = 9
    RES_STATUS = 11
    NOT_FUNCTIONING = 14
    NOT_IMPLEMENTED = 15


class ReqFrame(typing.NamedTuple):
    is_master: bool
    frame_count_bit: bool
    frame_count_valid: bool
    function: ReqFunction
    address: int
    data: Bytes


class ResFrame(typing.NamedTuple):
    is_master: bool
    access_demand: bool
    data_flow_control: bool
    function: ResFunction
    address: int
    data: Bytes


Frame = typing.Union[ReqFrame, ResFrame]


def get_broadcast_address(address_size: AddressSize):
    if address_size == AddressSize.ONE:
        return 0xFF

    if address_size == AddressSize.TWO:
        return 0xFFFF

    raise ValueError('unsupported address size')
