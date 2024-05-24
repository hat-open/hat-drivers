import hmac
import secrets
import typing

from hat import asn1

from hat.drivers.snmp import key
from hat.drivers.snmp.encoder import common
from hat.drivers.snmp.encoder import openssl
from hat.drivers.snmp.encoder import v2c


MsgType = v2c.MsgType
BasicPdu = v2c.BasicPdu
BulkPdu = v2c.BulkPdu
Pdu = v2c.Pdu


class AuthorativeEngine(typing.NamedTuple):
    id: str
    boots: int
    time: int


class Msg(typing.NamedTuple):
    type: MsgType
    id: int
    reportable: bool
    auth: bool
    priv: bool
    authorative_engine: AuthorativeEngine
    user: common.UserName
    context: common.Context
    pdu: Pdu


def encode_msg(msg: Msg,
               auth_key: key.Key | None = None,
               priv_key: key.Key | None = None
               ) -> asn1.Value:
    if ((msg.type == MsgType.GET_BULK_REQUEST and not isinstance(msg.pdu, BulkPdu)) or  # NOQA
            (msg.type != MsgType.GET_BULK_REQUEST and isinstance(msg.pdu, BulkPdu))):  # NOQA
        raise ValueError('unsupported message type / pdu')

    if msg.auth and auth_key is None:
        raise Exception('authentication key not provided')

    if msg.priv and priv_key is None:
        raise Exception('privacy key not provided')

    if msg.priv and not msg.auth:
        raise Exception('invalid auth/priv combination')

    msg_flags = bytes([(4 if msg.reportable else 0) |
                       (2 if msg.priv else 0) |
                       (1 if msg.auth else 0)])

    data = msg.type.value, v2c.encode_pdu(msg.pdu)

    pdu = {'contextEngineID': msg.context.engine_id.encode(),
           'contextName': msg.context.name.encode(),
           'data': data}

    if msg.priv:
        pdu_bytes = common.encoder.encode(
            'SNMPv3MessageSyntax', 'ScopedPDU', pdu)

        encrypted_pdu, priv_params_bytes = _encrypt_pdu(priv_key, pdu_bytes)
        msg_data = 'encryptedPDU', encrypted_pdu

    else:
        priv_params_bytes = b''
        msg_data = 'plaintext', pdu

    auth_params_bytes = b'\x00' * 12 if msg.auth else b''

    security_params = {
        'msgAuthoritativeEngineID': msg.authorative_engine.id.encode(),
        'msgAuthoritativeEngineBoots': msg.authorative_engine.boots,
        'msgAuthoritativeEngineTime': msg.authorative_engine.time,
        'msgUserName': msg.user.encode(),
        'msgAuthenticationParameters': auth_params_bytes,
        'msgPrivacyParameters': priv_params_bytes}

    security_params_bytes = common.encoder.encode(
        'USMSecurityParametersSyntax', 'UsmSecurityParameters',
        security_params)

    msg_value = {'msgVersion': common.Version.V3.value,
                 'msgGlobalData': {'msgID': msg.id,
                                   'msgMaxSize': 2147483647,
                                   'msgFlags': bytes([msg_flags]),
                                   'msgSecurityModel': 3},
                 'msgSecurityParameters': security_params_bytes,
                 'msgData': msg_data}

    if msg.auth:
        msg_bytes = common.encoder.encode(
            'SNMPv3MessageSyntax', 'SNMPv3Message', msg_value)

        auth_params_bytes = _gen_auth_params_bytes(auth_key, msg_bytes)

        security_params['msgAuthenticationParameters'] = auth_params_bytes

        security_params_bytes = common.encoder.encode(
            'USMSecurityParametersSyntax', 'UsmSecurityParameters',
            security_params)

        msg_value['msgSecurityParameters'] = security_params_bytes

    return msg_value


def decode_msg(msg: asn1.Value,
               auth_key_cb: key.KeyCb | None = None,
               priv_key_cb: key.KeyCb | None = None
               ) -> Msg:
    raise NotImplementedError()

    # msg_type = MsgType(msg['msgData'][1]['data'][0])
    # msg_id = msg['msgGlobalData']['msgID']
    # reportable = bool(msg['msgGlobalData']['msgFlags'][0] & 4)
    # context_engine_id = _decode_str(msg['msgData'][1]['contextEngineID'])
    # context_name = _decode_str(msg['msgData'][1]['contextName'])
    # context = common.Context(engine_id=context_engine_id,
    #                          name=context_name)

    # pdu = v2c.decode_pdu(msg_type, msg['msgData'][1]['data'][1])

    # return Msg(type=msg_type,
    #            id=msg_id,
    #            reportable=reportable,
    #            context=context,
    #            pdu=pdu)


def _encrypt_pdu(priv_key, pdu_bytes):
    if priv_key.key_type != key.KeyType.DES:
        raise Exception('invalid priv key type')

    if len(priv_key.data) != 16:
        raise Exception('invalid key length')

    des_key = priv_key.data[:8]
    pre_iv = priv_key.data[8:]

    # TODO use boot counter as first 4 bytes of salt
    salt = secrets.token_bytes(8)

    iv = bytes(x ^ y for x, y in zip(pre_iv, salt))

    encrypted_pdu = openssl.des_encrypt(des_key=des_key,
                                        data=pdu_bytes,
                                        iv=iv)

    return encrypted_pdu, salt


def _gen_auth_params_bytes(auth_key, msg_bytes):
    if auth_key.key_type == key.KeyType.MD5:
        return _gen_md5_auth_params_bytes(auth_key, msg_bytes)

    if auth_key.key_type == key.KeyType.SHA:
        return _gen_sha_auth_params_bytes(auth_key, msg_bytes)

    raise Exception('invalid auth key type')


def _gen_md5_auth_params_bytes(auth_key, msg_bytes):
    if len(auth_key.data) != 16:
        raise Exception('invalid key length')

    digest = hmac.digest(auth_key.data, msg_bytes, 'md5')
    return digest[:12]


def _gen_sha_auth_params_bytes(auth_key, msg_bytes):
    if len(auth_key.data) != 20:
        raise Exception('invalid key length')

    digest = hmac.digest(auth_key.data, msg_bytes, 'sha1')
    return digest[:12]


def _decode_str(x):
    return str(x, encoding='utf-8', errors='replace')
