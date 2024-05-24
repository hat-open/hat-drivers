from collections.abc import Callable
import enum
import typing

from hat import util

from hat.drivers.snmp import common


class KeyType(enum.Enum):
    MD5 = 1
    SHA = 2
    DES = 3


class Key(typing.NamedTuple):
    type: KeyType
    data: util.Bytes


KeyCb: typing.TypeAlias = Callable[[common.EngineId, common.UserName],
                                   Key | None]


def create_key(key_type: KeyType,
               password: str,
               engine_id: common.EngineId
               ) -> Key:
    raise NotImplementedError()
