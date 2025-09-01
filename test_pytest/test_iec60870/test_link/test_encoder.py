import pytest

from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link.encoder import Encoder


@pytest.mark.parametrize('address_size', common.AddressSize)
@pytest.mark.parametrize('direction_valid', [True, False])
@pytest.mark.parametrize('data, frame_size, with_addr', [
    (b'', 1, False),
    (b'\xe5', 1, False),
    (b'\xe5\xab\x01\x02', 1, False),
    (b'\x10\x00\x00', 4, True),
    (b'\x10', 4, True),
    (b'\x68\x02\x02\x68', 2 + 6, False),
    (b'\x68', 4, False)])
def test_get_next_frame_size(address_size, direction_valid, data, frame_size,
                             with_addr):
    encoder = Encoder(address_size, direction_valid)
    exp_frame_size = (frame_size if not with_addr
                      else frame_size + address_size.value)
    assert encoder.get_next_frame_size(data) == exp_frame_size


@pytest.mark.parametrize('address_size', common.AddressSize)
@pytest.mark.parametrize('direction_valid', [True, False])
@pytest.mark.parametrize('data', [b'\x68\x02\x01\x68',
                                  b'\x68\x02\x02\x00',
                                  b'\xab'])
def test_get_next_frame_size_error(address_size, direction_valid, data):
    encoder = Encoder(address_size, direction_valid)
    with pytest.raises(Exception):
        encoder.get_next_frame_size(data)


@pytest.mark.parametrize('direction', [None, *common.Direction])
@pytest.mark.parametrize('fcb', [True, False])
@pytest.mark.parametrize('fcv', [True, False])
@pytest.mark.parametrize('function', common.ReqFunction)
@pytest.mark.parametrize('data', [b'',
                                  b'\x00',
                                  b'\xab\xff',
                                  b'\x12\xcd' * 10])
@pytest.mark.parametrize('address, address_size', [
    (0, common.AddressSize.ZERO),
    (112, common.AddressSize.ONE),
    (456, common.AddressSize.TWO)])
def test_encode_decode_req(direction, fcb, fcv, function, data, address,
                           address_size):
    encoder = Encoder(address_size, direction is not None)
    frame = common.ReqFrame(direction=direction,
                            frame_count_bit=fcb,
                            frame_count_valid=fcv,
                            function=function,
                            address=address,
                            data=data)
    encoded = encoder.encode(frame)
    frame_decoded = encoder.decode(encoded)
    assert frame == frame_decoded


@pytest.mark.parametrize('direction', [None, *common.Direction])
@pytest.mark.parametrize('ac', [True, False])
@pytest.mark.parametrize('dfc', [True, False])
@pytest.mark.parametrize('function', common.ResFunction)
@pytest.mark.parametrize('data', [b'',
                                  b'\x00',
                                  b'\xab\xff',
                                  b'\x12\xcd' * 10])
@pytest.mark.parametrize('address, address_size', [
    (0, common.AddressSize.ZERO),
    (112, common.AddressSize.ONE),
    (456, common.AddressSize.TWO)])
def test_encode_decode_res(direction, function, data, ac, dfc, address,
                           address_size):
    encoder = Encoder(address_size, direction is not None)
    frame = common.ResFrame(direction=direction,
                            access_demand=ac,
                            data_flow_control=dfc,
                            function=function,
                            address=address,
                            data=data)
    encoded = encoder.encode(frame)
    frame_decoded = encoder.decode(encoded)
    assert frame == frame_decoded


@pytest.mark.parametrize('address_size', common.AddressSize)
@pytest.mark.parametrize('direction_valid', [True, False])
def test_encode_decode_short(address_size, direction_valid):
    encoder = Encoder(address_size, direction_valid)
    frame = common.ShortFrame()

    encoded = encoder.encode(frame)
    frame_decoded = encoder.decode(encoded)

    assert frame == frame_decoded
    assert bytes(encoded) == b'\xE5'


@pytest.mark.parametrize('direction_valid', [True, False])
@pytest.mark.parametrize('address_size, data', [
    (common.AddressSize.ONE, b'\x10\x49\x01\x4a\x16'),
    (common.AddressSize.ONE, b'\x68\x04\x04\x68\x43\x70\xab\xff\x5d\x16')])
def test_decode_valid(direction_valid, address_size, data):
    encoder = Encoder(address_size, direction_valid)
    frame = encoder.decode(data)
    assert isinstance(frame, (common.ReqFrame,
                              common.ResFrame,
                              common.ShortFrame))


@pytest.mark.parametrize('address_size', common.AddressSize)
@pytest.mark.parametrize('direction_valid', [True, False])
@pytest.mark.parametrize('data', [
    b'\x12',                                       # invalid start
    b'\x12\xab',                                   # invalid start
    b'\x10\xab',                                   # invalid end
    b'\x10\xab\x00\x00\x00',                       # invalid end
    b'\x10\xab\x00\x00\x16',                       # invalid crc
    b'\x68\x04\x04\x68\x43\x70\xab\xff\x5d\x12',   # invalid end
    b'\x68\x04\x04\x68\x43\x70\xab\xff\x5f\x16',   # invalid crc
    b'\x68\x04\x05\x68\x43\x70\xab\xff\x5d\x16',   # invalid length
    b'\x68\x03\x04\x68\x43\x70\xab\xff\x5d\x16',   # invalid length
    b'\x68\x03\x03\x68\x43\x70\xab\xff\x5d\x16',   # invalid length
    b'\x68\x04\x04\x67\x43\x70\xab\xff\x5d\x16'])  # invalid repeated start
def test_decode_invalid(address_size, direction_valid, data):
    encoder = Encoder(address_size, direction_valid)
    with pytest.raises(Exception):
        encoder.decode(data)


@pytest.mark.parametrize('address', [0, 255, 256, 65535, 65536])
@pytest.mark.parametrize('address_size', common.AddressSize)
def test_address_size(address, address_size):
    encoder = Encoder(address_size, False)
    frame = common.ReqFrame(
        direction=None,
        frame_count_bit=True,
        frame_count_valid=False,
        function=common.ReqFunction.REQ_DATA_1,
        address=address,
        data=b'')

    if ((address > 255 and address_size == common.AddressSize.ONE) or
            (address > 65535 and address_size == common.AddressSize.TWO)):
        with pytest.raises(Exception):
            encoded = encoder.encode(frame)
        return

    encoded = encoder.encode(frame)
    frame_decoded = encoder.decode(encoded)

    if address_size == common.AddressSize.ZERO:
        assert frame_decoded.address == 0
    else:
        assert frame.address == frame_decoded.address
