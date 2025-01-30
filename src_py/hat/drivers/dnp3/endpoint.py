import abc

from hat import aio
from hat import util

from hat.drivers import serial
from hat.drivers import tcp
from hat.drivers import udp


class Endpoint(aio.Resource):

    @abc.abstractmethod
    async def read(self, size: int) -> util.Bytes:
        """Read

        Args:
            size: number of bytes to read

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def write(self, data: util.Bytes):
        """Write

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def drain(self):
        """Drain output buffer

        Raises:
            ConnectionError

        """


class SerialEndpoint(Endpoint):

    def __init__(self, endpoint: serial.Endpoint):
        self._endpoint = endpoint

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def read(self, size):
        return await self._endpoint.read(size)

    async def write(self, data):
        await self._endpoint.write(data)

    async def drain(self):
        await self._endpoint.drain()


class TcpEndpoint(Endpoint):

    def __init__(self, conn: tcp.Connection):
        self._conn = conn

    @property
    def async_group(self):
        return self._conn.async_group

    async def read(self, size):
        return await self._conn.readexactly(size)

    async def write(self, data):
        await self._conn.write(data)

    async def drain(self):
        await self._conn.drain()


class UdpEndpoint(Endpoint):

    def __init__(self, endpoint: udp.Endpoint, remote_addr: udp.Address):
        self._endpoint = endpoint
        self._remote_addr = remote_addr
        self._buff = util.BytesBuffer()

    @property
    def async_group(self):
        return self._conn.async_group

    async def read(self, size):
        while (len(self._buff) < size):
            data, addr = await self._endpoint.receive()
            if addr != self._remote_addr:
                continue

            self._buff.add(data)

        return self._buff.read(size)

    async def write(self, data):
        await self._endpoint.send(data, self._remote_addr)

    async def drain(self):
        pass
