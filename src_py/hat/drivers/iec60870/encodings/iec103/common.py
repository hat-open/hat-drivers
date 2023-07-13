from hat.drivers.iec60870.encodings.common import *  # NOQA

import enum
import typing

from hat import util

from hat.drivers.iec60870.encodings.common import Time


AsduAddress: typing.TypeAlias = int
"""ASDU address in range [0, 255]"""

OtherCause: typing.TypeAlias = int
"""Other cause in range [0, 255]"""


class AsduType(enum.Enum):
    TIME_TAGGED_MESSAGE = 1
    TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME = 2
    MEASURANDS_1 = 3
    TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME = 4
    IDENTIFICATION = 5
    TIME_SYNCHRONIZATION = 6
    GENERAL_INTERROGATION = 7
    GENERAL_INTERROGATION_TERMINATION = 8
    MEASURANDS_2 = 9
    GENERIC_DATA = 10
    GENERIC_IDENTIFICATION = 11
    GENERAL_COMMAND = 20
    GENERIC_COMMAND = 21
    LIST_OF_RECORDED_DISTURBANCES = 23
    ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION = 24
    ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION = 25
    READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA = 26
    READY_FOR_TRANSMISSION_OF_A_CHANNEL = 27
    READY_FOR_TRANSMISSION_OF_TAGS = 28
    TRANSMISSION_OF_TAGS = 29
    TRANSMISSION_OF_DISTURBANCE_VALUES = 30
    END_OF_TRANSMISSION = 31


class Cause(enum.Enum):
    SPONTANEOUS = 1
    CYCLIC = 2
    RESET_FRAME_COUNT_BIT = 3
    RESET_COMMUNICATION_UNIT = 4
    START_RESTART = 5
    POWER_ON = 6
    TEST_MODE = 7
    TIME_SYNCHRONIZATION = 8
    GENERAL_INTERROGATION = 9
    TERMINATION_OF_GENERAL_INTERROGATION = 10
    LOCAL_OPERATION = 11
    REMOTE_OPERATION = 12
    GENERAL_COMMAND = 20
    GENERAL_COMMAND_NACK = 21
    TRANSMISSION_OF_DISTURBANCE_DATA = 31
    GENERIC_WRITE_COMMAND = 40
    GENERIC_WRITE_COMMAND_NACK = 41
    GENERIC_READ_COMMAND = 42
    GENERIC_READ_COMMAND_NACK = 43
    GENERIC_WRITE_CONFIRMATION = 44


class Description(enum.Enum):
    NOT_SPECIFIED = 0
    ACTUAL_VALUE = 1
    DEFAULT_VALUE = 2
    RANGE = 3
    PRECISION = 5
    FACTOR = 6
    REFERENCE = 7
    ENUMERATION = 8
    DIMENSION = 9
    DESCRIPTION = 10
    PASSWORD = 12
    READ_ONLY = 13
    WRITE_ONLY = 14
    IO_ADDRESS = 19
    EVENT = 20
    TEXT_ARRAY = 21
    VALUE_ARRAY = 22
    RELATED = 23


