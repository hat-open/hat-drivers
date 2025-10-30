from hat import util

from hat.drivers.dnp3.transport import common


def decode_segment(data: util.Bytes) -> common.Segment:
    if len(data) < 2 or len(data) > 250:
        raise Exception('invalid segment size')

    return common.Segment(first=bool(data[0] & 0x40),
                          last=bool(data[0] & 0x80),
                          sequence=data[0] & 0x3f,
                          data=data[1:])


def encode_segment(segment: common.Segment) -> util.Bytes:
    if len(segment.data) < 1 or len(segment.data) > 249:
        raise Exception('invalid data size')

    if segment.sequence < 0 or segment.sequence > 63:
        raise Exception('invalid sequence')

    data = memoryview(bytearray(len(segment.data + 1)))
    data[0] = ((0x80 if segment.last else 0x00) |
               (0x40 if segment.first else 0x00) |
               segment.sequence)
    data[1:] = segment.data

    return data
