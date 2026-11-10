import enum
import typing

from hat import util

from hat.drivers.tls.l4 import fg254


class DataType(enum.Enum):
    FAULT_REPORT = 1
    OPERATING_PARAMETERS = 32


FaultReportData: typing.TypeAlias = fg254.ErrorData


class OperatingParametersData(typing.NamedTuple):
    local_automatics_enabled: bool
    local_automatics_parameters: util.Bytes


Data: typing.TypeAlias = (FaultReportData | OperatingParametersData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, FaultReportData):
        return fg254.encode(data)

    if isinstance(data, OperatingParametersData):
        return bytes([data.local_automatics_enabled,
                      *data.local_automatics_parameters])

    raise ValueError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.FAULT_REPORT:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.OPERATING_PARAMETERS:
        local_automatics_enabled = bool(data[0])
        local_automatics_parameters = data[1:]

        return OperatingParametersData(
                local_automatics_enabled=local_automatics_enabled,
                local_automatics_parameters=local_automatics_parameters)

    raise ValueError('unsupported data type')
