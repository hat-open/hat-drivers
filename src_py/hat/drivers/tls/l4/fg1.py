from collections.abc import Collection
import enum
import itertools
import typing

from hat import util

from hat.drivers.tls.l4 import common
from hat.drivers.tls.l4 import fg254


class AverageType(enum.Enum):
    MOVING = 0
    ARITHMETICAL = 1


class ShortRoadIntervalType(enum.Enum):
    SHORT = 1
    ROAD = 3


class DataType(enum.Enum):
    ERROR = 1
    ADDITIONAL_ERROR = 14
    NEGATIVE_ACKNOWLEDGEMENT = 16
    RETRIEVAL_BUFFER_CONTENT = 20
    CHANNEL_CONTROL = 29
    TIME_STAMP = 30
    LTA_OPERATING_PARAMETERS = 32
    RTA_OPERATING_PARAMETERS = 34
    GEOGRAPHICAL_CHARACTERISTICS = 36
    SHORT_DATA_SPEED_CLASS_PARAMETERS = 37
    LONG_DATA_SPEED_CLASS_PARAMETERS = 38
    SHORT_ROAD_INTERVAL_DATA = 48
    LTA_RESULT_V0_8 = 49
    LTA_RESULT_V1_8 = 50
    LTA_RESULT_V2_8 = 51
    LTA_RESULT_V3_8 = 52
    LTA_RESULT_V4_8 = 53
    INDIVIDUAL_VEHICLE_DATA = 63
    LONG_INTERVAL_DATA = 64
    LTA_RESULT_V10 = 65
    LTA_RESULT_V11 = 66
    LTA_RESULT_V12 = 67
    LTA_RESULT_V13 = 68
    LTA_RESULT_V14 = 69
    LTA_RESULT_V15 = 70
    LTA_RESULT_V16 = 71
    LTA_RESULT_V17 = 72
    LTA_RESULT_V18 = 73
    LTA_RESULT_V19 = 74
    LTA_RESULT_V20 = 75
    LTA_RESULT_V21 = 76
    LTA_RESULT_V22 = 77
    LTA_RESULT_V23 = 78
    RTA_RESULT_V0 = 96
    RTA_RESULT_V1 = 97
    LTA_RESULT_V0_16 = 113
    LTA_RESULT_V1_16 = 114
    LTA_RESULT_V2_16 = 115
    LTA_RESULT_V3_16 = 116
    LTA_RESULT_V4_16 = 117


ErrorData: typing.TypeAlias = fg254.ErrorData


AdditionalErrorData: typing.TypeAlias = fg254.AdditionalErrorData


NegativeAcknowledgementData: typing.TypeAlias = fg254.NegativeAcknowledgementData  # NOQA


class RetrievalBufferContentData(typing.NamedTuple):
    summer_time: bool
    year: common.UInt8
    """In range [0, 99]"""
    month: common.UInt8
    """In range [1, 12]"""
    day: common.UInt8
    """In range [1, 31]"""
    hour: common.UInt7
    """In range [0, 23]"""
    count: common.UInt8


class ChannelControlData(typing.NamedTuple):
    passive: bool
    manufacturer_definition: common.UInt4


TimeStampData: typing.TypeAlias = fg254.TimeStampData


class LtaOperatingParametersData(typing.NamedTuple):
    short_data_version: common.UInt8
    short_data_interval: common.UInt8
    long_data_version: common.UInt8
    long_data_interval: common.UInt8
    smoothing_1: common.UInt8
    smoothing_2: common.UInt8
    length_limit: common.UInt8
    average_type: AverageType
    initial_moving_average: common.UInt7


class RtaOperatingParametersData(typing.NamedTuple):
    version: common.UInt8
    interval: common.UInt8


GeographicalCharacteristicsData: typing.TypeAlias = fg254.GeographicalCharacteristicsData  # NOQA


class ShortDataSpeedClassParametersData(typing.NamedTuple):
    vehicle_class: common.UInt8
    limits: Collection[common.UInt8]


class LongDataSpeedClassParametersData(typing.NamedTuple):
    vehicle_class: common.UInt8
    limits: Collection[common.UInt8]


class ShortRoadIntervalData(typing.NamedTuple):
    summer_time: bool
    hour: common.UInt7
    minute: common.UInt8
    second: common.UInt8
    interval_type: ShortRoadIntervalType
    interval: common.UInt8


class LtaResultV0_8Data(typing.NamedTuple):
    volume_1: common.UInt8
    volume_2: common.UInt8
    speed_1: common.UInt8
    speed_2: common.UInt8


class LtaResultV1_8Data(typing.NamedTuple):
    volume_1: common.UInt8
    volume_2: common.UInt8
    speed_1: common.UInt8
    speed_2: common.UInt8
    time_gap: common.UInt8


