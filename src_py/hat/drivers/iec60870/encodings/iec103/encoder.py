import collections
import contextlib
import itertools
import math
import struct

from hat import util

from hat.drivers.iec60870.encodings import encoder
from hat.drivers.iec60870.encodings.iec103 import common


class Encoder:

    def __init__(self):
        self._encoder = encoder.Encoder(
            cause_size=common.CauseSize.ONE,
            asdu_address_size=common.AsduAddressSize.ONE,
            io_address_size=common.IoAddressSize.TWO,
            asdu_type_time_sizes={},
            inverted_sequence_bit=True,
            decode_io_element_cb=_decode_io_element,
            encode_io_element_cb=_encode_io_element)

    def decode_asdu(self,
                    asdu_bytes: util.Bytes
                    ) -> tuple[common.ASDU, util.Bytes]:
        asdu, rest = self._encoder.decode_asdu(asdu_bytes)

        asdu_type = common.AsduType(asdu.type)
        cause = _decode_cause(asdu.cause)
        address = asdu.address
        ios = [common.IO(address=_decode_io_address(io.address),
                         elements=io.elements)
               for io in asdu.ios]

        # TODO assert len(asdu.ios) == 1

        asdu = common.ASDU(type=asdu_type,
                           cause=cause,
                           address=address,
                           ios=ios)
        return asdu, rest

    def encode_asdu(self, asdu: common.ASDU) -> util.Bytes:
        asdu_type = asdu.type.value
        cause = _encode_cause(asdu.cause)
        address = asdu.address
        ios = [encoder.common.IO(address=_encode_io_address(io.address),
                                 elements=io.elements,
                                 time=None)
               for io in asdu.ios]

        asdu = encoder.common.ASDU(type=asdu_type,
                                   cause=cause,
                                   address=address,
                                   ios=ios)

        return self._encoder.encode_asdu(asdu)


def _decode_cause(value):
    with contextlib.suppress(ValueError):
        return common.Cause(value)
    return value


def _encode_cause(cause):
    return cause.value if isinstance(cause, common.Cause) else cause


def _decode_io_address(io_address):
    return common.IoAddress(function_type=io_address & 0xFF,
                            information_number=io_address >> 8)


def _encode_io_address(io_address):
    return io_address.function_type | (io_address.information_number << 8)


