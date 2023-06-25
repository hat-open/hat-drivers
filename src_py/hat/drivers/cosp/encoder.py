from hat import util

from hat.drivers.cosp import common


# TODO rewrite


def encode(spdu: common.Spdu) -> util.Bytes:
    params = bytearray()

    conn_acc = bytearray()
    if spdu.extended_spdus is not None:
        _encode_param(conn_acc, 19, [1] if spdu.extended_spdus else [0])
    if spdu.version_number is not None:
        _encode_param(conn_acc, 22, [spdu.version_number])
    if conn_acc:
        _encode_param(params, 5, conn_acc)

    if spdu.transport_disconnect is not None:
        _encode_param(params, 17, [1 if spdu.transport_disconnect else 0])
    if spdu.requirements is not None:
        _encode_param(params, 20, spdu.requirements)
    if spdu.beginning is not None and spdu.end is not None:
        _encode_param(params, 25, [(1 if spdu.beginning else 0) |
                                   (2 if spdu.end else 0)])
    if spdu.calling_ssel is not None:
        _encode_param(params, 51, spdu.calling_ssel.to_bytes(2, 'big'))
    if spdu.called_ssel is not None:
        _encode_param(params, 52, spdu.called_ssel.to_bytes(2, 'big'))
    if spdu.user_data is not None:
        _encode_param(params, 193, spdu.user_data)

    buff = bytearray()
    buff.append(spdu.type.value)
    _encode_length(buff, params)
    buff.extend(params)
    buff.extend(spdu.data)
    return buff


def decode(data: util.Bytes) -> common.Spdu:
    if data[:len(common.give_tokens_spdu_bytes)] == common.give_tokens_spdu_bytes:  # NOQA
        data = data[len(common.give_tokens_spdu_bytes):]

    spdu_type, data = common.SpduType(data[0]), data[1:]
    params_length, data = _decode_length(data)
    params, data = data[:params_length], data[params_length:]

    extended_spdus = None
    version_number = None
    transport_disconnect = None
    requirements = None
    beginning = None
    end = None
    calling_ssel = None
    called_ssel = None
    user_data = None
    while params:
        code, param, params = _decode_param(params)
        if code == 5:
            conn_acc = param
            while conn_acc:
                code, param, conn_acc = _decode_param(conn_acc)
                if code == 19:
                    extended_spdus = bool(param[0])
                elif code == 22:
                    version_number = param[0]
        elif code == 17:
            transport_disconnect = bool(param[0])
        elif code == 20:
            requirements = param
        elif code == 25:
            beginning = bool(param[0] & 1)
            end = bool(param[0] & 2)
        elif code == 51:
            calling_ssel = int.from_bytes(param, 'big')
        elif code == 52:
            called_ssel = int.from_bytes(param, 'big')
        elif code == 193:
            user_data = param

    return common.Spdu(type=spdu_type,
                       extended_spdus=extended_spdus,
                       version_number=version_number,
                       transport_disconnect=transport_disconnect,
                       requirements=requirements,
                       beginning=beginning,
                       end=end,
                       calling_ssel=calling_ssel,
                       called_ssel=called_ssel,
                       user_data=user_data,
                       data=data)


def _encode_param(buff, code, data):
    buff.append(code)
    _encode_length(buff, data)
    buff.extend(data)


def _decode_param(data):
    code, data = data[0], data[1:]
    length, data = _decode_length(data)
    return code, data[:length], data[length:]


def _encode_length(buff, data):
    li = len(data)
    if li < 0xFF:
        buff.append(li)
    else:
        buff.extend([0xFF, li >> 8, li & 0xFF])


def _decode_length(data):
    if data[0] != 0xFF:
        return data[0], data[1:]
    return ((data[1] << 8) | data[2]), data[3:]
