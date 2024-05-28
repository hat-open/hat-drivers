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
    id: common.EngineId
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

    pdu = {'contextEngineID': msg.context.engine_id,
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
        'msgAuthoritativeEngineID': msg.authorative_engine.id,
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
                                   'msgFlags': msg_flags,
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
    if msg['msgVersion'] != common.Version.V3.value:
        raise Exception('invalid msg version')

    if msg['msgGlobalData']['msgSecurityModel'] != 3:
        raise Exception('unsupported security model')

    msg_id = msg['msgGlobalData']['msgID']
    msg_flags = msg['msgGlobalData']['msgFlags']

    reportable = bool(msg_flags[0] & 4)
    auth = bool(msg_flags[0] & 1)
    priv = bool(msg_flags[0] & 2)

    security_params, _ = common.encoder.decode(
        'USMSecurityParametersSyntax', 'UsmSecurityParameters',
        msg['msgSecurityParameters'])

    authorative_engine = AuthorativeEngine(
        id=security_params['msgAuthoritativeEngineID'],
        boots=security_params['msgAuthoritativeEngineBoots'],
        time=security_params['msgAuthoritativeEngineTime'])

    user = _decode_str(security_params['msgUserName'])

    if auth:
        if auth_key_cb is None:
            raise Exception('auth not enabled')

        auth_key = auth_key_cb(authorative_engine.id, user)
        if auth_key is None:
            raise Exception('auth key not available')

        auth_params_bytes = security_params['msgAuthenticationParameters']

        security_params = {**security_params,
                           'msgAuthenticationParameters': b'\x00' * 12}
        security_params_bytes = common.encoder.encode(
            'USMSecurityParametersSyntax', 'UsmSecurityParameters',
            security_params)

        msg = {**msg,
               'msgSecurityParameters': security_params_bytes}
        msg_bytes = common.encoder.encode(
            'SNMPv3MessageSyntax', 'SNMPv3Message', msg)

        generated_auth_params_bytes = _gen_auth_params_bytes(auth_key,
                                                             msg_bytes)

        if auth_params_bytes != generated_auth_params_bytes:
            raise Exception('authentication failed')

    if priv:
        if priv_key_cb is None:
            raise Exception('priv not enabled')

        priv_key = priv_key_cb(authorative_engine.id, user)
        if priv_key is None:
            raise Exception('priv key not available')

        if msg['msgData'][0] != 'encryptedPDU':
            raise Exception('invalid pdu encoding')

        priv_params_bytes = security_params['msgPrivacyParameters']

        pdu_bytes = _decrypt_pdu(priv_key, priv_params_bytes,
                                 msg['msgData'][1])

        pdu, _ = common.encoder.decode(
            'SNMPv3MessageSyntax', 'ScopedPDU', pdu_bytes)

    else:
        if msg['msgData'][0] != 'plaintext':
            raise Exception('invalid pdu encoding')

        pdu = msg['msgData'][1]

    msg_type = MsgType(pdu['data'][0])

    context = common.Context(engine_id=pdu['contextEngineID'],
                             name=_decode_str(pdu['contextName']))

    msg_pdu = v2c.decode_pdu(msg_type, pdu['data'][1])

    return Msg(type=msg_type,
               id=msg_id,
               reportable=reportable,
               auth=auth,
               priv=priv,
               authorative_engine=authorative_engine,
               user=user,
               context=context,
               pdu=msg_pdu)


def _encrypt_pdu(priv_key, pdu_bytes):
    if priv_key.type != key.KeyType.DES:
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


def _decrypt_pdu(priv_key, salt, pdu_bytes):
    if priv_key.type != key.KeyType.DES:
        raise Exception('invalid priv key type')

    if len(priv_key.data) != 16:
        raise Exception('invalid key length')

    if len(salt) != 8:
        raise Exception('invalid salt length')

    des_key = priv_key.data[:8]
    pre_iv = priv_key.data[8:]

    iv = bytes(x ^ y for x, y in zip(pre_iv, salt))

    decrypted_pdu = openssl.des_decrypt(des_key=des_key,
                                        data=pdu_bytes,
                                        iv=iv)

    return decrypted_pdu


def _gen_auth_params_bytes(auth_key, msg_bytes):
    if auth_key.type == key.KeyType.MD5:
        return _gen_md5_auth_params_bytes(auth_key, msg_bytes)

    if auth_key.type == key.KeyType.SHA:
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
