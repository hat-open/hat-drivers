import pytest

from hat.drivers.snmp import encoder
from hat.drivers.snmp import common
from hat.drivers.snmp import key


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


md5_key = key.Key(type=key.KeyType.MD5,
                  data=b'1234567890abcdef')
sha_key = key.Key(type=key.KeyType.SHA,
                  data=b'1234567890abcdefghij')
des_key = key.Key(type=key.KeyType.DES,
                  data=b'1234567890abcdef')


def change_bytes(orig_bytes):
    bytes_array = [i for i in orig_bytes]
    bytes_array[-1] += 1
    return bytes(bytes_array)


@pytest.mark.parametrize("msg_type", [encoder.v3.MsgType.GET_REQUEST,
                                      encoder.v3.MsgType.GET_NEXT_REQUEST,
                                      encoder.v3.MsgType.RESPONSE,
                                      encoder.v3.MsgType.SET_REQUEST,
                                      encoder.v3.MsgType.INFORM_REQUEST,
                                      encoder.v3.MsgType.SNMPV2_TRAP,
                                      encoder.v3.MsgType.REPORT])
@pytest.mark.parametrize("error_type", common.ErrorType)
@pytest.mark.parametrize("data", [data])
@pytest.mark.parametrize("auth_key, priv_key", [
    (None, None),
    (md5_key, None),
    (sha_key, None),
    (sha_key, des_key),
    (md5_key, des_key)])
def test_encode_decode_basic(msg_type, error_type, data, auth_key, priv_key):

    def on_auth_key(engine_id, user):
        return auth_key

    def on_priv_key(engine_id, user):
        return priv_key

    msg = encoder.v3.Msg(type=msg_type,
                         id=100,
                         reportable=True,
                         auth=auth_key is not None,
                         priv=priv_key is not None,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_xyz',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=error_type,
                                 index=456),
                             data=data))

    msg_bytes = encoder.encode(msg, auth_key=auth_key, priv_key=priv_key)
    msg_decode = encoder.decode(
        msg_bytes, auth_key_cb=on_auth_key, priv_key_cb=on_priv_key)
    assert msg_decode == msg


@pytest.mark.parametrize("data", [data])
@pytest.mark.parametrize("auth_key, priv_key", [
    (None, None),
    (md5_key, None),
    (sha_key, None),
    (sha_key, des_key),
    (md5_key, des_key)])
def test_encode_decode_bulk(data, auth_key, priv_key):

    def on_auth_key(engine_id, user):
        return auth_key

    def on_priv_key(engine_id, user):
        return priv_key

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_BULK_REQUEST,
                         id=100,
                         reportable=True,
                         auth=auth_key is not None,
                         priv=priv_key is not None,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_abc',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BulkPdu(
                             request_id=123,
                             non_repeaters=100,
                             max_repetitions=200,
                             data=data))

    msg_bytes = encoder.encode(msg, auth_key=auth_key, priv_key=priv_key)
    msg_decode = encoder.decode(
        msg_bytes, auth_key_cb=on_auth_key, priv_key_cb=on_priv_key)
    assert msg_decode == msg


@pytest.mark.parametrize('auth, auth_key, priv, priv_key', [
    (True, None, False, None),       # missing auth key
    (True, None, True, des_key),     # missing auth key
    (True, des_key, False, None),    # invalid auth key
    (True, md5_key, True, None),     # missing priv key
    (False, None, True, des_key),    # no auth, priv
    (True, md5_key, True, md5_key),  # invalid priv key
    (True, md5_key, True, sha_key),  # invalid priv key
    ])
def test_encode_invalid_keys(auth, auth_key, priv, priv_key):
    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                         id=100,
                         reportable=True,
                         auth=auth,
                         priv=priv,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_xyz',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=456),
                             data=[]))

    with pytest.raises(Exception):
        encoder.encode(msg, auth_key=auth_key, priv_key=priv_key)


@pytest.mark.parametrize("encode_auth_key, decode_auth_key", [
    (md5_key, None),
    (md5_key, md5_key._replace(data=b'x' * 16)),
    (md5_key, sha_key),
    (md5_key, des_key),
    (sha_key, None),
    (sha_key, sha_key._replace(data=b'x' * 20)),
    (sha_key, md5_key),
    (sha_key, des_key),
    ])
def test_auth_keys_dont_match(encode_auth_key, decode_auth_key):

    def on_auth_key(engine_id, user):
        return decode_auth_key

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                         id=100,
                         reportable=True,
                         auth=True,
                         priv=False,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_xyz',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=456),
                             data=[]))

    msg_bytes = encoder.encode(msg, auth_key=encode_auth_key)

    if decode_auth_key is None:
        error = 'auth key not available'

    elif decode_auth_key.type not in (key.KeyType.MD5, key.KeyType.SHA):
        error = 'invalid auth key type'

    else:
        error = 'authentication failed'

    with pytest.raises(Exception, match=error):
        encoder.decode(msg_bytes, auth_key_cb=on_auth_key)


