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
                          value=b'xyz'),
        common.ObjectIdData(name=(1, 4),
                            value=(1, 6, 3, 4, 5)),
        common.ObjectIdData(name=(1, 5),
                            value=(1, 6, 3, 4, 5)),
        common.TimeTicksData(name=(1, 6),
                             value=10),
        common.ArbitraryData(name=(1, 7),
                             value=b'xyz'),
        common.EmptyData(name=(1, 8))]


@pytest.mark.parametrize("msg_type", [encoder.v1.MsgType.GET_REQUEST,
                                      encoder.v1.MsgType.GET_NEXT_REQUEST,
                                      encoder.v1.MsgType.GET_RESPONSE,
                                      encoder.v1.MsgType.SET_REQUEST])
@pytest.mark.parametrize("error_type", [common.ErrorType.NO_ERROR,
                                        common.ErrorType.TOO_BIG,
                                        common.ErrorType.NO_SUCH_NAME,
                                        common.ErrorType.BAD_VALUE,
                                        common.ErrorType.READ_ONLY,
                                        common.ErrorType.GEN_ERR])
@pytest.mark.parametrize("data", [data])
def test_encode_decode_basic(msg_type, error_type, data):
    msg = encoder.v1.Msg(type=msg_type,
                         community='abc',
                         pdu=encoder.v1.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=error_type,
                                 index=456),
                             data=data))

    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


@pytest.mark.parametrize("enterprise", [(1, 2, 0)])
@pytest.mark.parametrize("addr", [(5, 6, 7, 8)])
@pytest.mark.parametrize("cause_type", common.CauseType)
@pytest.mark.parametrize("data", [data])
def test_encode_decode_trap(enterprise, addr, cause_type, data):
    msg = encoder.v1.Msg(type=encoder.v1.MsgType.TRAP,
                         community='abc',
                         pdu=encoder.v1.TrapPdu(
                             enterprise=enterprise,
                             addr=addr,
                             cause=common.Cause(
                                 type=cause_type,
                                 value=543),
                             timestamp=1234567,
                             data=data))

    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


@pytest.mark.parametrize("msg", [
    # trap type, basic pdu
    encoder.v1.Msg(
        type=encoder.v1.MsgType.TRAP,
        community='abc',
        pdu=encoder.v1.BasicPdu(
            request_id=1,
            error=common.Error(common.ErrorType.NO_ERROR, 1),
            data=[])),
    # basic type, trap pdu
    encoder.v1.Msg(
        type=encoder.v1.MsgType.GET_REQUEST,
        community='abc',
        pdu=encoder.v1.TrapPdu(
            enterprise=(1, 2, 0),
            addr=(123, 4, 5, 6),
            cause=common.Cause(common.CauseType.COLD_START, 1),
            timestamp=10,
            data=[])),
    ])
def test_encode_invalid_msg_pdu(msg):
    with pytest.raises(ValueError):
        encoder.encode(msg)


@pytest.mark.parametrize("invalid_bytes", [b'xyz', b'some random bytes'])
def test_decode_invalid(invalid_bytes):
    with pytest.raises(Exception):
        encoder.v1.decode_msg(invalid_bytes)
