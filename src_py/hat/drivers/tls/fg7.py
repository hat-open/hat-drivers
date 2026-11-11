import enum
import typing

from hat import util

from hat.drivers.tls import fg254


class DataType(enum.Enum):
    ERROR = 1
    ADDITIONAL_ERROR = 14
    NEGATIVE_ACKNOWLEDGEMENT = 16
    TIME_STAMP = 30


ErrorData: typing.TypeAlias = fg254.ErrorData


AdditionalErrorData: typing.TypeAlias = fg254.AdditionalErrorData


NegativeAcknowledgementData: typing.TypeAlias = fg254.NegativeAcknowledgementData  # NOQA


TimeStampData: typing.TypeAlias = fg254.TimeStampData


Data: typing.TypeAlias = (ErrorData |
                          AdditionalErrorData |
                          NegativeAcknowledgementData |
                          TimeStampData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, ErrorData):
        return fg254.encode(data)

    if isinstance(data, AdditionalErrorData):
        return fg254.encode(data)

    if isinstance(data, NegativeAcknowledgementData):
        return fg254.encode(data)

    if isinstance(data, TimeStampData):
        return fg254.encode(data)

    raise TypeError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.ERROR:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.ADDITIONAL_ERROR:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.NEGATIVE_ACKNOWLEDGEMENT:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.TIME_STAMP:
        return fg254.decode(fg254.DataType.TIME_STAMP, data)

    raise ValueError('unsupported data type')