@pytest.mark.parametrize("encode_priv_key, decode_priv_key", [
    (des_key, None),
    (des_key, des_key._replace(data=b'x' * 16)),
    (des_key, sha_key)
    ])
def test_priv_keys_dont_match(encode_priv_key, decode_priv_key):

    def on_auth_key(engine_id, user):
        return md5_key

    def on_priv_key(engine_id, user):
        return decode_priv_key

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                         id=100,
                         reportable=True,
                         auth=True,
                         priv=True,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_xyz',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=456),
                             data=[]))

    msg_bytes = encoder.encode(msg, auth_key=md5_key, priv_key=encode_priv_key)
    with pytest.raises(Exception):
        encoder.decode(
            msg_bytes, auth_key_cb=on_auth_key, priv_key_cb=on_priv_key)


@pytest.mark.parametrize("auth_key", [md5_key, sha_key])
def test_auth_change_in_the_middle(auth_key):

    def on_auth_key(engine_id, user):
        return auth_key

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                         id=100,
                         reportable=True,
                         auth=True,
                         priv=False,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_xyz',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=456),
                             data=[]))

    msg_json = encoder.v3.encode_msg(msg, auth_key=auth_key)
    msg_json['msgSecurityParameters'] = change_bytes(
        msg_json['msgSecurityParameters'])

    with pytest.raises(Exception, match='authentication failed'):
        encoder.v3.decode_msg(msg_json, auth_key_cb=on_auth_key)


def test_priv_change_in_the_middle():
    auth_key = md5_key
    priv_key = des_key

    def on_auth_key(engine_id, user):
        return auth_key

    def on_priv_key(engine_id, user):
        return priv_key

    msg = encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                         id=100,
                         reportable=True,
                         auth=True,
                         priv=True,
                         authorative_engine=encoder.v3.AuthorativeEngine(
                            id=b'engine_xyz',
                            boots=123,
                            time=456),
                         user='user_xyz',
                         context=common.Context(
                            engine_id=b'ctx_engine_id',
                            name='engine_name'),
                         pdu=encoder.v3.BasicPdu(
                             request_id=123,
                             error=common.Error(
                                 type=common.ErrorType.NO_ERROR,
                                 index=456),
                             data=[]))

    msg_json = encoder.v3.encode_msg(msg, auth_key=auth_key, priv_key=priv_key)
    data_type, pdu_bytes = msg_json['msgData']
    msg_json['msgData'] = (data_type, change_bytes(pdu_bytes))

    with pytest.raises(Exception):
        encoder.v3.decode_msg(
            msg_json, auth_key_cb=on_auth_key, priv_key_cb=on_priv_key)


@pytest.mark.parametrize("msg", [
    # bulk type, basic pdu
    encoder.v3.Msg(type=encoder.v3.MsgType.GET_BULK_REQUEST,
                   id=100,
                   reportable=True,
                   auth=False,
                   priv=False,
                   authorative_engine=encoder.v3.AuthorativeEngine(
                      id=b'engine_abc',
                      boots=123,
                      time=456),
                   user='user_xyz',
                   context=common.Context(
                      engine_id=b'ctx_engine_id',
                      name='engine_name'),
                   pdu=encoder.v3.BasicPdu(
                       request_id=123,
                       error=common.Error(
                           type=common.ErrorType.NO_ERROR,
                           index=456),
                       data=[])),
    # basic type, bulk pdu
    encoder.v3.Msg(type=encoder.v3.MsgType.GET_REQUEST,
                   id=100,
                   reportable=True,
                   auth=False,
                   priv=False,
                   authorative_engine=encoder.v3.AuthorativeEngine(
                      id=b'engine_xyz',
                      boots=123,
                      time=456),
                   user='user_xyz',
                   context=common.Context(
                      engine_id=b'ctx_engine_id',
                      name='engine_name'),
                   pdu=encoder.v3.BulkPdu(
                      request_id=123,
                      non_repeaters=100,
                      max_repetitions=200,
                      data=[]))
    ])
def test_encode_invalid_pdu(msg):
    with pytest.raises(ValueError):
        encoder.encode(msg)


@pytest.mark.parametrize("invalid_bytes", [b'xyz', b'some random bytes'])
def test_decode_invalid(invalid_bytes):
    with pytest.raises(Exception):
        encoder.v3.decode_msg(invalid_bytes)
