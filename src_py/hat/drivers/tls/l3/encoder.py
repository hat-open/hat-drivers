import itertools

from hat import util

from hat.drivers.tls.l3 import common


def decode(data: util.Bytes) -> common.Msg:
    priority = common.Priority(data[0] >> 7)
    length = (data[0] >> 3) & 0x03
    pointer = data[0] & 0x03

    addresses = [(data[i * 2 + 1], data[i * 2 + 2])
                 for i in range(length)]
    msg_data = data[length * 2 + 1:]

    return common.Msg(priority=priority,
                      pointer=pointer,
                      addresses=addresses,
                      data=msg_data)


def encode(msg: common.Msg) -> util.Bytes:
    if len(msg.addresses) > 7:
        raise ValueError('invalid address count')

    if not (0 <= msg.pointer <= 7) or msg.pointer > len(msg.addresses):
        raise ValueError('invalid pointer')

    identifier = ((msg.priority.value << 7) |
                  (len(msg.addresses) << 3) |
                  msg.pointer)

    data = bytes(itertools.chain(
        [identifier],
        itertools.chain.from_iterable(msg.addresses),
        msg.data))

    return data
