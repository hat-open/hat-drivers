import pytest

from hat.drivers.iec60870.link.encoder import Encoder
from hat.drivers.iec60870.link import AddressSize
import hat.drivers.iec60870.link.common as common


@pytest.mark.parametrize("address_size", [AddressSize.ZERO,
                                          AddressSize.ONE,
                                          AddressSize.TWO])
@pytest.mark.parametrize("data, frame_size, include_addr", [
    (b'', 1, False),
    (b'\xe5', 1, False),
    (b'\xe5\xab\x01\x02', 1, False),
    (b'\x10\x00\x00', 4, True),
    (b'\x10', 4, True),
    (b'\x68\x02\x02\x68', 2 + 6, False),
    (b'\x68\x02\x01\x68', None, False),
    (b'\x68\x02\x02\x00', None, False),
    (b'\x68', 4, False),
    (b'\xab', None, False),
    ])
def test_get_next_frame_size(data, frame_size, address_size, include_addr):
    encoder = Encoder(address_size, False)
    if frame_size is None:
        with pytest.raises(Exception):
            encoder.get_next_frame_size(data)
        return
    exp_frame_size = (frame_size if not include_addr
                      else frame_size + address_size.value)
    assert encoder.get_next_frame_size(data) == exp_frame_size


@pytest.mark.parametrize('direction', [None])
@pytest.mark.parametrize('fcb_ac', [False])
@pytest.mark.parametrize('fcv_dfc', [False])
@pytest.mark.parametrize('function', [
    common.ReqFunction.RESET_LINK,
    common.ReqFunction.RESET_PROCESS,
    common.ReqFunction.TEST,
    common.ReqFunction.DATA,
    common.ReqFunction.DATA_NO_RES,
    common.ReqFunction.REQ_ACCESS_DEMAND,
    common.ReqFunction.REQ_STATUS,
    common.ReqFunction.REQ_DATA_1,
    common.ReqFunction.REQ_DATA_2,
    common.ResFunction.ACK,
    common.ResFunction.NACK,
    common.ResFunction.RES_DATA,
    common.ResFunction.RES_NACK,
    common.ResFunction.RES_STATUS,
    common.ResFunction.NOT_FUNCTIONING,
    common.ResFunction.NOT_IMPLEMENTED,
    ])
@pytest.mark.parametrize('data', [b'', b'\x00', b'\xab\xff', b'\x12\xcd' * 10])
@pytest.mark.parametrize('address, address_size', [
    (123, AddressSize.ZERO),
    (112, AddressSize.ONE),
    (456, AddressSize.TWO),
    ])
def test_encoder(direction, function, data, fcb_ac, fcv_dfc,
                 address, address_size):
    encoder = Encoder(address_size, False)
    if isinstance(function, common.ReqFunction):
        frame = common.ReqFrame(
            direction=direction,
            frame_count_bit=fcb_ac,
            frame_count_valid=fcv_dfc,
            function=function,
            address=address,
            data=data)
    else:
        frame = common.ResFrame(
            direction=direction,
            access_demand=fcb_ac,
            data_flow_control=fcv_dfc,
            function=function,
            address=address,
            data=data)

    encoded = encoder.encode(frame)
    frame_decoded = encoder.decode(encoded)

    if (address_size == AddressSize.ZERO or frame == _short_ack):
        assert frame._replace(address=None) == frame_decoded
    else:
        assert frame == frame_decoded


@pytest.mark.parametrize('address', [
    0, 255, 256, 65535, 65536])
@pytest.mark.parametrize('address_size', [
    AddressSize.ZERO,
    AddressSize.ONE,
    AddressSize.TWO])
def test_address_size(address, address_size):
    encoder = Encoder(address_size, False)
    frame = common.ReqFrame(
        direction=None,
        frame_count_bit=True,
        frame_count_valid=False,
        function=common.ReqFunction.REQ_DATA_1,
        address=address,
        data=b'')

    if ((address > 255 and address_size == AddressSize.ONE) or
            (address > 65535 and address_size == AddressSize.TWO)):
        with pytest.raises(Exception):
            encoded = encoder.encode(frame)
        return

    encoded = encoder.encode(frame)
    frame_decoded = encoder.decode(encoded)

    if address_size == AddressSize.ZERO:
        assert frame_decoded.address is None
    else:
        assert frame.address == frame_decoded.address


_short_ack = common.ResFrame(direction=None,
                             access_demand=False,
                             data_flow_control=False,
                             function=common.ResFunction.ACK,
                             address=None,
                             data=b'')
