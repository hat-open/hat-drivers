import abc

from hat import aio

from hat.drivers import serial
from hat.drivers import tcp
from hat.drivers.modbus.transport import common
from hat.drivers.modbus.transport import encoder


class Connection(aio.Resource):

    async def send(self, adu: common.Adu):
        adu_bytes = bytes(encoder.encode_adu(adu))
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

        buff = memoryview(buff)
        adu, _ = encoder.decode_adu(modbus_type, direction, buff)
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
    return _SerialConnection(endpoint)


async def tcp_connect(addr: tcp.Address,
                      **kwargs
                      ) -> Connection:
    conn = await tcp.connect(addr, **kwargs)
    return _TcpConnection(conn)


async def tcp_listen(connection_cb: ConnectionCb,
                     addr: tcp.Address,
                     **kwargs
                     ) -> tcp.Server:

    async def on_connection(conn):
        await aio.call(connection_cb, _TcpConnection(conn))

    return await tcp.listen(on_connection, addr,
                            bind_connections=True,
                            **kwargs)


class _SerialConnection(Connection):

    def __init__(self, endpoint):
        self._endpoint = endpoint

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def _write(self, data):
        await self._endpoint.write(bytes(data))

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
        self._conn.write(bytes(data))
        await self._conn.drain()

    async def _read(self, size):
        return await self._conn.readexactly(size)

    async def _reset_input_buffer(self):
        return await self._conn.reset_input_buffer()