class OrderType(enum.Enum):
    SELECTION_OF_FAULT = 1
    REQUEST_FOR_DISTURBANCE_DATA = 2
    ABORTION_OF_DISTURBANCE_DATA = 3
    REQUEST_FOR_CHANNEL = 8
    ABORTION_OF_CHANNEL = 9
    REQUEST_FOR_TAGS = 16
    ABORTION_OF_TAGS = 17
    REQUEST_FOR_LIST_OF_RECORDED_DISTURBANCES = 24
    END_OF_DISTURBANCE_DATA_TRANSMISSION_WITHOUT_ABORTION = 32
    END_OF_DISTURBANCE_DATA_TRANSMISSION_WITH_ABORTION_BY_CONTROL_SYSTEM = 33
    END_OF_DISTURBANCE_DATA_TRANSMISSION_WITH_ABORTION_BY_THE_PROTECTION_EQUIPMENT = 34  # NOQA
    END_OF_CHANNEL_TRANSMISSION_WITHOUT_ABORTION = 35
    END_OF_CHANNEL_TRANSMISSION_WITH_ABORTION_BY_CONTROL_SYSTEM = 36
    END_OF_CHANNEL_TRANSMISSION_WITH_ABORTION_BY_THE_PROTECTION_EQUIPMENT = 37
    END_OF_TAG_TRANSMISSION_WITHOUT_ABORTION = 38
    END_OF_TAG_TRANSMISSION_WITH_ABORTION_BY_CONTROL_SYSTEM = 39
    END_OF_TAG_TRANSMISSION_WITH_ABORTION_BY_THE_PROTECTION_EQUIPMENT = 40
    DISTURBANCE_DATA_TRANSMITTED_SUCCESSFULLY = 64
    DISTURBANCE_DATA_TRANSMITTED_NOT_SUCCESSFULLY = 65
    CHANNEL_TRANSMITTED_SUCCESSFULLY = 66
    CHANNEL_TRANSMITTED_NOT_SUCCESSFULLY = 67
    TAGS_TRANSMITTED_SUCCESSFULLY = 68
    TAGS_TRANSMITTED_NOT_SUCCESSFULLY = 69


class Channel(enum.Enum):
    GLOBAL = 0
    I_L1 = 1
    I_L2 = 2
    I_L3 = 3
    I_N = 4
    V_L1E = 5
    V_L2E = 6
    V_L3E = 7
    V_EN = 8


class IoAddress(typing.NamedTuple):
    function_type: int
    """function_type is in range [0, 255]"""
    information_number: int
    """information_number is in range [0, 255]"""


class Identification(typing.NamedTuple):
    group_id: int
    """group_id in range [0, 255]"""
    entry_id: int
    """entry_id in range [0, 255]"""


class ValueType(enum.Enum):
    NONE = 0
    TEXT = 1
    BITSTRING = 2
    UINT = 3
    INT = 4
    UFIXED = 5
    FIXED = 6
    REAL32 = 7
    REAL64 = 8
    DOUBLE = 9
    SINGLE = 10
    EXTENDED_DOUBLE = 11
    MEASURAND = 12
    TIME = 14
    IDENTIFICATION = 15
    RELATIVE_TIME = 16
    IO_ADDRESS = 17
    DOUBLE_WITH_TIME = 18
    DOUBLE_WITH_RELATIVE_TIME = 19
    MEASURAND_WITH_RELATIVE_TIME = 20
    TEXT_NUMBER = 21
    REPLY = 22
    ARRAY = 23
    INDEX = 24


class NoneValue(typing.NamedTuple):
    pass


class TextValue(typing.NamedTuple):
    value: util.Bytes


class BitstringValue(typing.NamedTuple):
    value: list[bool]


class UIntValue(typing.NamedTuple):
    value: int


class IntValue(typing.NamedTuple):
    value: int


class UFixedValue(typing.NamedTuple):
    value: float
    """value in range [0, 1.0]"""


class FixedValue(typing.NamedTuple):
    value: float
    """value in range [-1.0, 1.0)"""


class Real32Value(typing.NamedTuple):
    value: float


class Real64Value(typing.NamedTuple):
    value: float


class DoubleValue(enum.Enum):
    TRANSIENT = 0
    OFF = 1
    ON = 2
    ERROR = 3


class SingleValue(enum.Enum):
    OFF = 0
    ON = 1


class ExtendedDoubleValue(enum.Enum):
    TRANSIENT = 0
    OFF = 1
    ON = 2
    ERROR = 3


class MeasurandValue(typing.NamedTuple):
    overflow: bool
    invalid: bool
    value: float
    """value in range [-1.0, 1.0)"""


class TimeValue(typing.NamedTuple):
    value: Time
    """time size is SEVEN"""


class IdentificationValue(typing.NamedTuple):
    value: Identification


class RelativeTimeValue(typing.NamedTuple):
    value: int
    """value in range [0, 65535]"""


class IoAddressValue(typing.NamedTuple):
    value: IoAddress


