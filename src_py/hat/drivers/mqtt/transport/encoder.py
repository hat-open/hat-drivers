import collections
import enum

from hat import util

from hat.drivers.mqtt.transport import common


class _PacketType(enum.Enum):
    CONNECT = 1
    CONNACK = 2
    PUBLISH = 3
    PUBACK = 4
    PUBREC = 5
    PUBREL = 6
    PUBCOMP = 7
    SUBSCRIBE = 8
    SUBACK = 9
    UNSUBSCRIBE = 10
    UNSUBACK = 11
    PINGREQ = 12
    PINGRESP = 13
    DISCONNECT = 14
    AUTH = 15


class _PropertyType(enum.Enum):
    PAYLOAD_FORMAT_INDICATOR = 1
    MESSAGE_EXPIRY_INTERVAL = 2
    CONTENT_TYPE = 3
    RESPONSE_TOPIC = 8
    CORRELATION_DATA = 9
    SUBSCRIPTION_IDENTIFIER = 11
    SESSION_EXPIRY_INTERVAL = 17
    ASSIGNED_CLIENT_IDENTIFIER = 18
    SERVER_KEEP_ALIVE = 19
    AUTHENTICATION_METHOD = 21
    AUTHENTICATION_DATA = 22
    REQUEST_PROBLEM_INFORMATION = 23
    WILL_DELAY_INTERVAL = 24
    REQUEST_RESPONSE_INFORMATION = 25
    RESPONSE_INFORMATION = 26
    SERVER_REFERENCE = 28
    REASON_STRING = 31
    RECEIVE_MAXIMUM = 33
    TOPIC_ALIAS_MAXIMUM = 34
    TOPIC_ALIAS = 35
    MAXIMUM_QOS = 36
    RETAIN_AVAILABLE = 37
    USER_PROPERTY = 38
    MAXIMUM_PACKET_SIZE = 39
    WILDCARD_SUBSCRIPTION_AVAILABLE = 40
    SUBSCRIPTION_IDENTIFIER_AVAILABLE = 41
    SHARED_SUBSCRIPTION_AVAILABLE = 42


def get_next_packet_size(data: util.Bytes) -> int:
    if len(data) < 2:
        return 2

    i = 0
    while True:
        if i > 3:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid variable byte integer encoding')

        if len(data) < i + 2:
            return i + 2

        if not (data[i+1] & 0x80):
            break

        i += 1

    remaining_len, _ = _decode_uintvar(data[1:])

    return 2 + i + remaining_len


def encode_packet(packet: common.Packet) -> util.Bytes:
    if isinstance(packet, common.ConnectPacket):
        packet_type = _PacketType.CONNECT
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_connect_packet(packet))

    elif isinstance(packet, common.ConnAckPacket):
        packet_type = _PacketType.CONNACK
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_connack_packet(packet))

    elif isinstance(packet, common.PublishPacket):
        packet_type = _PacketType.PUBLISH
        duplicate = packet.duplicate
        qos = packet.qos
        retain = packet.retain
        packet_data = collections.deque(_encode_publish_packet(packet))

    elif isinstance(packet, common.PubAckPacket):
        packet_type = _PacketType.PUBACK
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_puback_packet(packet))

    elif isinstance(packet, common.PubRecPacket):
        packet_type = _PacketType.PUBREC
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_pubrec_packet(packet))

    elif isinstance(packet, common.PubRelPacket):
        packet_type = _PacketType.PUBREL
        duplicate = False
        qos = common.QoS.AT_LEAST_ONCE
        retain = False
        packet_data = collections.deque(_encode_pubrel_packet(packet))

    elif isinstance(packet, common.PubCompPacket):
        packet_type = _PacketType.PUBCOMP
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_pubcomp_packet(packet))

    elif isinstance(packet, common.SubscribePacket):
        packet_type = _PacketType.SUBSCRIBE
        duplicate = False
        qos = common.QoS.AT_LEAST_ONCE
        retain = False
        packet_data = collections.deque(_encode_subscribe_packet(packet))

    elif isinstance(packet, common.SubAckPacket):
        packet_type = _PacketType.SUBACK
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_suback_packet(packet))

    elif isinstance(packet, common.UnsubscribePacket):
        packet_type = _PacketType.UNSUBSCRIBE
        duplicate = False
        qos = common.QoS.AT_LEAST_ONCE
        retain = False
        packet_data = collections.deque(_encode_unsubscribe_packet(packet))

    elif isinstance(packet, common.UnsubAckPacket):
        packet_type = _PacketType.UNSUBACK
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_unsuback_packet(packet))

    elif isinstance(packet, common.PingReqPacket):
        packet_type = _PacketType.PINGREQ
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_pingreq_packet(packet))

    elif isinstance(packet, common.PingResPacket):
        packet_type = _PacketType.PINGRESP
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_pingresp_packet(packet))

    elif isinstance(packet, common.DisconnectPacket):
        packet_type = _PacketType.DISCONNECT
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_disconnect_packet(packet))

    elif isinstance(packet, common.AuthPacket):
        packet_type = _PacketType.AUTH
        duplicate = False
        qos = common.QoS.AT_MOST_ONCE
        retain = False
        packet_data = collections.deque(_encode_auth_packet(packet))

    else:
        raise ValueError('unsupported packet type')

    data = collections.deque()
    data.append((packet_type.value << 4) |
                (0x08 if duplicate else 0x00) |
                (qos.value << 1) |
                (0x01 if retain else 0x00))
    data.extend(_encode_uintvar(len(packet_data)))
    data.extend(packet_data)

    return bytes(data)