def _decode_io_element(io_bytes, asdu_type):
    asdu_type = common.AsduType(asdu_type)

    if asdu_type == common.AsduType.TIME_TAGGED_MESSAGE:
        value, io_bytes = _decode_value(
            io_bytes, common.ValueType.DOUBLE_WITH_TIME)

        element = common.IoElement_TIME_TAGGED_MESSAGE(value)
        return element, io_bytes

    if asdu_type == common.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME:
        value, io_bytes = _decode_value(
            io_bytes, common.ValueType.DOUBLE_WITH_RELATIVE_TIME)

        element = common.IoElement_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME(
            value)
        return element, io_bytes

    if asdu_type == common.AsduType.MEASURANDS_1:
        value, io_bytes = _decode_value(
            io_bytes, common.ValueType.MEASURAND)

        element = common.IoElement_MEASURANDS_1(value)
        return element, io_bytes

    if asdu_type == common.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME:
        value, io_bytes = _decode_value(
            io_bytes, common.ValueType.MEASURAND_WITH_RELATIVE_TIME)

        element = common.IoElement_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME(
            value)
        return element, io_bytes

    if asdu_type == common.AsduType.IDENTIFICATION:
        compatibility = io_bytes[0]
        value = io_bytes[1:9]
        software = io_bytes[9:13]
        io_bytes = io_bytes[13:]

        element = common.IoElement_IDENTIFICATION(
            compatibility=compatibility,
            value=value,
            software=software)
        return element, io_bytes

    if asdu_type == common.AsduType.TIME_SYNCHRONIZATION:
        time = encoder.decode_time(io_bytes[:7], common.TimeSize.SEVEN)
        io_bytes = io_bytes[7:]

        element = common.IoElement_TIME_SYNCHRONIZATION(time)
        return element, io_bytes

    if asdu_type == common.AsduType.GENERAL_INTERROGATION:
        scan_number = io_bytes[0]
        io_bytes = io_bytes[1:]

        element = common.IoElement_GENERAL_INTERROGATION(scan_number)
        return element, io_bytes

    if asdu_type == common.AsduType.GENERAL_INTERROGATION_TERMINATION:
        scan_number = io_bytes[0]
        io_bytes = io_bytes[1:]

        element = common.IoElement_GENERAL_INTERROGATION_TERMINATION(
            scan_number=scan_number)
        return element, io_bytes

    if asdu_type == common.AsduType.MEASURANDS_2:
        value, io_bytes = _decode_value(
            io_bytes, common.ValueType.MEASURAND)

        element = common.IoElement_MEASURANDS_2(value)
        return element, io_bytes

    if asdu_type == common.AsduType.GENERIC_DATA:
        return_identifier = io_bytes[0]
        data_size = io_bytes[1] & 0x3F
        counter = bool(io_bytes[1] & 0x40)
        more_follows = bool(io_bytes[1] & 0x80)
        io_bytes = io_bytes[2:]

        data = collections.deque()
        for _ in range(data_size):
            identification, io_bytes = _decode_value(
                io_bytes, common.ValueType.IDENTIFICATION)
            data_i, io_bytes = _decode_descriptive_data(io_bytes)
            data.append((identification.value, data_i))
        data = list(data)

        element = common.IoElement_GENERIC_DATA(
            return_identifier=return_identifier,
            counter=counter,
            more_follows=more_follows,
            data=data)
        return element, io_bytes

    if asdu_type == common.AsduType.GENERIC_IDENTIFICATION:
        return_identifier = io_bytes[0]
        identification, _ = _decode_value(io_bytes[1:3],
                                          common.ValueType.IDENTIFICATION)
        data_size = io_bytes[3] & 0x3F
        counter = bool(io_bytes[3] & 0x40)
        more_follows = bool(io_bytes[3] & 0x80)
        io_bytes = io_bytes[4:]

        data = collections.deque()
        for _ in range(data_size):
            data_i, io_bytes = _decode_descriptive_data(io_bytes)
            data.append(data_i)
        data = list(data)

        element = common.IoElement_GENERIC_IDENTIFICATION(
            return_identifier=return_identifier,
            identification=identification.value,
            counter=counter,
            more_follows=more_follows,
            data=data)
        return element, io_bytes

    if asdu_type == common.AsduType.GENERAL_COMMAND:
        value, _ = _decode_value(io_bytes, common.ValueType.DOUBLE)
        return_identifier = io_bytes[1]
        io_bytes = io_bytes[2:]

        element = common.IoElement_GENERAL_COMMAND(
            value=value,
            return_identifier=return_identifier)
        return element, io_bytes

    if asdu_type == common.AsduType.GENERIC_COMMAND:
        return_identifier = io_bytes[0]
        data_size = io_bytes[1]
        io_bytes = io_bytes[2:]

        data = collections.deque()
        for _ in range(data_size):
            identification, io_bytes = _decode_value(
                io_bytes, common.ValueType.IDENTIFICATION)
            description = common.Description(io_bytes[0])
            io_bytes = io_bytes[1:]
            data.append((identification.value, description))
        data = list(data)

        element = common.IoElement_GENERIC_COMMAND(
            return_identifier=return_identifier,
            data=data)
        return element, io_bytes

    if asdu_type == common.AsduType.LIST_OF_RECORDED_DISTURBANCES:
        fault_number = int.from_bytes(io_bytes[:2], 'little')
        trip = bool(io_bytes[2] & 0x01)
        transmitted = bool(io_bytes[2] & 0x02)
        test = bool(io_bytes[2] & 0x04)
        other = bool(io_bytes[2] & 0x08)
        time = encoder.decode_time(io_bytes[3:10], common.TimeSize.SEVEN)
        io_bytes = io_bytes[10:]

        element = common.IoElement_LIST_OF_RECORDED_DISTURBANCES(
            fault_number=fault_number,
            trip=trip,
            transmitted=transmitted,
            test=test,
            other=other,
            time=time)
        return element, io_bytes

    if asdu_type == common.AsduType.ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION:
        order_type = common.OrderType(io_bytes[0])
        fault_number = int.from_bytes(io_bytes[2:4], 'little')
        channel = common.Channel(io_bytes[4])
        io_bytes = io_bytes[5:]

        element = common.IoElement_ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION(
            order_type=order_type,
            fault_number=fault_number,
            channel=channel)
        return element, io_bytes

    if asdu_type == common.AsduType.ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION:  # NOQA
        order_type = common.OrderType(io_bytes[0])
        fault_number = int.from_bytes(io_bytes[2:4], 'little')
        channel = common.Channel(io_bytes[4])
        io_bytes = io_bytes[5:]

        element = common.IoElement_ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION(  # NOQA
            order_type=order_type,
            fault_number=fault_number,
            channel=channel)
        return element, io_bytes

    if asdu_type == common.AsduType.READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA:
        fault_number = int.from_bytes(io_bytes[1:3], 'little')
        number_of_faults = int.from_bytes(io_bytes[3:5], 'little')
        number_of_channels = io_bytes[5]
        number_of_elements = int.from_bytes(io_bytes[6:8], 'little')
        interval = int.from_bytes(io_bytes[8:10], 'little')
        time = encoder.decode_time(io_bytes[10:14], common.TimeSize.FOUR)
        io_bytes = io_bytes[14:]

        element = common.IoElement_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA(
            fault_number=fault_number,
            number_of_faults=number_of_faults,
            number_of_channels=number_of_channels,
            number_of_elements=number_of_elements,
            interval=interval,
            time=time)
        return element, io_bytes

    if asdu_type == common.AsduType.READY_FOR_TRANSMISSION_OF_A_CHANNEL:
        fault_number = int.from_bytes(io_bytes[1:3], 'little')
        channel = common.Channel(io_bytes[3])
        io_bytes = io_bytes[4:]
        primary, io_bytes = _decode_value(io_bytes, common.ValueType.REAL32)
        secondary, io_bytes = _decode_value(io_bytes, common.ValueType.REAL32)
        reference, io_bytes = _decode_value(io_bytes, common.ValueType.REAL32)

        element = common.IoElement_READY_FOR_TRANSMISSION_OF_A_CHANNEL(
            fault_number=fault_number,
            channel=channel,
            primary=primary,
            secondary=secondary,
            reference=reference)
        return element, io_bytes

    if asdu_type == common.AsduType.READY_FOR_TRANSMISSION_OF_TAGS:
        fault_number = int.from_bytes(io_bytes[2:4], 'little')
        io_bytes = io_bytes[4:]

        element = common.IoElement_READY_FOR_TRANSMISSION_OF_TAGS(
            fault_number=fault_number)
        return element, io_bytes

    if asdu_type == common.AsduType.TRANSMISSION_OF_TAGS:
        fault_number = int.from_bytes(io_bytes[:2], 'little')
        values_size = io_bytes[2]
        tag_position = int.from_bytes(io_bytes[3:5], 'little')
        io_bytes = io_bytes[5:]

        values = collections.deque()
        for _ in range(values_size):
            address, io_bytes = _decode_value(io_bytes,
                                              common.ValueType.IO_ADDRESS)
            value, io_bytes = _decode_value(io_bytes, common.ValueType.DOUBLE)
            values.append((address.value, value))
        values = list(values)

        element = common.IoElement_TRANSMISSION_OF_TAGS(
            fault_number=fault_number,
            tag_position=tag_position,
            values=values)
        return element, io_bytes

    if asdu_type == common.AsduType.TRANSMISSION_OF_DISTURBANCE_VALUES:
        fault_number = int.from_bytes(io_bytes[1:3], 'little')
        channel = common.Channel(io_bytes[3])
        values_size = io_bytes[4]
        element_number = int.from_bytes(io_bytes[5:7], 'little')
        io_bytes = io_bytes[7:]

        values = collections.deque()
        for _ in range(values_size):
            value = _decode_fixed(io_bytes[:2], 0, 16, True)
            io_bytes = io_bytes[2:]
            values.append(value)
        values = list(values)

        element = common.IoElement_TRANSMISSION_OF_DISTURBANCE_VALUES(
            fault_number=fault_number,
            channel=channel,
            element_number=element_number,
            values=values)
        return element, io_bytes

    if asdu_type == common.AsduType.END_OF_TRANSMISSION:
        order_type = common.OrderType(io_bytes[0])
        fault_number = int.from_bytes(io_bytes[2:4], 'little')
        channel = common.Channel(io_bytes[4])
        io_bytes = io_bytes[5:]

        element = common.IoElement_END_OF_TRANSMISSION(
            order_type=order_type,
            fault_number=fault_number,
            channel=channel)
        return element, io_bytes

    raise ValueError('unsupported asdu type')