class LtaResultV2_8Data(typing.NamedTuple):
    volume_1: common.UInt8
    volume_2: common.UInt8
    speed_1: common.UInt8
    speed_2: common.UInt8
    occupancy: common.UInt8


class LtaResultV3_8Data(typing.NamedTuple):
    volume_1: common.UInt8
    volume_2: common.UInt8
    speed_1: common.UInt8
    speed_2: common.UInt8
    time_gap: common.UInt8
    occupancy: common.UInt8
    standard_deviation: common.UInt8
    smoothed_speed: common.UInt8


class LtaResultV4_8Data(typing.NamedTuple):
    volume_1: common.UInt8
    volume_2: common.UInt8
    speed_1: common.UInt8
    speed_2: common.UInt8
    time_gap: common.UInt8
    occupancy: common.UInt8
    standard_deviation: common.UInt8
    smoothed_speed: common.UInt8
    speed_classes_1: Collection[common.UInt8]
    speed_classes_2: Collection[common.UInt8]


class IndividualVehicleData(typing.NamedTuple):
    status: common.UInt8
    vehicle_class: common.UInt8
    speed: common.UInt16
    occupied_time: common.UInt16
    time_gap: common.UInt16
    vehicle_length: common.UInt8


class LongIntervalData(typing.NamedTuple):
    summer_time: bool
    year: common.UInt8
    """In range [0, 99]"""
    month: common.UInt8
    """In range [1, 12]"""
    day: common.UInt8
    """In range [1, 31]"""
    hour: common.UInt7
    """In range [0, 23]"""
    interval: common.UInt8


class LtaResultV10Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16


class LtaResultV11Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed: common.UInt8


class LtaResultV12Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8


class LtaResultV13Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    speed_85: common.UInt8


class LtaResultV14Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16


class LtaResultV15Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8


class LtaResultV16Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    speed_85: common.UInt8


class LtaResultV17Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    speed_85: common.UInt8
    speed_classes_1: Collection[common.UInt16]
    speed_classes_2: Collection[common.UInt16]


class LtaResultV18Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    speed_3: common.UInt8
    speed_4: common.UInt8
    speed_5: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    standard_deviation_3: common.UInt8
    standard_deviation_4: common.UInt8
    standard_deviation_5: common.UInt8
    speed_85: common.UInt8
    speed_classes_1: Collection[common.UInt16]
    speed_classes_2: Collection[common.UInt16]
    speed_classes_3: Collection[common.UInt16]
    speed_classes_4: Collection[common.UInt16]
    speed_classes_5: Collection[common.UInt16]


class LtaResultV19Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    volume_7: common.UInt16
    volume_8: common.UInt16
    volume_9: common.UInt16


class LtaResultV20Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    volume_7: common.UInt16
    volume_8: common.UInt16
    volume_9: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8


class LtaResultV21Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    volume_7: common.UInt16
    volume_8: common.UInt16
    volume_9: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    speed_85: common.UInt8


class LtaResultV22Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    volume_7: common.UInt16
    volume_8: common.UInt16
    volume_9: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    speed_85: common.UInt8
    speed_classes_1: Collection[common.UInt16]
    speed_classes_2: Collection[common.UInt16]


class LtaResultV23Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    volume_3: common.UInt16
    volume_4: common.UInt16
    volume_5: common.UInt16
    volume_6: common.UInt16
    volume_7: common.UInt16
    volume_8: common.UInt16
    volume_9: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    speed_3: common.UInt8
    speed_4: common.UInt8
    speed_5: common.UInt8
    speed_6: common.UInt8
    speed_7: common.UInt8
    speed_8: common.UInt8
    standard_deviation_1: common.UInt8
    standard_deviation_2: common.UInt8
    standard_deviation_3: common.UInt8
    standard_deviation_4: common.UInt8
    standard_deviation_5: common.UInt8
    standard_deviation_6: common.UInt8
    standard_deviation_7: common.UInt8
    standard_deviation_8: common.UInt8
    speed_85: common.UInt8
    speed_classes_1: Collection[common.UInt16]
    speed_classes_2: Collection[common.UInt16]
    speed_classes_3: Collection[common.UInt16]
    speed_classes_4: Collection[common.UInt16]
    speed_classes_5: Collection[common.UInt16]
    speed_classes_6: Collection[common.UInt16]
    speed_classes_7: Collection[common.UInt16]
    speed_classes_8: Collection[common.UInt16]


class RtaResultV0Data(typing.NamedTuple):
    density: common.UInt16
    speed: common.UInt8