def decode_packet(data: util.Bytes) -> common.Packet:
    if len(data) < 2:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'insufficient packet data')

    try:
        packet_type = _PacketType(data[0] >> 4)

    except ValueError as e:
        raise common.MqttError(common.Reason.MALFORMED_PACKET, str(e))

    duplicate = bool(data[0] & 0x08)
    retain = bool(data[0] & 0x01)

    try:
        qos = common.QoS((data[0] >> 1) & 0x03)

    except ValueError as e:
        raise common.MqttError(common.Reason.MALFORMED_PACKET, str(e))

    remaining_len, data = _decode_uintvar(data[1:])
    if len(data) != remaining_len:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    if packet_type == _PacketType.CONNECT:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_connect_packet(data)

    elif packet_type == _PacketType.CONNACK:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_connack_packet(data)

    elif packet_type == _PacketType.PUBLISH:
        packet, data = _decode_publish_packet(data, duplicate, qos, retain)

    elif packet_type == _PacketType.PUBACK:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_puback_packet(data)

    elif packet_type == _PacketType.PUBREC:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_pubrec_packet(data)

    elif packet_type == _PacketType.PUBREL:
        if duplicate or qos != common.QoS.AT_LEAST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_pubrel_packet(data)

    elif packet_type == _PacketType.PUBCOMP:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_pubcomp_packet(data)

    elif packet_type == _PacketType.SUBSCRIBE:
        if duplicate or qos != common.QoS.AT_LEAST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_subscribe_packet(data)

    elif packet_type == _PacketType.SUBACK:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_suback_packet(data)

    elif packet_type == _PacketType.UNSUBSCRIBE:
        if duplicate or qos != common.QoS.AT_LEAST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_unsubscribe_packet(data)

    elif packet_type == _PacketType.UNSUBACK:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_unsuback_packet(data)

    elif packet_type == _PacketType.PINGREQ:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_pingreq_packet(data)

    elif packet_type == _PacketType.PINGRESP:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_pingresp_packet(data)

    elif packet_type == _PacketType.DISCONNECT:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_disconnect_packet(data)

    elif packet_type == _PacketType.AUTH:
        if duplicate or qos != common.QoS.AT_MOST_ONCE or retain:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid fixed header flags')

        packet, data = _decode_auth_packet(data)

    else:
        raise ValueError('unsupported packet type')

    if data:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'excess packet data')

    return packet


def _encode_connect_packet(packet):
    yield from _encode_string('MQTT')
    yield 5

    yield ((0x02 if packet.clean_start else 0x00) |
           (0x04 if packet.will else 0x00) |
           ((packet.will.qos.value << 3) if packet.will else 0x00) |
           (0x20 if packet.will and packet.will.retain else 0x00) |
           (0x80 if packet.user_name is not None else 0x00) |
           (0x40 if packet.password is not None else 0x00))

    yield from _encode_uint16(packet.keep_alive)

    props = {}

    if packet.session_expiry_interval != 0:
        props[_PropertyType.SESSION_EXPIRY_INTERVAL] = \
            packet.session_expiry_interval

    if packet.receive_maximum != 0xffff:
        props[_PropertyType.RECEIVE_MAXIMUM] = packet.receive_maximum

    if packet.maximum_packet_size is not None:
        props[_PropertyType.MAXIMUM_PACKET_SIZE] = packet.maximum_packet_size

    if packet.topic_alias_maximum != 0:
        props[_PropertyType.TOPIC_ALIAS_MAXIMUM] = packet.topic_alias_maximum

    if packet.request_response_information:
        props[_PropertyType.REQUEST_RESPONSE_INFORMATION] = 1

    if not packet.request_problem_information:
        props[_PropertyType.REQUEST_PROBLEM_INFORMATION] = 0

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    if packet.authentication_method is not None:
        props[_PropertyType.AUTHENTICATION_METHOD] = \
            packet.authentication_method

    if packet.authentication_data is not None:
        props[_PropertyType.AUTHENTICATION_DATA] = packet.authentication_data

    yield from _encode_props(props)

    yield from _encode_string(packet.client_identifier)

    if packet.will:
        yield from _encode_will(packet.will)

    if packet.user_name is not None:
        yield from _encode_string(packet.user_name)

    if packet.password is not None:
        yield from _encode_binary(packet.password)