def _encode_io_element(element, asdu_type):
    asdu_type = common.AsduType(asdu_type)

    if asdu_type == common.AsduType.TIME_TAGGED_MESSAGE:
        yield from _encode_value(element.value)

    elif asdu_type == common.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME:
        yield from _encode_value(element.value)

    elif asdu_type == common.AsduType.MEASURANDS_1:
        yield from _encode_value(element.value)

    elif asdu_type == common.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME:  # NOQA
        yield from _encode_value(element.value)

    elif asdu_type == common.AsduType.IDENTIFICATION:
        yield element.compatibility
        yield from element.value[:8]
        yield from itertools.repeat(0, 8 - len(element.value))
        yield from element.software[:4]
        yield from itertools.repeat(0, 4 - len(element.software))

    elif asdu_type == common.AsduType.TIME_SYNCHRONIZATION:
        yield from encoder.encode_time(element.time, common.TimeSize.SEVEN)

    elif asdu_type == common.AsduType.GENERAL_INTERROGATION:
        yield element.scan_number

    elif asdu_type == common.AsduType.GENERAL_INTERROGATION_TERMINATION:
        yield element.scan_number

    elif asdu_type == common.AsduType.MEASURANDS_2:
        yield from _encode_value(element.value)

    elif asdu_type == common.AsduType.GENERIC_DATA:
        yield element.return_identifier
        yield ((0x80 if element.more_follows else 0x00) |
               (0x40 if element.counter else 0x00) |
               (len(element.data) & 0x3F))
        for identification, data in element.data:
            identification = common.IdentificationValue(identification)
            yield from _encode_value(identification)
            yield from _encode_descriptive_data(data)

    elif asdu_type == common.AsduType.GENERIC_IDENTIFICATION:
        identification = common.IdentificationValue(element.identification)
        yield element.return_identifier
        yield from _encode_value(identification)
        yield ((0x80 if element.more_follows else 0x00) |
               (0x40 if element.counter else 0x00) |
               (len(element.data) & 0x3F))
        for data in element.data:
            yield from _encode_descriptive_data(data)

    elif asdu_type == common.AsduType.GENERAL_COMMAND:
        yield from _encode_value(element.value)
        yield element.return_identifier

    elif asdu_type == common.AsduType.GENERIC_COMMAND:
        yield element.return_identifier
        yield len(element.data)
        for identification, description in element.data:
            identification = common.IdentificationValue(identification)
            yield from _encode_value(identification)
            yield description.value

    elif asdu_type == common.AsduType.LIST_OF_RECORDED_DISTURBANCES:
        yield from element.fault_number.to_bytes(2, 'little')
        yield ((0x08 if element.other else 0x00) |
               (0x04 if element.test else 0x00) |
               (0x02 if element.transmitted else 0x00) |
               (0x01 if element.trip else 0x00))
        yield from encoder.encode_time(element.time, common.TimeSize.SEVEN)

    elif asdu_type == common.AsduType.ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION:
        yield element.order_type.value
        yield 0x01
        yield from element.fault_number.to_bytes(2, 'little')
        yield element.channel.value

    elif asdu_type == common.AsduType.ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION:  # NOQA
        yield element.order_type.value
        yield 0x01
        yield from element.fault_number.to_bytes(2, 'little')
        yield element.channel.value

    elif asdu_type == common.AsduType.READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA:  # NOQA
        yield 0x01
        yield from element.fault_number.to_bytes(2, 'little')
        yield from element.number_of_faults.to_bytes(2, 'little')
        yield element.number_of_channels
        yield from element.number_of_elements.to_bytes(2, 'little')
        yield from element.interval.to_bytes(2, 'little')
        yield from encoder.encode_time(element.time, common.TimeSize.FOUR)

    elif asdu_type == common.AsduType.READY_FOR_TRANSMISSION_OF_A_CHANNEL:
        yield 0x01
        yield from element.fault_number.to_bytes(2, 'little')
        yield element.channel.value
        yield from _encode_value(element.primary)
        yield from _encode_value(element.secondary)
        yield from _encode_value(element.reference)

    elif asdu_type == common.AsduType.READY_FOR_TRANSMISSION_OF_TAGS:
        yield from [0x00, 0x00]
        yield from element.fault_number.to_bytes(2, 'little')

    elif asdu_type == common.AsduType.TRANSMISSION_OF_TAGS:
        yield from element.fault_number.to_bytes(2, 'little')
        yield len(element.values)
        yield from element.tag_position.to_bytes(2, 'little')
        for address, value in element.values:
            address = common.IoAddressValue(address)
            yield from _encode_value(address)
            yield from _encode_value(value)

    elif asdu_type == common.AsduType.TRANSMISSION_OF_DISTURBANCE_VALUES:
        yield 0x01
        yield from element.fault_number.to_bytes(2, 'little')
        yield element.channel.value
        yield len(element.values)
        yield from element.element_number.to_bytes(2, 'little')
        for value in element.values:
            yield from _encode_fixed(value, 0, 16, True)

    elif asdu_type == common.AsduType.END_OF_TRANSMISSION:
        yield element.order_type.value
        yield 0x01
        yield from element.fault_number.to_bytes(2, 'little')
        yield element.channel.value

    else:
        raise ValueError('unsupported asdu type')


