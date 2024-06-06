import pytest

from hat.drivers.snmp import encoder
from hat.drivers.snmp import common


data = [common.IntegerData(name=(1, 0),
                           value=-10),
        common.UnsignedData(name=(1, 1),
                            value=10),
        common.CounterData(name=(1, 2),
                           value=10),
        common.StringData(name=(1, 3),
                          value='xyz'),
        common.ObjectIdData(name=(1, 4),
                            value=(1, 6, 3, 4, 5)),
        common.ObjectIdData(name=(1, 5),
                            value=(1, 6, 3, 4, 5)),
        common.TimeTicksData(name=(1, 6),
                             value=10),
        common.ArbitraryData(name=(1, 7),
                             value=b'xyz'),
        common.BigCounterData(name=(1, 8),
                              value=129041231),
        common.UnspecifiedData(name=(2, 456))]


@pytest.mark.parametrize("msg_type", [encoder.v2c.MsgType.GET_REQUEST,
                                      encoder.v2c.MsgType.GET_NEXT_REQUEST,
                                      encoder.v2c.MsgType.RESPONSE,
                                      encoder.v2c.MsgType.SET_REQUEST,
                                      encoder.v2c.MsgType.INFORM_REQUEST,
                                      encoder.v2c.MsgType.SNMPV2_TRAP,
                                      encoder.v2c.MsgType.REPORT])
@pytest.mark.parametrize("error_type", common.ErrorType)
@pytest.mark.parametrize("data", [data])
def test_encode_decode_basic(msg_type, error_type, data):
    msg = encoder.v2c.Msg(type=msg_type,
                          community='abc',
                          pdu=encoder.v2c.BasicPdu(
                              request_id=123,
                              error=common.Error(
                                  type=error_type,
                                  index=456),
                              data=data))

    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


@pytest.mark.parametrize("data", [data])
def test_encode_decode_bulk(data):
    msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.GET_BULK_REQUEST,
                          community='abc',
                          pdu=encoder.v2c.BulkPdu(
                              request_id=123,
                              non_repeaters=100,
                              max_repetitions=200,
                              data=data))
    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


@pytest.mark.parametrize("msg", [
    # bulk type, basic pdu
    encoder.v2c.Msg(
        type=encoder.v2c.MsgType.GET_BULK_REQUEST,
        community='abc',
        pdu=encoder.v2c.BasicPdu(
            request_id=1,
            error=common.Error(common.ErrorType.NO_ERROR, 1),
            data=[])),
    # basic type, bulk pdu
    encoder.v2c.Msg(
        type=encoder.v2c.MsgType.GET_REQUEST,
        community='abc',
        pdu=encoder.v2c.BulkPdu(
            request_id=1,
            non_repeaters=1,
            max_repetitions=1,
            data=[]))
    ])
def test_encode_invalid_msg_pdu(msg):
    with pytest.raises(ValueError):
        encoder.encode(msg)


@pytest.mark.parametrize("invalid_bytes", [b'xyz', b'some random bytes'])
def test_decode_invalid(invalid_bytes):
    with pytest.raises(Exception):
        encoder.v2c.decode_msg(invalid_bytes)
