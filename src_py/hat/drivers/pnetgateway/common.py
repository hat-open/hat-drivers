import enum
import typing

from hat import json


class Status(enum.Enum):
    DISCONNECTED = 'DISCONNECTED'
    CONNECTING = 'CONNECTING'
    CONNECTED = 'CONNECTED'


class Quality(enum.Enum):
    NONE = 'NONE'
    GOOD = 'GOOD'
    UNRELIABLE = 'UNRELIABLE'
    BAD = 'BAD'


class Source(enum.Enum):
    APPLICATION = 'APPLICATION'
    CALCULATED = 'CALCULATED'
    MANUAL_ENTRY = 'MANUAL_ENTRY'
    NONSPECIFIC = 'NONSPECIFIC'
    PROC_MOD = 'PROC_MOD'
    REMOTE_SRC = 'REMOTE_SRC'
    REMOTE_SRC_INVALID = 'REMOTE_SRC_INVALID'
    SCHEDULED = 'SCHEDULED'


class DataType(enum.Enum):
    BLOB = 'BLOB'
    COMMAND = 'COMMAND'
    COUNTER = 'COUNTER'
    EVENT = 'EVENT'
    GROUP = 'GROUP'
    NUMERIC = 'NUMERIC'
    STATES = 'STATES'
    UNKNOWN = 'UNKNOWN'


class Data(typing.NamedTuple):
    key: str
    value: json.Data
    quality: Quality
    timestamp: float
    type: DataType
    source: Source


class Change(typing.NamedTuple):
    key: str
    value: typing.Optional[json.Data]
    quality: typing.Optional[Quality]
    timestamp: typing.Optional[float]
    source: typing.Optional[Source]


class Command(typing.NamedTuple):
    key: str
    value: json.Data