def _decode_fixed(data, bit_offset, bit_size, signed):
    limit = 1 << (bit_size - (1 if signed else 0))
    size = math.ceil((bit_offset + bit_size) / 8)

    if len(data) < size:
        raise ValueError('invalid data length')

    value = int.from_bytes(data[:size], 'little')
    value = (value >> bit_offset) & ((1 << bit_size) - 1)

    if signed and (value & limit):
        value = value | (-1 << bit_size)

    return value / limit


def _encode_fixed(value, bit_offset, bit_size, signed):
    if not ((-1 if signed else 0) <= value < 1):
        raise ValueError('unsupported value')

    limit = 1 << (bit_size - (1 if signed else 0))
    size = math.ceil((bit_offset + bit_size) / 8)

    data = int(value * limit)
    if data < 0:
        data = data & ((1 << bit_size) - 1)
    data = data << bit_offset

    yield from data.to_bytes(size, 'little')


def _decode_descriptive_data(data):
    description = common.Description(data[0])
    value, data = _decode_value(data[1:], common.ValueType.ARRAY)
    descriptive_data = common.DescriptiveData(description=description,
                                              value=value)
    return descriptive_data, data


def _encode_descriptive_data(data):
    yield data.description.value
    yield from _encode_value(data.value)


def _decode_value(data, value_type):
    if value_type == common.ValueType.NONE:
        return common.NoneValue(), data

    if value_type == common.ValueType.TEXT:
        return common.TextValue(data), b''

    if value_type == common.ValueType.BITSTRING:
        value = collections.deque()
        for i in data:
            for j in range(8):
                value.append(bool(i & (1 << j)))
        return common.BitstringValue(list(value)), b''

    if value_type == common.ValueType.UINT:
        value = int.from_bytes(data, 'little')
        return common.UIntValue(value), b''

    if value_type == common.ValueType.INT:
        value = int.from_bytes(data, 'little')
        if data[-1] & 0x80:
            value = (-1 << (8 * len(data))) | value
        return common.IntValue(value), b''

    if value_type == common.ValueType.FIXED:
        value = _decode_fixed(data, 0, 8 * len(data), True)
        return common.FixedValue(value), b''

    if value_type == common.ValueType.UFIXED:
        value = _decode_fixed(data, 0, 8 * len(data), False)
        return common.FixedValue(value), b''

    if value_type == common.ValueType.REAL32:
        value = struct.unpack('<f', data[:4])[0]
        return common.Real32Value(value), data[4:]

    if value_type == common.ValueType.REAL64:
        value = struct.unpack('<d', data[:8])[0]
        return common.Real64Value(value), data[8:]

    if value_type == common.ValueType.DOUBLE:
        return common.DoubleValue(data[0]), data[1:]

    if value_type == common.ValueType.SINGLE:
        return common.SingleValue(data[0]), data[1:]

    if value_type == common.ValueType.EXTENDED_DOUBLE:
        return common.ExtendedDoubleValue(data[0]), data[1:]

    if value_type == common.ValueType.MEASURAND:
        overflow = bool(data[0] & 0x01)
        invalid = bool(data[0] & 0x02)
        value = _decode_fixed(data, 3, 13, True)
        return common.MeasurandValue(overflow=overflow,
                                     invalid=invalid,
                                     value=value), data[2:]

    if value_type == common.ValueType.TIME:
        value = encoder.decode_time(data, common.TimeSize.SEVEN)
        return common.TimeValue(value), data[7:]

    if value_type == common.ValueType.IDENTIFICATION:
        value = common.Identification(group_id=data[0],
                                      entry_id=data[1])
        return common.IdentificationValue(value), data[2:]

    if value_type == common.ValueType.RELATIVE_TIME:
        value = int.from_bytes(data[:2], 'little')
        return common.RelativeTimeValue(value), data[2:]

    if value_type == common.ValueType.IO_ADDRESS:
        value = common.IoAddress(function_type=data[0],
                                 information_number=data[1])
        return common.IoAddressValue(value), data[2:]

    if value_type == common.ValueType.DOUBLE_WITH_TIME:
        value = common.DoubleValue(data[0])
        time = encoder.decode_time(data[1:5], common.TimeSize.FOUR)
        supplementary = data[5]
        return common.DoubleWithTimeValue(
            value=value,
            time=time,
            supplementary=supplementary), data[6:]

    if value_type == common.ValueType.DOUBLE_WITH_RELATIVE_TIME:
        value = common.DoubleValue(data[0])
        relative_time = int.from_bytes(data[1:3], 'little')
        fault_number = int.from_bytes(data[3:5], 'little')
        time = encoder.decode_time(data[5:9], common.TimeSize.FOUR)
        supplementary = data[9]
        return common.DoubleWithRelativeTimeValue(
            value=value,
            relative_time=relative_time,
            fault_number=fault_number,
            time=time,
            supplementary=supplementary), data[10:]

    if value_type == common.ValueType.MEASURAND_WITH_RELATIVE_TIME:
        value = struct.unpack('<f', data[:4])[0]
        relative_time = int.from_bytes(data[4:6], 'little')
        fault_number = int.from_bytes(data[6:8], 'little')
        time = encoder.decode_time(data[8:12], common.TimeSize.FOUR)
        return common.MeasurandWithRelativeTimeValue(
            value=value,
            relative_time=relative_time,
            fault_number=fault_number,
            time=time), data[12:]

    if value_type == common.ValueType.TEXT_NUMBER:
        value = int.from_bytes(data, 'little')
        return common.TextNumberValue(value), b''

    if value_type == common.ValueType.REPLY:
        return common.ReplyValue(data[0]), data[1:]

    if value_type == common.ValueType.ARRAY:
        data_type = common.ValueType(data[0])
        data_size = data[1]
        byte_size = (math.ceil(data_size / 8)
                     if data_type == common.ValueType.BITSTRING
                     else data_size)
        number = data[2] & 0x7F
        more_follows = bool(data[2] & 0x80)
        data = data[3:]
        values = collections.deque()
        for _ in range(number):
            value, _ = _decode_value(data[:byte_size], data_type)
            values.append(value)
            data = data[byte_size:]
        values = list(values)
        return common.ArrayValue(value_type=data_type,
                                 more_follows=more_follows,
                                 values=values), data

    if value_type == common.ValueType.INDEX:
        value = int.from_bytes(data, 'little')
        return common.IndexValue(value), b''

    raise ValueError('unsupported value type')