def _decode_connect_packet(data):
    protocol_name, data = _decode_string(data)
    if protocol_name != 'MQTT':
        raise common.MqttError(common.Reason.UNSUPPORTED_PROTOCOL_VERSION,
                               'invalid protocol name')

    protocol_version, data = _decode_uint8(data)
    if protocol_version != 5:
        raise common.MqttError(common.Reason.UNSUPPORTED_PROTOCOL_VERSION,
                               'unsupported protocol version')

    connect_flags, data = _decode_uint8(data)
    clean_start = bool(connect_flags & 0x02)
    will_flag = bool(connect_flags & 0x04)
    will_retain = bool(connect_flags & 0x20)
    user_name_flag = bool(connect_flags & 0x80)
    password_flag = bool(connect_flags & 0x40)

    try:
        will_qos = common.QoS((connect_flags >> 3) & 0x03)

    except ValueError as e:
        raise common.MqttError(common.Reason.MALFORMED_PACKET, str(e))

    keep_alive, data = _decode_uint16(data)

    props, data = _decode_props(
        data, {_PropertyType.SESSION_EXPIRY_INTERVAL,
               _PropertyType.RECEIVE_MAXIMUM,
               _PropertyType.MAXIMUM_PACKET_SIZE,
               _PropertyType.TOPIC_ALIAS_MAXIMUM,
               _PropertyType.REQUEST_RESPONSE_INFORMATION,
               _PropertyType.REQUEST_PROBLEM_INFORMATION,
               _PropertyType.USER_PROPERTY,
               _PropertyType.AUTHENTICATION_METHOD,
               _PropertyType.AUTHENTICATION_DATA})

    authentication_method = props.get(_PropertyType.AUTHENTICATION_METHOD)
    authentication_data = props.get(_PropertyType.AUTHENTICATION_DATA)
    if authentication_method is None and authentication_data is not None:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'authentication method not specified')

    client_identifier, data = _decode_string(data)

    if will_flag:
        will, data = _decode_will(data, will_qos, will_retain)

    else:
        will = None

    if user_name_flag:
        user_name, data = _decode_string(data)

    else:
        user_name = None

    if password_flag:
        password, data = _decode_binary(data)

    else:
        password = None

    packet = common.ConnectPacket(
        clean_start=clean_start,
        keep_alive=keep_alive,
        session_expiry_interval=props.get(
            _PropertyType.SESSION_EXPIRY_INTERVAL, 0),
        receive_maximum=props.get(_PropertyType.RECEIVE_MAXIMUM, 0xffff),
        maximum_packet_size=props.get(_PropertyType.MAXIMUM_PACKET_SIZE),
        topic_alias_maximum=props.get(_PropertyType.TOPIC_ALIAS_MAXIMUM, 0),
        request_response_information=bool(
            props.get(_PropertyType.REQUEST_RESPONSE_INFORMATION, 0)),
        request_problem_information=bool(
            props.get(_PropertyType.REQUEST_PROBLEM_INFORMATION, 1)),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        authentication_method=authentication_method,
        authentication_data=authentication_data,
        client_identifier=client_identifier,
        will=will,
        user_name=user_name,
        password=password)

    return packet, data


def _encode_connack_packet(packet):
    yield (0x01 if packet.session_present else 0x00)

    yield from _encode_reason(packet.reason)

    props = {}

    if packet.session_expiry_interval is not None:
        props[_PropertyType.SESSION_EXPIRY_INTERVAL] = \
            packet.session_expiry_interval

    if packet.receive_maximum != 0xffff:
        props[_PropertyType.RECEIVE_MAXIMUM] = packet.receive_maximum

    if packet.maximum_qos != common.QoS.EXACLTY_ONCE:
        props[_PropertyType.MAXIMUM_QOS] = packet.maximum_qos

    if not packet.retain_available:
        props[_PropertyType.RETAIN_AVAILABLE] = 0

    if packet.maximum_packet_size is not None:
        props[_PropertyType.MAXIMUM_PACKET_SIZE] = packet.maximum_packet_size

    if packet.assigned_client_identifier is not None:
        props[_PropertyType.ASSIGNED_CLIENT_IDENTIFIER] = \
            packet.assigned_client_identifier

    if packet.topic_alias_maximum != 0:
        props[_PropertyType.TOPIC_ALIAS_MAXIMUM] = packet.topic_alias_maximum

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    if not packet.wildcard_subscription_available:
        props[_PropertyType.WILDCARD_SUBSCRIPTION_AVAILABLE] = 0

    if not packet.subscription_identifier_available:
        props[_PropertyType.SUBSCRIPTION_IDENTIFIER_AVAILABLE] = 0

    if not packet.shared_subscription_available:
        props[_PropertyType.SHARED_SUBSCRIPTION_AVAILABLE] = 0

    if packet.server_keep_alive is not None:
        props[_PropertyType.SERVER_KEEP_ALIVE] = packet.server_keep_alive

    if packet.response_information is not None:
        props[_PropertyType.RESPONSE_INFORMATION] = packet.response_information

    if packet.server_reference is not None:
        props[_PropertyType.SERVER_REFERENCE] = packet.server_reference

    if packet.authentication_method is not None:
        props[_PropertyType.AUTHENTICATION_METHOD] = \
            packet.authentication_method

    if packet.authentication_data is not None:
        props[_PropertyType.AUTHENTICATION_DATA] = packet.authentication_data

    yield from _encode_props(props)