class RtaResultV1Data(typing.NamedTuple):
    density_1: common.UInt16
    density_2: common.UInt16
    density_3: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    speed_3: common.UInt8


class LtaResultV0_16Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt18


class LtaResultV1_16Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    time_gap: common.UInt8


class LtaResultV2_16Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    occupancy: common.UInt8


class LtaResultV3_16Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    occupancy: common.UInt8
    standard_deviation: common.UInt8
    smoothed_speed: common.UInt8


class LtaResultV4_16Data(typing.NamedTuple):
    volume_1: common.UInt16
    volume_2: common.UInt16
    speed_1: common.UInt8
    speed_2: common.UInt8
    occupancy: common.UInt8
    standard_deviation: common.UInt8
    smoothed_speed: common.UInt8
    speed_classes_1: Collection[common.UInt16]
    speed_classes_2: Collection[common.UInt16]


Data: typing.TypeAlias = (ErrorData |
                          AdditionalErrorData |
                          NegativeAcknowledgementData |
                          RetrievalBufferContentData |
                          ChannelControlData |
                          TimeStampData |
                          LtaOperatingParametersData |
                          RtaOperatingParametersData |
                          GeographicalCharacteristicsData |
                          ShortDataSpeedClassParametersData |
                          LongDataSpeedClassParametersData |
                          ShortRoadIntervalData |
                          LtaResultV0_8Data |
                          LtaResultV1_8Data |
                          LtaResultV2_8Data |
                          LtaResultV3_8Data |
                          LtaResultV4_8Data |
                          IndividualVehicleData |
                          LongIntervalData |
                          LtaResultV10Data |
                          LtaResultV11Data |
                          LtaResultV12Data |
                          LtaResultV13Data |
                          LtaResultV14Data |
                          LtaResultV15Data |
                          LtaResultV16Data |
                          LtaResultV17Data |
                          LtaResultV18Data |
                          LtaResultV19Data |
                          LtaResultV20Data |
                          LtaResultV21Data |
                          LtaResultV22Data |
                          LtaResultV23Data |
                          RtaResultV0Data |
                          RtaResultV1Data |
                          LtaResultV0_16Data |
                          LtaResultV1_16Data |
                          LtaResultV2_16Data |
                          LtaResultV3_16Data |
                          LtaResultV4_16Data)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, ErrorData):
        return fg254.encode(data)

    if isinstance(data, AdditionalErrorData):
        return fg254.encode(data)

    if isinstance(data, NegativeAcknowledgementData):
        return fg254.encode(data)

    if isinstance(data, RetrievalBufferContentData):
        return bytes([data.year,
                      data.month,
                      data.day,
                      _encode_hour(data.summer_time, data.hour),
                      data.count])

    if isinstance(data, ChannelControlData):
        return bytes([(0x01 if data.passive else 0x00) |
                      ((data.manufacturer_definition & 0x0F) << 4)])

    if isinstance(data, TimeStampData):
        return fg254.encode(data)

    if isinstance(data, LtaOperatingParametersData):
        return bytes([data.short_data_version,
                      data.short_data_interval,
                      data.long_data_version,
                      data.long_data_interval,
                      data.smoothing_1,
                      data.smoothing_2,
                      data.length_limit,
                      ((data.average_type.value << 7) |
                       (data.initial_moving_average & 0x7F))])

    if isinstance(data, RtaOperatingParametersData):
        return bytes([data.version,
                      data.interval])

    if isinstance(data, GeographicalCharacteristicsData):
        return fg254.encode(data)

    if isinstance(data, ShortDataSpeedClassParametersData):
        return bytes(itertools.chain(
            [data.vehicle_class],
            _encode_int8_list(data.limits)))

    if isinstance(data, LongDataSpeedClassParametersData):
        return bytes(itertools.chain(
            [data.vehicle_class],
            _encode_int8_list(data.limits)))

    if isinstance(data, ShortRoadIntervalData):
        return bytes([_encode_hour(data.summer_time, data.hour),
                      data.minute,
                      data.second,
                      data.interval_type.value,
                      data.interval])

    if isinstance(data, LtaResultV0_8Data):
        return bytes([data.volume_1,
                      data.volume_2,
                      data.speed_1,
                      data.speed_2])

    if isinstance(data, LtaResultV1_8Data):
        return bytes([data.volume_1,
                      data.volume_2,
                      data.speed_1,
                      data.speed_2,
                      data.time_gap])

    if isinstance(data, LtaResultV2_8Data):
        return bytes([data.volume_1,
                      data.volume_2,
                      data.speed_1,
                      data.speed_2,
                      data.occupancy])

    if isinstance(data, LtaResultV3_8Data):
        return bytes([data.volume_1,
                      data.volume_2,
                      data.speed_1,
                      data.speed_2,
                      data.time_gap,
                      data.occupancy,
                      data.standard_deviation,
                      data.smoothed_speed])

    if isinstance(data, LtaResultV4_8Data):
        return bytes(itertools.chain(
            [data.volume_1,
             data.volume_2,
             data.speed_1,
             data.speed_2,
             data.time_gap,
             data.occupancy,
             data.standard_deviation,
             data.smoothed_speed],
            _encode_int8_list(data.speed_classes_1),
            _encode_int8_list(data.speed_classes_2)))

    if isinstance(data, IndividualVehicleData):
        return bytes(itertools.chain(
            [data.status,
             data.vehicle_class],
            _encode_int16(data.speed),
            _encode_int16(data.occupied_time),
            _encode_int16(data.time_gap),
            [data.vehicle_length]))

    if isinstance(data, LongIntervalData):
        return bytes([data.year,
                      data.month,
                      data.day,
                      _encode_hour(data.summer_time, data.hour),
                      data.interval])

    if isinstance(data, LtaResultV10Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2)))

    if isinstance(data, LtaResultV11Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed]))

    if isinstance(data, LtaResultV12Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2]))

    if isinstance(data, LtaResultV13Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.speed_85]))

    if isinstance(data, LtaResultV14Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6)))

    if isinstance(data, LtaResultV15Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2]))

    if isinstance(data, LtaResultV16Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.speed_85]))

    if isinstance(data, LtaResultV17Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.speed_85],
            _encode_int16_list(data.speed_classes_1),
            _encode_int16_list(data.speed_classes_2)))

    if isinstance(data, LtaResultV18Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            [data.speed_1,
             data.speed_2,
             data.speed_3,
             data.speed_4,
             data.speed_5,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.standard_deviation_3,
             data.standard_deviation_4,
             data.standard_deviation_5,
             data.speed_85],
            _encode_int16_list(data.speed_classes_1),
            _encode_int16_list(data.speed_classes_2),
            _encode_int16_list(data.speed_classes_3),
            _encode_int16_list(data.speed_classes_4),
            _encode_int16_list(data.speed_classes_5)))

    if isinstance(data, LtaResultV19Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            _encode_int16(data.volume_7),
            _encode_int16(data.volume_8),
            _encode_int16(data.volume_9)))

    if isinstance(data, LtaResultV20Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            _encode_int16(data.volume_7),
            _encode_int16(data.volume_8),
            _encode_int16(data.volume_9),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2]))

    if isinstance(data, LtaResultV21Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            _encode_int16(data.volume_7),
            _encode_int16(data.volume_8),
            _encode_int16(data.volume_9),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.speed_85]))

    if isinstance(data, LtaResultV22Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            _encode_int16(data.volume_7),
            _encode_int16(data.volume_8),
            _encode_int16(data.volume_9),
            [data.speed_1,
             data.speed_2,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.speed_85],
            _encode_int16_list(data.speed_classes_1),
            _encode_int16_list(data.speed_classes_2)))

    if isinstance(data, LtaResultV23Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            _encode_int16(data.volume_3),
            _encode_int16(data.volume_4),
            _encode_int16(data.volume_5),
            _encode_int16(data.volume_6),
            _encode_int16(data.volume_7),
            _encode_int16(data.volume_8),
            _encode_int16(data.volume_9),
            [data.speed_1,
             data.speed_2,
             data.speed_3,
             data.speed_4,
             data.speed_5,
             data.speed_6,
             data.speed_7,
             data.speed_8,
             data.standard_deviation_1,
             data.standard_deviation_2,
             data.standard_deviation_3,
             data.standard_deviation_4,
             data.standard_deviation_5,
             data.standard_deviation_6,
             data.standard_deviation_7,
             data.standard_deviation_8,
             data.speed_85],
            _encode_int16_list(data.speed_classes_1),
            _encode_int16_list(data.speed_classes_2),
            _encode_int16_list(data.speed_classes_3),
            _encode_int16_list(data.speed_classes_4),
            _encode_int16_list(data.speed_classes_5),
            _encode_int16_list(data.speed_classes_6),
            _encode_int16_list(data.speed_classes_7),
            _encode_int16_list(data.speed_classes_8)))

    if isinstance(data, RtaResultV0Data):
        return bytes(itertools.chain(
            _encode_int16(data.density),
            [data.speed]))

    if isinstance(data, RtaResultV1Data):
        return bytes(itertools.chain(
            _encode_int16(data.density_1),
            [data.speed_1],
            _encode_int16(data.density_2),
            _encode_int16(data.density_3),
            [data.speed_2,
             data.speed_3]))

    if isinstance(data, LtaResultV0_16Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2]))

    if isinstance(data, LtaResultV1_16Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2,
             data.time_gap]))

    if isinstance(data, LtaResultV2_16Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2,
             data.occupancy]))

    if isinstance(data, LtaResultV3_16Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2,
             data.time_gap,
             data.occupancy,
             data.standard_deviation,
             data.smoothed_speed]))

    if isinstance(data, LtaResultV4_16Data):
        return bytes(itertools.chain(
            _encode_int16(data.volume_1),
            _encode_int16(data.volume_2),
            [data.speed_1,
             data.speed_2,
             data.time_gap,
             data.occupancy,
             data.standard_deviation,
             data.smoothed_speed],
            _encode_int16_list(data.speed_classes_1),
            _encode_int16_list(data.speed_classes_2)))

    raise TypeError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.ERROR:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.ADDITIONAL_ERROR:
        return fg254.decode(fg254.DataType.ADDITIONAL_ERROR, data)

    if data_type == DataType.NEGATIVE_ACKNOWLEDGEMENT:
        return fg254.decode(fg254.DataType.NEGATIVE_ACKNOWLEDGEMENT, data)

    if data_type == DataType.RETRIEVAL_BUFFER_CONTENT:
        year = data[0]
        month = data[1]
        day = data[2]
        summer_time, hour, _ = _decode_hour(data[3:])
        count = data[4]

        return RetrievalBufferContentData(summer_time=summer_time,
                                          year=year,
                                          month=month,
                                          day=day,
                                          hour=hour,
                                          count=count)

    if data_type == DataType.CHANNEL_CONTROL:
        passive = bool(data[0] & 0x01)
        manufacturer_definition = data[0] >> 4

        return ChannelControlData(
            passive=passive,
            manufacturer_definition=manufacturer_definition)

    if data_type == DataType.TIME_STAMP:
        return fg254.decode(fg254.DataType.TIME_STAMP, data)

    if data_type == DataType.LTA_OPERATING_PARAMETERS:
        short_data_version = data[0]
        short_data_interval = data[1]
        long_data_version = data[2]
        long_data_interval = data[3]
        smoothing_1 = data[4]
        smoothing_2 = data[5]
        length_limit = data[6]
        average_type = AverageType(data[7] >> 7)
        initial_moving_average = data[7] & 0x7F

        return LtaOperatingParametersData(
            short_data_version=short_data_version,
            short_data_interval=short_data_interval,
            long_data_version=long_data_version,
            long_data_interval=long_data_interval,
            smoothing_1=smoothing_1,
            smoothing_2=smoothing_2,
            length_limit=length_limit,
            average_type=average_type,
            initial_moving_average=initial_moving_average)

    if data_type == DataType.RTA_OPERATING_PARAMETERS:
        version = data[0]
        interval = data[1]

        return RtaOperatingParametersData(version=version,
                                          interval=interval)

    if data_type == DataType.GEOGRAPHICAL_CHARACTERISTICS:
        return fg254.decode(fg254.DataType.GEOGRAPHICAL_CHARACTERISTICS, data)

    if data_type == DataType.SHORT_DATA_SPEED_CLASS_PARAMETERS:
        vehicle_class = data[0]
        limits, _ = _decode_int8_list(data[1:])

        return ShortDataSpeedClassParametersData(vehicle_class=vehicle_class,
                                                 limits=limits)

    if data_type == DataType.LONG_DATA_SPEED_CLASS_PARAMETERS:
        vehicle_class = data[0]
        limits, _ = _decode_int8_list(data[1:])

        return LongDataSpeedClassParametersData(vehicle_class=vehicle_class,
                                                limits=limits)

    if data_type == DataType.SHORT_ROAD_INTERVAL_DATA:
        summer_time, hour, _ = _decode_hour(data)
        minute = data[1]
        second = data[2]
        interval_type = ShortRoadIntervalType(data[3])
        interval = data[4]

        return ShortRoadIntervalData(summer_time=summer_time,
                                     hour=hour,
                                     minute=minute,
                                     second=second,
                                     interval_type=interval_type,
                                     interval=interval)

    if data_type == DataType.LTA_RESULT_V0_8:
        volume_1 = data[0]
        volume_2 = data[1]
        speed_1 = data[2]
        speed_2 = data[3]

        return LtaResultV0_8Data(volume_1=volume_1,
                                 volume_2=volume_2,
                                 speed_1=speed_1,
                                 speed_2=speed_2)

    if data_type == DataType.LTA_RESULT_V1_8:
        volume_1 = data[0]
        volume_2 = data[1]
        speed_1 = data[2]
        speed_2 = data[3]
        time_gap = data[4]

        return LtaResultV1_8Data(volume_1=volume_1,
                                 volume_2=volume_2,
                                 speed_1=speed_1,
                                 speed_2=speed_2,
                                 time_gap=time_gap)

    if data_type == DataType.LTA_RESULT_V2_8:
        volume_1 = data[0]
        volume_2 = data[1]
        speed_1 = data[2]
        speed_2 = data[3]
        occupancy = data[4]

        return LtaResultV2_8Data(volume_1=volume_1,
                                 volume_2=volume_2,
                                 speed_1=speed_1,
                                 speed_2=speed_2,
                                 occupancy=occupancy)

    if data_type == DataType.LTA_RESULT_V3_8:
        volume_1 = data[0]
        volume_2 = data[1]
        speed_1 = data[2]
        speed_2 = data[3]
        time_gap = data[4]
        occupancy = data[5]
        standard_deviation = data[6]
        smoothed_speed = data[7]

        return LtaResultV3_8Data(volume_1=volume_1,
                                 volume_2=volume_2,
                                 speed_1=speed_1,
                                 speed_2=speed_2,
                                 time_gap=time_gap,
                                 occupancy=occupancy,
                                 standard_deviation=standard_deviation,
                                 smoothed_speed=smoothed_speed)

    if data_type == DataType.LTA_RESULT_V4_8:
        volume_1 = data[0]
        volume_2 = data[1]
        speed_1 = data[2]
        speed_2 = data[3]
        time_gap = data[4]
        occupancy = data[5]
        standard_deviation = data[6]
        smoothed_speed = data[7]
        data = data[8:]
        speed_classes_1, data = _decode_int8_list(data)
        speed_classes_2, data = _decode_int8_list(data)

        return LtaResultV4_8Data(volume_1=volume_1,
                                 volume_2=volume_2,
                                 speed_1=speed_1,
                                 speed_2=speed_2,
                                 time_gap=time_gap,
                                 occupancy=occupancy,
                                 standard_deviation=standard_deviation,
                                 smoothed_speed=smoothed_speed,
                                 speed_classes_1=speed_classes_1,
                                 speed_classes_2=speed_classes_2)

    if data_type == DataType.INDIVIDUAL_VEHICLE_DATA:
        status = data[0]
        vehicle_class = data[1]
        speed, _ = _decode_int16(data[2:])
        occupied_time, _ = _decode_int16(data[4:])
        time_gap, _ = _decode_int16(data[6:])
        vehicle_length = data[8]

        return IndividualVehicleData(status=status,
                                     vehicle_class=vehicle_class,
                                     speed=speed,
                                     occupied_time=occupied_time,
                                     time_gap=time_gap,
                                     vehicle_length=vehicle_length)

    if data_type == DataType.LONG_INTERVAL_DATA:
        year = data[0]
        month = data[1]
        day = data[2]
        summer_time, hour, _ = _decode_hour(data[3:])
        interval = data[4]

        return LongIntervalData(summer_time=summer_time,
                                year=year,
                                month=month,
                                day=day,
                                hour=hour,
                                interval=interval)

    if data_type == DataType.LTA_RESULT_V10:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)

        return LtaResultV10Data(volume_1=volume_1,
                                volume_2=volume_2)

    if data_type == DataType.LTA_RESULT_V11:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed = data[0]

        return LtaResultV11Data(volume_1=volume_1,
                                volume_2=volume_2,
                                speed=speed)

    if data_type == DataType.LTA_RESULT_V12:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]

        return LtaResultV12Data(volume_1=volume_1,
                                volume_2=volume_2,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2)

    if data_type == DataType.LTA_RESULT_V13:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]
        speed_85 = data[4]

        return LtaResultV13Data(volume_1=volume_1,
                                volume_2=volume_2,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                speed_85=speed_85)

    if data_type == DataType.LTA_RESULT_V14:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)

        return LtaResultV14Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6)

    if data_type == DataType.LTA_RESULT_V15:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]

        return LtaResultV15Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2)

    if data_type == DataType.LTA_RESULT_V16:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]
        speed_85 = data[4]

        return LtaResultV16Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                speed_85=speed_85)

    if data_type == DataType.LTA_RESULT_V17:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]
        speed_85 = data[4]
        data = data[5:]
        speed_classes_1, data = _decode_int16_list(data)
        speed_classes_2, data = _decode_int16_list(data)

        return LtaResultV17Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                speed_85=speed_85,
                                speed_classes_1=speed_classes_1,
                                speed_classes_2=speed_classes_2)

    if data_type == DataType.LTA_RESULT_V18:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        speed_3 = data[2]
        speed_4 = data[3]
        speed_5 = data[4]
        standard_deviation_1 = data[5]
        standard_deviation_2 = data[6]
        standard_deviation_3 = data[7]
        standard_deviation_4 = data[8]
        standard_deviation_5 = data[9]
        speed_85 = data[10]
        data = data[11:]
        speed_classes_1, data = _decode_int16_list(data)
        speed_classes_2, data = _decode_int16_list(data)
        speed_classes_3, data = _decode_int16_list(data)
        speed_classes_4, data = _decode_int16_list(data)
        speed_classes_5, data = _decode_int16_list(data)

        return LtaResultV18Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                speed_3=speed_3,
                                speed_4=speed_4,
                                speed_5=speed_5,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                standard_deviation_3=standard_deviation_3,
                                standard_deviation_4=standard_deviation_4,
                                standard_deviation_5=standard_deviation_5,
                                speed_85=speed_85,
                                speed_classes_1=speed_classes_1,
                                speed_classes_2=speed_classes_2,
                                speed_classes_3=speed_classes_3,
                                speed_classes_4=speed_classes_4,
                                speed_classes_5=speed_classes_5)

    if data_type == DataType.LTA_RESULT_V19:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        volume_7, data = _decode_int16(data)
        volume_8, data = _decode_int16(data)
        volume_9, data = _decode_int16(data)

        return LtaResultV19Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                volume_7=volume_7,
                                volume_8=volume_8,
                                volume_9=volume_9)

    if data_type == DataType.LTA_RESULT_V20:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        volume_7, data = _decode_int16(data)
        volume_8, data = _decode_int16(data)
        volume_9, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]

        return LtaResultV20Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                volume_7=volume_7,
                                volume_8=volume_8,
                                volume_9=volume_9,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2)

    if data_type == DataType.LTA_RESULT_V21:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        volume_7, data = _decode_int16(data)
        volume_8, data = _decode_int16(data)
        volume_9, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]
        speed_85 = data[4]

        return LtaResultV21Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                volume_7=volume_7,
                                volume_8=volume_8,
                                volume_9=volume_9,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                speed_85=speed_85)

    if data_type == DataType.LTA_RESULT_V22:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        volume_7, data = _decode_int16(data)
        volume_8, data = _decode_int16(data)
        volume_9, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        standard_deviation_1 = data[2]
        standard_deviation_2 = data[3]
        speed_85 = data[4]
        data = data[5:]
        speed_classes_1, data = _decode_int16_list(data)
        speed_classes_2, data = _decode_int16_list(data)

        return LtaResultV22Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                volume_7=volume_7,
                                volume_8=volume_8,
                                volume_9=volume_9,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                speed_85=speed_85,
                                speed_classes_1=speed_classes_1,
                                speed_classes_2=speed_classes_2)

    if data_type == DataType.LTA_RESULT_V23:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        volume_3, data = _decode_int16(data)
        volume_4, data = _decode_int16(data)
        volume_5, data = _decode_int16(data)
        volume_6, data = _decode_int16(data)
        volume_7, data = _decode_int16(data)
        volume_8, data = _decode_int16(data)
        volume_9, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        speed_3 = data[2]
        speed_4 = data[3]
        speed_5 = data[4]
        speed_6 = data[5]
        speed_7 = data[6]
        speed_8 = data[7]
        standard_deviation_1 = data[8]
        standard_deviation_2 = data[9]
        standard_deviation_3 = data[10]
        standard_deviation_4 = data[11]
        standard_deviation_5 = data[12]
        standard_deviation_6 = data[13]
        standard_deviation_7 = data[14]
        standard_deviation_8 = data[15]
        speed_85 = data[16]
        data = data[17:]
        speed_classes_1, data = _decode_int16_list(data)
        speed_classes_2, data = _decode_int16_list(data)
        speed_classes_3, data = _decode_int16_list(data)
        speed_classes_4, data = _decode_int16_list(data)
        speed_classes_5, data = _decode_int16_list(data)
        speed_classes_6, data = _decode_int16_list(data)
        speed_classes_7, data = _decode_int16_list(data)
        speed_classes_8, data = _decode_int16_list(data)

        return LtaResultV23Data(volume_1=volume_1,
                                volume_2=volume_2,
                                volume_3=volume_3,
                                volume_4=volume_4,
                                volume_5=volume_5,
                                volume_6=volume_6,
                                volume_7=volume_7,
                                volume_8=volume_8,
                                volume_9=volume_9,
                                speed_1=speed_1,
                                speed_2=speed_2,
                                speed_3=speed_3,
                                speed_4=speed_4,
                                speed_5=speed_5,
                                speed_6=speed_6,
                                speed_7=speed_7,
                                speed_8=speed_8,
                                standard_deviation_1=standard_deviation_1,
                                standard_deviation_2=standard_deviation_2,
                                standard_deviation_3=standard_deviation_3,
                                standard_deviation_4=standard_deviation_4,
                                standard_deviation_5=standard_deviation_5,
                                standard_deviation_6=standard_deviation_6,
                                standard_deviation_7=standard_deviation_7,
                                standard_deviation_8=standard_deviation_8,
                                speed_85=speed_85,
                                speed_classes_1=speed_classes_1,
                                speed_classes_2=speed_classes_2,
                                speed_classes_3=speed_classes_3,
                                speed_classes_4=speed_classes_4,
                                speed_classes_5=speed_classes_5,
                                speed_classes_6=speed_classes_6,
                                speed_classes_7=speed_classes_7,
                                speed_classes_8=speed_classes_8)

    if data_type == DataType.RTA_RESULT_V0:
        density, _ = _decode_int16(data)
        speed = data[2]

        return RtaResultV0Data(density=density,
                               speed=speed)

    if data_type == DataType.RTA_RESULT_V1:
        density_1, _ = _decode_int16(data)
        speed_1 = data[2]
        density_2, _ = _decode_int16(data[3:])
        density_3, _ = _decode_int16(data[5:])
        speed_2 = data[7]
        speed_3 = data[8]

        return RtaResultV1Data(density_1=density_1,
                               density_2=density_2,
                               density_3=density_3,
                               speed_1=speed_1,
                               speed_2=speed_2,
                               speed_3=speed_3)

    if data_type == DataType.LTA_RESULT_V0_16:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]

        return LtaResultV0_16Data(volume_1=volume_1,
                                  volume_2=volume_2,
                                  speed_1=speed_1,
                                  speed_2=speed_2)

    if data_type == DataType.LTA_RESULT_V1_16:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        time_gap = data[2]

        return LtaResultV1_16Data(volume_1=volume_1,
                                  volume_2=volume_2,
                                  speed_1=speed_1,
                                  speed_2=speed_2,
                                  time_gap=time_gap)

    if data_type == DataType.LTA_RESULT_V2_16:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        occupancy = data[2]

        return LtaResultV2_16Data(volume_1=volume_1,
                                  volume_2=volume_2,
                                  speed_1=speed_1,
                                  speed_2=speed_2,
                                  occupancy=occupancy)

    if data_type == DataType.LTA_RESULT_V3_16:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        time_gap = data[2]
        occupancy = data[3]
        standard_deviation = data[4]
        smoothed_speed = data[5]

        return LtaResultV3_16Data(volume_1=volume_1,
                                  volume_2=volume_2,
                                  speed_1=speed_1,
                                  speed_2=speed_2,
                                  time_gap=time_gap,
                                  occupancy=occupancy,
                                  standard_deviation=standard_deviation,
                                  smoothed_speed=smoothed_speed)

    if data_type == DataType.LTA_RESULT_V4_16:
        volume_1, data = _decode_int16(data)
        volume_2, data = _decode_int16(data)
        speed_1 = data[0]
        speed_2 = data[1]
        time_gap = data[2]
        occupancy = data[3]
        standard_deviation = data[4]
        smoothed_speed = data[5]
        data = data[6:]
        speed_classes_1, data = _decode_int16_list(data)
        speed_classes_2, data = _decode_int16_list(data)

        return LtaResultV4_16Data(volume_1=volume_1,
                                  volume_2=volume_2,
                                  speed_1=speed_1,
                                  speed_2=speed_2,
                                  time_gap=time_gap,
                                  occupancy=occupancy,
                                  standard_deviation=standard_deviation,
                                  smoothed_speed=smoothed_speed,
                                  speed_classes_1=speed_classes_1,
                                  speed_classes_2=speed_classes_2)

    raise ValueError('unsupported data type')


def _encode_hour(summer_time, hour):
    return ((0x80 if summer_time else 0x00) |
            (hour & 0x7F))


def _decode_hour(data):
    return (bool(data[0] & 0x80),
            (data[0] & 0x7F),
            data[1:])


def _encode_int16(x):
    yield x & 0xFF
    yield (x >> 8) & 0xFF


def _decode_int16(data):
    return ((data[1] << 8) | data[0]), data[2:]


def _encode_int8_list(speed_classes):
    yield len(speed_classes)
    yield from speed_classes


def _decode_int8_list(data):
    return list(data[1:1+data[0]]), data[1+data[0]:]


def _encode_int16_list(speed_classes):
    yield len(speed_classes)
    for i in speed_classes:
        yield i & 0xFF
        yield (i >> 8) & 0xFF


def _decode_int16_list(data):
    return ([((data[2+i*2] << 8) | data[1+i*2])
             for i in range(data[0])],
            data[1+data[0]*2:])
