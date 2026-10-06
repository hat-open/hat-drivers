from hat.drivers.common import *  # NOQA

from collections.abc import Collection
import typing

from hat import util

from hat.drivers.tls import l2


Priority: typing.TypeAlias = l2.Priority

AddressPath: typing.TypeAlias = Collection[tuple[l2.Address, l2.Address]]


class Msg(typing.NamedTuple):
    priority: Priority
    pointer: int
    addresses: AddressPath
    data: util.Bytes


def reverse_addresses(addrs: AddressPath) -> AddressPath:
    return [(dst, src) for src, dst in reversed(addrs)]