def _encode_value(value, size=None):
    min_size = _get_value_min_size(value)
    if size is None:
        size = min_size
    elif size < min_size:
        raise ValueError('invalid size')

    if isinstance(value, common.NoneValue):
        yield from itertools.repeat(0, size)

    elif isinstance(value, common.TextValue):
        yield from value.value
        yield from itertools.repeat(0, size - len(value.value))

    elif isinstance(value, common.BitstringValue):
        for i in range(size):
            acc = 0
            for j in range(8):
                index = i * 8 + j
                if index < len(value.value) and value.value[index]:
                    acc = acc | (1 << j)
            yield acc

    elif isinstance(value, common.UIntValue):
        yield from value.value.to_bytes(size, 'little')

    elif isinstance(value, common.IntValue):
        yield from (value.value & ((1 << (8 * size)) - 1)).to_bytes(size,
                                                                    'little')

    elif isinstance(value, common.UFixedValue):
        yield from _encode_fixed(value.value, 0, 8 * size, False)

    elif isinstance(value, common.FixedValue):
        yield from _encode_fixed(value.value, 0, 8 * size, True)

    elif isinstance(value, common.Real32Value):
        yield from struct.pack('<f', value.value)
        yield from itertools.repeat(0, size - 4)

    elif isinstance(value, common.Real64Value):
        yield from struct.pack('<d', value.value)
        yield from itertools.repeat(0, size - 8)

    elif isinstance(value, common.DoubleValue):
        yield value.value
        yield from itertools.repeat(0, size - 1)

    elif isinstance(value, common.SingleValue):
        yield value.value
        yield from itertools.repeat(0, size - 1)

    elif isinstance(value, common.ExtendedDoubleValue):
        yield value.value
        yield from itertools.repeat(0, size - 1)

    elif isinstance(value, common.MeasurandValue):
        data = list(_encode_fixed(value.value, 3, 13, True))
        data[0] = data[0] | ((0x01 if value.overflow else 0x00) |
                             (0x02 if value.invalid else 0x00))
        yield from data
        yield from itertools.repeat(0, size - 2)

    elif isinstance(value, common.TimeValue):
        yield from encoder.encode_time(value.value, common.TimeSize.SEVEN)
        yield from itertools.repeat(0, size - 7)

    elif isinstance(value, common.IdentificationValue):
        yield value.value.group_id
        yield value.value.entry_id
        yield from itertools.repeat(0, size - 2)

    elif isinstance(value, common.RelativeTimeValue):
        yield from value.value.to_bytes(2, 'little')
        yield from itertools.repeat(0, size - 2)

    elif isinstance(value, common.IoAddressValue):
        yield value.value.function_type
        yield value.value.information_number
        yield from itertools.repeat(0, size - 2)

    elif isinstance(value, common.DoubleWithTimeValue):
        yield value.value.value
        yield from encoder.encode_time(value.time, common.TimeSize.FOUR)
        yield value.supplementary
        yield from itertools.repeat(0, size - 6)

    elif isinstance(value, common.DoubleWithRelativeTimeValue):
        yield value.value.value
        yield from value.relative_time.to_bytes(2, 'little')
        yield from value.fault_number.to_bytes(2, 'little')
        yield from encoder.encode_time(value.time, common.TimeSize.FOUR)
        yield value.supplementary
        yield from itertools.repeat(0, size - 10)

    elif isinstance(value, common.MeasurandWithRelativeTimeValue):
        yield from struct.pack('<f', value.value)
        yield from value.relative_time.to_bytes(2, 'little')
        yield from value.fault_number.to_bytes(2, 'little')
        yield from encoder.encode_time(value.time, common.TimeSize.FOUR)
        yield from itertools.repeat(0, size - 12)

    elif isinstance(value, common.TextNumberValue):
        yield from value.value.to_bytes(size, 'little')

    elif isinstance(value, common.ReplyValue):
        yield value.value
        yield from itertools.repeat(0, size - 12)

    elif isinstance(value, common.ArrayValue):
        for i in value.values:
            if _get_value_type(i) != value.value_type:
                raise ValueError('invalid array value')
        yield value.value_type.value
        size = max((_get_value_min_size(i) for i in value.values), default=0)
        yield (size if value.value_type != common.ValueType.BITSTRING
               else max((len(i.value) for i in value.values), default=0))
        yield ((0x80 if value.more_follows else 0x00) |
               (len(value.values) & 0x7F))
        for i in value.values:
            yield from _encode_value(i, size)

    elif isinstance(value, common.IndexValue):
        yield from value.value.to_bytes(size, 'little')

    else:
        raise ValueError('unsupported value type')


