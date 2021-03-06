import pytest

from hat.drivers.snmp import encoder
from hat.drivers.snmp import common


def _cover_data_types(version):
    yield common.Data(type=common.DataType.INTEGER,
                      name=(1, 0),
                      value=-10)
    yield common.Data(type=common.DataType.UNSIGNED,
                      name=(1, 1),
                      value=10)
    yield common.Data(type=common.DataType.COUNTER,
                      name=(1, 2),
                      value=10)
    yield common.Data(type=common.DataType.STRING,
                      name=(1, 3),
                      value='xyz')
    yield common.Data(type=common.DataType.OBJECT_ID,
                      name=(1, 4),
                      value=(1, 6, 3, 4, 5))
    yield common.Data(type=common.DataType.OBJECT_ID,
                      name=(1, 5),
                      value=(1, 6, 3, 4, 5))
    yield common.Data(type=common.DataType.TIME_TICKS,
                      name=(1, 6),
                      value=10)
    yield common.Data(type=common.DataType.ARBITRARY,
                      name=(1, 7),
                      value=b'xyz')
    if version == 'v1':
        yield common.Data(type=common.DataType.EMPTY,
                          name=(1, 8),
                          value=None)
    elif version in ('v2c', 'v3'):
        yield common.Data(type=common.DataType.BIG_COUNTER,
                          name=(1, 8),
                          value=129041231)


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
@pytest.mark.parametrize("data", [list(_cover_data_types('v1'))])
def test_encode_decode_v1_basic(msg_type, error_type, data):
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


@pytest.mark.parametrize("enterprise", [(1, 2)])
@pytest.mark.parametrize("addr", [(5, 6, 7, 8)])
@pytest.mark.parametrize("cause_type", common.CauseType)
@pytest.mark.parametrize("data", [list(_cover_data_types('v1'))])
def test_encode_decode_v1_trap(enterprise, addr, cause_type, data):
    msg = encoder.v1.Msg(type=encoder.v1.MsgType.TRAP,
                         community='abc',
                         pdu=encoder.v1.TrapPdu(
                             enterprise=enterprise,
                             addr=addr,
                             cause=common.Cause(
                                 type=cause_type,
                                 value=500),
                             timestamp=100,
                             data=data))
    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


@pytest.mark.parametrize("msg_type", [encoder.v2c.MsgType.GET_REQUEST,
                                      encoder.v2c.MsgType.GET_NEXT_REQUEST,
                                      encoder.v2c.MsgType.RESPONSE,
                                      encoder.v2c.MsgType.SET_REQUEST,
                                      encoder.v2c.MsgType.INFORM_REQUEST,
                                      encoder.v2c.MsgType.SNMPV2_TRAP,
                                      encoder.v2c.MsgType.REPORT])
@pytest.mark.parametrize("error_type", common.ErrorType)
@pytest.mark.parametrize("data", [list(_cover_data_types('v2c'))])
def test_encode_decode_v2c_basic(msg_type, error_type, data):
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


@pytest.mark.parametrize("data", [list(_cover_data_types('v2c'))])
def test_encode_decode_v2c_bulk(data):
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


@pytest.mark.parametrize("msg_type", [encoder.v3.MsgType.GET_REQUEST,
                                      encoder.v3.MsgType.GET_NEXT_REQUEST,
                                      encoder.v3.MsgType.RESPONSE,
                                      encoder.v3.MsgType.SET_REQUEST,
                                      encoder.v3.MsgType.INFORM_REQUEST,
                                      encoder.v3.MsgType.SNMPV2_TRAP,
                                      encoder.v3.MsgType.REPORT])
@pytest.mark.parametrize("error_type", common.ErrorType)
@pytest.mark.parametrize("data", [list(_cover_data_types('v3'))])
def test_encode_decode_v3_basic(msg_type, error_type, data):
    msg = encoder.v3.Msg(type=msg_type,
                         id=100,
                         reportable=True,
                         context=common.Context('engine_id', 'engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=error_type,
                                 index=456),
                             data=data))
    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


@pytest.mark.parametrize("data", [list(_cover_data_types('v3'))])
def test_encode_decode_v3_bulk(data):
    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_BULK_REQUEST,
                         id=100,
                         reportable=True,
                         context=common.Context('engine_id', 'engine_name'),
                         pdu=encoder.v3.BulkPdu(
                             request_id=123,
                             non_repeaters=100,
                             max_repetitions=200,
                             data=data))
    msg_bytes = encoder.encode(msg)
    msg_decode = encoder.decode(msg_bytes)
    assert msg_decode == msg


