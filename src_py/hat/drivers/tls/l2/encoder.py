import itertools

from hat import util

from hat.drivers.tls.l2 import common


def get_next_frame_size(data: util.Bytes) -> int:
    if not data or data[0] == 0xE5:
        return 1

    if data[0] == 0x10:
        return 5

    if data[0] == 0x68:
        if len(data) < 4:
            return 4

        if data[1] != data[2]:
            raise Exception('length not matching')

        if data[3] != 0x68:
            raise Exception('invalid repeated start identifier')

        if data[1] < 2:
            raise Exception('invalid length')

        return data[1] + 6

    raise Exception('invalid start identifier')


def decode_frame(data: util.Bytes) -> common.Frame:
    if data[0] == 0xE5:
        return common.ShortFrame()

    if data[0] == 0x10:
        data = data[1:5]

    elif data[0] == 0x68:
        if data[1] != data[2]:
            raise Exception('length not matching')

        if data[3] != 0x68:
            raise Exception('invalid repeated start identifier')

        if data[1] < 2:
            raise Exception('invalid length')

        data = data[4:data[1] + 6]

    else:
        raise Exception('invalid start identifier')

    if data[-1] != 0x16:
        raise Exception('invalid end identifier')

    if data[-2] != sum(data[:-2]) % 0x100:
        raise Exception('invalid crc')

    control = data[0]
    address = data[1]
    data = data[2:-2]

    if control & 0x40:
        frame = common.ReqFrame(frame_count_bit=bool(control & 0x20),
                                frame_count_valid=bool(control & 0x10),
                                function=common.ReqFunction(control & 0x0F),
                                address=address,
                                data=data)

    else:
        frame = common.ResFrame(access_demand=bool(control & 0x20),
                                data_flow_control=bool(control & 0x10),
                                function=common.ResFunction(control & 0x0F),
                                address=address,
                                data=data)

    return frame


def encode_frame(frame: common.Frame) -> bytes:
    if isinstance(frame, common.ShortFrame):
        return b'\xE5'

    if isinstance(frame, common.ReqFrame):
        control = (0x40 |
                   (0x20 if frame.frame_count_bit else 0) |
                   (0x10 if frame.frame_count_valid else 0) |
                   frame.function.value)

    elif isinstance(frame, common.ResFrame):
        control = ((0x20 if frame.access_demand else 0) |
                   (0x10 if frame.data_flow_control else 0) |
                   frame.function.value)

    else:
        raise ValueError('unsupported frame type')

    body = [control, frame.address, *frame.data]
    header = [0x68, len(body), len(body), 0x68] if frame.data else [0x10]
    footer = [sum(body) % 0x100, 0x16]

    return bytes(itertools.chain(header, body, footer))
