import abc
import logging

from hat import aio

from hat.drivers import serial
from hat.drivers import tcp
from hat.drivers.modbus.transport import common
from hat.drivers.modbus.transport import encoder


mlog: logging.Logger = logging.getLogger(__name__)


class Connection(aio.Resource):

    async def send(self, adu: common.Adu):
        mlog.debug("sending adu: %s", adu)
        adu_bytes = encoder.encode_adu(adu)

        if mlog.isEnabledFor(logging.DEBUG):
            mlog.debug("writing bytes: %s", bytes(adu_bytes).hex(' '))

        await self._write(adu_bytes)

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
            buff.extend(await self._read(next_adu_size - len(buff)))

        if mlog.isEnabledFor(logging.DEBUG):
            mlog.debug("received bytes: %s", buff.hex(' '))

        buff = memoryview(buff)
        adu, _ = encoder.decode_adu(modbus_type, direction, buff)

        mlog.debug("received adu: %s", adu)
        return adu

    async def reset_input_buffer(self) -> int:
        counter = 0

        while True:
            i = await self._reset_input_buffer()
            if not i:
                break
            counter += i

        return counter

    @abc.abstractmethod
    async def _write(self, data: common.Bytes):
        pass

    @abc.abstractmethod
    async def _read(self, size: int) -> common.Bytes:
        pass

    @abc.abstractmethod
    async def _reset_input_buffer(self):
        pass


ConnectionCb = aio.AsyncCallable[[Connection], None]


async def serial_create(port: str,
                        **kwargs
                        ) -> Connection:
    endpoint = await serial.create(port, **kwargs)

    mlog.debug("serial endpoint opened: %s", port)
    return _SerialConnection(endpoint)


async def tcp_connect(addr: tcp.Address,
                      **kwargs
                      ) -> Connection:
    conn = await tcp.connect(addr, **kwargs)

    mlog.debug("tcp connection established: %s", conn.info)
    return _TcpConnection(conn)


async def tcp_listen(connection_cb: ConnectionCb,
                     addr: tcp.Address,
                     **kwargs
                     ) -> tcp.Server:

    async def on_connection(conn):
        mlog.debug("new incomming tcp connection: %s", conn.info)
        await aio.call(connection_cb, _TcpConnection(conn))

    server = await tcp.listen(on_connection, addr,
                              bind_connections=True,
                              **kwargs)

    mlog.debug("tcp server listening: %s", server.addresses)
    return server


class _SerialConnection(Connection):

    def __init__(self, endpoint):
        self._endpoint = endpoint

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def _write(self, data):
        await self._endpoint.write(data)

    async def _read(self, size):
        return await self._endpoint.read(size)

    async def _reset_input_buffer(self):
        return await self._endpoint.reset_input_buffer()


class _TcpConnection(Connection):

    def __init__(self, conn):
        self._conn = conn

    @property
    def async_group(self):
        return self._conn.async_group

    async def _write(self, data):
        self._conn.write(data)
        await self._conn.drain()

    async def _read(self, size):
        return await self._conn.readexactly(size)

    async def _reset_input_buffer(self):
        return await self._conn.reset_input_buffer()
