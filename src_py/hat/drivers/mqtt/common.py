import enum
import typing

from hat import util


UInt8: typing.TypeAlias = int
"""Single byte integer in range [0, 0xff]"""

UInt16: typing.TypeAlias = int
"""Two byte integer in range [0, 0xffff]"""

UInt32: typing.TypeAlias = int
"""Four byte integer in range [0, 0xffff_ffff]"""

UIntVar: typing.TypeAlias = int
"""Variable byte integer in range [0, 0x0fff_ffff]"""

String: typing.TypeAlias = str
"""UTF-8 string limited to maximum of 0xffff bytes"""

Binary: typing.TypeAlias = util.Bytes
"""Binary data limited to maximum of 0xffff bytes"""


class QoS(enum.Enum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACLTY_ONCE = 2


class RetainHandling(enum.Enum):
    SEND_ON_SUBSCRIBE = 0
    SEND_ON_NEW_SUBSCRIBE = 1
    DONT_SEND = 2


class Reason(enum.Enum):
    SUCCESS = 0x00
    GRANTED_QOS_1 = 0x01
    GRANTED_QOS_2 = 0x02
    DISCONNECT_WITH_WILL_MESSAGE = 0x04
    NO_MATCHING_SUBSCRIBERS = 0x10
    NO_SUBSCRIPTION_EXISTED = 0x11
    CONTINUE_AUTHENTICATION = 0x24
    RE_AUTHENTICATE = 0x25
    UNSPECIFIED_ERROR = 0x80
    MALFORMED_PACKET = 0x81
    PROTOCOL_ERROR = 0x82
    IMPLEMENTATION_SPECIFIC_ERROR = 0x83
    UNSUPPORTED_PROTOCOL_VERSION = 0x84
    CLIENT_IDENTIFIER_NOT_VALID = 0x85
    BAD_USER_NAME_OR_PASSWORD = 0x86
    NOT_AUTHORIZED = 0x87
    SERVER_UNAVAILABLE = 0x88
    SERVER_BUSY = 0x89
    BANNED = 0x8a
    SERVER_SHUTTING_DOWN = 0x8b
    BAD_AUTHENTICATION_METHOD = 0x8c
    KEEP_ALIVE_TIMEOUT = 0x8d
    SESSION_TAKEN_OVER = 0x8e
    TOPIC_FILTER_INVALID = 0x8f
    TOPIC_NAME_INVALID = 0x90
    PACKET_IDENTIFIER_IN_USE = 0x91
    PACKET_IDENTIFIER_NOT_FOUND = 0x92
    RECEIVE_MAXIMUM_EXCEEDED = 0x93
    TOPIC_ALIAS_INVALID = 0x94
    PACKET_TOO_LARGE = 0x95
    MESSAGE_RATE_TOO_HIGH = 0x96
    QUOTA_EXCEEDED = 0x97
    ADMINISTRATIVE_ACTION = 0x98
    PAYLOAD_FORMAT_INVALID = 0x99
    RETAIN_NOT_SUPPORTED = 0x9a
    QOS_NOT_SUPPORTED = 0x9b
    USE_ANOTHER_SERVER = 0x9c
    SERVER_MOVED = 0x9d
    SHARED_SUBSCRIPTIONS_NOT_SUPPORTED = 0x9e
    CONNECTION_RATE_EXCEEDED = 0x9f
    MAXIMUM_CONNECT_TIME = 0xa0
    SUBSCRIPTION_IDENTIFIERS_NOT_SUPPORTED = 0xa1
    WILDCARD_SUBSCRIPTIONS_NOT_SUPPORTED = 0xa2


class MqttError(Exception):

    def __init__(self,
                 reason: Reason,
                 description: str | None):
        super().__init__(reason, description)
        self._reason = reason
        self._description = description

    @property
    def reason(self) -> Reason:
        return self._reason

    @property
    def description(self) -> str | None:
        return self._description


class Subscription(typing.NamedTuple):
    topic_filter: String
    maximum_qos: QoS
    no_local: bool
    retain_as_published: bool
    retain_handling: RetainHandling


def is_error_reason(reason: Reason) -> bool:
    return reason.value >= 0x80
