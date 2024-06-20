import itertools

from hat import util

from hat.drivers.icmp import common


def encode_msg(msg: common.Msg) -> util.Bytes:
    if isinstance(msg, common.EchoMsg):
        msg_type = 0 if msg.is_reply else 8
        code = 0
        header_data = _encode_echo_header_data(msg)
        msg_data = msg.data

    else:
        raise ValueError('unsupported message type')

    msg_bytes = bytearray(itertools.chain([msg_type, code, 0, 0],
                                          header_data,
                                          msg_data))

    checksum = _calculate_checksum(msg_bytes)
    msg_bytes[2] = checksum >> 8
    msg_bytes[3] = checksum & 0xff

    return msg_bytes


def decode_msg(msg_bytes: util.Bytes) -> common.Msg:
    if len(msg_bytes) < 8:
        raise Exception('invalid message size')

    checksum = _calculate_checksum(msg_bytes)
    if checksum != ((msg_bytes[2] << 8) | msg_bytes[3]):
        raise Exception('invalid checksum')

    msg_type = msg_bytes[0]
    code = msg_bytes[1]
    header_data = msg_bytes[4:8]
    msg_data = msg_bytes[8:]

    if msg_type == 0:
        return _decode_echo_msg(True, code, header_data, msg_data)

    if msg_type == 8:
        return _decode_echo_msg(False, code, header_data, msg_data)

    raise Exception('unsupported message type')


def _decode_echo_msg(is_reply, code, header_data, msg_data):
    if code != 0:
        raise Exception('invalid code')

    identifier = (header_data[0] << 8) | header_data[1]
    sequence_number = (header_data[2] << 8) | header_data[3]

    return common.EchoMsg(is_reply=is_reply,
                          identifier=identifier,
                          sequence_number=sequence_number,
                          data=msg_data)


def _encode_echo_header_data(msg):
    if msg.identifier < 0 or msg.identifier > 0xffff:
        raise ValueError('invalid identifier')

    if msg.sequence_number < 0 or msg.sequence_number > 0xffff:
        raise ValueError('invalid sequence number')

    yield msg.identifier >> 8
    yield msg.identifier & 0xff

    yield msg.sequence_number >> 8
    yield msg.sequence_number & 0xff


def _calculate_checksum(msg_bytes):
    acc = (msg_bytes[0] << 8) & msg_bytes[1]

    for i in range(4, len(msg_bytes)):
        acc += (msg_bytes[i] if i % 2 else (msg_bytes[i] << 8))

    return (~((acc >> 16) + (acc & 0xffff))) & 0xffff