def _get_value_type(value):
    if isinstance(value, common.NoneValue):
        return common.ValueType.NONE

    if isinstance(value, common.TextValue):
        return common.ValueType.TEXT

    if isinstance(value, common.BitstringValue):
        return common.ValueType.BITSTRING

    if isinstance(value, common.UIntValue):
        return common.ValueType.UINT

    if isinstance(value, common.IntValue):
        return common.ValueType.INT

    if isinstance(value, common.UFixedValue):
        return common.ValueType.UFIXED

    if isinstance(value, common.FixedValue):
        return common.ValueType.FIXED

    if isinstance(value, common.Real32Value):
        return common.ValueType.REAL32

    if isinstance(value, common.Real64Value):
        return common.ValueType.REAL64

    if isinstance(value, common.DoubleValue):
        return common.ValueType.DOUBLE

    if isinstance(value, common.SingleValue):
        return common.ValueType.SINGLE

    if isinstance(value, common.ExtendedDoubleValue):
        return common.ValueType.EXTENDED_DOUBLE

    if isinstance(value, common.MeasurandValue):
        return common.ValueType.MEASURAND

    if isinstance(value, common.TimeValue):
        return common.ValueType.TIME

    if isinstance(value, common.IdentificationValue):
        return common.ValueType.IDENTIFICATION

    if isinstance(value, common.RelativeTimeValue):
        return common.ValueType.RELATIVE_TIME

    if isinstance(value, common.IoAddressValue):
        return common.ValueType.IO_ADDRESS

    if isinstance(value, common.DoubleWithTimeValue):
        return common.ValueType.DOUBLE_WITH_TIME

    if isinstance(value, common.DoubleWithRelativeTimeValue):
        return common.ValueType.DOUBLE_WITH_RELATIVE_TIME

    if isinstance(value, common.MeasurandWithRelativeTimeValue):
        return common.ValueType.MEASURAND_WITH_RELATIVE_TIME

    if isinstance(value, common.TextNumberValue):
        return common.ValueType.TEXT_NUMBER

    if isinstance(value, common.ReplyValue):
        return common.ValueType.REPLY

    if isinstance(value, common.ArrayValue):
        return common.ValueType.ARRAY

    if isinstance(value, common.IndexValue):
        return common.ValueType.INDEX

    raise ValueError('unsupported value type')


