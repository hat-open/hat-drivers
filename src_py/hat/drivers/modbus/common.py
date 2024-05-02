"""Modbus common data structures"""

import enum


class ModbusType(enum.Enum):
    TCP = 0
    RTU = 1
    ASCII = 2


class DataType(enum.Enum):
    COIL = 1
    DISCRETE_INPUT = 2
    HOLDING_REGISTER = 3
    INPUT_REGISTER = 4
    QUEUE = 5


class Error(enum.Enum):
    INVALID_FUNCTION_CODE = 0x01
    INVALID_DATA_ADDRESS = 0x02
    INVALID_DATA_VALUE = 0x03
    FUNCTION_ERROR = 0x04
    GATEWAY_PATH_UNAVAILABLE = 0x0a
    GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0b


def apply_mask(value: int, and_mask: int, or_mask: int) -> int:
    """Apply mask to value"""
    return (value & and_mask) | (or_mask & (~and_mask))
