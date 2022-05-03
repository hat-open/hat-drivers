import enum
import typing

from hat import asn1

from hat.drivers.snmp import common


class MsgType(enum.Enum):
    GET_REQUEST = 'get-request'
    GET_NEXT_REQUEST = 'get-next-request'
    GET_RESPONSE = 'get-response'
    SET_REQUEST = 'set-request'
    TRAP = 'trap'


class BasicPdu(typing.NamedTuple):
    request_id: int
    error: common.Error
    data: typing.List[common.Data]


class TrapPdu(typing.NamedTuple):
    enterprise: common.ObjectIdentifier
    addr: typing.Tuple[int, int, int, int]
    cause: common.Cause
    timestamp: int
    data: typing.List[common.Data]


Pdu = typing.Union[BasicPdu, TrapPdu]


class Msg(typing.NamedTuple):
    type: MsgType
    community: str
    pdu: Pdu


def encode_msg(msg: Msg) -> asn1.Value:
    if ((msg.type == MsgType.TRAP and not isinstance(msg.pdu, TrapPdu)) or
            (msg.type != MsgType.TRAP and isinstance(msg.pdu, TrapPdu))):
        raise ValueError('unsupported message type / pdu')

    data = msg.type.value, _encode_pdu(msg.pdu)

    return {'version': common.Version.V1.value,
            'community': msg.community.encode('utf-8'),
            'data':  data}


def decode_msg(msg: asn1.Value) -> Msg:
    msg_type = MsgType(msg['data'][0])
    pdu = _decode_pdu(msg_type, msg['data'][1])

    return Msg(type=msg_type,
               community=_decode_str(msg['community']),
               pdu=pdu)


def _encode_pdu(pdu):
    if isinstance(pdu, BasicPdu):
        return {'request-id': pdu.request_id,
                'error-status': pdu.error.type.value,
                'error-index': pdu.error.index,
                'variable-bindings': [_encode_data(data)
                                      for data in pdu.data]}

    if isinstance(pdu, TrapPdu):
        return {'enterprise': pdu.enterprise,
                'agent-addr': ('internet', bytes(pdu.addr)),
                'generic-trap': pdu.cause.type.value,
                'specific-trap': pdu.cause.value,
                'time-stamp': pdu.timestamp,
                'variable-bindings': [_encode_data(data)
                                      for data in pdu.data]}

    raise ValueError('unsupported pdu')


def _decode_pdu(msg_type, pdu):
    if msg_type in {MsgType.GET_REQUEST,
                    MsgType.GET_NEXT_REQUEST,
                    MsgType.GET_RESPONSE,
                    MsgType.SET_REQUEST}:
        error = common.Error(type=common.ErrorType(pdu['error-status']),
                             index=pdu['error-index'])
        data = [_decode_data(data)
                for data in pdu['variable-bindings']]
        return BasicPdu(request_id=pdu['request-id'],
                        error=error,
                        data=data)

    if msg_type == MsgType.TRAP:
        cause = common.Cause(type=common.CauseType(pdu['generic-trap']),
                             value=pdu['specific-trap'])
        data = [_decode_data(data)
                for data in pdu['variable-bindings']]
        return TrapPdu(enterprise=pdu['enterprise'],
                       addr=tuple(pdu['agent-addr'][1]),
                       cause=cause,
                       timestamp=pdu['time-stamp'],
                       data=data)

    raise ValueError('unsupported message type')


def _encode_data(data):
    if data.type == common.DataType.INTEGER:
        value = ('simple', ('number', data.value))

    elif data.type == common.DataType.STRING:
        value = ('simple', ('string', data.value.encode('utf-8')))

    elif data.type == common.DataType.OBJECT_ID:
        value = ('simple', ('object', data.value))

    elif data.type == common.DataType.EMPTY:
        value = ('simple', ('empty', None))

    elif data.type == common.DataType.IP_ADDRESS:
        value = ('application-wide',
                 ('address', ('internet', bytes(data.value))))

    elif data.type == common.DataType.COUNTER:
        value = ('application-wide', ('counter', data.value))

    elif data.type == common.DataType.UNSIGNED:
        value = ('application-wide', ('gauge', data.value))

    elif data.type == common.DataType.TIME_TICKS:
        value = ('application-wide', ('ticks', data.value))

    elif data.type == common.DataType.ARBITRARY:
        value = ('application-wide', ('arbitrary', data.value))

    else:
        raise ValueError('unsupported data type')

    return {'name': data.name,
            'value': value}


def _decode_data(data):
    name = data['name']
    t1, (t2, value) = data['value']

    if t1 == 'simple':
        if t2 == 'number':
            return common.Data(type=common.DataType.INTEGER,
                               name=name,
                               value=value)

        elif t2 == 'string':
            return common.Data(type=common.DataType.STRING,
                               name=name,
                               value=_decode_str(value))

        elif t2 == 'object':
            return common.Data(type=common.DataType.OBJECT_ID,
                               name=name,
                               value=value)

        elif t2 == 'empty':
            return common.Data(type=common.DataType.EMPTY,
                               name=name,
                               value=None)

    elif t1 == 'application-wide':
        if t2 == 'address':
            return common.Data(type=common.DataType.IP_ADDRESS,
                               name=name,
                               value=tuple(value[1]))

        elif t2 == 'counter':
            return common.Data(type=common.DataType.COUNTER,
                               name=name,
                               value=value)

        elif t2 == 'gauge':
            return common.Data(type=common.DataType.UNSIGNED,
                               name=name,
                               value=value)

        elif t2 == 'ticks':
            return common.Data(type=common.DataType.TIME_TICKS,
                               name=name,
                               value=value)

        elif t2 == 'arbitrary':
            return common.Data(type=common.DataType.ARBITRARY,
                               name=name,
                               value=value)

    raise ValueError('unsupported type')


def _decode_str(x):
    return str(x, encoding='utf-8', errors='replace')
