import enum
import typing

from hat import asn1

from hat.drivers.snmp import common
from hat.drivers.snmp.encoder import v1


class MsgType(enum.Enum):
    GET_REQUEST = 'get-request'
    GET_NEXT_REQUEST = 'get-next-request'
    GET_BULK_REQUEST = 'get-bulk-request'
    RESPONSE = 'response'
    SET_REQUEST = 'set-request'
    INFORM_REQUEST = 'inform-request'
    SNMPV2_TRAP = 'snmpV2-trap'
    REPORT = 'report'


BasicPdu = v1.BasicPdu


class BulkPdu(typing.NamedTuple):
    request_id: int
    non_repeaters: int
    max_repetitions: int
    data: typing.List[common.Data]


Pdu = typing.Union[BasicPdu, BulkPdu]


class Msg(typing.NamedTuple):
    type: MsgType
    community: str
    pdu: Pdu


def encode_msg(msg: Msg) -> asn1.Value:
    if ((msg.type == MsgType.GET_BULK_REQUEST and not isinstance(msg.pdu, BulkPdu)) or  # NOQA
            (msg.type != MsgType.GET_BULK_REQUEST and isinstance(msg.pdu, BulkPdu))):  # NOQA
        raise ValueError('unsupported message type / pdu')

    data = msg.type.value, encode_pdu(msg.pdu)

    return {'version': common.Version.V2C.value,
            'community': msg.community.encode('utf-8'),
            'data':  data}


def decode_msg(msg: asn1.Value) -> Msg:
    msg_type = MsgType(msg['data'][0])
    pdu = decode_pdu(msg_type, msg['data'][1])

    return Msg(type=msg_type,
               community=_decode_str(msg['community']),
               pdu=pdu)


def encode_pdu(pdu: Pdu) -> asn1.Value:
    if isinstance(pdu, BasicPdu):
        return {'request-id': pdu.request_id,
                'error-status': pdu.error.type.value,
                'error-index': pdu.error.index,
                'variable-bindings': [_encode_data(data)
                                      for data in pdu.data]}

    if isinstance(pdu, BulkPdu):
        return {'request-id': pdu.request_id,
                'non-repeaters': pdu.non_repeaters,
                'max-repetitions': pdu.max_repetitions,
                'variable-bindings': [_encode_data(data)
                                      for data in pdu.data]}

    raise ValueError('unsupported pdu')


def decode_pdu(msg_type: MsgType, pdu: asn1.Value) -> Pdu:
    if msg_type in {MsgType.GET_REQUEST,
                    MsgType.GET_NEXT_REQUEST,
                    MsgType.RESPONSE,
                    MsgType.SET_REQUEST,
                    MsgType.INFORM_REQUEST,
                    MsgType.SNMPV2_TRAP,
                    MsgType.REPORT}:
        error = common.Error(type=common.ErrorType(pdu['error-status']),
                             index=pdu['error-index'])
        data = [_decode_data(data)
                for data in pdu['variable-bindings']]
        return BasicPdu(request_id=pdu['request-id'],
                        error=error,
                        data=data)

    if msg_type == MsgType.GET_BULK_REQUEST:
        data = [_decode_data(data)
                for data in pdu['variable-bindings']]
        return BulkPdu(request_id=pdu['request-id'],
                       non_repeaters=pdu['non-repeaters'],
                       max_repetitions=pdu['max-repetitions'],
                       data=data)

    raise ValueError('unsupported message type')


def _encode_data(data):
    if data.type == common.DataType.INTEGER:
        data_type = 'value'
        value = ('simple', ('integer-value', data.value))

    elif data.type == common.DataType.STRING:
        data_type = 'value'
        value = ('simple', ('string-value', data.value.encode('utf-8')))

    elif data.type == common.DataType.OBJECT_ID:
        data_type = 'value'
        value = ('simple', ('objectID-value', data.value))

    elif data.type == common.DataType.IP_ADDRESS:
        data_type = 'value'
        value = ('application-wide', ('ipAddress-value', bytes(data.value)))

    elif data.type == common.DataType.COUNTER:
        data_type = 'value'
        value = ('application-wide', ('counter-value', data.value))

    elif data.type == common.DataType.TIME_TICKS:
        data_type = 'value'
        value = ('application-wide', ('timeticks-value', data.value))

    elif data.type == common.DataType.ARBITRARY:
        data_type = 'value'
        value = ('application-wide', ('arbitrary-value', data.value))

    elif data.type == common.DataType.BIG_COUNTER:
        data_type = 'value'
        value = ('application-wide', ('big-counter-value', data.value))

    elif data.type == common.DataType.UNSIGNED:
        data_type = 'value'
        value = ('application-wide', ('unsigned-integer-value', data.value))

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


def _decode_data(data):
    name = data['name']
    t1, v1 = data['data']

    if t1 == 'value':
        t2, (t3, v2) = v1

        if t2 == 'simple':
            if t3 == 'integer-value':
                return common.Data(type=common.DataType.INTEGER,
                                   name=name,
                                   value=v2)

            elif t3 == 'string-value':
                return common.Data(type=common.DataType.STRING,
                                   name=name,
                                   value=_decode_str(v2))

            elif t3 == 'objectID-value':
                return common.Data(type=common.DataType.OBJECT_ID,
                                   name=name,
                                   value=v2)

        elif t2 == 'application-wide':
            if t3 == 'ipAddress-value':
                return common.Data(type=common.DataType.IP_ADDRESS,
                                   name=name,
                                   value=tuple(v2))

            elif t3 == 'counter-value':
                return common.Data(type=common.DataType.COUNTER,
                                   name=name,
                                   value=v2)

            elif t3 == 'timeticks-value':
                return common.Data(type=common.DataType.TIME_TICKS,
                                   name=name,
                                   value=v2)

            elif t3 == 'arbitrary-value':
                return common.Data(type=common.DataType.ARBITRARY,
                                   name=name,
                                   value=v2)

            elif t3 == 'big-counter-value':
                return common.Data(type=common.DataType.BIG_COUNTER,
                                   name=name,
                                   value=v2)

            elif t3 == 'unsigned-integer-value':
                return common.Data(type=common.DataType.UNSIGNED,
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


def _decode_str(x):
    return str(x, encoding='utf-8', errors='replace')