def _decode_connack_packet(data):
    connack_flags, data = _decode_uint8(data)
    session_present = bool(connack_flags & 0x01)

    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.SESSION_EXPIRY_INTERVAL,
               _PropertyType.RECEIVE_MAXIMUM,
               _PropertyType.MAXIMUM_QOS,
               _PropertyType.RETAIN_AVAILABLE,
               _PropertyType.MAXIMUM_PACKET_SIZE,
               _PropertyType.ASSIGNED_CLIENT_IDENTIFIER,
               _PropertyType.TOPIC_ALIAS_MAXIMUM,
               _PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY,
               _PropertyType.WILDCARD_SUBSCRIPTION_AVAILABLE,
               _PropertyType.SUBSCRIPTION_IDENTIFIER_AVAILABLE,
               _PropertyType.SHARED_SUBSCRIPTION_AVAILABLE,
               _PropertyType.SERVER_KEEP_ALIVE,
               _PropertyType.RESPONSE_INFORMATION,
               _PropertyType.SERVER_REFERENCE,
               _PropertyType.AUTHENTICATION_METHOD,
               _PropertyType.AUTHENTICATION_DATA})

    packet = common.ConnAckPacket(
        session_present=session_present,
        reason=reason,
        session_expiry_interval=props.get(
            _PropertyType.SESSION_EXPIRY_INTERVAL),
        receive_maximum=props.get(_PropertyType.RECEIVE_MAXIMUM, 0xffff),
        maximum_qos=props.get(_PropertyType.MAXIMUM_QOS,
                              common.QoS.EXACLTY_ONCE),
        retain_available=bool(props.get(_PropertyType.RETAIN_AVAILABLE, 1)),
        maximum_packet_size=props.get(_PropertyType.MAXIMUM_PACKET_SIZE),
        assigned_client_identifier=props.get(
            _PropertyType.ASSIGNED_CLIENT_IDENTIFIER),
        topic_alias_maximum=props.get(_PropertyType.TOPIC_ALIAS_MAXIMUM, 0),
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        wildcard_subscription_available=bool(
            props.get(_PropertyType.WILDCARD_SUBSCRIPTION_AVAILABLE, 1)),
        subscription_identifier_available=bool(
            props.get(_PropertyType.SUBSCRIPTION_IDENTIFIER_AVAILABLE, 1)),
        shared_subscription_available=bool(
            props.get(_PropertyType.SHARED_SUBSCRIPTION_AVAILABLE, 1)),
        server_keep_alive=props.get(_PropertyType.SERVER_KEEP_ALIVE),
        response_information=props.get(_PropertyType.RESPONSE_INFORMATION),
        server_reference=props.get(_PropertyType.SERVER_REFERENCE),
        authentication_method=props.get(_PropertyType.AUTHENTICATION_METHOD),
        authentication_data=props.get(_PropertyType.AUTHENTICATION_DATA))

    return packet, data


def _encode_publish_packet(packet):
    yield from _encode_string(packet.topic_name)

    if packet.qos != common.QoS.AT_MOST_ONCE:
        if packet.packet_identifier is None:
            raise Exception('invalid packet identifier')

        yield from _encode_uint16(packet.packet_identifier)

    props = {}

    if isinstance(packet.payload, str):
        props[_PropertyType.PAYLOAD_FORMAT_INDICATOR] = 1

    if packet.message_expiry_interval is not None:
        props[_PropertyType.MESSAGE_EXPIRY_INTERVAL] = \
            packet.message_expiry_interval

    if packet.topic_alias is not None:
        props[_PropertyType.TOPIC_ALIAS] = packet.topic_alias

    if packet.response_topic is not None:
        props[_PropertyType.RESPONSE_TOPIC] = packet.response_topic

    if packet.correlation_data is not None:
        props[_PropertyType.CORRELATION_DATA] = packet.correlation_data

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    if packet.subscription_identifiers:
        props[_PropertyType.SUBSCRIPTION_IDENTIFIER] = \
            packet.subscription_identifier

    if packet.content_type is not None:
        props[_PropertyType.CONTENT_TYPE] = packet.content_type

    yield from _encode_props(props)

    if isinstance(packet.payload, str):
        yield from packet.payload.encode()

    else:
        yield from packet.payload


def _decode_publish_packet(data, duplicate, qos, retain):
    topic_name, data = _decode_string(data)

    if qos != common.QoS.AT_MOST_ONCE:
        packet_identifier, data = _decode_uint16(data)

    else:
        packet_identifier = None

    props, data = _decode_props(
        data, {_PropertyType.PAYLOAD_FORMAT_INDICATOR,
               _PropertyType.MESSAGE_EXPIRY_INTERVAL,
               _PropertyType.TOPIC_ALIAS,
               _PropertyType.RESPONSE_TOPIC,
               _PropertyType.CORRELATION_DATA,
               _PropertyType.USER_PROPERTY,
               _PropertyType.SUBSCRIPTION_IDENTIFIER,
               _PropertyType.CONTENT_TYPE})

    if props.get(_PropertyType.PAYLOAD_FORMAT_INDICATOR):
        try:
            payload, data = str(data, encoding='utf-8'), b''

        except UnicodeError:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid utf-8 encoding')

    else:
        payload, data = data, b''

    packet = common.PublishPacket(
        duplicate=duplicate,
        qos=qos,
        retain=retain,
        topic_name=topic_name,
        packet_identifier=packet_identifier,
        message_expiry_interval=props.get(
            _PropertyType.MESSAGE_EXPIRY_INTERVAL),
        topic_alias=props.get(_PropertyType.TOPIC_ALIAS),
        response_topic=props.get(_PropertyType.RESPONSE_TOPIC),
        correlation_data=props.get(_PropertyType.CORRELATION_DATA),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        subscription_identifiers=props.get(
            _PropertyType.SUBSCRIPTION_IDENTIFIER, []),
        content_type=props.get(_PropertyType.CONTENT_TYPE),
        payload=payload)

    return packet, data


