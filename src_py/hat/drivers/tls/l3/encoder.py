import itertools

from hat import util

from hat.drivers.tls.l3 import common


def decode_packet(data: util.Bytes) -> common.Packet:
    priority = common.Priority(data[0] >> 7)
    length = (data[0] >> 3) & 0x03
    pointer = data[0] & 0x03

    addresses = [(data[i * 2 + 1], data[i * 2 + 2])
                 for i in range(length)]
    packet_data = data[length * 2 + 1:]

    return common.Packet(priority=priority,
                         pointer=pointer,
                         addresses=addresses,
                         data=packet_data)


def encode_packet(packet: common.Packet) -> util.Bytes:
    if len(packet.addresses) > 7:
        raise ValueError('invalid address count')

    if not (0 <= packet.pointer <= 7) or packet.pointer > len(packet.addresses):  # NOQA
        raise ValueError('invalid pointer')

    identifier = ((packet.priority.value << 7) |
                  (len(packet.addresses) << 3) |
                  packet.pointer)

    data = bytes(itertools.chain(
        [identifier],
        itertools.chain.from_iterable(packet.addresses),
        packet.data))

    return data
