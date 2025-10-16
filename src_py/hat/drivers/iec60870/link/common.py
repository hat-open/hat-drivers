import abc
import enum
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import serial


Address: typing.TypeAlias = int
"""addres is 0 or in range [0, 255] or in range [0, 65535]"""


class AddressSize(enum.Enum):
    ZERO = 0
    ONE = 1
    TWO = 2


class Direction(enum.Enum):
    B_TO_A = 0
    A_TO_B = 1


class ReqFunction(enum.Enum):
    RESET_LINK = 0
    RESET_PROCESS = 1
    TEST = 2
    DATA = 3
    DATA_NO_RES = 4
    REQ_ACCESS_DEMAND = 8
    REQ_STATUS = 9
    REQ_DATA_1 = 10
    REQ_DATA_2 = 11


class ResFunction(enum.Enum):
    ACK = 0
    NACK = 1
    RES_DATA = 8
    RES_NACK = 9
    RES_STATUS = 11
    NOT_FUNCTIONING = 14
    NOT_IMPLEMENTED = 15


class ReqFrame(typing.NamedTuple):
    direction: Direction | None
    frame_count_bit: bool
    frame_count_valid: bool
    function: ReqFunction
    address: Address
    data: util.Bytes


class ResFrame(typing.NamedTuple):
    direction: Direction | None
    access_demand: bool
    data_flow_control: bool
    function: ResFunction
    address: Address
    data: util.Bytes


class ShortFrame(typing.NamedTuple):
    pass


Frame: typing.TypeAlias = ReqFrame | ResFrame | ShortFrame


class ConnectionInfo(typing.NamedTuple):
    name: str | None
    port: str
    address: Address


class Connection(aio.Resource):

    @property
    @abc.abstractmethod
    def info(self) -> ConnectionInfo:
        pass

    @abc.abstractmethod
    async def send(self,
                   data: util.Bytes,
                   sent_cb: aio.AsyncCallable[[], None] | None = None):
        pass

    @abc.abstractmethod
    async def receive(self) -> util.Bytes:
        pass


def get_broadcast_address(address_size: AddressSize):
    if address_size == AddressSize.ONE:
        return 0xFF

    if address_size == AddressSize.TWO:
        return 0xFFFF

    raise ValueError('unsupported address size')


def create_logger_adapter(logger: logging.Logger,
                          info: serial.EndpointInfo
                          ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870Link',
                      'name': info.name,
                      'port': info.port}}

    return logging.LoggerAdapter(logger, extra)


def create_connection_logger_adapter(logger: logging.Logger,
                                     info: ConnectionInfo
                                     ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870LinkConnection',
                      'name': info.name,
                      'port': info.port,
                      'address': info.address}}

    return logging.LoggerAdapter(logger, extra)
