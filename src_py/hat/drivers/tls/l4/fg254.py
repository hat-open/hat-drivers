from collections.abc import Collection
import collections
import enum
import itertools
import typing

from hat import util

from hat.drivers.tls import l2
from hat.drivers.tls import l3
from hat.drivers.tls.l4 import common


class Channel(typing.NamedTuple):
    physical_channel: common.UInt8
    function_group: common.UInt8
    logical_channel: common.UInt8


class Conf(typing.NamedTuple):
    address: l2.Address
    physical_channel: common.UInt8
    function_group: common.UInt8
    logical_channel: common.UInt8


class Route(typing.NamedTuple):
    function_group: common.UInt8
    addresses: l3.AddressPath


class DataType(enum.Enum):
    ERROR = 1
    ADDITIONAL_ERROR = 14
    NEGATIVE_ACKNOWLEDGEMENT = 16
    INITIALIZATION = 17
    TIME_SYNCHRONISATION = 18
    COMMUNICATION_STATUS = 19
    POSITIVE_ACKNOWLEDGEMENT = 28
    TIME_STAMP = 30
    STATIC_DEVICE_CHARACTERISTICS = 32
    DT_ASSIGNMENT = 33
    CONFIGURATION_TABLE = 34
    ROUTING_FIELD = 35
    GEOGRAPHICAL_CHARACTERISTICS = 36
    NODE_NUMBER = 37
    RESET = 38


class ErrorData(typing.NamedTuple):
    manufacturer_code: common.UInt8
    ioc_error: bool
    cm_error: bool
    projection_error: bool
    passive: bool


class AdditionalErrorData(typing.NamedTuple):
    manufacturer_code: common.UInt8
    error: util.Bytes
    """Length is 4"""
    manufacturer_error: util.Bytes


class NegativeAcknowledgementData(typing.NamedTuple):
    manufacturer_code: common.UInt8
    cause: common.UInt8


class TimeSynchronisationData(typing.NamedTuple):
    summer_time: bool
    hour: common.UInt7
    """In range [0, 23]"""
    minute: common.UInt8
    """In range [0, 59]"""
    second: common.UInt8
    """In range [0, 59]"""
    day: common.UInt8
    """In range [1, 31]"""
    month: common.UInt8
    """In range [1, 12]"""
    year: common.UInt8
    """In range [0, 99]"""
    day_of_week: common.UInt8
    """In range [1, 7]"""


class CommunicationStatusData(typing.NamedTuple):
    out_of_order: bool
    uncertain: bool


class TimeStampData(typing.NamedTuple):
    summer_time: bool
    hour: common.UInt7
    """In range [0, 23]"""
    minute: common.UInt8
    """In range [0, 59]"""
    second: common.UInt8
    """In range [0, 59]"""


class StaticDeviceCharacteristicsData(typing.NamedTuple):
    manufacturer_code: common.UInt8
    device_identification: util.Bytes


class DtAssignmentData(typing.NamedTuple):
    channels: Collection[Channel]


class ConfigurationTableData(typing.NamedTuple):
    confs: Collection[Conf]


class RoutingFieldData(typing.NamedTuple):
    routes: Collection[Route]


class GeographicalCharacteristicsData(typing.NamedTuple):
    country: common.UInt8
    road_type: common.UInt8
    road_number: common.UInt16
    """In range [0, 9999]"""
    kilometrage: float
    """In range [0, 9999.99]"""
    direction: common.UInt8
    """In range [0, 1]"""


class NodeNumberData(typing.NamedTuple):
    node: common.UInt24


class ResetData(typing.NamedTuple):
    reset_cm: bool
    reset_ioc: bool


