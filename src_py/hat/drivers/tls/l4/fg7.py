import enum
import typing

from hat import util

from hat.drivers.tls import common
from hat.drivers.tls.l4 import fg254


class BarrierPositionConfirm(enum.Enum):
    BARRIER_LOWERED = 0
    BARRIER_RAISED = 1
    UNKNOWN_POSITION = 2


class DataType(enum.Enum):
    FAULT_REPORT = 1
    TIME_STAMP = 30
    STATUS_REPORT = 58
    INTERNAL_REGISTER_STATUS_REPORT = 122


FaultReportData: typing.TypeAlias = fg254.ErrorData


TimeStampData: typing.TypeAlias = fg254.TimeStampData


class StatusReportData(typing.NamedTuple):
    state: util.Bytes
    manufacturer_code: common.UInt8


class InternalRegisterStatusReportData(typing.NamedTuple):
    signal_not_active: common.UInt16
    manufacturer_code: common.UInt8


Data: typing.TypeAlias = (FaultReportData |
                          TimeStampData |
                          StatusReportData |
                          InternalRegisterStatusReportData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, FaultReportData):
        return fg254.encode(data)

    if isinstance(data, TimeStampData):
        return fg254.encode(data)

    if isinstance(data, StatusReportData):
        return bytes([*data.state,
                      data.manufacturer_code])

    if isinstance(data, InternalRegisterStatusReportData):
        return bytes([data.signal_not_active & 0xFF,
                      data.signal_not_active >> 8,
                      data.manufacturer_code])

    raise ValueError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.FAULT_REPORT:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.TIME_STAMP:
        return fg254.decode(fg254.DataType.TIME_STAMP, data)

    if data_type == DataType.STATUS_REPORT:
        state = bytes([data[0]])
        manufacturer_code = data[1]

        return StatusReportData(state=state,
                                manufacturer_code=manufacturer_code)

    if data_type == DataType.INTERNAL_REGISTER_STATUS_REPORT:
        signal_not_active = (data[1] << 8) | data[0]
        manufacturer_code = data[2]

        return InternalRegisterStatusReportData(
                signal_not_active=signal_not_active,
                manufacturer_code=manufacturer_code)

    raise ValueError('unsupported data type')
