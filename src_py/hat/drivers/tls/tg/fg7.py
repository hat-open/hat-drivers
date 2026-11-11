import enum
import typing

from hat import util

from hat.drivers.tls import common


class DataType(enum.Enum):
    STATUS_REPORT = 58
    INTERNAL_REGISTER_STATUS_REPORT = 122


class StatusReportData(typing.NamedTuple):
    state: common.UInt8
    manufacturer_code: common.UInt8


class InternalRegisterStatusReportData(typing.NamedTuple):
    state: common.UInt16
    manufacturer_code: common.UInt8


Data: typing.TypeAlias = (StatusReportData |
                          InternalRegisterStatusReportData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, StatusReportData):
        return bytes([data.state,
                      data.manufacturer_code])

    if isinstance(data, InternalRegisterStatusReportData):
        return bytes([data.state & 0xFF,
                      data.state >> 8,
                      data.manufacturer_code])

    raise TypeError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.STATUS_REPORT:
        state = data[0]
        manufacturer_code = data[1]

        return StatusReportData(state=state,
                                manufacturer_code=manufacturer_code)

    if data_type == DataType.INTERNAL_REGISTER_STATUS_REPORT:
        state = (data[1] << 8) | data[0]
        manufacturer_code = data[2]

        return InternalRegisterStatusReportData(
            state=state,
            manufacturer_code=manufacturer_code)

    raise ValueError('unsupported data type')
