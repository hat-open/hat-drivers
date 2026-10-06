import itertools

from hat import util

from hat.drivers.tls.l2 import common


def get_next_msg_size(data: util.Bytes) -> int:
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


def decode(data: util.Bytes) -> common.Msg:
    if data[0] == 0xE5:
        return common.ShortMsg()

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
        msg = common.ReqMsg(frame_count=bool(control & 0x20),
                            frame_count_valid=bool(control & 0x10),
                            function=common.ReqFunction(control & 0x0F),
                            address=address,
                            data=data)

    else:
        msg = common.ResMsg(access_demand=bool(control & 0x20),
                            data_flow_control=bool(control & 0x10),
                            function=common.ResFunction(control & 0x0F),
                            address=address,
                            data=data)

    return msg


def encode(msg: common.Msg) -> bytes:
    if isinstance(msg, common.ShortMsg):
        return b'\xE5'

    if isinstance(msg, common.ReqMsg):
        control = (0x40 |
                   (0x20 if msg.frame_count else 0) |
                   (0x10 if msg.frame_count_valid else 0) |
                   msg.function.value)

    elif isinstance(msg, common.ResMsg):
        control = ((0x20 if msg.access_demand else 0) |
                   (0x10 if msg.data_flow_control else 0) |
                   msg.function.value)

    else:
        raise ValueError('unsupported msg type')

    body = [control, msg.address, *msg.data]
    header = [0x68, len(body), len(body), 0x68] if msg.data else [0x10]
    footer = [sum(body) % 0x100, 0x16]

    return bytes(itertools.chain(header, body, footer))