def _encode_puback_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    yield from _encode_reason(packet.reason)

    props = {}

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)


def _decode_puback_packet(data):
    packet_identifier, data = _decode_uint16(data)

    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    packet = common.PubAckPacket(
        packet_identifier=packet_identifier,
        reason=reason,
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []))

    return packet, data


def _encode_pubrec_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    yield from _encode_reason(packet.reason)

    props = {}

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)


def _decode_pubrec_packet(data):
    packet_identifier, data = _decode_uint16(data)

    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    packet = common.PubRecPacket(
        packet_identifier=packet_identifier,
        reason=reason,
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []))

    return packet, data


def _encode_pubrel_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    yield from _encode_reason(packet.reason)

    props = {}

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)


def _decode_pubrel_packet(data):
    packet_identifier, data = _decode_uint16(data)

    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    packet = common.PubRelPacket(
        packet_identifier=packet_identifier,
        reason=reason,
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []))

    return packet, data


def _encode_pubcomp_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    yield from _encode_reason(packet.reason)

    props = {}

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)


def _decode_pubcomp_packet(data):
    packet_identifier, data = _decode_uint16(data)

    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    packet = common.PubCompPacket(
        packet_identifier=packet_identifier,
        reason=reason,
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []))

    return packet, data


def _encode_subscribe_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    props = {}

    if packet.subscription_identifier is not None:
        props[_PropertyType.SUBSCRIPTION_IDENTIFIER] = [
            packet.subscription_identifier]

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)

    if not packet.subscriptions:
        raise Exception('invalid subscriptions length')

    for subscription in packet.subscriptions:
        yield from _encode_subscription(subscription)


def _decode_subscribe_packet(data):
    packet_identifier, data = _decode_uint16(data)

    props, data = _decode_props(
        data, {_PropertyType.SUBSCRIPTION_IDENTIFIER,
               _PropertyType.USER_PROPERTY})

    subscription_identifiers = props.get(
        _PropertyType.SUBSCRIPTION_IDENTIFIER, [])
    if len(subscription_identifiers) > 1:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'multiple SUBSCRIPTION_IDENTIFIER entries')

    subscription_identifier = (subscription_identifiers[0]
                               if subscription_identifiers else None)

    subscriptions = collections.deque()
    while data:
        subscription, data = _decode_subscription(data)
        subscriptions.append(subscription)

    if not subscriptions:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'invalid subscriptions length')

    packet = common.SubscribePacket(
        packet_identifier=packet_identifier,
        subscription_identifier=subscription_identifier,
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        subscriptions=subscriptions)

    return packet, b''


def _encode_suback_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    props = {}

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)

    if not packet.reasons:
        raise Exception('invalid reasons length')

    for reason in packet.reasons:
        yield from _encode_reason(reason)


def _decode_suback_packet(data):
    packet_identifier, data = _decode_uint16(data)

    props, data = _decode_props(
        data, {_PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    reasons = collections.deque()
    while data:
        reason, data = _decode_reason(data)
        reasons.append(reason)

    if not reasons:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'invalid reasons length')

    packet = common.SubAckPacket(
        packet_identifier=packet_identifier,
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        reasons=reasons)

    return packet, b''


def _encode_unsubscribe_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    props = {}

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)

    if not packet.topic_filters:
        raise Exception('invalid topic filters length')

    for topic_filter in packet.topic_filters:
        yield from _encode_string(topic_filter)


def _decode_unsubscribe_packet(data):
    packet_identifier, data = _decode_uint16(data)

    props, data = _decode_props(
        data, {_PropertyType.USER_PROPERTY})

    topic_filters = collections.deque()
    while data:
        topic_filter, data = _decode_string(data)
        topic_filters.append(topic_filter)

    if not topic_filters:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'invalid topic filters length')

    packet = common.UnsubscribePacket(
        packet_identifier=packet_identifier,
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        topic_filters=topic_filters)

    return packet, b''


def _encode_unsuback_packet(packet):
    yield from _encode_uint16(packet.packet_identifier)

    props = {}

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)

    if not packet.reasons:
        raise Exception('invalid reasons length')

    for reason in packet.reasons:
        yield from _encode_reason(reason)


