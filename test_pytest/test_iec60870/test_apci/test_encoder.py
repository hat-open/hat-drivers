import pytest

from hat.drivers.iec60870.apci import common
from hat.drivers.iec60870.apci import encoder


@pytest.mark.parametrize("data, size", [
    (b'\xab', 2),
    (b'', 2),
    (b'\xab\xcd', None),
    (b'\x68\x04', 6),
    (b'\x68\x05', 7),
    (b'\x68\x05\xab\xcd\xef\xff\x12', 7),
    (b'\x68\x00', None),
    (b'\x68\x03', None),
    (b'\x68\xaa', 172),
    (b'\x68\xff', 257),
    ])
def test_get_next_apdu_size(data, size):
    if size is None:
        with pytest.raises(Exception):
            assert encoder.get_next_apdu_size(b'\xab\xcd')
    else:
        assert encoder.get_next_apdu_size(data) == size


@pytest.mark.parametrize("apdu", [
    common.APDUI(ssn=1, rsn=2, data=b''),
    common.APDUI(ssn=1, rsn=2, data=b'\x01\xab\x23'),
    common.APDUI(ssn=32767, rsn=2, data=b'\xff\xdd\x99'),
    common.APDUI(ssn=32767, rsn=2, data=b'\x12' * 249),
    common.APDUS(rsn=0),
    common.APDUS(rsn=256),
    common.APDUS(rsn=32767),
    common.APDUS(rsn=123),
    common.APDUU(function=common.ApduFunction.TESTFR_CON),
    common.APDUU(function=common.ApduFunction.TESTFR_ACT),
    common.APDUU(function=common.ApduFunction.STOPDT_CON),
    common.APDUU(function=common.ApduFunction.STOPDT_ACT),
    common.APDUU(function=common.ApduFunction.STARTDT_CON),
    common.APDUU(function=common.ApduFunction.STARTDT_ACT),
    ])
def test_encode_decode(apdu):
    apdu_encoded = encoder.encode(apdu)
    apdu_decoded = encoder.decode(apdu_encoded)
    assert apdu == apdu_decoded


@pytest.mark.parametrize("data, apdu_format", [
    (b'\xab', None),  # invalid start identifier
    (b'\xab\xcd\x12', None),  # invalid start identifier
    (b'\x68\x00', None),  # invalid length
    (b'\x68\x01', None),  # invalid length
    (b'\x68\x02', None),  # invalid length
    (b'\x68\x03', None),  # invalid length
    (b'\x68\x04', None),  # no control fields
    (b'\x68\x04' + b'\x00' * 4, common.APDUI),  # valid APDUI
    (b'\x68\x04' + int('0b10000011', 2).to_bytes(4, 'little'),  # valid APDUU
        common.APDUU),
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(4, 'little'),  # valid APDUS
        common.APDUS),
    ])
def test_decode(data, apdu_format):
    if apdu_format is None:
        with pytest.raises(Exception):
            encoder.decode(data)
    else:
        apdu = encoder.decode(data)
        assert isinstance(apdu, apdu_format)


@pytest.mark.parametrize("data, function", [
    (b'\x68\x04' + int('0b10000011', 2).to_bytes(4, 'little'),
        common.ApduFunction.TESTFR_CON),
    (b'\x68\x04' + int('0b01000011', 2).to_bytes(4, 'little'),
        common.ApduFunction.TESTFR_ACT),
    (b'\x68\x04' + int('0b00100011', 2).to_bytes(4, 'little'),
        common.ApduFunction.STOPDT_CON),
    (b'\x68\x04' + int('0b00010011', 2).to_bytes(4, 'little'),
        common.ApduFunction.STOPDT_ACT),
    (b'\x68\x04' + int('0b00001011', 2).to_bytes(4, 'little'),
        common.ApduFunction.STARTDT_CON),
    (b'\x68\x04' + int('0b00000111', 2).to_bytes(4, 'little'),
        common.ApduFunction.STARTDT_ACT),
    (b'\x68\x05' + int('0b00000111', 2).to_bytes(4, 'little'),
        common.ApduFunction.STARTDT_ACT),
    (b'\x68\x04' + int('0b00000011', 2).to_bytes(4, 'little'), None),
    (b'\x68\x04' + int('0b11000011', 2).to_bytes(4, 'little'), None),
    ])
def test_decode_apduu(data, function):
    if function is None:
        with pytest.raises(Exception):
            encoder.decode(data)
    else:
        apdu = encoder.decode(data)
        assert isinstance(apdu, common.APDUU)
        assert apdu.function == function


@pytest.mark.parametrize("apdu_bytes, ssn, rsn, data", [
    (b'\x68\x04' + b'\x00' * 4, 0, 0, b''),
    (b'\x68\x04' + b'\x00' * 4 + b'\xab\xcd', 0, 0, b''),
    (b'\x68\x05' + b'\x00' * 4 + b'\xab\xcd', 0, 0, b'\xab'),
    ])
def test_decode_apdui(apdu_bytes, ssn, rsn, data):
    apdu = encoder.decode(apdu_bytes)
    assert isinstance(apdu, common.APDUI)
    assert apdu.ssn == ssn
    assert apdu.rsn == rsn
    assert apdu.data == data


@pytest.mark.parametrize("asdu_size, raises_exc", [
    (249, False),
    (250, True),
    (251, True),
    (252, True),
    ])
def test_encode_asdu_size(asdu_size, raises_exc):
    apdu = common.APDUI(ssn=1, rsn=2, data=b'\x12' * asdu_size)
    if raises_exc:
        with pytest.raises(Exception):
            apdu_encoded = encoder.encode(apdu)
    else:
        apdu_encoded = encoder.encode(apdu)
        assert type(apdu_encoded) == bytes
        assert len(apdu_encoded) == 6 + asdu_size


@pytest.mark.parametrize("apdu_bytes, rsn", [
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(4, 'little'), 0),
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(2, 'little') + b'\x02\x00',
        1),
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(2, 'little') + b'\x04\x00',
        2),
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(2, 'little') + b'\x05\x00',
        2),
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(2, 'little') + b'\x06\x00',
        3),
    (b'\x68\x04' + int('0b00000001', 2).to_bytes(2, 'little') + b'\x07\x00',
        3),
    ])
def test_decode_apdus(apdu_bytes, rsn):
    apdu = encoder.decode(apdu_bytes)
    assert isinstance(apdu, common.APDUS)
    assert apdu.rsn == rsn


@pytest.mark.parametrize("s_i", ['s', 'i'])
@pytest.mark.parametrize("sn, sn_exp", [
    (32767, 32767),
    (32768, 0),
    (32769, 1),
    (32768 + 100, 100),
    ])
def test_sn(sn, sn_exp, s_i):
    if s_i == 'i':
        apdu = common.APDUI(ssn=sn, rsn=sn, data=b'')
    else:
        apdu = common.APDUS(rsn=sn)

    apdu_encoded = encoder.encode(apdu)
    apdu_decoded = encoder.decode(apdu_encoded)
    if s_i == 'i':
        assert apdu_decoded.ssn == sn_exp
        assert apdu_decoded.rsn == sn_exp
    else:
        assert apdu_decoded.rsn == sn_exp
