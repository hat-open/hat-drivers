import enum
import struct
import typing

from hat import util

from hat.drivers.tls import common
from hat.drivers.tls import fg1
from hat.drivers.tls import fg254


class TransmissionProcedure(enum.Enum):
    REQUEST = 0
    PERIODIC = 1


class DataType(enum.Enum):
    ERROR = 1
    ADDITIONAL_ERROR = 14
    NEGATIVE_ACKNOWLEDGEMENT = 16
    CHANNEL_CONTROL = 29
    TIME_STAMP = 30
    OPERATING_PARAMETERS = 32
    GEOGRAPHICAL_CHARACTERISTICS = 36
    AIR_TEMPERATURE = 48
    ROAD_SURFACE_TEMPERATURE = 49
    RESIDUAL_SALT = 52
    PRECIPITATION_INTENSITY = 53
    AIR_PRESSURE = 54
    RELATIVE_AIR_HUMIDITY = 55
    WIND_DIRECTION = 56
    WIND_SPEED_AVERAGE = 57
    SNOW_HEIGHT = 58
    VISIBILITY = 60
    BRIGHTNESS = 61
    WIND_SPEED_PEAK = 64
    FREEZING_TEMPERATURE = 65
    MELTING_POINT_TEMPERATURE = 66
    TEMPERATURE_IN_DEPTH_1 = 67
    TEMPERATURE_IN_DEPTH_2 = 68
    TEMPERATURE_IN_DEPTH_3 = 69
    ROAD_SURFACE_CONDITION = 70
    PRECIPITATION_TYPE = 71
    WATER_FILM_THICKNESS = 72


ErrorData: typing.TypeAlias = fg254.ErrorData


AdditionalErrorData: typing.TypeAlias = fg254.AdditionalErrorData


NegativeAcknowledgementData: typing.TypeAlias = fg254.NegativeAcknowledgementData  # NOQA


ChannelControlData: typing.TypeAlias = fg1.ChannelControlData


TimeStampData: typing.TypeAlias = fg254.TimeStampData


class OperatingParametersData(typing.NamedTuple):
    acquisition_period_length: common.UInt16
    transmission_procedure: TransmissionProcedure


GeographicalCharacteristicsData: typing.TypeAlias = fg254.GeographicalCharacteristicsData  # NOQA


class AirTemperatureData(typing.NamedTuple):
    value: float
    """In range [-30, 60] with resolution 0.1"""


class RoadSurfaceTemperatureData(typing.NamedTuple):
    value: float
    """In range [-30, 80] with resolution 0.1"""


class ResidualSaltData(typing.NamedTuple):
    value: common.UInt8
    """In range [0, 100]"""


class PrecipitationIntensityData(typing.NamedTuple):
    value: float
    """In range [0, 200] with resolution 0.1"""


class AirPressureData(typing.NamedTuple):
    value: common.UInt16
    """In range [800, 1200]"""


class RelativeAirHumidityData(typing.NamedTuple):
    value: common.UInt8
    """In range [10, 100]"""


class WindDirectionData(typing.NamedTuple):
    value: common.UInt16
    """In range [0, 359]"""


class WindSpeedAverageData(typing.NamedTuple):
    value: float
    """In range [0, 60] with resolution 0.1"""


class SnowHeightData(typing.NamedTuple):
    value: common.UInt8
    """In range [0, 200]"""


class VisibilityData(typing.NamedTuple):
    value: common.UInt16
    """In range [10, 1000]"""


class BrightnessData(typing.NamedTuple):
    value: common.UInt16
    """In range [0, 60000]"""


class WindSpeedPeakData(typing.NamedTuple):
    value: float
    """In range [0, 60] with resolution 0.1"""


class FreezingTemperatureData(typing.NamedTuple):
    value: float
    """In range [-30, 0] with resolution 0.1"""


class MeltingPointTemperatureData(typing.NamedTuple):
    value: float
    """In range [-30, 60] with resolution 0.1"""