class DoubleWithTimeValue(typing.NamedTuple):
    value: DoubleValue
    time: Time
    """time size is FOUR"""
    supplementary: int
    """supplementary in range [0, 255]"""


class DoubleWithRelativeTimeValue(typing.NamedTuple):
    value: DoubleValue
    relative_time: int
    """relative_time in range [0, 65535]"""
    fault_number: int
    """fault_number in range [0, 65535]"""
    time: Time
    """time size is FOUR"""
    supplementary: int
    """supplementary in range [0, 255]"""


class MeasurandWithRelativeTimeValue(typing.NamedTuple):
    value: float
    relative_time: int
    """relative_time in range [0, 65535]"""
    fault_number: int
    """fault_number in range [0, 65535]"""
    time: Time
    """time size is FOUR"""


class TextNumberValue(typing.NamedTuple):
    value: int


class ReplyValue(enum.Enum):
    ACK = 0
    INVALID_IDENTIFICATION = 1
    DATA_NOT_EXISTS = 2
    DATA_NOT_AVAILABLE = 3
    VERIFY_ERROR = 4
    OUT_OF_RANGE = 5
    ENTRY_TO_LARGE = 6
    TOO_MANY_COMMANDS = 7
    ENTRY_READ_ONLY = 8
    PASSWORD_PROTECTED = 9
    IN_PROGRESS = 10
    FOLLOWING_DESCRIPTION = 11


class ArrayValue(typing.NamedTuple):
    value_type: ValueType
    more_follows: bool
    values: typing.List['Value']


class IndexValue(typing.NamedTuple):
    value: int


Value: typing.TypeAlias = (NoneValue |
                           TextValue |
                           BitstringValue |
                           UIntValue |
                           IntValue |
                           FixedValue |
                           UFixedValue |
                           Real32Value |
                           Real64Value |
                           DoubleValue |
                           SingleValue |
                           ExtendedDoubleValue |
                           MeasurandValue |
                           TimeValue |
                           IdentificationValue |
                           RelativeTimeValue |
                           IoAddressValue |
                           DoubleWithTimeValue |
                           DoubleWithRelativeTimeValue |
                           MeasurandWithRelativeTimeValue |
                           TextNumberValue |
                           ReplyValue |
                           ArrayValue |
                           IndexValue)


class DescriptiveData(typing.NamedTuple):
    description: Description
    value: ArrayValue


class IoElement_TIME_TAGGED_MESSAGE(typing.NamedTuple):
    value: DoubleWithTimeValue


class IoElement_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME(typing.NamedTuple):
    value: DoubleWithRelativeTimeValue


class IoElement_MEASURANDS_1(typing.NamedTuple):
    value: MeasurandValue


class IoElement_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME(typing.NamedTuple):
    value: MeasurandWithRelativeTimeValue


class IoElement_IDENTIFICATION(typing.NamedTuple):
    compatibility: int
    """compatibility in range [0, 255]"""
    value: util.Bytes
    """value length is 8"""
    software: util.Bytes
    """software length is 4"""


class IoElement_TIME_SYNCHRONIZATION(typing.NamedTuple):
    time: Time
    """time size is SEVEN"""


class IoElement_GENERAL_INTERROGATION(typing.NamedTuple):
    scan_number: int
    """scan_number in range [0, 255]"""


class IoElement_GENERAL_INTERROGATION_TERMINATION(typing.NamedTuple):
    scan_number: int
    """scan_number in range [0, 255]"""


class IoElement_MEASURANDS_2(typing.NamedTuple):
    value: MeasurandValue


class IoElement_GENERIC_DATA(typing.NamedTuple):
    return_identifier: int
    """return_identifier in range [0, 255]"""
    counter: bool
    more_follows: bool
    data: list[tuple[Identification, DescriptiveData]]


class IoElement_GENERIC_IDENTIFICATION(typing.NamedTuple):
    return_identifier: int
    """return_identifier in range [0, 255]"""
    identification: Identification
    counter: bool
    more_follows: bool
    data: list[DescriptiveData]


