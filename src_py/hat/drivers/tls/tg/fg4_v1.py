from collections.abc import Collection
import collections
import enum
import math
import typing

from hat import util

from hat.drivers.tls import common
from hat.drivers.tls import fg4


FunctionType: typing.TypeAlias = fg4.FunctionType


class StopBits(enum.Enum):
    DEFAULT = 0
    ONE = 1
    TWO = 2


class Parity(enum.Enum):
    DEFAULT = 0
    NONE = 1
    EVEN = 2
    ODD = 3


class BaudRate(enum.Enum):
    DEFAULT = 0
    B1200 = 1
    B2400 = 2
    B4800 = 3
    B9600 = 4
    B19200 = 5
    B38400 = 6


class VmsType(enum.Enum):
    SYMBOLS = 64
    TEXT = 128
    DISPLAY = 200


class PictureFormat(enum.Enum):
    UNCOMPRESSED = 0
    COMPRESSED = 1
    COMPRESSED_STREAM = 2


class Function(typing.NamedTuple):
    type: FunctionType
    indication_time: common.UInt4
    brightness_value: common.UInt7
    """In range [0, 100]"""
    brightness_automatic: bool


class DriverStatus(typing.NamedTuple):
    comm_error: bool
    transistor_error: bool
    led_errors: common.UInt7


class DriverStatusV2(typing.NamedTuple):
    comm_error: bool
    led_errors: common.UInt8


class LuxmeterStatus(typing.NamedTuple):
    cal_error: bool
    comm_error: bool


class PictureSequenceItem(typing.NamedTuple):
    picture: common.UInt8 | util.Bytes
    duration: common.UInt8


class DataType(enum.Enum):
    POSITIVE_ACKNOWLEDGEMENT = 28
    PICTURE = 133
    SYNCH = 135
    RESET = 136
    VMS_TYPE = 140
    COMMUNICATION_PARAMETERS = 143
    VMS_PARAMETERS = 144
    SOFTWARE_VERSION = 145
    POWER_SUPPLY_TEMPERATURE = 146
    TEXT = 149
    CONTROLLER_STATUS_V1 = 192
    DETAILED_DRIVER_STATUS_V1 = 193
    DISPLAY_PARAMETERS = 196
    PICTURE_SEQUENCE = 202
    LUXMETER_INTENSITY = 203
    LUXMETER_STATUS = 204
    TTF_TEXT = 207
    CONFIGURATION_VERSION = 208
    CONTROLLER_STATUS_V3 = 209
    CONTROLLER_STATUS_V2 = 223
    DETAILED_DRIVER_STATUS_V2 = 224
    ERASE = 230


class PictureData(typing.NamedTuple):
    code: common.UInt8
    function: Function


class SynchData(typing.NamedTuple):
    store: bool


class ResetData(typing.NamedTuple):
    code: common.UInt8


class VmsTypeData(typing.NamedTuple):
    vms_type: VmsType
    shape: common.UInt8
    program0: common.UInt8
    program1: common.UInt8
    program2: common.UInt8
    program3: common.UInt8


class CommunicationParametersData(typing.NamedTuple):
    address: common.UInt8
    stopbits: StopBits
    parity: Parity
    baudrate: BaudRate
    databits: common.UInt8
    """In range [5, 9]"""
    response_time: common.UInt8
    rts_time_before: common.UInt8
    rts_time_after: common.UInt8


class VmsParametersData(typing.NamedTuple):
    parameters: Collection[common.UInt8]


class SoftwareVersionData(typing.NamedTuple):
    version: tuple[common.UInt8, common.UInt8]
    day: common.UInt8
    month: common.UInt8
    year: common.UInt16
    crc: common.UInt32


class PowerSupplyTemperatureData(typing.NamedTuple):
    temperature: common.UInt8


class TextData(typing.NamedTuple):
    function: Function
    text: util.Bytes


class ControllerStatusV1Data(typing.NamedTuple):
    controller: common.UInt6
    comm_error: bool
    conf_error: bool
    drivers: Collection[DriverStatus]
    """Length is 32"""