class TemperatureInDepth1Data(typing.NamedTuple):
    value: float
    """In range [-30, 80] with resolution 0.1"""


class TemperatureInDepth2Data(typing.NamedTuple):
    value: float
    """In range [-30, 80] with resolution 0.1"""


class TemperatureInDepth3Data(typing.NamedTuple):
    value: float
    """In range [-30, 80] with resolution 0.1"""


class RoadSurfaceConditionData(typing.NamedTuple):
    value: common.UInt8


class PrecipitationTypeData(typing.NamedTuple):
    value: common.UInt8


class WaterFilmThicknessData(typing.NamedTuple):
    value: float
    """In range [0, 10] with resolution 0.01"""


Data: typing.TypeAlias = (ErrorData |
                          AdditionalErrorData |
                          NegativeAcknowledgementData |
                          ChannelControlData |
                          TimeStampData |
                          OperatingParametersData |
                          GeographicalCharacteristicsData |
                          AirTemperatureData |
                          RoadSurfaceTemperatureData |
                          ResidualSaltData |
                          PrecipitationIntensityData |
                          AirPressureData |
                          RelativeAirHumidityData |
                          WindDirectionData |
                          WindSpeedAverageData |
                          SnowHeightData |
                          VisibilityData |
                          BrightnessData |
                          WindSpeedPeakData |
                          FreezingTemperatureData |
                          MeltingPointTemperatureData |
                          TemperatureInDepth1Data |
                          TemperatureInDepth2Data |
                          TemperatureInDepth3Data |
                          RoadSurfaceConditionData |
                          PrecipitationTypeData |
                          WaterFilmThicknessData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, ErrorData):
        return fg254.encode(data)

    if isinstance(data, AdditionalErrorData):
        return fg254.encode(data)

    if isinstance(data, NegativeAcknowledgementData):
        return fg254.encode(data)

    if isinstance(data, ChannelControlData):
        return fg1.encode(data)

    if isinstance(data, TimeStampData):
        return fg254.encode(data)

    if isinstance(data, OperatingParametersData):
        return bytes([*_encode_uint16(data.acquisition_period_length),
                      data.transmission_procedure.value])

    if isinstance(data, GeographicalCharacteristicsData):
        return fg254.encode(data)

    if isinstance(data, AirTemperatureData):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, RoadSurfaceTemperatureData):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, ResidualSaltData):
        return bytes([data.value])

    if isinstance(data, PrecipitationIntensityData):
        return _encode_uint16(round(data.value * 10))

    if isinstance(data, AirPressureData):
        return _encode_uint16(data.value)

    if isinstance(data, RelativeAirHumidityData):
        return bytes([data.value])

    if isinstance(data, WindDirectionData):
        return _encode_uint16(data.value)

    if isinstance(data, WindSpeedAverageData):
        return _encode_uint16(round(data.value * 10))

    if isinstance(data, SnowHeightData):
        return bytes([data.value])

    if isinstance(data, VisibilityData):
        return _encode_uint16(data.value)

    if isinstance(data, BrightnessData):
        return _encode_uint16(data.value)

    if isinstance(data, WindSpeedPeakData):
        return _encode_uint16(round(data.value * 10))

    if isinstance(data, FreezingTemperatureData):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, MeltingPointTemperatureData):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, TemperatureInDepth1Data):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, TemperatureInDepth2Data):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, TemperatureInDepth3Data):
        return _encode_int16(round(data.value * 10))

    if isinstance(data, RoadSurfaceConditionData):
        return bytes([data.value])

    if isinstance(data, PrecipitationTypeData):
        return bytes([data.value])

    if isinstance(data, WaterFilmThicknessData):
        return _encode_int16(round(data.value * 100))

    raise TypeError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.ERROR:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.ADDITIONAL_ERROR:
        return fg254.decode(fg254.DataType.ADDITIONAL_ERROR, data)

    if data_type == DataType.NEGATIVE_ACKNOWLEDGEMENT:
        return fg254.decode(fg254.DataType.NEGATIVE_ACKNOWLEDGEMENT, data)

    if data_type == DataType.CHANNEL_CONTROL:
        return fg1.decode(fg1.DataType.CHANNEL_CONTROL, data)

    if data_type == DataType.TIME_STAMP:
        return fg254.decode(fg254.DataType.TIME_STAMP, data)

    if data_type == DataType.OPERATING_PARAMETERS:
        acquisition_period_length = _decode_uint16(data)
        transmission_procedure = TransmissionProcedure(data[2])

        return OperatingParametersData(
            acquisition_period_length=acquisition_period_length,
            transmission_procedure=transmission_procedure)

    if data_type == DataType.GEOGRAPHICAL_CHARACTERISTICS:
        return fg254.decode(fg254.DataType.GEOGRAPHICAL_CHARACTERISTICS, data)

    if data_type == DataType.AIR_TEMPERATURE:
        value = _decode_int16(data) / 10

        return AirTemperatureData(value=value)

    if data_type == DataType.ROAD_SURFACE_TEMPERATURE:
        value = _decode_int16(data) / 10

        return RoadSurfaceTemperatureData(value=value)

    if data_type == DataType.RESIDUAL_SALT:
        value = data[0]

        return ResidualSaltData(value=value)

    if data_type == DataType.PRECIPITATION_INTENSITY:
        value = _decode_uint16(data) / 10

        return PrecipitationIntensityData(value=value)

    if data_type == DataType.AIR_PRESSURE:
        value = _decode_uint16(data)

        return AirPressureData(value=value)

    if data_type == DataType.RELATIVE_AIR_HUMIDITY:
        value = data[0]

        return RelativeAirHumidityData(value=value)

    if data_type == DataType.WIND_DIRECTION:
        value = _decode_uint16(data)

        return WindDirectionData(value=value)

    if data_type == DataType.WIND_SPEED_AVERAGE:
        value = _decode_uint16(data) / 10

        return WindSpeedAverageData(value=value)

    if data_type == DataType.SNOW_HEIGHT:
        value = data[0]

        return SnowHeightData(value=value)

    if data_type == DataType.VISIBILITY:
        value = _decode_uint16(data)

        return VisibilityData(value=value)

    if data_type == DataType.BRIGHTNESS:
        value = _decode_uint16(data)

        return BrightnessData(value=value)

    if data_type == DataType.WIND_SPEED_PEAK:
        value = _decode_uint16(data) / 10

        return WindSpeedPeakData(value=value)

    if data_type == DataType.FREEZING_TEMPERATURE:
        value = _decode_int16(data) / 10

        return FreezingTemperatureData(value=value)

    if data_type == DataType.MELTING_POINT_TEMPERATURE:
        value = _decode_int16(data) / 10

        return MeltingPointTemperatureData(value=value)

    if data_type == DataType.TEMPERATURE_IN_DEPTH_1:
        value = _decode_int16(data) / 10

        return TemperatureInDepth1Data(value=value)

    if data_type == DataType.TEMPERATURE_IN_DEPTH_2:
        value = _decode_int16(data) / 10

        return TemperatureInDepth2Data(value=value)

    if data_type == DataType.TEMPERATURE_IN_DEPTH_3:
        value = _decode_int16(data) / 10

        return TemperatureInDepth3Data(value=value)

    if data_type == DataType.ROAD_SURFACE_CONDITION:
        value = data[0]

        return RoadSurfaceConditionData(value=value)

    if data_type == DataType.PRECIPITATION_TYPE:
        value = data[0]

        return PrecipitationTypeData(value=value)

    if data_type == DataType.WATER_FILM_THICKNESS:
        value = _decode_int16(data) / 100

        return WaterFilmThicknessData(value=value)

    raise ValueError('unsupported data type')


def _decode_uint16(data):
    return struct.unpack("<H", data[:2])[0]


def _encode_uint16(value):
    return struct.pack("<H", value)


def _decode_int16(data):
    return struct.unpack("<h", data[:2])[0]


def _encode_int16(value):
    return struct.pack("<h", value)