def _decode_unsuback_packet(data):
    packet_identifier, data = _decode_uint16(data)

    props, data = _decode_props(
        data, {_PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    reasons = collections.deque()
    while data:
        reason, data = _decode_reason(data)
        reasons.append(reason)

    if not reasons:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'invalid reasons length')

    packet = common.UnsubAckPacket(
        packet_identifier=packet_identifier,
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        reasons=reasons)

    return packet, b''


def _encode_pingreq_packet(packet):
    yield from b''


def _decode_pingreq_packet(data):
    packet = common.PingReqPacket()

    return packet, data


def _encode_pingresp_packet(packet):
    yield from b''


def _decode_pingresp_packet(data):
    packet = common.PingResPacket()

    return packet, data


def _encode_disconnect_packet(packet):
    yield from _encode_reason(packet.reason)

    props = {}

    if packet.session_expiry_interval is not None:
        props[_PropertyType.SESSION_EXPIRY_INTERVAL] = \
            packet.session_expiry_interval

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    if packet.server_reference is not None:
        props[_PropertyType.SERVER_REFERENCE] = packet.server_reference

    yield from _encode_props(props)


def _decode_disconnect_packet(data):
    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.SESSION_EXPIRY_INTERVAL,
               _PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY,
               _PropertyType.SERVER_REFERENCE})

    packet = common.DisconnectPacket(
        reason=reason,
        session_expiry_interval=props.get(
            _PropertyType.SESSION_EXPIRY_INTERVAL),
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        server_reference=props.get(_PropertyType.SERVER_REFERENCE))

    return packet, data


def _encode_auth_packet(packet):
    yield from _encode_reason(packet.reason)

    props = {_PropertyType.AUTHENTICATION_METHOD: packet.authentication_method}

    if packet.authentication_data is not None:
        props[_PropertyType.AUTHENTICATION_DATA] = packet.authentication_data

    if packet.reason_string is not None:
        props[_PropertyType.REASON_STRING] = packet.reason_string

    if packet.user_properties:
        props[_PropertyType.USER_PROPERTY] = packet.user_properties

    yield from _encode_props(props)


def _decode_auth_packet(data):
    reason, data = _decode_reason(data)

    props, data = _decode_props(
        data, {_PropertyType.AUTHENTICATION_METHOD,
               _PropertyType.AUTHENTICATION_DATA,
               _PropertyType.REASON_STRING,
               _PropertyType.USER_PROPERTY})

    authentication_method = props.get(_PropertyType.AUTHENTICATION_METHOD)
    if authentication_method is None:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                               'missing authentication method')

    packet = common.AuthPacket(
        reason=reason,
        authentication_method=authentication_method,
        authentication_data=props.get(_PropertyType.AUTHENTICATION_DATA),
        reason_string=props.get(_PropertyType.REASON_STRING),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []))

    return packet, data


def _encode_will(will):
    props = {}

    if will.delay_interval != 0:
        props[_PropertyType.WILL_DELAY_INTERVAL] = will.delay_interval

    if isinstance(will.payload, str):
        props[_PropertyType.PAYLOAD_FORMAT_INDICATOR] = 1

    if will.message_expiry_interval is not None:
        props[_PropertyType.MESSAGE_EXPIRY_INTERVAL] = \
            will.message_expiry_interval

    if will.content_type is not None:
        props[_PropertyType.CONTENT_TYPE] = will.content_type

    if will.response_topic is not None:
        props[_PropertyType.RESPONSE_TOPIC] = will.response_topic

    if will.correlation_data is not None:
        props[_PropertyType.CORRELATION_DATA] = will.correlation_data

    if will.user_properties:
        props[_PropertyType.USER_PROPERTY] = will.user_properties

    yield from _encode_props(props)

    yield from _encode_string(will.topic)

    if isinstance(will.payload, str):
        yield from _encode_string(will.payload)

    else:
        yield from _encode_binary(will.payload)


def _decode_will(data, qos, retain):
    props, data = _decode_props(
        data, {_PropertyType.WILL_DELAY_INTERVAL,
               _PropertyType.PAYLOAD_FORMAT_INDICATOR,
               _PropertyType.MESSAGE_EXPIRY_INTERVAL,
               _PropertyType.CONTENT_TYPE,
               _PropertyType.RESPONSE_TOPIC,
               _PropertyType.CORRELATION_DATA,
               _PropertyType.USER_PROPERTY})

    topic, data = _decode_string(data)

    if props.get(_PropertyType.PAYLOAD_FORMAT_INDICATOR):
        payload, data = _decode_string(data)

    else:
        payload, data = _decode_binary(data)

    will = common.Will(
        qos=qos,
        retain=retain,
        delay_interval=props.get(_PropertyType.WILL_DELAY_INTERVAL, 0),
        message_expiry_interval=props.get(
            _PropertyType.MESSAGE_EXPIRY_INTERVAL),
        content_type=props.get(_PropertyType.CONTENT_TYPE),
        response_topic=props.get(_PropertyType.RESPONSE_TOPIC),
        correlation_data=props.get(_PropertyType.CORRELATION_DATA),
        user_properties=props.get(_PropertyType.USER_PROPERTY, []),
        topic=topic,
        payload=payload)

    return will, data


def _encode_subscription(subscription):
    yield from _encode_string(subscription.topic_filter)

    yield (subscription.maximum_qos.value |
           (0x03 if subscription.no_local else 0x00) |
           (0x04 if subscription.retain_as_published else 0x00) |
           (subscription.retain_handling.value << 4))


def _decode_subscription(data):
    topic_filter, data = _decode_string(data)

    options, data = _decode_uint8(data)
    no_local = bool(options & 0x04)
    retain_as_published = bool(options & 0x08)

    try:
        maximum_qos = common.QoS(options & 0x03)
        retain_handling = common.RetainHandling((options >> 4) & 0x03)

    except ValueError as e:
        raise common.MqttError(common.Reason.PROTOCOL_ERROR, str(e))

    subscription = common.Subscription(
        topic_filter=topic_filter,
        maximum_qos=maximum_qos,
        no_local=no_local,
        retain_as_published=retain_as_published,
        retain_handling=retain_handling)

    return subscription, data


