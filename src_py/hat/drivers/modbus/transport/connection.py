import abc
import logging

from hat import aio
from hat import util

from hat.drivers import serial
from hat.drivers import tcp
from hat.drivers.modbus.transport import common
from hat.drivers.modbus.transport import encoder
from hat.drivers.modbus.transport import logger


mlog: logging.Logger = logging.getLogger(__name__)


class Link(aio.Resource):

    @property
    @abc.abstractmethod
    def info(self) -> tcp.ConnectionInfo | serial.EndpointInfo:
        pass

    @abc.abstractmethod
    async def write(self, data: util.Bytes):
        pass

    @abc.abstractmethod
    async def read(self, size: int) -> util.Bytes:
        pass

    @abc.abstractmethod
    async def drain(self):
        pass

    @abc.abstractmethod
    async def clear_input_buffer(self):
        pass


class SerialLink(Link):

    def __init__(self, endpoint: serial.Endpoint):
        self._endpoint = endpoint

    @property
    def async_group(self):
        return self._endpoint.async_group

    @property
    def info(self):
        return self._endpoint.info

    async def write(self, data):
        await self._endpoint.write(data)

    async def read(self, size):
        return await self._endpoint.read(size)

    async def drain(self):
        await self._endpoint.drain()

    async def clear_input_buffer(self):
        return await self._endpoint.clear_input_buffer()


class TcpLink(Link):

    def __init__(self, conn: tcp.Connection):
        self._conn = conn

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def info(self):
        return self._conn.info

    async def write(self, data):
        await self._conn.write(data)

    async def read(self, size):
        return await self._conn.readexactly(size)

    async def drain(self):
        await self._conn.drain()

    async def clear_input_buffer(self):
        return self._conn.clear_input_buffer()


class Connection(aio.Resource):

    def __init__(self, link: Link):
        self._link = link
        self._log = logger.create_logger(mlog, link.info)
        self._comm_log = logger.CommunicationLogger(mlog, link.info)

        self.async_group.spawn(aio.call_on_cancel, self._comm_log.log,
                               common.CommLogAction.CLOSE)
        self._comm_log.log(common.CommLogAction.OPEN)

    @property
    def async_group(self) -> aio.Group:
        return self._link.async_group

    @property
    def info(self) -> tcp.ConnectionInfo | serial.EndpointInfo:
        return self._link.info

    async def send(self, adu: common.Adu):
        self._comm_log.log(common.CommLogAction.SEND, adu)

        adu_bytes = encoder.encode_adu(adu)
        await self._link.write(adu_bytes)

    async def receive(self,
                      modbus_type: common.ModbusType,
                      direction: common.Direction
                      ) -> common.Adu:
        buff = bytearray()

        while True:
            next_adu_size = encoder.get_next_adu_size(modbus_type, direction,
                                                      buff)
            if len(buff) >= next_adu_size:
                break
            buff.extend(await self._link.read(next_adu_size - len(buff)))

        buff = memoryview(buff)
        adu, _ = encoder.decode_adu(modbus_type, direction, buff)

        self._comm_log.log(common.CommLogAction.RECEIVE, adu)

        return adu

    async def drain(self):
        self._log.debug("draining output buffer")
        await self._link.drain()
        self._log.debug("output buffer empty")

    async def clear_input_buffer(self) -> int:
        counter = 0

        while True:
            i = await self._link.clear_input_buffer()
            if not i:
                break
            counter += i

        return counter

    async def read_byte(self) -> bytes:
        return await self._link.read(1)
