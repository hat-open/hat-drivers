from hat.drivers.mqtt.common import *  # NOQA

from collections.abc import Collection
import typing

from hat import util

from hat.drivers.mqtt.common import (UInt16,
                                     UInt32,
                                     UIntVar,
                                     String,
                                     Binary,
                                     QoS,
                                     Reason,
                                     Subscription)


class Will(typing.NamedTuple):
    qos: QoS
    retain: bool
    delay_interval: UInt32
    message_expiry_interval: UInt32 | None
    content_type: String | None
    response_topic: String | None
    correlation_data: Binary | None
    user_properties: Collection[tuple[String, String]]
    topic: String
    payload: String | Binary


class ConnectPacket(typing.NamedTuple):
    clean_start: bool
    keep_alive: UInt16
    session_expiry_interval: UInt32
    receive_maximum: UInt16
    maximum_packet_size: UInt32 | None
    topic_alias_maximum: UInt16
    request_response_information: bool
    request_problem_information: bool
    user_properties: Collection[tuple[String, String]]
    authentication_method: String | None
    authentication_data: Binary | None
    client_identifier: String
    will: Will | None
    user_name: String | None
    password: Binary | None


class ConnAckPacket(typing.NamedTuple):
    session_present: bool
    reason: Reason
    session_expiry_interval: UInt32 | None
    receive_maximum: UInt16
    maximum_qos: QoS
    retain_available: bool
    maximum_packet_size: UInt32 | None
    assigned_client_identifier: String | None
    topic_alias_maximum: UInt16
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]
    wildcard_subscription_available: bool
    subscription_identifier_available: bool
    shared_subscription_available: bool
    server_keep_alive: UInt16 | None
    response_information: String | None
    server_reference: String | None
    authentication_method: String | None
    authentication_data: Binary | None


class PublishPacket(typing.NamedTuple):
    duplicate: bool
    qos: QoS
    retain: bool
    topic_name: String
    packet_identifier: UInt16 | None
    message_expiry_interval: UInt32 | None
    topic_alias: UInt16 | None
    response_topic: String | None
    correlation_data: Binary | None
    user_properties: Collection[tuple[String, String]]
    subscription_identifiers: Collection[UIntVar]
    content_type: String | None
    payload: str | util.Bytes


class PubAckPacket(typing.NamedTuple):
    packet_identifier: UInt16
    reason: Reason
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]


class PubRecPacket(typing.NamedTuple):
    packet_identifier: UInt16
    reason: Reason
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]


class PubRelPacket(typing.NamedTuple):
    packet_identifier: UInt16
    reason: Reason
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]


class PubCompPacket(typing.NamedTuple):
    packet_identifier: UInt16
    reason: Reason
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]


class SubscribePacket(typing.NamedTuple):
    packet_identifier: UInt16
    subscription_identifier: UIntVar | None
    user_properties: Collection[tuple[String, String]]
    subscriptions: Collection[Subscription]


class SubAckPacket(typing.NamedTuple):
    packet_identifier: UInt16
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]
    reasons: Collection[Reason]


class UnsubscribePacket(typing.NamedTuple):
    packet_identifier: UInt16
    user_properties: Collection[tuple[String, String]]
    topic_filters: Collection[String]


class UnsubAckPacket(typing.NamedTuple):
    packet_identifier: UInt16
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]
    reasons: Collection[Reason]


class PingReqPacket(typing.NamedTuple):
    pass


class PingResPacket(typing.NamedTuple):
    pass


class DisconnectPacket(typing.NamedTuple):
    reason: Reason
    session_expiry_interval: UInt32 | None
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]
    server_reference: String | None


class AuthPacket(typing.NamedTuple):
    reason: Reason
    authentication_method: String
    authentication_data: Binary | None
    reason_string: String | None
    user_properties: Collection[tuple[String, String]]


Packet: typing.TypeAlias = (ConnectPacket |
                            ConnAckPacket |
                            PublishPacket |
                            PubAckPacket |
                            PubRecPacket |
                            PubRelPacket |
                            PubCompPacket |
                            SubscribePacket |
                            SubAckPacket |
                            UnsubscribePacket |
                            UnsubAckPacket |
                            PingReqPacket |
                            PingResPacket |
                            DisconnectPacket |
                            AuthPacket)
