import itertools

import pytest

from hat.drivers.tls.l2 import common
from hat.drivers.tls.l2 import encoder


addresses = [0, 1, 112, common.broadcast_address]

datas = [b'',
         b'\x00',
         b'\xab\xff',
         b'\x12\xcd' * 10,
         bytes(range(253))]


def all_frames():
    for function, address, data, fcb, fcv in itertools.product(
            common.ReqFunction, [0, 112], [b'', b'\xab\xff'],
            [True, False], [True, False]):
        yield common.ReqFrame(frame_count_bit=fcb,
                              frame_count_valid=fcv,
                              function=function,
                              address=address,
                              data=data)

    for function, address, data, acd, dfc in itertools.product(
            common.ResFunction, [0, 112], [b'', b'\xab\xff'],
            [True, False], [True, False]):
        yield common.ResFrame(access_demand=acd,
                              data_flow_control=dfc,
                              function=function,
                              address=address,
                              data=data)

    yield common.ShortFrame()


@pytest.mark.parametrize('data, frame_size', [
    (b'', 1),
    (b'\xe5', 1),
    (b'\xe5\xab\x01', 1),
    (b'\x10', 5),
    (b'\x10\x49\x01', 5),
    (b'\x10\x49\x01\x4a\x16\xe5', 5),
    (b'\x68', 4),
    (b'\x68\x04\x04', 4),
    (b'\x68\x02\x02\x68', 2 + 6),
    (b'\x68\x04\x04\x68', 4 + 6),
    (b'\x68\x04\x04\x68\x73\x01', 4 + 6),
    (b'\x68\xff\xff\x68', 0xff + 6)])
def test_get_next_frame_size(data, frame_size):
    assert encoder.get_next_frame_size(data) == frame_size


@pytest.mark.parametrize('data', [
    b'\x12',                   # invalid start
    b'\x16',                   # invalid start
    b'\x68\x04\x05\x68',       # length not matching
    b'\x68\x04\x04\x67',       # invalid repeated start
    b'\x68\x01\x01\x68',       # invalid length
    b'\x68\x00\x00\x68'])      # invalid length
def test_get_next_frame_size_error(data):
    with pytest.raises(Exception):
        encoder.get_next_frame_size(data)


@pytest.mark.parametrize('fcb', [True, False])
@pytest.mark.parametrize('fcv', [True, False])
@pytest.mark.parametrize('function', common.ReqFunction)
@pytest.mark.parametrize('data', datas)
@pytest.mark.parametrize('address', addresses)
def test_encode_decode_req(fcb, fcv, function, data, address):
    frame = common.ReqFrame(frame_count_bit=fcb,
                            frame_count_valid=fcv,
                            function=function,
                            address=address,
                            data=data)

    encoded = encoder.encode_frame(frame)
    decoded = encoder.decode_frame(encoded)

    assert decoded == frame


@pytest.mark.parametrize('acd', [True, False])
@pytest.mark.parametrize('dfc', [True, False])
@pytest.mark.parametrize('function', common.ResFunction)
@pytest.mark.parametrize('data', datas)
@pytest.mark.parametrize('address', addresses)
def test_encode_decode_res(acd, dfc, function, data, address):
    frame = common.ResFrame(access_demand=acd,
                            data_flow_control=dfc,
                            function=function,
                            address=address,
                            data=data)

    encoded = encoder.encode_frame(frame)
    decoded = encoder.decode_frame(encoded)

    assert decoded == frame


def test_encode_decode_short():
    frame = common.ShortFrame()

    encoded = encoder.encode_frame(frame)
    decoded = encoder.decode_frame(encoded)

    assert decoded == frame
    assert encoded == b'\xe5'


