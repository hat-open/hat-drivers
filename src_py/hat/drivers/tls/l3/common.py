from hat.drivers.tls.common import *  # NOQA

from collections.abc import Collection
import enum
import typing

from hat import util

from hat.drivers.tls import l2

from hat.drivers.tls.common import UInt3


class Priority(enum.Enum):
    CLASS_1 = 0
    CLASS_2 = 1


AddressPath: typing.TypeAlias = Collection[tuple[l2.Address, l2.Address]]


class Packet(typing.NamedTuple):
    priority: Priority
    pointer: UInt3
    addresses: AddressPath
    data: util.Bytes


def reverse_addresses(addrs: AddressPath) -> AddressPath:
    return [(dst, src) for src, dst in reversed(addrs)]
