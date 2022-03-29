from pathlib import Path

from hat import asn1
from hat.drivers.snmp import common
import hat.asn1.common
import hat.asn1.ber


_repo = asn1.Repository.from_json(Path(__file__).parent / 'asn1_repo.json')
_encoder = asn1.Encoder(asn1.Encoding.BER, _repo)


def encode(msg: common.Msg) -> common.Bytes:
    """Encode message"""
    if isinstance(msg, common.MsgV1):
        data = _encode_msg_v1(msg)
        name = 'MessageV1'

    elif isinstance(msg, common.MsgV2C):
        name = 'MessageV2C'
        data = _encode_msg_v2c(msg)

    elif isinstance(msg, common.MsgV3):
        name = 'MessageV3'
        data = _encode_msg_v3(msg)

    else:
        raise ValueError('unsupported message')

    return _encoder.encode('SNMP', name, data)


def decode(msg_bytes: common.Bytes) -> common.Msg:
    entity, _ = _encoder.decode_entity(msg_bytes)
    version = _get_version(entity)
    name = f'Message{version.name}'
    msg = _encoder.decode_value('SNMP', name, entity)

    if version == common.Version.V1:
        return _decode_msg_v1(msg)

    if version == common.Version.V2C:
        return _decode_msg_v2c(msg)

    if version == common.Version.V3:
        return _decode_msg_v3(msg)

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

    return common.Version(entity.content.elements[0].value)


def _encode_msg_v1(msg):
    data = msg.type.value, _encode_pdu(common.Version.V1, msg.type, msg.pdu)

    return {'version': common.Version.V1.value,
            'community': msg.community.encode('utf-8'),
            'data':  data}


def _decode_msg_v1(msg):
    msg_type = common.MsgType(msg['data'][0])
    pdu = _decode_pdu(common.Version.V1, msg_type, msg['data'][1])

    return common.MsgV1(type=msg_type,
                        community=msg['community'],
                        pdu=pdu)


def _encode_msg_v2c(msg):
    data = msg.type.value, _encode_pdu(common.Version.V2C, msg.type, msg.pdu)

    return {'version': common.Version.V2C.value,
            'community': msg.community.encode('utf-8'),
            'data':  data}


def _decode_msg_v2c(msg):
    msg_type = common.MsgType(msg['data'][0])
    pdu = _decode_pdu(common.Version.V2C, msg_type, msg['data'][1])

    return common.MsgV2C(type=msg_type,
                         community=msg['community'],
                         pdu=pdu)


def _encode_msg_v3(msg):
    data = msg.type.value, _encode_pdu(common.Version.V3, msg.type, msg.pdu)

    return {'version': common.Version.V3.value,
            'msgGlobalData': {'msgID': msg.id,
                              'msgMaxSize': 2147483647,
                              'msgFlags': bytes([4 if msg.reportable else 0]),
                              'msgSecurityModel': 1},
            'msgSecurityParameters': b'',
            'msgData': ('plaintext', {
                'contextEngineID': msg.context.engine_id.encode('utf-8'),
                'contextName': msg.context.name.encode('utf-8'),
                'data': data})}


def _decode_msg_v3(msg):
    msg_type = common.MsgType(msg['msgData'][1]['data'][0])
    msg_id = msg['msgGlobalData']['msgID']
    reportable = bool(msg['msgGlobalData']['msgFlags'][0] & 4)
    context_engine_id = msg['msgData'][1]['contextEngineID'].decode('utf-8')
    context_name = msg['msgData'][1]['contextName'].decode('utf-8')
    pdu = _decode_pdu(common.Version.V3, msg_type,
                      msg['msgData'][1]['data'][1])

    return common.MsgV3(type=msg_type,
                        id=msg_id,
                        reportable=reportable,
                        context=common.Context(engine_id=context_engine_id,
                                               name=context_name),
                        pdu=pdu)


def _encode_pdu(version, msg_type, pdu):
    if msg_type == common.MsgType.GET_BULK_REQUEST:
        return _encode_bulk_pdu(version, pdu)

    if msg_type == common.MsgType.TRAP:
        return _encode_trap_pdu(version, pdu)

    if msg_type in {common.MsgType.GET_REQUEST,
                    common.MsgType.GET_NEXT_REQUEST,
                    common.MsgType.RESPONSE,
                    common.MsgType.SET_REQUEST,
                    common.MsgType.INFORM_REQUEST,
                    common.MsgType.SNMPV2_TRAP,
                    common.MsgType.REPORT}:
        return _encode_basic_pdu(version, pdu)

    raise ValueError('unsupported message type')


def _decode_pdu(version, msg_type, pdu):
    if msg_type == common.MsgType.GET_BULK_REQUEST:
        return _decode_bulk_pdu(version, pdu)

    if msg_type == common.MsgType.TRAP:
        return _decode_trap_pdu(version, pdu)

    if msg_type in {common.MsgType.GET_REQUEST,
                    common.MsgType.GET_NEXT_REQUEST,
                    common.MsgType.RESPONSE,
                    common.MsgType.SET_REQUEST,
                    common.MsgType.INFORM_REQUEST,
                    common.MsgType.SNMPV2_TRAP,
                    common.MsgType.REPORT}:
        return _decode_basic_pdu(version, pdu)

    raise ValueError('unsupported message type')


def _encode_basic_pdu(version, pdu):
    return {'request-id': pdu.request_id,
            'error-status': pdu.error.type.value,
            'error-index': pdu.error.index,
            'variable-bindings': [_encode_data(version, data)
                                  for data in pdu.data]}


def _decode_basic_pdu(version, pdu):
    error = common.Error(type=common.ErrorType(pdu['error-status']),
                         index=pdu['error-index'])
    data = [_decode_data(version, data)
            for data in pdu['variable-bindings']]

    return common.BasicPdu(request_id=pdu['request-id'],
                           error=error,
                           data=data)


