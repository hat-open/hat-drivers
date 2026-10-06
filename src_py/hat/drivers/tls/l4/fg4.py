from collections.abc import Collection
import collections
import enum
import itertools
import typing

from hat import util

from hat.drivers.tls.l4 import common
from hat.drivers.tls.l4 import fg1
from hat.drivers.tls.l4 import fg254


class DisplayPrinciple(enum.Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    CLUSTER = 8
    ERROR = 21


class FunctionType(enum.Enum):
    OFF = 0
    ON = 1
    INDICATE = 2


class Function(typing.NamedTuple):
    type: FunctionType
    status_error: bool
    status_not_terminated: bool
    indication_time: common.UInt4


class DataType(enum.Enum):
    ERROR = 1
    NON_DISPLAYABLE_VMS = 2
    DEFECTIVE_LAMPS = 3
    MALFUNCTIONING_TEXT_ITEMS = 4
    ADDITIONAL_ERROR = 14
    NEGATIVE_ACKNOWLEDGEMENT = 16
    OPERATING_MODE = 17
    RETRIEVAL_BUFFER_CONTENT = 20
    RETRIEVAL_CODE_DEFINITION = 21
    CHANNEL_CONTROL = 29
    TIME_STAMP = 30
    TIME_STAMP_WITH_SEQUENCE_NUMBER = 31
    VMS_BASIC_SETTING = 32
    BASIC_SETTING = 33
    GEOGRAPHICAL_CHARACTERISTICS = 36
    BASIC_PROGRAMME = 42
    CODE_LIST = 43
    CODE_DEFINITION = 44
    VMS_SETTING_STATUS = 48
    BRIGHTNESS = 49
    VARIABLE_TEXT = 50
    SETTING_STATUS = 55
    SETTING_PROGRAMME = 58


ErrorData: typing.TypeAlias = fg254.ErrorData


class NonDisplayableVmsData(typing.NamedTuple):
    codes: typing.List[common.UInt8]


class DefectiveLampsData(typing.NamedTuple):
    defective_main_lamps: typing.List[bool]
    defective_additional_lamps: typing.List[bool]


class MalfunctioningTextItemsData(typing.NamedTuple):
    items: typing.List[common.UInt8]


AdditionalErrorData: typing.TypeAlias = fg254.AdditionalErrorData


NegativeAcknowledgementData: typing.TypeAlias = fg254.NegativeAcknowledgementData  # NOQA


class OperatingModeData(typing.NamedTuple):
    mode: common.UInt8


class RetrievalBufferContentData(typing.NamedTuple):
    sequence_number: common.UInt16
    message_count: common.UInt8


class RetrievalCodeDefinitionData(typing.NamedTuple):
    setting_code: common.UInt8


ChannelControlData: typing.TypeAlias = fg1.ChannelControlData


TimeStampData: typing.TypeAlias = fg254.TimeStampData


class TimeStampWithSequenceNumberData(typing.NamedTuple):
    summer_time: bool
    hour: common.UInt8
    """In range [0, 23]"""
    minute: common.UInt8
    """In range [0, 59]"""
    second: common.UInt8
    """In range [0, 59]"""
    day: common.UInt8
    """In range [1, 31]"""
    sequence_number: common.UInt16


class VmsBasicSettingData(typing.NamedTuple):
    code: common.UInt8
    function: Function


class BasicSettingData(typing.NamedTuple):
    display_principle: DisplayPrinciple
    basic_setting_code: common.UInt8
    function: Function
    component_setting_codes: (Collection[common.UInt8] |
                              Collection[tuple[common.UInt8, Function]])


GeographicalCharacteristicsData: typing.TypeAlias = fg254.GeographicalCharacteristicsData  # NOQA


class BasicProgrammeData(typing.NamedTuple):
    number: common.UInt8


class CodeListData(typing.NamedTuple):
    display_principle: DisplayPrinciple
    setting_codes: typing.List[common.UInt8]


class CodeDefinitionData(typing.NamedTuple):
    display_principle: DisplayPrinciple
    setting_code: common.UInt8
    component_definitions: (Collection[common.UInt8] |
                            Collection[tuple[common.UInt8, Function]] |
                            Collection[tuple[common.UInt8,
                                             DisplayPrinciple,
                                             common.UInt8,
                                             Function]])


class VmsSettingStatusData(typing.NamedTuple):
    code: common.UInt8
    function: Function


class BrightnessData(typing.NamedTuple):
    value: common.UInt8
    """In range [0, 100]"""
    automatic: bool
    messages: bool


class VariableTextData(typing.NamedTuple):
    function: Function
    text: util.Bytes


class SettingStatusData(typing.NamedTuple):
    display_principle: DisplayPrinciple
    setting_code: common.UInt8
    function: Function
    component_statuses: (Collection[common.UInt8] |
                         Collection[tuple[common.UInt8, Function]])


class SettingProgrammeData(typing.NamedTuple):
    number: common.UInt8
    status_not_terminated: bool
    status_error: bool


Data: typing.TypeAlias = (ErrorData |
                          NonDisplayableVmsData |
                          DefectiveLampsData |
                          MalfunctioningTextItemsData |
                          AdditionalErrorData |
                          NegativeAcknowledgementData |
                          OperatingModeData |
                          RetrievalBufferContentData |
                          RetrievalCodeDefinitionData |
                          ChannelControlData |
                          TimeStampData |
                          TimeStampWithSequenceNumberData |
                          VmsBasicSettingData |
                          BasicSettingData |
                          GeographicalCharacteristicsData |
                          BasicProgrammeData |
                          CodeListData |
                          CodeDefinitionData |
                          VmsSettingStatusData |
                          BrightnessData |
                          VariableTextData |
                          SettingStatusData |
                          SettingProgrammeData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, ErrorData):
        return fg254.encode(data)

    if isinstance(data, NonDisplayableVmsData):
        return bytes(itertools.chain([len(data.codes)], data.codes))

    if isinstance(data, DefectiveLampsData):
        res = collections.deque()
        res.append(max(len(data.defective_main_lamps),
                       len(data.defective_additional_lamps)))
        for i, (main, additional) in enumerate(itertools.zip_longest(
                data.defective_main_lamps,
                data.defective_additional_lamps,
                fillvalue=False)):
            i = i % 4
            status = res.pop() if i else 0
            if main:
                status = status | (1 << (i * 2))
            if additional:
                status = status | (1 << ((i * 2) + 1))
            res.append(status)
        return bytes(res)

    if isinstance(data, MalfunctioningTextItemsData):
        return bytes(itertools.chain([len(data.items)], data.items))

    if isinstance(data, AdditionalErrorData):
        return fg254.encode(data)

    if isinstance(data, NegativeAcknowledgementData):
        return fg254.encode(data)

    if isinstance(data, OperatingModeData):
        return bytes([data.mode])

    if isinstance(data, RetrievalBufferContentData):
        return bytes([data.sequence_number & 0xFF,
                      data.sequence_number >> 8,
                      data.message_count])

    if isinstance(data, RetrievalCodeDefinitionData):
        return bytes([data.setting_code])

    if isinstance(data, ChannelControlData):
        return fg1.encode(data)

    if isinstance(data, TimeStampData):
        return fg254.encode(data)

    if isinstance(data, TimeStampWithSequenceNumberData):
        return bytes([((0x80 if data.summer_time else 0) |
                       data.hour),
                      data.minute,
                      data.second,
                      data.day,
                      data.sequence_number & 0xFF,
                      data.sequence_number >> 8])

    if isinstance(data, VmsBasicSettingData):
        return bytes([data.code,
                      encode_function(data.function)])

    if isinstance(data, BasicSettingData):
        ret = [data.display_principle.value,
               data.basic_setting_code,
               encode_function(data.function)]
        if data.display_principle in (DisplayPrinciple.C,
                                      DisplayPrinciple.D,
                                      DisplayPrinciple.E):
            ret = itertools.chain(
                ret,
                [len(data.component_setting_codes)],
                itertools.chain.from_iterable(
                    ([i] if isinstance(i, int) else
                     [i[0], encode_function(i[1])])
                    for i in data.component_setting_codes))
        return bytes(ret)

    if isinstance(data, GeographicalCharacteristicsData):
        return fg254.encode(data)

    if isinstance(data, BasicProgrammeData):
        return bytes([data.number])

    if isinstance(data, CodeListData):
        return bytes(itertools.chain(
            [data.display_principle.value,
             len(data.setting_codes)],
            data.setting_codes))

    if isinstance(data, CodeDefinitionData):
        return bytes(itertools.chain(
            [data.display_principle.value,
             data.setting_code,
             len(data.component_definitions)],
            itertools.chain.from_iterable(
                ([i] if isinstance(i, int) else
                 [i[0], encode_function(i[1])] if len(i) == 2 else
                 [i[0], i[1].value, i[2], encode_function(i[3])])
                for i in data.component_definitions)))

    if isinstance(data, VmsSettingStatusData):
        return bytes([data.code,
                      encode_function(data.function)])

    if isinstance(data, BrightnessData):
        return bytes([data.value,
                      ((0x01 if data.automatic else 0x00) |
                       (0x02 if data.messages else 0x00))])

    if isinstance(data, VariableTextData):
        return bytes(itertools.chain(
            [encode_function(data.function),
             len(data.text)],
            data.text))

    if isinstance(data, SettingStatusData):
        ret = [data.display_principle.value,
               data.setting_code,
               encode_function(data.function)]
        if data.display_principle in (DisplayPrinciple.C,
                                      DisplayPrinciple.D,
                                      DisplayPrinciple.E):
            ret = itertools.chain(
                ret,
                [len(data.component_statuses)],
                itertools.chain.from_iterable(
                    ([i] if isinstance(i, int) else
                     [i[0], encode_function(i[1])])
                    for i in data.component_statuses))
        return bytes(ret)

    if isinstance(data, SettingProgrammeData):
        return bytes([data.number,
                      ((0x01 if data.status_not_terminated else 0x00) |
                       (0x02 if data.status_error else 0x00))])

    raise ValueError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.ERROR:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.NON_DISPLAYABLE_VMS:
        codes = list(data[1:1+data[0]])

        return NonDisplayableVmsData(codes=codes)

    if data_type == DataType.DEFECTIVE_LAMPS:
        defective_main_lamps = []
        defective_additional_lamps = []
        for i in range(data[0]):
            defective_main_lamps.append(
                bool(data[1 + (i // 4)] & (1 << (i % 4) * 2)))
            defective_additional_lamps.append(
                bool(data[1 + (i // 4)] & (1 << (((i % 4) * 2) + 1))))

        return DefectiveLampsData(
            defective_main_lamps=defective_main_lamps,
            defective_additional_lamps=defective_additional_lamps)

    if data_type == DataType.MALFUNCTIONING_TEXT_ITEMS:
        items = list(data[1:1+data[0]])

        return MalfunctioningTextItemsData(items=items)

    if data_type == DataType.ADDITIONAL_ERROR:
        return fg254.decode(fg254.DataType.ADDITIONAL_ERROR, data)

    if data_type == DataType.NEGATIVE_ACKNOWLEDGEMENT:
        return fg254.decode(fg254.DataType.NEGATIVE_ACKNOWLEDGEMENT, data)

    if data_type == DataType.OPERATING_MODE:
        mode = data[0]

        return OperatingModeData(mode)

    if data_type == DataType.RETRIEVAL_BUFFER_CONTENT:
        sequence_number = (data[1] << 8) | data[0]
        message_count = data[2]

        return RetrievalBufferContentData(sequence_number=sequence_number,
                                          message_count=message_count)

    if data_type == DataType.RETRIEVAL_CODE_DEFINITION:
        setting_code = data[0]

        return RetrievalCodeDefinitionData(setting_code=setting_code)

    if data_type == DataType.CHANNEL_CONTROL:
        return fg1.decode(fg1.DataType.CHANNEL_CONTROL, data)

    if data_type == DataType.TIME_STAMP:
        return fg254.decode(fg254.DataType.TIME_STAMP, data)

    if data_type == DataType.TIME_STAMP_WITH_SEQUENCE_NUMBER:
        summer_time = bool(data[0] & 0x80)
        hour = data[0] & 0x7F
        minute = data[1]
        second = data[2]
        day = data[3]
        sequence_number = (data[5] << 8) | data[4]

        return TimeStampWithSequenceNumberData(summer_time=summer_time,
                                               hour=hour,
                                               minute=minute,
                                               second=second,
                                               day=day,
                                               sequence_number=sequence_number)

    if data_type == DataType.VMS_BASIC_SETTING:
        code = data[0]
        function = decode_function(data[1])

        return VmsBasicSettingData(code=code,
                                   function=function)

    if data_type == DataType.BASIC_SETTING:
        display_principle = DisplayPrinciple(data[0])
        basic_setting_code = data[1]
        function = decode_function(data[2])
        component_setting_codes = []
        if display_principle in (DisplayPrinciple.C,
                                 DisplayPrinciple.D,
                                 DisplayPrinciple.E):
            for i in range(data[3]):
                if display_principle == DisplayPrinciple.E:
                    code = (data[4 + (i * 2)],
                            decode_function(data[5 + (i * 2)]))
                else:
                    code = data[4 + i]
                component_setting_codes.append(code)

        return BasicSettingData(
            display_principle=display_principle,
            basic_setting_code=basic_setting_code,
            function=function,
            component_setting_codes=component_setting_codes)

    if data_type == DataType.GEOGRAPHICAL_CHARACTERISTICS:
        return fg254.decode(fg254.DataType.GEOGRAPHICAL_CHARACTERISTICS, data)

    if data_type == DataType.BASIC_PROGRAMME:
        number = data[0]

        return BasicProgrammeData(number=number)

    if data_type == DataType.CODE_LIST:
        display_principle = DisplayPrinciple(data[0])
        setting_codes = list(data[2:2+data[1]])

        return CodeListData(display_principle=display_principle,
                            setting_codes=setting_codes)

    if data_type == DataType.CODE_DEFINITION:
        display_principle = DisplayPrinciple(data[0])
        setting_code = data[1]
        component_definitions = []
        for i in range(data[2]):
            if display_principle == DisplayPrinciple.E:
                definition = (data[3 + (i * 2)],
                              decode_function(data[4 + (i * 2)]))
            elif display_principle == DisplayPrinciple.CLUSTER:
                definition = (data[3 + (i * 4)],
                              DisplayPrinciple(data[4 + (i * 4)]),
                              data[5 + (i * 4)],
                              decode_function(data[6 + (i * 4)]))
            else:
                definition = data[3 + i]
            component_definitions.append(definition)

        return CodeDefinitionData(display_principle=display_principle,
                                  setting_code=setting_code,
                                  component_definitions=component_definitions)

    if data_type == DataType.VMS_SETTING_STATUS:
        code = data[0]
        function = decode_function(data[1])

        return VmsSettingStatusData(code=code,
                                    function=function)

    if data_type == DataType.BRIGHTNESS:
        value = data[0]
        automatic = bool(data[1] & 0x01)
        messages = bool(data[1] & 0x02)

        return BrightnessData(value=value,
                              automatic=automatic,
                              messages=messages)

    if data_type == DataType.VARIABLE_TEXT:
        function = decode_function(data[0])
        text = data[2:2+data[1]]

        return VariableTextData(function=function,
                                text=text)

    if data_type == DataType.SETTING_STATUS:
        display_principle = DisplayPrinciple(data[0])
        setting_code = data[1]
        function = decode_function(data[2])
        component_statuses = []
        if display_principle in (DisplayPrinciple.C,
                                 DisplayPrinciple.D,
                                 DisplayPrinciple.E):
            for i in range(data[3]):
                if display_principle == DisplayPrinciple.E:
                    status = (data[4 + (i * 2)],
                              decode_function(data[5 + (i * 2)]))
                else:
                    status = data[4 + i]
                component_statuses.append(status)

        return SettingStatusData(display_principle=display_principle,
                                 setting_code=setting_code,
                                 function=function,
                                 component_statuses=component_statuses)

    if data_type == DataType.SETTING_PROGRAMME:
        number = data[0]
        status_not_terminated = bool(data[1] & 0x01)
        status_error = bool(data[1] & 0x02)

        return SettingProgrammeData(
            number=number,
            status_not_terminated=status_not_terminated,
            status_error=status_error)

    raise ValueError('unsupported data type')


def encode_function(function: Function) -> common.UInt8:
    return (function.type.value |
            (0x04 if function.status_error else 0x00) |
            (0x08 if function.status_not_terminated else 0x00) |
            (function.indication_time << 4))


def decode_function(function: common.UInt8) -> Function:
    return Function(type=FunctionType(function & 0x03),
                    status_error=bool(function & 0x04),
                    status_not_terminated=bool(function & 0x08),
                    indication_time=(function >> 4))