class IoElement_GENERAL_COMMAND(typing.NamedTuple):
    value: DoubleValue
    return_identifier: int
    """return_identifier in range [0, 255]"""


class IoElement_GENERIC_COMMAND(typing.NamedTuple):
    return_identifier: int
    """return_identifier in range [0, 255]"""
    data: list[tuple[Identification, Description]]


class IoElement_LIST_OF_RECORDED_DISTURBANCES(typing.NamedTuple):
    fault_number: int
    """fault_number in range [0, 65535]"""
    trip: bool
    transmitted: bool
    test: bool
    other: bool
    time: Time
    """time size is SEVEN"""


class IoElement_ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION(typing.NamedTuple):
    order_type: OrderType
    fault_number: int
    """fault_number in range [0, 65535]"""
    channel: Channel


class IoElement_ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION(typing.NamedTuple):  # NOQA
    order_type: OrderType
    fault_number: int
    """fault_number in range [0, 65535]"""
    channel: Channel


class IoElement_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA(typing.NamedTuple):
    fault_number: int
    """fault_number in range [0, 65535]"""
    number_of_faults: int
    """number_of_faults in range [0, 65535]"""
    number_of_channels: int
    """number_of_channels in range [0, 255]"""
    number_of_elements: int
    """number_of_elements in range [1, 65535]"""
    interval: int
    """interval in range [1, 65535]"""
    time: Time
    """time size is FOUR"""


class IoElement_READY_FOR_TRANSMISSION_OF_A_CHANNEL(typing.NamedTuple):
    fault_number: int
    """fault_number in range [0, 65535]"""
    channel: Channel
    primary: Real32Value
    secondary: Real32Value
    reference: Real32Value


class IoElement_READY_FOR_TRANSMISSION_OF_TAGS(typing.NamedTuple):
    fault_number: int
    """fault_number in range [0, 65535]"""


class IoElement_TRANSMISSION_OF_TAGS(typing.NamedTuple):
    fault_number: int
    """fault_number in range [0, 65535]"""
    tag_position: int
    """tag_position in range [0, 65535]"""
    values: list[tuple[IoAddress, DoubleValue]]


class IoElement_TRANSMISSION_OF_DISTURBANCE_VALUES(typing.NamedTuple):
    fault_number: int
    """fault_number in range [0, 65535]"""
    channel: Channel
    element_number: int
    """element_number in range [0, 65535]"""
    values: list[float]
    """values are in range [-1.0, 1.0)"""


class IoElement_END_OF_TRANSMISSION(typing.NamedTuple):
    order_type: OrderType
    fault_number: int
    """fault_number in range [0, 65535]"""
    channel: Channel


IoElement: typing.TypeAlias = (
    IoElement_TIME_TAGGED_MESSAGE |
    IoElement_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME |
    IoElement_MEASURANDS_1 |
    IoElement_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME |
    IoElement_IDENTIFICATION |
    IoElement_TIME_SYNCHRONIZATION |
    IoElement_GENERAL_INTERROGATION |
    IoElement_GENERAL_INTERROGATION_TERMINATION |
    IoElement_MEASURANDS_2 |
    IoElement_GENERIC_DATA |
    IoElement_GENERIC_IDENTIFICATION |
    IoElement_GENERAL_COMMAND |
    IoElement_GENERIC_COMMAND |
    IoElement_LIST_OF_RECORDED_DISTURBANCES |
    IoElement_ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION |
    IoElement_ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION |
    IoElement_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA |
    IoElement_READY_FOR_TRANSMISSION_OF_A_CHANNEL |
    IoElement_READY_FOR_TRANSMISSION_OF_TAGS |
    IoElement_TRANSMISSION_OF_TAGS |
    IoElement_TRANSMISSION_OF_DISTURBANCE_VALUES |
    IoElement_END_OF_TRANSMISSION)


class IO(typing.NamedTuple):
    address: IoAddress
    elements: list[IoElement]


class ASDU(typing.NamedTuple):
    type: AsduType
    cause: Cause | OtherCause
    address: AsduAddress
    ios: list[IO]
