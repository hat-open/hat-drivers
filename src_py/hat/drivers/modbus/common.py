"""Modbus common data structures"""

from hat.drivers.common import *  # NOQA

from collections.abc import Sequence
import enum
import typing


# TODO: define behavior in case of broadcast device_id 0

DeviceId: typing.TypeAlias = int
"""Device id"""

DataAddress: typing.TypeAlias = int
"""Data address"""

DataValues: typing.TypeAlias = Sequence[int]
"""Data values"""


class ModbusType(enum.Enum):
    """Modbus type"""
    TCP = 0
    RTU = 1
    ASCII = 2


class DataType(enum.Enum):
    """Data type"""
    COIL = 1
    DISCRETE_INPUT = 2
    HOLDING_REGISTER = 3
    INPUT_REGISTER = 4
    QUEUE = 5


class Error(enum.Enum):
    """Error"""
    INVALID_FUNCTION_CODE = 0x01
    INVALID_DATA_ADDRESS = 0x02
    INVALID_DATA_VALUE = 0x03
    FUNCTION_ERROR = 0x04
    GATEWAY_PATH_UNAVAILABLE = 0x0a
    GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0b


class Success(typing.NamedTuple):
    """Success"""


class ReadReq(typing.NamedTuple):
    """Read request

    If `data_type` is ``DataType.QUEUE``, `quantity` is ignored.

    """
    device_id: DeviceId
    data_type: DataType
    start_address: DataAddress
    quantity: int


ReadRes: typing.TypeAlias = DataValues | Error
"""Read response"""


class WriteReq(typing.NamedTuple):
    """Write request"""
    device_id: DeviceId
    data_type: DataType
    start_address: DataAddress
    values: DataValues


WriteRes: typing.TypeAlias = Success | Error
"""Write response"""


class WriteMaskReq(typing.NamedTuple):
    """Write mask request"""
    device_id: DeviceId
    address: DataAddress
    and_mask: int
    or_mask: int


WriteMaskRes: typing.TypeAlias = Success | Error
"""Write mask response"""


Request: typing.TypeAlias = ReadReq | WriteReq | WriteMaskReq
"""Request"""


Response: typing.TypeAlias = ReadRes | WriteRes | WriteMaskRes
"""Response"""


def apply_mask(value: int, and_mask: int, or_mask: int) -> int:
    """Apply mask to value"""
    return (value & and_mask) | (or_mask & (~and_mask))
