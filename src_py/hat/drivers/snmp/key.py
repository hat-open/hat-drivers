from collections.abc import Callable
import enum
import hashlib
import itertools
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
    if not password:
        raise Exception('invalid password')

    if key_type == KeyType.MD5:
        key_data = _create_key_data('md5', password, engine_id)

    elif key_type == KeyType.SHA:
        key_data = _create_key_data('sha1', password, engine_id)

    elif key_type == KeyType.DES:
        key_data = _create_key_data('md5', password, engine_id)

    else:
        raise ValueError('unsupported key type')

    return Key(type=key_type,
               data=key_data)


def auth_type_to_key_type(auth_type: common.AuthType) -> KeyType:
    if auth_type == common.AuthType.MD5:
        return KeyType.MD5

    if auth_type == common.AuthType.SHA:
        return KeyType.SHA

    raise ValueError('unsupported auth type')


def priv_type_to_key_type(priv_type: common.PrivType) -> KeyType:
    if priv_type == common.PrivType.DES:
        return KeyType.DES

    raise ValueError('unsupported priv type')


def _create_key_data(hash_name, password, engine_id):
    password_cycle = itertools.cycle(password.encode())
    extended_password = bytes(itertools.islice(password_cycle, 1024 * 1024))

    h = hashlib.new(hash_name)
    h.update(extended_password)
    extended_password_hash = h.digest()

    h = hashlib.new(hash_name)
    h.update(extended_password_hash)
    h.update(bytes(engine_id))
    h.update(extended_password_hash)

    return h.digest()
