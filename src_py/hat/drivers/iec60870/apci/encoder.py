import itertools

from hat.drivers.iec60870.apci import common


def get_next_apdu_size(data: common.Bytes) -> int:
    if len(data) < 2:
        return 2

    if data[0] != 0x68:
        raise Exception('invalid start identifier')

    if data[1] < 4:
        raise Exception('invalid length')

    return data[1] + 2


def decode(data: common.Bytes) -> common.APDU:
    if data[0] != 0x68:
        raise Exception('invalid start identifier')

    length = data[1]
    if length < 4:
        raise Exception("invalid length")

    control_fields, data = data[2:6], data[6:2+length]

    if control_fields[0] & 1 and control_fields[0] & 2:
        function = common.ApduFunction(control_fields[0])
        return common.APDUU(function=function)

    if control_fields[0] & 1:
        rsn = (control_fields[3] << 7) | (control_fields[2] >> 1)
        return common.APDUS(rsn=rsn)

    ssn = (control_fields[1] << 7) | (control_fields[0] >> 1)
    rsn = (control_fields[3] << 7) | (control_fields[2] >> 1)
    return common.APDUI(ssn=ssn,
                        rsn=rsn,
                        data=data)


def encode(apdu: common.APDU) -> common.Bytes:
    if isinstance(apdu, common.APDUI):
        if apdu.ssn > 0x7FFF:
            raise ValueError('invalid send sequence number')
        if apdu.rsn > 0x7FFF:
            raise ValueError('invalid receive sequence number')
        if len(apdu.data) > 249:
            raise ValueError('unsupported data size')
        data = [(apdu.ssn << 1) & 0xFF,
                (apdu.ssn >> 7) & 0xFF,
                (apdu.rsn << 1) & 0xFF,
                (apdu.rsn >> 7) & 0xFF,
                *apdu.data]

    elif isinstance(apdu, common.APDUS):
        if apdu.rsn > 0x7FFF:
            raise ValueError('invalid receive sequence number')
        data = [1,
                0,
                (apdu.rsn << 1) & 0xFF,
                (apdu.rsn >> 7) & 0xFF]

    elif isinstance(apdu, common.APDUU):
        data = [apdu.function.value,
                0,
                0,
                0]

    else:
        raise ValueError('unsupported apdu')

    return bytes(itertools.chain([0x68, len(data)], data))