class DetailedDriverStatusV1Data(typing.NamedTuple):
    controller: common.UInt8
    driver: common.UInt8
    """In range [0, 31]"""
    errors: Collection[bool]
    """Length is 96"""


class DisplayParametersData(typing.NamedTuple):
    colors_per_pixel: common.UInt8
    width: common.UInt16
    height: common.UInt16
    picture_formats: Collection[PictureFormat]


class PictureSequenceData(typing.NamedTuple):
    intensity: common.UInt8
    """In range [0, 100]"""
    on: bool
    sequence: Collection[PictureSequenceItem]


class TtfTextData(typing.NamedTuple):
    function: Function
    text: str


class LuxmeterIntensityData(typing.NamedTuple):
    intensities: Collection[common.UInt16]
    """Length is 8"""


class LuxmeterStatusData(typing.NamedTuple):
    statuses: Collection[LuxmeterStatus]
    """Length is 8"""


class ConfigurationVersionData(typing.NamedTuple):
    date: util.Bytes
    """Length is 8"""
    name: util.Bytes


class ControllerStatusV3Data(typing.NamedTuple):
    controller: common.UInt8
    comm_error: bool
    conf_error: bool
    drivers: Collection[DriverStatus]
    """Length is 64"""


class ControllerStatusV2Data(typing.NamedTuple):
    controller: common.UInt8
    comm_error: bool
    conf_error: bool
    group_count: common.UInt8
    group_index: common.UInt8
    drivers: Collection[DriverStatus]
    """Length is 128"""


class DetailedDriverStatusV2Data(typing.NamedTuple):
    controller: common.UInt8
    driver: common.UInt16
    errors: Collection[bool]
    """Length is 48"""


class EraseData(typing.NamedTuple):
    bitmap: common.UInt8