def _get_value_min_size(value):
    if isinstance(value, common.NoneValue):
        return 0

    if isinstance(value, common.TextValue):
        return len(value.value)

    if isinstance(value, common.BitstringValue):
        return math.ceil(len(value.value) / 8)

    if isinstance(value, common.UIntValue):
        return (value.value.bit_length() + 7) // 8

    if isinstance(value, common.IntValue):
        return (value.value.bit_length() + 8) // 8

    if isinstance(value, common.UFixedValue):
        return 2

    if isinstance(value, common.FixedValue):
        return 2

    if isinstance(value, common.Real32Value):
        return 4

    if isinstance(value, common.Real64Value):
        return 8

    if isinstance(value, common.DoubleValue):
        return 1

    if isinstance(value, common.SingleValue):
        return 1

    if isinstance(value, common.ExtendedDoubleValue):
        return 1

    if isinstance(value, common.MeasurandValue):
        return 2

    if isinstance(value, common.TimeValue):
        return 7

    if isinstance(value, common.IdentificationValue):
        return 2

    if isinstance(value, common.RelativeTimeValue):
        return 2

    if isinstance(value, common.IoAddressValue):
        return 2

    if isinstance(value, common.DoubleWithTimeValue):
        return 6

    if isinstance(value, common.DoubleWithRelativeTimeValue):
        return 10

    if isinstance(value, common.MeasurandWithRelativeTimeValue):
        return 12

    if isinstance(value, common.TextNumberValue):
        return (value.value.bit_length() + 7) // 8

    if isinstance(value, common.ReplyValue):
        return 1

    if isinstance(value, common.ArrayValue):
        return 3 + len(value.values) * max((_get_value_min_size(i)
                                            for i in value.values),
                                           default=0)

    if isinstance(value, common.IndexValue):
        return (value.value.bit_length() + 7) // 8

    raise ValueError('unsupported value type')
