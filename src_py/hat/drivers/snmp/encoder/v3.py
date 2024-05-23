import typing

from hat import asn1

from hat.drivers.snmp import common
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
               auth_key: common.Key | None = None,
               priv_key: common.Key | None = None
               ) -> asn1.Value:
    if ((msg.type == MsgType.GET_BULK_REQUEST and not isinstance(msg.pdu, BulkPdu)) or  # NOQA
            (msg.type != MsgType.GET_BULK_REQUEST and isinstance(msg.pdu, BulkPdu))):  # NOQA
        raise ValueError('unsupported message type / pdu')

    raise NotImplementedError()

    # data = msg.type.value, v2c.encode_pdu(msg.pdu)

    # return {'msgVersion': common.Version.V3.value,
    #         'msgGlobalData': {'msgID': msg.id,
    #                           'msgMaxSize': 2147483647,
    #                           'msgFlags': bytes([4 if msg.reportable else 0]),
    #                           'msgSecurityModel': 3},
    #         'msgSecurityParameters': b'',
    #         'msgData': ('plaintext', {
    #             'contextEngineID': msg.context.engine_id.encode(),
    #             'contextName': msg.context.name.encode(),
    #             'data': data})}


def decode_msg(msg: asn1.Value,
               auth_key_cb: common.KeyCb | None = None,
               priv_key_cb: common.KeyCb | None = None
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


def _decode_str(x):
    return str(x, encoding='utf-8', errors='replace')
