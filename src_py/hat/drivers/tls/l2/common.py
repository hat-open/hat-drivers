from hat.drivers.tls.common import *  # NOQA

import abc
import enum
import typing

from hat import aio
from hat import util

from hat.drivers import net
from hat.drivers import serial
from hat.drivers.tls import l1

from hat.drivers.tls.common import UInt8


Address: typing.TypeAlias = UInt8
"""addres is 0 or in range [0, 255]"""


class ReqFunction(enum.Enum):
    RESET_UNIT = 0
    RESET_COMMUNICATION = 1
    SEND_DATA = 3
    SEND_DATA_NO_RES = 4
    SEND_TEST = 7
    REQ_DATA_1_OR_2 = 8
    REQ_STATUS = 9
    REQ_DATA_1 = 10
    REQ_DATA_2 = 11
    REQ_TEST = 15


class ResFunction(enum.Enum):
    RESET_ACK = 0
    REJECT = 1
    RES_DATA = 8
    RES_ACK = 9
    RES_REJECT = 10
    RES_STATUS = 11
    RES_TEST = 15


class ReqFrame(typing.NamedTuple):
    frame_count_bit: bool
    frame_count_valid: bool
    function: ReqFunction
    address: Address
    data: util.Bytes


class ResFrame(typing.NamedTuple):
    access_demand: bool
    data_flow_control: bool
    function: ResFunction
    address: Address
    data: util.Bytes


class ShortFrame(typing.NamedTuple):
    pass


Frame: typing.TypeAlias = ReqFrame | ResFrame | ShortFrame


class TcpConnectionInfo(typing.NamedTuple):
    name: str | None
    l1_local_addr: net.TcpAddress
    l1_remote_addr: net.TcpAddress
    l2_addr: Address


class UnixConnectionInfo(typing.NamedTuple):
    name: str | None
    l1_addr: net.UnixAddress
    l2_addr: Address


class SerialConnectionInfo(typing.NamedTuple):
    name: str | None
    l1_port: str
    l2_addr: Address


ConnectionInfo: typing.TypeAlias = (TcpConnectionInfo |
                                    UnixConnectionInfo |
                                    SerialConnectionInfo)


Test: typing.TypeAlias = bool


class Connection(aio.Resource):

    @property
    @abc.abstractmethod
    def info(self) -> ConnectionInfo:
        pass

    @abc.abstractmethod
    async def send(self,
                   data: util.Bytes,
                   *,
                   sent_cb: aio.AsyncCallable[[], None] | None = None,
                   with_ack: bool = True,
                   test: Test = False):
        pass

    @abc.abstractmethod
    async def receive(self) -> [util.Bytes, Test]:
        pass


broadcast_address: Address = 0xff


def create_connection_info(name: str | None,
                           addr: Address,
                           info: l1.LinkInfo
                           ) -> ConnectionInfo:
    if isinstance(info, net.TcpConnectionInfo):
        return TcpConnectionInfo(name=name,
                                 addr=addr,
                                 tcp_local_addr=info.local_addr,
                                 tcp_remote_addr=info.remote_addr)

    if isinstance(info, net.UnixConnectionInfo):
        return UnixConnectionInfo(name=name,
                                  addr=addr,
                                  unix_addr=info.addr)

    if isinstance(info, serial.EndpointInfo):
        return SerialConnectionInfo(name=name,
                                    addr=addr,
                                    port=info.port)

    raise TypeError('unsupported info type')