def _encode_reason(reason):
    yield reason.value


def _decode_reason(data):
    if not data:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    try:
        return common.Reason(data[0]), data[1:]

    except ValueError as e:
        raise common.MqttError(common.Reason.MALFORMED_PACKET, str(e))


def _encode_props(props):
    props_bytes = collections.deque()
    for prop_type, prop in props.items():
        if prop_type not in (_PropertyType.USER_PROPERTY,
                             _PropertyType.SUBSCRIPTION_IDENTIFIER):
            props_bytes.extend(_encode_uintvar(prop_type.value))

        if prop_type == _PropertyType.PAYLOAD_FORMAT_INDICATOR:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        elif prop_type == _PropertyType.MESSAGE_EXPIRY_INTERVAL:
            props_bytes.extend(_encode_uint32(prop))

        elif prop_type == _PropertyType.CONTENT_TYPE:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.RESPONSE_TOPIC:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.CORRELATION_DATA:
            props_bytes.extend(_encode_binary(prop))

        elif prop_type == _PropertyType.SUBSCRIPTION_IDENTIFIER:
            for i in prop:
                if i == 0:
                    raise Exception(f'invalid {prop_type.name} value')

                props_bytes.extend(_encode_uintvar(prop_type.value))
                props_bytes.extend(_encode_uintvar(i))

        elif prop_type == _PropertyType.SESSION_EXPIRY_INTERVAL:
            props_bytes.extend(_encode_uint32(prop))

        elif prop_type == _PropertyType.ASSIGNED_CLIENT_IDENTIFIER:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.SERVER_KEEP_ALIVE:
            props_bytes.extend(_encode_uint16(prop))

        elif prop_type == _PropertyType.AUTHENTICATION_METHOD:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.AUTHENTICATION_DATA:
            props_bytes.extend(_encode_binary(prop))

        elif prop_type == _PropertyType.REQUEST_PROBLEM_INFORMATION:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        elif prop_type == _PropertyType.WILL_DELAY_INTERVAL:
            props_bytes.extend(_encode_uint32(prop))

        elif prop_type == _PropertyType.REQUEST_RESPONSE_INFORMATION:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        elif prop_type == _PropertyType.RESPONSE_INFORMATION:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.SERVER_REFERENCE:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.REASON_STRING:
            props_bytes.extend(_encode_string(prop))

        elif prop_type == _PropertyType.RECEIVE_MAXIMUM:
            if prop == 0:
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint16(prop))

        elif prop_type == _PropertyType.TOPIC_ALIAS_MAXIMUM:
            props_bytes.extend(_encode_uint16(prop))

        elif prop_type == _PropertyType.TOPIC_ALIAS:
            # TODO value 0 is not permitted

            props_bytes.extend(_encode_uint16(prop))

        elif prop_type == _PropertyType.MAXIMUM_QOS:
            if prop not in (common.QoS.AT_MOST_ONCE,
                            common.QoS.AT_LEAST_ONCE):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop.value))

        elif prop_type == _PropertyType.RETAIN_AVAILABLE:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        elif prop_type == _PropertyType.USER_PROPERTY:
            for k, v in prop:
                props_bytes.extend(_encode_uintvar(prop_type.value))
                props_bytes.extend(_encode_string(k))
                props_bytes.extend(_encode_string(v))

        elif prop_type == _PropertyType.MAXIMUM_PACKET_SIZE:
            if prop == 0:
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint32(prop))

        elif prop_type == _PropertyType.WILDCARD_SUBSCRIPTION_AVAILABLE:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        elif prop_type == _PropertyType.SUBSCRIPTION_IDENTIFIER_AVAILABLE:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        elif prop_type == _PropertyType.SHARED_SUBSCRIPTION_AVAILABLE:
            if prop not in (0, 1):
                raise Exception(f'invalid {prop_type.name} value')

            props_bytes.extend(_encode_uint8(prop))

        else:
            raise ValueError('unsupported property type')

    yield from _encode_uintvar(len(props_bytes))
    yield from props_bytes


