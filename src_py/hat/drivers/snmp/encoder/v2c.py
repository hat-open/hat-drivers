from collections.abc import Collection
import enum
import typing

from hat import asn1

from hat.drivers.snmp.encoder import common


class MsgType(enum.Enum):
    GET_REQUEST = 'get-request'
    GET_NEXT_REQUEST = 'get-next-request'
    GET_BULK_REQUEST = 'get-bulk-request'
    RESPONSE = 'response'
    SET_REQUEST = 'set-request'
    INFORM_REQUEST = 'inform-request'
    SNMPV2_TRAP = 'snmpV2-trap'
    REPORT = 'report'


class BasicPdu(typing.NamedTuple):
    request_id: int
    error: common.Error
    data: Collection[common.Data]


class BulkPdu(typing.NamedTuple):
    request_id: int
    non_repeaters: int
    max_repetitions: int
    data: Collection[common.Data]


Pdu: typing.TypeAlias = BasicPdu | BulkPdu


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
            'community': msg.community.encode(),
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
    if isinstance(data, common.IntegerData):
        data_type = 'value'
        value = ('simple', ('integer-value', data.value))

    elif isinstance(data, common.StringData):
        data_type = 'value'
        value = ('simple', ('string-value', data.value))

    elif isinstance(data, common.ObjectIdData):
        data_type = 'value'
        value = ('simple', ('objectID-value', data.value))

    elif isinstance(data, common.IpAddressData):
        data_type = 'value'
        value = ('application-wide', ('ipAddress-value', bytes(data.value)))

    elif isinstance(data, common.CounterData):
        data_type = 'value'
        value = ('application-wide', ('counter-value', data.value))

    elif isinstance(data, common.TimeTicksData):
        data_type = 'value'
        value = ('application-wide', ('timeticks-value', data.value))

    elif isinstance(data, common.ArbitraryData):
        data_type = 'value'
        value = ('application-wide', ('arbitrary-value', data.value))

    elif isinstance(data, common.BigCounterData):
        data_type = 'value'
        value = ('application-wide', ('big-counter-value', data.value))

    elif isinstance(data, common.UnsignedData):
        data_type = 'value'
        value = ('application-wide', ('unsigned-integer-value', data.value))

    elif isinstance(data, common.UnspecifiedData):
        data_type = 'unSpecified'
        value = None

    elif isinstance(data, common.NoSuchObjectData):
        data_type = 'noSuchObject'
        value = None

    elif isinstance(data, common.NoSuchInstanceData):
        data_type = 'noSuchInstance'
        value = None

    elif isinstance(data, common.EndOfMibViewData):
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
                return common.IntegerData(name=name,
                                          value=v2)

            elif t3 == 'string-value':
                return common.StringData(name=name,
                                         value=v2)

            elif t3 == 'objectID-value':
                return common.ObjectIdData(name=name,
                                           value=v2)

        elif t2 == 'application-wide':
            if t3 == 'ipAddress-value':
                return common.IpAddressData(name=name,
                                            value=tuple(v2))

            elif t3 == 'counter-value':
                return common.CounterData(name=name,
                                          value=v2)

            elif t3 == 'timeticks-value':
                return common.TimeTicksData(name=name,
                                            value=v2)

            elif t3 == 'arbitrary-value':
                return common.ArbitraryData(name=name,
                                            value=v2)

            elif t3 == 'big-counter-value':
                return common.BigCounterData(name=name,
                                             value=v2)

            elif t3 == 'unsigned-integer-value':
                return common.UnsignedData(name=name,
                                           value=v2)

    elif t1 == 'unSpecified':
        return common.UnspecifiedData(name=name)

    elif t1 == 'noSuchObject':
        return common.NoSuchObjectData(name=name)

    elif t1 == 'noSuchInstance':
        return common.NoSuchInstanceData(name=name)

    elif t1 == 'endOfMibView':
        return common.EndOfMibViewData(name=name)

    raise ValueError('unsupported type')


def _decode_str(x):
    return str(x, encoding='utf-8', errors='replace')