def test_decode_invalid():
    invalid_bytes = b'xyz'
    with pytest.raises(Exception):
        encoder.v1.decode(invalid_bytes)
    with pytest.raises(Exception):
        encoder.v2c.decode(invalid_bytes)
    with pytest.raises(Exception):
        encoder.v3.decode(invalid_bytes)


def _data_msg(data_type, value):
    if data_type == common.DataType.EMPTY:
        return encoder.v1.Msg(
            type=encoder.v1.MsgType.GET_REQUEST,
            community='abc',
            pdu=encoder.v1.BasicPdu(
                request_id=1,
                error=common.Error(common.ErrorType.NO_ERROR, 1),
                data=[common.Data(
                    type=data_type,
                    name=(1, 2, 3),
                    value=value)]))
    return encoder.v2c.Msg(
        type=encoder.v2c.MsgType.GET_REQUEST,
        community='abc',
        pdu=encoder.v2c.BasicPdu(
            request_id=1,
            error=common.Error(common.ErrorType.NO_ERROR, 1),
            data=[common.Data(
                type=data_type,
                name=(1, 2, 3),
                value=value)]))


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
            enterprise=(1, 2, 3),
            addr=(123, 4, 5, 6),
            cause=common.Cause(common.CauseType.COLD_START, 1),
            timestamp=10,
            data=[])),
    # # error type not in v1
    # encoder.v1.Msg(
    #     type=encoder.v1.MsgType.GET_REQUEST,
    #     community='abc',
    #     pdu=encoder.v1.BasicPdu(
    #         request_id=1,
    #         error=common.Error(common.ErrorType.NO_ACCESS, 1),
    #         data=[])),
    # data type not in v1
    encoder.v1.Msg(
        type=encoder.v1.MsgType.GET_REQUEST,
        community='abc',
        pdu=encoder.v1.BasicPdu(
            request_id=1,
            error=common.Error(common.ErrorType.NO_ERROR, 1),
            data=[common.Data(
                type=common.DataType.BIG_COUNTER,
                name=(1, 2, 3),
                value=1290341043)])),
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
            data=[])),
    # v2c msg, v3 pdu
    encoder.v2c.Msg(
        type=encoder.v2c.MsgType.GET_BULK_REQUEST,
        community='abc',
        pdu=encoder.v3.BasicPdu(
            request_id=1,
            error=common.Error(common.ErrorType.NO_ERROR, 1),
            data=[])),
    # # invalid data
    # _data_msg(common.DataType.INTEGER, 'not integer'),
    # _data_msg(common.DataType.UNSIGNED, 'not integer'),
    # _data_msg(common.DataType.UNSIGNED, -100),
    # _data_msg(common.DataType.COUNTER, 2**33),
    # _data_msg(common.DataType.STRING, 11),
    # _data_msg(common.DataType.OBJECT_ID, (100, 1, 2)),
    # _data_msg(common.DataType.OBJECT_ID, 'abc'),
    # _data_msg(common.DataType.IP_ADDRESS, (1, 2, 3)),
    # _data_msg(common.DataType.IP_ADDRESS, (1, 2, 3, 4, 5)),
    # _data_msg(common.DataType.IP_ADDRESS, (1, '2', '3', 4)),
    # _data_msg(common.DataType.TIME_TICKS, 2 ** 65),
    # _data_msg(common.DataType.TIME_TICKS, 'tick tock'),
    # _data_msg(common.DataType.ARBITRARY, 1234),
    # _data_msg(common.DataType.EMPTY, 'not empty'),
    # _data_msg(common.DataType.UNSPECIFIED, 'specified'),
    # _data_msg(common.DataType.NO_SUCH_OBJECT, 'such object'),
    # _data_msg(common.DataType.NO_SUCH_INSTANCE, 'such instance'),
    # _data_msg(common.DataType.END_OF_MIB_VIEW, 23592)
])
def test_encode_invalid(msg):
    if isinstance(msg, encoder.v1.Msg):
        fn = encoder.v1.encode_msg
    elif isinstance(msg, encoder.v2c.Msg):
        fn = encoder.v2c.encode_msg
    elif isinstance(msg, encoder.v3.Msg):
        fn = encoder.v3.encode_msg
    else:
        raise Exception('could not select encode function')
    with pytest.raises(ValueError):
        fn(msg)
