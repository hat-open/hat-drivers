import collections
import itertools
import math

from hat import util

from hat.drivers.cotp import common


def encode(tpdu: common.Tpdu) -> util.Bytes:
    if isinstance(tpdu, common.DT):
        tpdu_type = common.TpduType.DT

    elif isinstance(tpdu, common.CR):
        tpdu_type = common.TpduType.CR

    elif isinstance(tpdu, common.CC):
        tpdu_type = common.TpduType.CC

    elif isinstance(tpdu, common.DR):
        tpdu_type = common.TpduType.DR

    elif isinstance(tpdu, common.ER):
        tpdu_type = common.TpduType.ER

    else:
        raise ValueError('invalid tpdu')

    header = collections.deque()
    header.append(tpdu_type.value)

    if tpdu_type == common.TpduType.DT:
        header.append(0x80 if tpdu.eot else 0)
        return bytes(itertools.chain([len(header)], header, tpdu.data))

    if tpdu_type == common.TpduType.CR:
        header.extend([0, 0])

    else:
        header.extend(tpdu.dst.to_bytes(2, 'big'))

    if tpdu_type == common.TpduType.ER:
        header.append(tpdu.cause)

    else:
        header.extend(tpdu.src.to_bytes(2, 'big'))

    if tpdu_type == common.TpduType.DR:
        header.append(tpdu.reason)

    elif tpdu_type == common.TpduType.CR or tpdu_type == common.TpduType.CC:
        header.append(tpdu.cls << 4)

        if tpdu.calling_tsel is not None:
            header.append(0xC1)
            header.append(2)
            header.extend(tpdu.calling_tsel.to_bytes(2, 'big'))

        if tpdu.called_tsel is not None:
            header.append(0xC2)
            header.append(2)
            header.extend(tpdu.called_tsel.to_bytes(2, 'big'))

        if tpdu.max_tpdu is not None:
            header.append(0xC0)
            header.append(1)
            header.append(tpdu.max_tpdu.bit_length() - 1)

        if tpdu.pref_max_tpdu is not None:
            pref_max_tpdu_data = _uint_to_bebytes(tpdu.pref_max_tpdu // 128)
            header.append(0xC0)
            header.append(len(pref_max_tpdu_data))
            header.extend(pref_max_tpdu_data)

    return bytes(itertools.chain([len(header)], header))


def decode(data: util.Bytes) -> common.Tpdu:
    length_indicator = data[0]
    if length_indicator >= len(data) or length_indicator > 254:
        raise ValueError("invalid length indicator")

    header = data[:length_indicator + 1]
    tpdu_data = data[length_indicator + 1:]
    tpdu_type = common.TpduType(header[1] & 0xF0)

    if tpdu_type == common.TpduType.DT:
        eot = bool(header[2] & 0x80)
        return common.DT(eot=eot,
                         data=tpdu_data)

    if tpdu_type in (common.TpduType.CR,
                     common.TpduType.CC,
                     common.TpduType.DR):
        src = (header[4] << 8) | header[5]

    if tpdu_type in (common.TpduType.CC,
                     common.TpduType.DR,
                     common.TpduType.ER):
        dst = (header[2] << 8) | header[3]

    if tpdu_type in (common.TpduType.CR, common.TpduType.CC):
        cls = header[6] >> 4
        calling_tsel = None
        called_tsel = None
        max_tpdu = None
        pref_max_tpdu = None
        vp_data = header[7:]
        while vp_data:
            k, v, vp_data = (vp_data[0],
                             vp_data[2:2 + vp_data[1]],
                             vp_data[2 + vp_data[1]:])
            if k == 0xC1:
                calling_tsel = _bebytes_to_uint(v)
            elif k == 0xC2:
                called_tsel = _bebytes_to_uint(v)
            elif k == 0xC0:
                max_tpdu = 1 << v[0]
            elif k == 0xF0:
                pref_max_tpdu = 128 * _bebytes_to_uint(v)

    if tpdu_type == common.TpduType.CR:
        return common.CR(src=src,
                         cls=cls,
                         calling_tsel=calling_tsel,
                         called_tsel=called_tsel,
                         max_tpdu=max_tpdu,
                         pref_max_tpdu=pref_max_tpdu)

    if tpdu_type == common.TpduType.CC:
        return common.CC(dst=dst,
                         src=src,
                         cls=cls,
                         calling_tsel=calling_tsel,
                         called_tsel=called_tsel,
                         max_tpdu=max_tpdu,
                         pref_max_tpdu=pref_max_tpdu)

    if tpdu_type == common.TpduType.DR:
        reason = header[6]
        return common.DR(dst=dst,
                         src=src,
                         reason=reason)

    if tpdu_type == common.TpduType.ER:
        cause = header[4]
        return common.ER(dst=dst,
                         cause=cause)

    raise ValueError("invalid tpdu code")


def _bebytes_to_uint(b):
    return int.from_bytes(b, 'big')


def _uint_to_bebytes(x):
    bytes_len = max(math.ceil(x.bit_length() / 8), 1)
    return x.to_bytes(bytes_len, 'big')
