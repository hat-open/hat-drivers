"""Asyncio TCP wrapper"""

import typing
import warnings

from hat.drivers import net


warnings.warn("replaced with hat.drivers.net", DeprecationWarning,
              stacklevel=2)


Address: typing.TypeAlias = net.TcpAddress
ConnectionInfo: typing.TypeAlias = net.TcpConnectionInfo
ServerInfo: typing.TypeAlias = net.TcpServerInfo
ConnectionCb: typing.TypeAlias = net.ConnectionCb
Server: typing.TypeAlias = net.Server
Connection: typing.TypeAlias = net.Connection

connect = net.connect
listen = net.listen