def _decode_props(data, valid_prop_types):
    props_data_len, data = _decode_uintvar(data)
    if len(data) < props_data_len:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid property length')

    props = {}
    data, rest_data = data[:props_data_len], data[props_data_len:]

    while data:
        prop_type_value, data = _decode_uintvar(data)

        try:
            prop_type = _PropertyType(prop_type_value)

        except ValueError as e:
            raise common.MqttError(common.Reason.MALFORMED_PACKET, str(e))

        if prop_type not in valid_prop_types:
            raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                   f'invalid property {prop_type.name}')

        if prop_type in props and prop_type not in (
                _PropertyType.USER_PROPERTY,
                _PropertyType.SUBSCRIPTION_IDENTIFIER):
            raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                   f'multiple {prop_type.name} entries')

        if prop_type == _PropertyType.PAYLOAD_FORMAT_INDICATOR:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.MESSAGE_EXPIRY_INTERVAL:
            prop, data = _decode_uint32(data)

        elif prop_type == _PropertyType.CONTENT_TYPE:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.RESPONSE_TOPIC:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.CORRELATION_DATA:
            prop, data = _decode_binary(data)

        elif prop_type == _PropertyType.SUBSCRIPTION_IDENTIFIER:
            prop, data = _decode_uintvar(data)

            if prop == 0:
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.SESSION_EXPIRY_INTERVAL:
            prop, data = _decode_uint32(data)

        elif prop_type == _PropertyType.ASSIGNED_CLIENT_IDENTIFIER:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.SERVER_KEEP_ALIVE:
            prop, data = _decode_uint16(data)

        elif prop_type == _PropertyType.AUTHENTICATION_METHOD:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.AUTHENTICATION_DATA:
            prop, data = _decode_binary(data)

        elif prop_type == _PropertyType.REQUEST_PROBLEM_INFORMATION:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.WILL_DELAY_INTERVAL:
            prop, data = _decode_uint32(data)

        elif prop_type == _PropertyType.REQUEST_RESPONSE_INFORMATION:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.RESPONSE_INFORMATION:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.SERVER_REFERENCE:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.REASON_STRING:
            prop, data = _decode_string(data)

        elif prop_type == _PropertyType.RECEIVE_MAXIMUM:
            prop, data = _decode_uint16(data)

            if prop == 0:
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.TOPIC_ALIAS_MAXIMUM:
            prop, data = _decode_uint16(data)

        elif prop_type == _PropertyType.TOPIC_ALIAS:
            prop, data = _decode_uint16(data)

            # TODO value 0 is not permitted

        elif prop_type == _PropertyType.MAXIMUM_QOS:
            prop, data = _decode_uint8(data)

            try:
                prop = common.QoS(prop)

            except ValueError as e:
                raise common.MqttError(common.Reason.PROTOCOL_ERROR, str(e))

            if prop == common.QoS.EXACLTY_ONCE:
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.RETAIN_AVAILABLE:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.USER_PROPERTY:
            prop1, data = _decode_string(data)
            prop2, data = _decode_string(data)
            prop = (prop1, prop2)

        elif prop_type == _PropertyType.MAXIMUM_PACKET_SIZE:
            prop, data = _decode_uint32(data)

            if prop == 0:
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.WILDCARD_SUBSCRIPTION_AVAILABLE:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.SUBSCRIPTION_IDENTIFIER_AVAILABLE:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        elif prop_type == _PropertyType.SHARED_SUBSCRIPTION_AVAILABLE:
            prop, data = _decode_uint8(data)

            if prop not in (0, 1):
                raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                       f'invalid {prop_type.name} value')

        else:
            raise ValueError('unsupported property type')

        if prop_type in (_PropertyType.USER_PROPERTY,
                         _PropertyType.SUBSCRIPTION_IDENTIFIER):
            if prop_type not in props:
                props[prop_type] = collections.deque()

            props[prop_type].append(prop)

        else:
            props[prop_type] = prop

    return props, rest_data


def _encode_uint8(value):
    if value < 0 or value > 0xff:
        raise ValueError('unsupported one byte integer value')

    yield value


def _decode_uint8(data):
    if len(data) < 1:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    return data[0], data[1:]


def _encode_uint16(value):
    if value < 0 or value > 0xffff:
        raise ValueError('unsupported two byte integer value')

    yield (value >> 8) & 0xff
    yield value & 0xff


def _decode_uint16(data):
    if len(data) < 2:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    value = (data[0] << 8) | data[1]

    return value, data[2:]


def _encode_uint32(value):
    if value < 0 or value > 0xffff_ffff:
        raise ValueError('unsupported four byte integer value')

    yield (value >> 24) & 0xff
    yield (value >> 16) & 0xff
    yield (value >> 8) & 0xff
    yield value & 0xff


def _decode_uint32(data):
    if len(data) < 4:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    value = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]

    return value, data[4:]


def _encode_uintvar(value):
    if value < 0 or value > 0x0fff_ffff:
        raise ValueError('unsupported variable byte integer value')

    while True:
        byte = value & 0x7f
        value = value >> 7

        if value:
            byte = byte | 0x80

        yield byte

        if not value:
            break


def _decode_uintvar(data):
    more_follows = True
    i = 0
    value = 0

    while more_follows:
        if i > 3:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid variable byte integer encoding')

        if len(data) < i + 1:
            raise common.MqttError(common.Reason.MALFORMED_PACKET,
                                   'invalid data length')

        value = value | ((data[i] & 0x7f) << (i * 7))
        more_follows = data[i] & 0x80
        i += 1

    return value, data[i:]


def _encode_string(value):
    value_bytes = value.encode()

    yield from _encode_uint16(len(value_bytes))
    yield from value_bytes


def _decode_string(data):
    value_len, data = _decode_uint16(data)
    if len(data) < value_len:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    try:
        value, data = (str(data[:value_len], encoding='utf-8'),
                       data[value_len:])

    except UnicodeError:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid utf-8 encoding')

    return value, data


def _encode_binary(value):
    yield from _encode_uint16(len(value))
    yield from value


def _decode_binary(data):
    value_len, data = _decode_uint16(data)
    if len(data) < value_len:
        raise common.MqttError(common.Reason.MALFORMED_PACKET,
                               'invalid data length')

    return data[:value_len], data[value_len:]
