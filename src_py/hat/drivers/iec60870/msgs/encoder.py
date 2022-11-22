import collections
import typing

from hat.drivers.iec60870.msgs import common


AsduType = int
AsduTypeTimeSizes = typing.Dict[AsduType, common.TimeSize]
DecodeIoElementCb = typing.Callable[[common.Bytes, AsduType],
                                    typing.Tuple[typing.Any, common.Bytes]]
EncodeIoElementCb = typing.Callable[[typing.Any, AsduType],
                                    typing.Iterable[int]]


def decode_time(time_bytes: common.Bytes,
                time_size: common.TimeSize
                ) -> common.Time:
    milliseconds = (time_bytes[1] << 8) | time_bytes[0]
    invalid = (bool(time_bytes[2] & 0x80) if time_size.value > 2 else None)
    minutes = (time_bytes[2] & 0x3F if time_size.value > 2 else None)
    summer_time = (bool(time_bytes[3] & 0x80) if time_size.value > 3 else None)
    hours = (time_bytes[3] & 0x1F if time_size.value > 3 else None)
    day_of_week = (time_bytes[4] >> 5 if time_size.value > 4 else None)
    day_of_month = (time_bytes[4] & 0x1F if time_size.value > 4 else None)
    months = (time_bytes[5] & 0x0F if time_size.value > 4 else None)
    years = (time_bytes[6] & 0x7F if time_size.value > 4 else None)

    return common.Time(size=time_size,
                       milliseconds=milliseconds,
                       invalid=invalid,
                       minutes=minutes,
                       summer_time=summer_time,
                       hours=hours,
                       day_of_week=day_of_week,
                       day_of_month=day_of_month,
                       months=months,
                       years=years)


def encode_time(time: common.Time,
                time_size: common.TimeSize
                ) -> typing.Iterable[int]:
    if time_size.value > time.size.value:
        raise ValueError('unsupported time size')

    yield time.milliseconds & 0xFF
    yield (time.milliseconds >> 8) & 0xFF

    if time_size.value > 2:
        yield ((0x80 if time.invalid else 0) |
               (time.minutes & 0x3F))

    if time_size.value > 3:
        yield ((0x80 if time.summer_time else 0) |
               (time.hours & 0x1F))

    if time_size.value > 4:
        yield (((time.day_of_week & 0x07) << 5) |
               (time.day_of_month & 0x1F))
        yield time.months & 0x0F
        yield time.years & 0x7F


class Encoder:

    def __init__(self,
                 cause_size: common.CauseSize,
                 asdu_address_size: common.AsduAddressSize,
                 io_address_size: common.IoAddressSize,
                 asdu_type_time_sizes: AsduTypeTimeSizes,
                 inverted_sequence_bit: bool,
                 decode_io_element_cb: DecodeIoElementCb,
                 encode_io_element_cb: EncodeIoElementCb):
        self._cause_size = cause_size
        self._asdu_address_size = asdu_address_size
        self._io_address_size = io_address_size
        self._asdu_type_time_sizes = asdu_type_time_sizes
        self._inverted_sequence_bit = inverted_sequence_bit
        self._decode_io_element_cb = decode_io_element_cb
        self._encode_io_element_cb = encode_io_element_cb

    def decode_asdu(self, asdu_bytes: common.Bytes) -> common.ASDU:
        asdu_type = asdu_bytes[0]
        io_number = asdu_bytes[1] & 0x7F
        is_sequence = bool(asdu_bytes[1] & 0x80)
        if self._inverted_sequence_bit:
            is_sequence = not is_sequence
        io_count = 1 if is_sequence else io_number
        ioe_element_count = io_number if is_sequence else 1

        rest = asdu_bytes[2:]
        cause, rest = _decode_int(rest, self._cause_size.value)
        address, rest = _decode_int(rest, self._asdu_address_size.value)

        ios = collections.deque()
        for _ in range(io_count):
            io, rest = self._decode_io(asdu_type, ioe_element_count, rest)
            ios.append(io)

        return common.ASDU(type=asdu_type,
                           cause=cause,
                           address=address,
                           ios=list(ios))

    def encode_asdu(self, asdu: common.ASDU) -> common.Bytes:
        data = collections.deque()
        data.append(asdu.type)

        is_sequence = len(asdu.ios) == 1 and len(asdu.ios[0].elements) > 1
        if is_sequence:
            data.append(
                (0x00 if self._inverted_sequence_bit else 0x80) |
                len(asdu.ios[0].elements))
        else:
            data.append(
                (0x80 if self._inverted_sequence_bit else 0x00) |
                len(asdu.ios))

        data.extend(_encode_int(asdu.cause, self._cause_size.value))
        data.extend(_encode_int(asdu.address, self._asdu_address_size.value))

        for io in asdu.ios:
            if not is_sequence and len(io.elements) != 1:
                raise ValueError('invalid number of IO elements')
            data.extend(self._encode_io(asdu.type, io))

        return bytes(data)

    def _decode_io(self, asdu_type, ioe_element_count, io_bytes):
        address, rest = _decode_int(io_bytes, self._io_address_size.value)

        elements = collections.deque()
        for _ in range(ioe_element_count):
            element, rest = self._decode_io_element_cb(rest, asdu_type)
            elements.append(element)

        time_size = self._asdu_type_time_sizes.get(asdu_type)
        if time_size:
            time, rest = decode_time(rest, time_size), rest[time_size.value:]
        else:
            time = None

        io = common.IO(address=address,
                       elements=list(elements),
                       time=time)
        return io, rest

    def _encode_io(self, asdu_type, io):
        yield from _encode_int(io.address, self._io_address_size.value)

        for element in io.elements:
            yield from self._encode_io_element_cb(element, asdu_type)

        time_size = self._asdu_type_time_sizes.get(asdu_type)
        if time_size:
            yield from encode_time(io.time, time_size)


def _decode_int(data, size):
    return int.from_bytes(data[:size], 'little'), data[size:]


def _encode_int(x, size):
    return x.to_bytes(size, 'little')
