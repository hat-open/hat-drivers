from collections.abc import Collection
import enum
import typing

from hat import asn1

from hat.drivers.snmp.encoder import common


class MsgType(enum.Enum):
    GET_REQUEST = 'get-request'
    GET_NEXT_REQUEST = 'get-next-request'
    GET_RESPONSE = 'get-response'
    SET_REQUEST = 'set-request'
    TRAP = 'trap'


class BasicPdu(typing.NamedTuple):
    request_id: int
    error: common.Error
    data: Collection[common.Data]


class TrapPdu(typing.NamedTuple):
    enterprise: asn1.ObjectIdentifier
    addr: tuple[int, int, int, int]
    cause: common.Cause
    timestamp: int
    data: Collection[common.Data]


Pdu: typing.TypeAlias = BasicPdu | TrapPdu


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
            'community': msg.community.encode(),
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
    if isinstance(data, common.IntegerData):
        value = ('simple', ('number', data.value))

    elif isinstance(data, common.StringData):
        value = ('simple', ('string', data.value))

    elif isinstance(data, common.ObjectIdData):
        value = ('simple', ('object', data.value))

    elif isinstance(data, common.EmptyData):
        value = ('simple', ('empty', None))

    elif isinstance(data, common.IpAddressData):
        value = ('application-wide',
                 ('address', ('internet', bytes(data.value))))

    elif isinstance(data, common.CounterData):
        value = ('application-wide', ('counter', data.value))

    elif isinstance(data, common.UnsignedData):
        value = ('application-wide', ('gauge', data.value))

    elif isinstance(data, common.TimeTicksData):
        value = ('application-wide', ('ticks', data.value))

    elif isinstance(data, common.ArbitraryData):
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
            return common.IntegerData(name=name,
                                      value=value)

        elif t2 == 'string':
            return common.StringData(name=name,
                                     value=value)

        elif t2 == 'object':
            return common.ObjectIdData(name=name,
                                       value=value)

        elif t2 == 'empty':
            return common.EmptyData(name=name)

    elif t1 == 'application-wide':
        if t2 == 'address':
            return common.IpAddressData(name=name,
                                        value=tuple(value[1]))

        elif t2 == 'counter':
            return common.CounterData(name=name,
                                      value=value)

        elif t2 == 'gauge':
            return common.UnsignedData(name=name,
                                       value=value)

        elif t2 == 'ticks':
            return common.TimeTicksData(name=name,
                                        value=value)

        elif t2 == 'arbitrary':
            return common.ArbitraryData(name=name,
                                        value=value)

    raise ValueError('unsupported type')


def _decode_str(x):
    return str(x, encoding='utf-8', errors='replace')