Data: typing.TypeAlias = (ErrorData |
                          AdditionalErrorData |
                          NegativeAcknowledgementData |
                          TimeSynchronisationData |
                          CommunicationStatusData |
                          TimeStampData |
                          StaticDeviceCharacteristicsData |
                          DtAssignmentData |
                          ConfigurationTableData |
                          RoutingFieldData |
                          GeographicalCharacteristicsData |
                          NodeNumberData |
                          ResetData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, ErrorData):
        return bytes([((1 if data.ioc_error else 0) |
                       (2 if data.cm_error else 0) |
                       (4 if data.projection_error else 0) |
                       (8 if data.passive else 0)),
                      data.manufacturer_code])

    if isinstance(data, AdditionalErrorData):
        return bytes([data.manufacturer_code,
                      4,
                      *([*data.error, *([0] * 4)][:4]),
                      len(data.manufacturer_error),
                      *data.manufacturer_error])

    if isinstance(data, NegativeAcknowledgementData):
        return bytes([data.cause,
                      data.manufacturer_code])

    if isinstance(data, TimeSynchronisationData):
        return bytes([((0x80 if data.summer_time else 0) |
                       data.hour),
                      data.minute,
                      data.second,
                      data.day,
                      data.month,
                      data.year,
                      data.day_of_week])

    if isinstance(data, CommunicationStatusData):
        return bytes([(1 if data.out_of_order else 0) |
                      (2 if data.uncertain else 0)])

    if isinstance(data, TimeStampData):
        return bytes([((0x80 if data.summer_time else 0) |
                       data.hour),
                      data.minute,
                      data.second])

    if isinstance(data, StaticDeviceCharacteristicsData):
        return bytes([data.manufacturer_code,
                      *data.device_identification])

    if isinstance(data, DtAssignmentData):
        return bytes(itertools.chain(
            [len(data.channels)],
            itertools.chain.from_iterable([i.physical_channel,
                                           i.function_group,
                                           i.logical_channel]
                                          for i in data.channels)))

    if isinstance(data, ConfigurationTableData):
        return bytes(itertools.chain(
            [len(data.confs)],
            itertools.chain.from_iterable([i.address,
                                           i.physical_channel,
                                           i.function_group,
                                           i.logical_channel]
                                          for i in data.confs)))

    if isinstance(data, RoutingFieldData):
        return bytes(itertools.chain(
            [len(data.routes)],
            itertools.chain.from_iterable(
                itertools.chain(
                    [2 * (len(route.addresses) + 1),
                     route.function_group,
                     len(route.addresses) << 3],
                    itertools.chain.from_iterable(route.addresses))
                for route in data.routes)))

    if isinstance(data, GeographicalCharacteristicsData):
        return bytes([data.country,
                      data.road_type,
                      (data.road_number // 100) % 100,
                      data.road_number % 100,
                      int(data.kilometrage / 100) % 100,
                      int(data.kilometrage) % 100,
                      int(data.kilometrage * 100) % 100,
                      data.direction,
                      0])

    if isinstance(data, NodeNumberData):
        return bytes([(data.node & 0xFF),
                      ((data.node >> 8) & 0xFF),
                      ((data.node >> 16) & 0xFF)])

    if isinstance(data, ResetData):
        return bytes([(0x01 if data.reset_cm else 0) |
                      (0x10 if data.reset_ioc else 0)])

    raise TypeError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.ERROR:
        ioc_error = bool(data[0] & 1)
        cm_error = bool(data[0] & 2)
        projection_error = bool(data[0] & 4)
        passive = bool(data[0] & 8)
        manufacturer_code = data[1]

        return ErrorData(manufacturer_code=manufacturer_code,
                         ioc_error=ioc_error,
                         cm_error=cm_error,
                         projection_error=projection_error,
                         passive=passive)

    if data_type == DataType.ADDITIONAL_ERROR:
        manufacturer_code = data[0]
        error_len = data[1]
        error = data[2:2+error_len]
        manufacturer_error_len = data[2+error_len]
        manufacturer_error = data[3+error_len:
                                  3+error_len+manufacturer_error_len]

        return AdditionalErrorData(manufacturer_code=manufacturer_code,
                                   error=error,
                                   manufacturer_error=manufacturer_error)

    if data_type == DataType.NEGATIVE_ACKNOWLEDGEMENT:
        cause = data[0]
        manufacturer_code = data[1]

        return NegativeAcknowledgementData(manufacturer_code=manufacturer_code,
                                           cause=cause)

    if data_type == DataType.TIME_SYNCHRONISATION:
        summer_time = bool(data[0] & 0x80)
        hour = data[0] & 0x7F
        minute = data[1]
        second = data[2]
        day = data[3]
        month = data[4]
        year = data[5]
        day_of_week = data[6]

        return TimeSynchronisationData(summer_time=summer_time,
                                       hour=hour,
                                       minute=minute,
                                       second=second,
                                       day=day,
                                       month=month,
                                       year=year,
                                       day_of_week=day_of_week)

    if data_type == DataType.COMMUNICATION_STATUS:
        out_of_order = bool(data[0] & 1)
        uncertain = bool(data[0] & 2)

        return CommunicationStatusData(out_of_order=out_of_order,
                                       uncertain=uncertain)

    if data_type == DataType.TIME_STAMP:
        summer_time = bool(data[0] & 0x80)
        hour = data[0] & 0x7F
        minute = data[1]
        second = data[2]

        return TimeStampData(summer_time=summer_time,
                             hour=hour,
                             minute=minute,
                             second=second)

    if data_type == DataType.STATIC_DEVICE_CHARACTERISTICS:
        manufacturer_code = data[0]
        device_identification = data[1:]

        return StaticDeviceCharacteristicsData(
            manufacturer_code=manufacturer_code,
            device_identification=device_identification)

    if data_type == DataType.DT_ASSIGNMENT:
        channels = collections.deque()

        for i in range(data[0]):
            physical_channel = data[i * 3 + 1]
            function_group = data[i * 3 + 2]
            logical_channel = data[i * 3 + 3]

            channels.append(Channel(physical_channel=physical_channel,
                                    function_group=function_group,
                                    logical_channel=logical_channel))

        return DtAssignmentData(channels=channels)

    if data_type == DataType.CONFIGURATION_TABLE:
        confs = collections.deque()

        for i in range(data[0]):
            address = data[i * 4 + 1]
            physical_channel = data[i * 4 + 2]
            function_group = data[i * 4 + 3]
            logical_channel = data[i * 4 + 4]

            confs.append(Conf(address=address,
                              physical_channel=physical_channel,
                              function_group=function_group,
                              logical_channel=logical_channel))

        return ConfigurationTableData(confs=confs)

    if data_type == DataType.ROUTING_FIELD:
        routes = collections.deque()
        routes_len, data = data[0], data[1:]

        for _ in range(routes_len):
            addresses = []
            block_len = data[0]
            function_group = data[1]
            addresses_len = data[2] >> 3

            if addresses_len != (block_len / 2 - 1):
                raise ValueError('addresses length not matching')

            data = data[3:]
            for _ in range(addresses_len):
                addresses.append((data[0], data[1]))
                data = data[2:]

            routes.append(Route(function_group=function_group,
                                addresses=addresses))

        return RoutingFieldData(routes=routes)

    if data_type == DataType.GEOGRAPHICAL_CHARACTERISTICS:
        country = data[0]
        road_type = data[1]
        road_number = data[2] * 100 + data[3]
        kilometrage = data[4] * 100 + data[5] + data[6] / 100
        direction = data[7]

        return GeographicalCharacteristicsData(country=country,
                                               road_type=road_type,
                                               road_number=road_number,
                                               kilometrage=kilometrage,
                                               direction=direction)

    if data_type == DataType.NODE_NUMBER:
        node = (data[0] |
                (data[1] << 8) |
                (data[2] << 16))

        return NodeNumberData(node=node)

    if data_type == DataType.RESET:
        reset_cm = bool(data[0] & 0x01)
        reset_ioc = bool(data[0] & 0x10)

        return ResetData(reset_cm=reset_cm,
                         reset_ioc=reset_ioc)

    raise ValueError('unsupported data type')
