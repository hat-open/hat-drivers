import enum
import logging
import typing

from hat import util

from hat.drivers import tcp


# HACK should be str - bytes because of invalid ascii encoding
MessageId: typing.TypeAlias = util.Bytes  # max len 64


class Priority(enum.Enum):
    BULK = 0
    NORMAL = 1
    URGENT = 2
    VERY_URGENT = 3


class TypeOfNumber(enum.Enum):
    UNKNOWN = 0
    INTERNATIONAL = 1
    NATIONAL = 2
    NETWORK_SPECIFIC = 3
    SUBSCRIBER_NUMBER = 4
    ALPHANUMERIC = 5
    ABBREVIATED = 6


class DataCoding(enum.Enum):
    DEFAULT = 0
    ASCII = 1
    UNSPECIFIED_1 = 2
    LATIN_1 = 3
    UNSPECIFIED_2 = 4
    JIS = 5
    CYRLLIC = 6
    LATIN_HEBREW = 7
    UCS2 = 8
    PICTOGRAM = 9
    MUSIC = 10
    EXTENDED_KANJI = 13
    KS = 14


def create_connection_logger_adapter(logger: logging.Logger,
                                     communication: bool,
                                     info: tcp.ConnectionInfo):
    extra = {'meta': {'type': 'SmppConnection',
                      'communication': communication,
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(logger, extra)