def _encode_bulk_pdu(version, pdu):
    return {'request-id': pdu.request_id,
            'non-repeaters': pdu.non_repeaters,
            'max-repetitions': pdu.max_repetitions,
            'variable-bindings': [_encode_data(version, data)
                                  for data in pdu.data]}


def _decode_bulk_pdu(version, pdu):
    data = [_decode_data(version, data)
            for data in pdu['variable-bindings']]

    return common.BulkPdu(request_id=pdu['request-id'],
                          non_repeaters=pdu['non-repeaters'],
                          max_repetitions=pdu['max-repetitions'],
                          data=data)


def _encode_trap_pdu(version, pdu):
    return {'enterprise': pdu.enterprise,
            'agent-addr': pdu.addr,
            'generic-trap': pdu.cause.type.value,
            'specific-trap': pdu.cause.value,
            'time-stamp': pdu.timestamp,
            'variable-bindings': [_encode_data(version, data)
                                  for data in pdu.data]}


def _decode_trap_pdu(version, pdu):
    cause = common.Cause(type=common.CauseType(pdu['generic-trap']),
                         value=pdu['specific-trap'])
    data = [_decode_data(version, data)
            for data in pdu['variable-bindings']]

    return common.TrapPdu(enterprise=pdu['enterprise'],
                          addr=tuple(pdu['agent-addr']),
                          cause=cause,
                          timestamp=pdu['time-stamp'],
                          data=data)


def _encode_data(version, data):
    if data.type == common.DataType.INTEGER:
        data_type = 'value'
        value = ('simple', ('integer', data.value))

    elif data.type == common.DataType.UNSIGNED:
        data_type = 'value'
        value = ('application-wide', ('unsigned', data.value))

    elif data.type == common.DataType.COUNTER:
        data_type = 'value'
        value = ('application-wide', ('counter', data.value))

    elif data.type == common.DataType.BIG_COUNTER:
        data_type = 'value'
        value = ('application-wide', ('bigCounter', data.value))

    elif data.type == common.DataType.STRING:
        data_type = 'value'
        value = ('simple', ('string', data.value.encode('utf-8')))

    elif data.type == common.DataType.OBJECT_ID:
        data_type = 'value'
        value = ('simple', ('objectId', data.value))

    elif data.type == common.DataType.IP_ADDRESS:
        data_type = 'value'
        value = ('application-wide', ('ipAddress', bytes(data.value)))

    elif data.type == common.DataType.TIME_TICKS:
        data_type = 'value'
        value = ('application-wide', ('timeTicks', data.value))

    elif data.type == common.DataType.ARBITRARY:
        data_type = 'value'
        value = ('application-wide', ('arbitrary', data.value))

    elif data.type == common.DataType.EMPTY:
        data_type = 'value'
        value = ('simple', ('empty', None))

    elif data.type == common.DataType.UNSPECIFIED:
        data_type = 'unSpecified'
        value = None

    elif data.type == common.DataType.NO_SUCH_OBJECT:
        data_type = 'noSuchObject'
        value = None

    elif data.type == common.DataType.NO_SUCH_INSTANCE:
        data_type = 'noSuchInstance'
        value = None

    elif data.type == common.DataType.END_OF_MIB_VIEW:
        data_type = 'endOfMibView'
        value = None

    else:
        raise ValueError('unsupported data type')

    return {'name': data.name,
            'data': (data_type, value)}


def _decode_data(version, data):
    name = tuple(data['name'])
    t1, v1 = data['data']

    if t1 == 'value':
        t2, (t3, v2) = v1

        if t2 == 'simple':
            if t3 == 'integer':
                return common.Data(type=common.DataType.INTEGER,
                                   name=name,
                                   value=v2)

            elif t3 == 'string':
                return common.Data(type=common.DataType.STRING,
                                   name=name,
                                   value=v2.decode('utf-8'))

            elif t3 == 'objectId':
                return common.Data(type=common.DataType.OBJECT_ID,
                                   name=name,
                                   value=tuple(v2))

            elif t3 == 'empty':
                return common.Data(type=common.DataType.EMPTY,
                                   name=name,
                                   value=None)

        elif t2 == 'application-wide':
            if t3 == 'ipAddress':
                return common.Data(type=common.DataType.IP_ADDRESS,
                                   name=name,
                                   value=tuple(v2))

            elif t3 == 'counter':
                return common.Data(type=common.DataType.COUNTER,
                                   name=name,
                                   value=v2)

            elif t3 == 'unsigned':
                return common.Data(type=common.DataType.UNSIGNED,
                                   name=name,
                                   value=v2)

            elif t3 == 'timeTicks':
                return common.Data(type=common.DataType.TIME_TICKS,
                                   name=name,
                                   value=v2)

            elif t3 == 'arbitrary':
                return common.Data(type=common.DataType.ARBITRARY,
                                   name=name,
                                   value=v2)

            elif t3 == 'bigCounter':
                return common.Data(type=common.DataType.BIG_COUNTER,
                                   name=name,
                                   value=v2)

    elif t1 == 'unSpecified':
        return common.Data(type=common.DataType.UNSPECIFIED,
                           name=name,
                           value=None)

    elif t1 == 'noSuchObject':
        return common.Data(type=common.DataType.NO_SUCH_OBJECT,
                           name=name,
                           value=None)

    elif t1 == 'noSuchInstance':
        return common.Data(type=common.DataType.NO_SUCH_INSTANCE,
                           name=name,
                           value=None)

    elif t1 == 'endOfMibView':
        return common.Data(type=common.DataType.END_OF_MIB_VIEW,
                           name=name,
                           value=None)

    raise ValueError('unsupported type')
