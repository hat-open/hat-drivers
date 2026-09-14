"""Asyncio UDP endpoint wrapper"""

import functools
import warnings
import typing

from hat.drivers import net


warnings.warn("replaced with hat.drivers.net", DeprecationWarning,
              stacklevel=2)


Address: typing.TypeAlias = net.UdpAddress
EndpointInfo: typing.TypeAlias = net.UdpEndpointInfo
Endpoint: typing.TypeAlias = net.Endpoint

create = functools.partial(net.create_endpoint, net.DatagramType.UDP)
