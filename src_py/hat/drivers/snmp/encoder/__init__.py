import typing

from hat import util
import hat.asn1.ber
import hat.asn1.common

from hat.drivers.snmp import key
from hat.drivers.snmp.encoder import common
from hat.drivers.snmp.encoder import v1
from hat.drivers.snmp.encoder import v2c
from hat.drivers.snmp.encoder import v3


__all__ = ['v1',
           'v2c',
           'v3',
           'Msg',
           'encode',
           'decode']


Msg: typing.TypeAlias = v1.Msg | v2c.Msg | v3.Msg


def encode(msg: Msg,
           auth_key: key.Key | None = None,
           priv_key: key.Key | None = None
           ) -> util.Bytes:
    if isinstance(msg, v1.Msg):
        data = v1.encode_msg(msg)
        return common.encoder.encode('RFC1157-SNMP', 'Message', data)

    elif isinstance(msg, v2c.Msg):
        data = v2c.encode_msg(msg)
        return common.encoder.encode('COMMUNITY-BASED-SNMPv2', 'Message', data)

    elif isinstance(msg, v3.Msg):
        data = v3.encode_msg(msg, auth_key, priv_key)
        return common.encoder.encode('SNMPv3MessageSyntax', 'SNMPv3Message',
                                     data)

    raise ValueError('unsupported message')


def decode(msg_bytes: util.Bytes,
           auth_key_cb: key.KeyCb | None = None,
           priv_key_cb: key.KeyCb | None = None
           ) -> Msg:
    entity, _ = common.encoder.decode_entity(msg_bytes)
    version = _get_version(entity)

    if version == common.Version.V1:
        msg = common.encoder.decode_value('RFC1157-SNMP', 'Message', entity)
        return v1.decode_msg(msg)

    if version == common.Version.V2C:
        msg = common.encoder.decode_value('COMMUNITY-BASED-SNMPv2', 'Message',
                                          entity)
        return v2c.decode_msg(msg)

    if version == common.Version.V3:
        msg = common.encoder.decode_value('SNMPv3MessageSyntax',
                                          'SNMPv3Message', entity)
        return v3.decode_msg(msg, auth_key_cb, priv_key_cb)

    raise ValueError('unsupported version')


def _get_version(entity):
    universal_class_type = hat.asn1.common.ClassType.UNIVERSAL
    constructed_content_cls = hat.asn1.ber.ConstructedContent

    if (entity.class_type != universal_class_type or
            entity.tag_number != 16 or
            not isinstance(entity.content, constructed_content_cls) or
            not entity.content.elements or
            entity.content.elements[0].class_type != universal_class_type or
            entity.content.elements[0].tag_number != 2):
        raise ValueError('unsupported entity')

    version = common.encoder.decode_value('SNMP', 'Version',
                                          entity.content.elements[0])

    return common.Version(version)
