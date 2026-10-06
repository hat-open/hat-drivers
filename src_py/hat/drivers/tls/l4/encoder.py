import contextlib
import itertools

from hat import util

from hat.drivers.tls.l4 import common


def decode_general_msg(data: util.Bytes) -> common.GeneralMsg:
    node = (data[0] |
            (data[1] << 8) |
            (data[2] << 16))
    msg_count = data[3]

    if not (1 <= msg_count <= 46):
        raise Exception('invalid number of messages')

    msgs = [None] * msg_count
    msgs_data = data[4:]

    for i in range(msg_count):
        msgs[i], msgs_data = decode_msg(msgs_data)

    return common.GeneralMsg(node=node,
                             msgs=msgs)


def encode_general_msg(general_msg: common.GeneralMsg) -> util.Bytes:
    if not general_msg.msgs:
        raise ValueError('invalid messages')

    node = [general_msg.node & 0xFF,
            (general_msg.node >> 8) & 0xFF,
            (general_msg.node >> 16) & 0xFF]
    msgs = itertools.chain.from_iterable(encode_msg(msg)
                                         for msg in general_msg.msgs)

    data = bytes(itertools.chain(node, [len(general_msg.msgs)], msgs))
    return data


def decode_msg(data: util.Bytes) -> tuple[common.Msg, util.Bytes]:
    length = data[0]
    msg_data, rest = data[1:1+length], data[1+length:]

    function_group = msg_data[0]

    if msg_data[1] & 0x80:
        msg_cls = common.ResMsg
        identifier = _decode_res_identifier(msg_data[1] & 0x7F)

    else:
        msg_cls = common.ReqMsg
        identifier = _decode_req_identifier(msg_data[1] & 0x7F)

    job_number = msg_data[2]
    dt_count = msg_data[3]

    dts = [None] * dt_count
    dts_data = msg_data[4:]

    for i in range(dt_count):
        dts[i], dts_data = _decode_dt(dts_data)

    msg = msg_cls(function_group=function_group,
                  identifier=identifier,
                  job_number=job_number,
                  dts=dts)
    return msg, rest


def encode_msg(msg: common.Msg) -> util.Bytes:
    data = [msg.function_group,
            ((0x80 if isinstance(msg, common.ResMsg) else 0) |
             (msg.identifier if isinstance(msg.identifier, int)
              else msg.identifier.value)),
            msg.job_number,
            len(msg.dts),
            *itertools.chain.from_iterable(_encode_dt(dt) for dt in msg.dts)]

    return bytes(itertools.chain([len(data)], data))


def _decode_dt(data: util.Bytes) -> tuple[common.DT, util.Bytes]:
    length = data[0]
    dt_data, rest = data[1:1+length], data[1+length:]

    channel = dt_data[0]
    dt_type = dt_data[1]

    dt = common.DT(channel=channel,
                   type=dt_type,
                   data=dt_data[2:])
    return dt, rest


def _encode_dt(dt: common.DT) -> util.Bytes:
    data = [dt.channel,
            dt.type,
            *dt.data]
    return bytes(itertools.chain([len(data)], data))


def _decode_req_identifier(value: int
                           ) -> common.ReqIdentifier | common.OtherIdentifier:
    with contextlib.suppress(ValueError):
        return common.ReqIdentifier(value)

    return value


def _decode_res_identifier(value: int
                           ) -> common.ResIdentifier | common.OtherIdentifier:
    with contextlib.suppress(ValueError):
        return common.ResIdentifier(value)

    return value