Data: typing.TypeAlias = (PictureData |
                          SynchData |
                          ResetData |
                          VmsTypeData |
                          CommunicationParametersData |
                          VmsParametersData |
                          SoftwareVersionData |
                          PowerSupplyTemperatureData |
                          TextData |
                          ControllerStatusV1Data |
                          DetailedDriverStatusV1Data |
                          DisplayParametersData |
                          PictureSequenceData |
                          TtfTextData |
                          LuxmeterIntensityData |
                          LuxmeterStatusData |
                          ConfigurationVersionData |
                          ControllerStatusV3Data |
                          ControllerStatusV2Data |
                          DetailedDriverStatusV2Data |
                          EraseData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, PictureData):
        return bytes([data.code,
                      *_encode_function(data.function),
                      0])

    if isinstance(data, SynchData):
        return bytes([1 if data.store else 0])

    if isinstance(data, ResetData):
        return bytes([data.code])

    if isinstance(data, VmsTypeData):
        return bytes([data.vms_type.value,
                      0,
                      data.shape,
                      data.program0,
                      data.program1,
                      data.program2,
                      data.program3])

    if isinstance(data, CommunicationParametersData):
        return bytes([data.address,
                      ((data.stopbits.value << 6) |
                       (data.parity.value << 4) |
                       data.baudrate.value),
                      data.databits,
                      data.response_time,
                      data.rts_time_before,
                      data.rts_time_after,
                      0])

    if isinstance(data, VmsParametersData):
        return bytes([len(data.parameters),
                      *data.parameters])

    if isinstance(data, SoftwareVersionData):
        return bytes([*data.version,
                      data.day,
                      data.month,
                      (data.year & 0xff),
                      (data.year >> 8),
                      (data.crc & 0xff),
                      ((data.crc >> 8) & 0xff),
                      ((data.crc >> 16) & 0xff),
                      (data.crc >> 24)])

    if isinstance(data, PowerSupplyTemperatureData):
        return bytes([data.temperature])

    if isinstance(data, TextData):
        return bytes([*_encode_function(data.function),
                      len(data.text),
                      *data.text])

    if isinstance(data, ControllerStatusV1Data):
        return bytes([((0x80 if data.conf_error else 0x00) |
                       (0x40 if data.comm_error else 0x00) |
                       data.controller),
                      *_encode_driver_statuses(data.drivers)])

    if isinstance(data, DetailedDriverStatusV1Data):
        return bytes([data.controller,
                      data.driver,
                      *_encode_bits(data.errors)])

    if isinstance(data, DisplayParametersData):
        return bytes([data.colors_per_pixel,
                      1,
                      8,
                      (data.width & 0xff),
                      (data.width >> 8),
                      (data.height & 0xff),
                      (data.height >> 8),
                      len(data.picture_formats),
                      *(i.value for i in data.picture_formats)])

    if isinstance(data, PictureSequenceData):
        return bytes([0,
                      data.intensity,
                      (1 if data.on else 0),
                      *_encode_picture_sequence(data.sequence)])

    if isinstance(data, LuxmeterIntensityData):
        intensities = [0] * (len(data.intensities) * 2)

        for i, intensity in enumerate(data.intensities):
            intensities[i * 2] = intensity & 0xff
            intensities[i * 2 + 1] = intensity >> 8

        return bytes(intensities)

    if isinstance(data, LuxmeterStatusData):
        return bytes([((0x02 if status.comm_error else 0x00) |
                       (0x01 if status.cal_error else 0x00))
                      for status in data.statuses])

    if isinstance(data, TtfTextData):
        return bytes([*_encode_function(data.function),
                      len(data.text),
                      *data.text])

    if isinstance(data, ConfigurationVersionData):
        return bytes([*data.date,
                      *data.name])

    if isinstance(data, ControllerStatusV3Data):
        return bytes([data.controller,
                      ((0x02 if data.conf_error else 0x00) |
                       (0x01 if data.comm_error else 0x00)),
                      *_encode_driver_statuses(data.drivers)])

    if isinstance(data, ControllerStatusV2Data):
        return bytes([data.controller,
                      ((0x02 if data.conf_error else 0x00) |
                       (0x01 if data.comm_error else 0x00)),
                      data.group_count,
                      data.group_index,
                      *_encode_driver_statuses_v2(data.drivers)])

    if isinstance(data, DetailedDriverStatusV2Data):
        return bytes([data.controller,
                      (data.driver & 0xff),
                      (data.driver >> 8),
                      *_encode_bits(data.errors)])

    if isinstance(data, EraseData):
        return bytes([data.bitmap])

    raise TypeError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.PICTURE:
        code = data[0]
        function = _decode_function(data[1:])

        return PictureData(code=code,
                           function=function)

    if data_type == DataType.SYNCH:
        store = bool(data[0])

        return SynchData(store=store)

    if data_type == DataType.RESET:
        code = data[0]

        return ResetData(code=code)

    if data_type == DataType.VMS_TYPE:
        vms_type = VmsType(data[0])
        shape = data[2]
        program0 = data[3]
        program1 = data[4]
        program2 = data[5]
        program3 = data[6]

        return VmsTypeData(vms_type=vms_type,
                           shape=shape,
                           program0=program0,
                           program1=program1,
                           program2=program2,
                           program3=program3)

    if data_type == DataType.COMMUNICATION_PARAMETERS:
        address = data[0]
        stopbits = StopBits(data[1] >> 6)
        parity = Parity((data[1] >> 4) & 0x03)
        baudrate = BaudRate(data[1] & 0x0f)
        databits = data[2]
        response_time = data[3]
        rts_time_before = data[4]
        rts_time_after = data[5]

        return CommunicationParametersData(address=address,
                                           stopbits=stopbits,
                                           parity=parity,
                                           baudrate=baudrate,
                                           databits=databits,
                                           response_time=response_time,
                                           rts_time_before=rts_time_before,
                                           rts_time_after=rts_time_after)

    if data_type == DataType.VMS_PARAMETERS:
        parameters = list(data[1:])

        return VmsParametersData(parameters=parameters)

    if data_type == DataType.SOFTWARE_VERSION:
        version = tuple(data[:2])
        day = data[2]
        month = data[3]
        year = data[4] | (data[5] << 8)
        crc = data[6] | (data[7] << 8) | (data[8] << 16) | (data[9] << 24)

        return SoftwareVersionData(version=version,
                                   day=day,
                                   month=month,
                                   year=year,
                                   crc=crc)

    if data_type == DataType.POWER_SUPPLY_TEMPERATURE:
        temperature = data[0]

        return PowerSupplyTemperatureData(temperature=temperature)

    if data_type == DataType.TEXT:
        function = _decode_function(data[:2])
        text = data[3:3+data[2]]

        return TextData(function=function,
                        text=text)

    if data_type == DataType.CONTROLLER_STATUS_V1:
        controller = data[0] & 0x3f
        comm_error = bool(data[0] & 0x40)
        conf_error = bool(data[0] & 0x80)
        drivers = _decode_driver_statuses(data[1:])

        return ControllerStatusV1Data(controller=controller,
                                      comm_error=comm_error,
                                      conf_error=conf_error,
                                      drivers=drivers)

    if data_type == DataType.DETAILED_DRIVER_STATUS_V1:
        controller = data[0]
        driver = data[1]
        errors = _decode_bits(data[2:])

        return DetailedDriverStatusV1Data(controller=controller,
                                          driver=driver,
                                          errors=errors)

    if data_type == DataType.DISPLAY_PARAMETERS:
        colors_per_pixel = data[0]
        width = data[3] | (data[4] << 8)
        height = data[5] | (data[6] << 8)
        picture_formats = [PictureFormat(data[8 + i])
                           for i in range(data[7])]

        return DisplayParametersData(colors_per_pixel=colors_per_pixel,
                                     width=width,
                                     height=height,
                                     picture_formats=picture_formats)

    if data_type == DataType.PICTURE_SEQUENCE:
        intensity = data[1]
        on = bool(data[2])
        sequence = _decode_picture_sequence(data[3:])

        return PictureSequenceData(intensity=intensity,
                                   on=on,
                                   sequence=sequence)

    if data_type == DataType.LUXMETER_INTENSITY:
        intensities = [0] * (len(data) // 2)

        for i in range(len(intensities)):
            intensities[i] = data[i * 2] | (data[i * 2 + 1] << 8)

        return LuxmeterIntensityData(intensities=intensities)

    if data_type == DataType.LUXMETER_STATUS:
        statuses = [LuxmeterStatus(cal_error=bool(i & 0x01),
                                   comm_error=bool(i & 0x02))
                    for i in data]

        return LuxmeterStatusData(statuses=statuses)

    if data_type == DataType.TTF_TEXT:
        function = _decode_function(data[:2])
        text = data[3:3+data[2]]

        return TextData(function=function,
                        text=text)

    if data_type == DataType.CONFIGURATION_VERSION:
        date = data[:8]
        name = data[8:]

        return ConfigurationVersionData(date=date,
                                        name=name)

    if data_type == DataType.CONTROLLER_STATUS_V3:
        controller = data[0]
        comm_error = bool(data[1] & 0x01)
        conf_error = bool(data[1] & 0x02)
        drivers = _decode_driver_statuses(data[2:])

        return ControllerStatusV3Data(controller=controller,
                                      comm_error=comm_error,
                                      conf_error=conf_error,
                                      drivers=drivers)

    if data_type == DataType.CONTROLLER_STATUS_V2:
        controller = data[0]
        comm_error = bool(data[1] & 0x01)
        conf_error = bool(data[1] & 0x02)
        group_count = data[2]
        group_index = data[3]
        drivers = _decode_driver_statuses_v2(data[4:])

        return ControllerStatusV2Data(controller=controller,
                                      comm_error=comm_error,
                                      conf_error=conf_error,
                                      group_count=group_count,
                                      group_index=group_index,
                                      drivers=drivers)

    if data_type == DataType.DETAILED_DRIVER_STATUS_V2:
        controller = data[0]
        driver = data[1] | (data[2] << 8)
        errors = _decode_bits(data[3:])

        return DetailedDriverStatusV2Data(controller=controller,
                                          driver=driver,
                                          errors=errors)

    if data_type == DataType.ERASE:
        bitmap = data[0]

        return EraseData(bitmap=bitmap)

    raise ValueError('unsupported data type')


def _encode_function(function):
    return bytes([((function.indication_time << 4) |
                   function.type.value),
                  ((0x80 if function.brightness_automatic else 0x00) |
                   function.brightness_value)])


def _decode_function(data):
    function_type = FunctionType(data[0] & 0x0f)
    indication_time = data[0] >> 4
    brightness_value = data[1] & 0x7f
    brightness_automatic = bool(data[1] & 0x80)

    return Function(type=function_type,
                    indication_time=indication_time,
                    brightness_value=brightness_value,
                    brightness_automatic=brightness_automatic)


def _encode_driver_statuses(drivers):
    if not drivers:
        return b''

    comm_errors = [0] * math.ceil(len(drivers) / 8)
    transistor_led_errors = collections.deque()

    for i, driver in enumerate(drivers):
        if driver.comm_error:
            comm_errors[i // 8] |= 1 << (i % 8)

        transistor_led_errors.append(
            (0x80 if driver.transistor_error else 0x00) |
            driver.led_errors)

    return bytes([*comm_errors, *transistor_led_errors])


def _decode_driver_statuses(data):
    if not data:
        return []

    drivers_len = len(data) - math.ceil(len(data) / 9)
    if math.ceil(drivers_len / 8) + drivers_len != len(data):
        raise ValueError('invalid data length')

    drivers = [None] * drivers_len
    for i in range(drivers_len):
        comm_error = bool(data[i // 8] & (1 << (i % 8)))
        transistor_error = bool(data[-(drivers_len - i)] & 0x80)
        led_errors = data[-(drivers_len - i)] & 0x7f

        drivers[i] = DriverStatus(comm_error=comm_error,
                                  transistor_error=transistor_error,
                                  led_errors=led_errors)

    return drivers


def _encode_driver_statuses_v2(drivers):
    if not drivers:
        return b''

    comm_errors = [0] * math.ceil(len(drivers) / 8)
    transistor_led_errors = collections.deque()

    for i, driver in enumerate(drivers):
        if driver.comm_error:
            comm_errors[i // 8] |= 1 << (i % 8)

        transistor_led_errors.append(driver.led_errors)

    return bytes([*comm_errors, *transistor_led_errors])


def _decode_driver_statuses_v2(data):
    if not data:
        return []

    drivers_len = len(data) - math.ceil(len(data) / 9)
    if math.ceil(drivers_len / 8) + drivers_len != len(data):
        raise ValueError('invalid data length')

    drivers = [None] * drivers_len
    for i in range(drivers_len):
        comm_error = bool(data[i // 8] & (1 << (i % 8)))
        led_errors = data[-(drivers_len - i)]

        drivers[i] = DriverStatusV2(comm_error=comm_error,
                                    led_errors=led_errors)

    return drivers


def _encode_picture_sequence(sequence):
    data = collections.deque([len(sequence)])

    for item in sequence:
        if isinstance(item.picture, int):
            data.append(item.picture)

        else:
            data.append(255)
            data.append(len(item.picture))
            data.extend(item.picture)

        data.append(item.duration)

    return bytes(data)


def _decode_picture_sequence(data):
    sequence = [None] * data[0]
    rest = data[1:]

    for i in range(len(sequence)):
        picture, rest = rest[0], rest[1:]
        if picture == 255:
            picture_len, rest = rest[0], rest[1:]
            picture, rest = rest[:picture_len], rest[picture_len:]

        duration, rest = rest[0], rest[1:]

        sequence[i] = PictureSequenceItem(picture=picture,
                                          duration=duration)

    return sequence


def _encode_bits(values):
    data = [0] * math.ceil(len(values) / 8)

    for i, value in enumerate(values):
        if value:
            data[i // 8] |= 1 << (i % 8)

    return bytes(data)


def _decode_bits(data):
    return [bool(value & (1 << i))
            for value in data
            for i in range(8)]