@pytest.mark.parametrize('data, frame', [
    (b'\xe5',
     common.ShortFrame()),

    (b'\x10\x49\x01\x4a\x16',
     common.ReqFrame(frame_count_bit=False,
                     frame_count_valid=False,
                     function=common.ReqFunction.REQ_STATUS,
                     address=1,
                     data=b'')),

    (b'\x10\x40\x05\x45\x16',
     common.ReqFrame(frame_count_bit=False,
                     frame_count_valid=False,
                     function=common.ReqFunction.RESET_UNIT,
                     address=5,
                     data=b'')),

    (b'\x10\x78\x01\x79\x16',
     common.ReqFrame(frame_count_bit=True,
                     frame_count_valid=True,
                     function=common.ReqFunction.REQ_DATA_1_OR_2,
                     address=1,
                     data=b'')),

    (b'\x68\x04\x04\x68\x73\x01\xab\xff\x1e\x16',
     common.ReqFrame(frame_count_bit=True,
                     frame_count_valid=True,
                     function=common.ReqFunction.SEND_DATA,
                     address=1,
                     data=b'\xab\xff')),

    (b'\x68\x03\x03\x68\x44\xff\x01\x44\x16',
     common.ReqFrame(frame_count_bit=False,
                     frame_count_valid=False,
                     function=common.ReqFunction.SEND_DATA_NO_RES,
                     address=common.broadcast_address,
                     data=b'\x01')),

    (b'\x10\x0b\x01\x0c\x16',
     common.ResFrame(access_demand=False,
                     data_flow_control=False,
                     function=common.ResFunction.RES_STATUS,
                     address=1,
                     data=b'')),

    (b'\x10\x29\x01\x2a\x16',
     common.ResFrame(access_demand=True,
                     data_flow_control=False,
                     function=common.ResFunction.RES_ACK,
                     address=1,
                     data=b'')),

    (b'\x68\x05\x05\x68\x18\x02\x61\x62\x63\x40\x16',
     common.ResFrame(access_demand=False,
                     data_flow_control=True,
                     function=common.ResFunction.RES_DATA,
                     address=2,
                     data=b'abc')),

    (b'\x68\x03\x03\x68\x0f\x01\x00\x10\x16',
     common.ResFrame(access_demand=False,
                     data_flow_control=False,
                     function=common.ResFunction.RES_TEST,
                     address=1,
                     data=b'\x00'))])
def test_known_frames(data, frame):
    assert encoder.get_next_frame_size(data) == len(data)
    assert encoder.decode_frame(data) == frame
    assert encoder.decode_frame(memoryview(data)) == frame
    assert encoder.encode_frame(frame) == data


def test_decode_variable_frame_without_data():
    data = b'\x68\x02\x02\x68\x49\x01\x4a\x16'
    frame = common.ReqFrame(frame_count_bit=False,
                            frame_count_valid=False,
                            function=common.ReqFunction.REQ_STATUS,
                            address=1,
                            data=b'')

    assert encoder.get_next_frame_size(data) == len(data)
    assert encoder.decode_frame(data) == frame
    assert encoder.encode_frame(frame) == b'\x10\x49\x01\x4a\x16'


@pytest.mark.parametrize('data', [
    b'\x12',                                         # invalid start
    b'\x10\x49\x01\x4a\x12',                         # invalid end
    b'\x10\x49\x01\x4b\x16',                         # invalid crc
    b'\x10\x49\x01',                                 # truncated
    b'\x68\x04\x04\x68\x73\x01\xab\xff\x1e\x12',     # invalid end
    b'\x68\x04\x04\x68\x73\x01\xab\xff\x1f\x16',     # invalid crc
    b'\x68\x04\x05\x68\x73\x01\xab\xff\x1e\x16',     # length not matching
    b'\x68\x05\x04\x68\x73\x01\xab\xff\x1e\x16',     # length not matching
    b'\x68\x03\x03\x68\x73\x01\xab\xff\x1e\x16',     # invalid length
    b'\x68\x04\x04\x67\x73\x01\xab\xff\x1e\x16',     # invalid repeated start
    b'\x68\x01\x01\x68\x49\x49\x16',                 # invalid length
    b'\x68\x04\x04\x68\x73\x01\xab',                 # truncated
    b'\x10\x42\x01\x43\x16',                         # unknown req function
    b'\x10\x02\x01\x03\x16'])                        # unknown res function
def test_decode_invalid(data):
    with pytest.raises(Exception):
        encoder.decode_frame(data)


@pytest.mark.parametrize('address', [-1, common.broadcast_address + 1])
def test_encode_invalid_address(address):
    frame = common.ReqFrame(frame_count_bit=False,
                            frame_count_valid=False,
                            function=common.ReqFunction.REQ_STATUS,
                            address=address,
                            data=b'')

    with pytest.raises(Exception):
        encoder.encode_frame(frame)


def test_encode_data_too_long():
    frame = common.ReqFrame(frame_count_bit=False,
                            frame_count_valid=False,
                            function=common.ReqFunction.SEND_DATA,
                            address=1,
                            data=bytes(254))

    with pytest.raises(Exception):
        encoder.encode_frame(frame)


def test_encode_invalid_frame_type():
    with pytest.raises(Exception):
        encoder.encode_frame(b'\xff')


@pytest.mark.parametrize('frame', list(all_frames()))
def test_get_next_frame_size_complete(frame):
    encoded = encoder.encode_frame(frame)
    trailing = b'\xe5\x10\x49'

    assert encoder.get_next_frame_size(encoded) == len(encoded)
    assert encoder.get_next_frame_size(encoded + trailing) == len(encoded)
