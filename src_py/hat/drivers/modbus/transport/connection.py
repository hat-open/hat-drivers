import abc
import logging

from hat import aio
from hat import util

from hat.drivers import serial
from hat.drivers import tcp
from hat.drivers.modbus.transport import common
from hat.drivers.modbus.transport import encoder


mlog: logging.Logger = logging.getLogger(__name__)


class Connection(aio.Resource):

    @property
    @abc.abstractmethod
    def log_prefix(self) -> str:
        pass

    async def send(self, adu: common.Adu):
        self._log(logging.DEBUG, "sending adu: %s", adu)
        adu_bytes = encoder.encode_adu(adu)

        if mlog.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, "writing bytes: %s",
                      bytes(adu_bytes).hex(' '))

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
            self._log(logging.DEBUG, "received bytes: %s", buff.hex(' '))

        buff = memoryview(buff)
        adu, _ = encoder.decode_adu(modbus_type, direction, buff)

        self._log(logging.DEBUG, "received adu: %s", adu)
        return adu

    async def drain(self):
        self._log(logging.DEBUG, "draining output buffer")
        await self._drain()
        self._log(logging.DEBUG, "output buffer empty")

    async def reset_input_buffer(self) -> int:
        counter = 0

        while True:
            i = await self._reset_input_buffer()
            if not i:
                break
            counter += i

        return counter

    async def read_byte(self) -> bytes:
        return await self._read(1)

    def _log(self, level, msg, *args, **kwargs):
        if not mlog.isEnabledFor(level):
            return

        mlog.log(level, f"{self.log_prefix}: {msg}", *args, **kwargs)

    @abc.abstractmethod
    async def _write(self, data: util.Bytes):
        pass

    @abc.abstractmethod
    async def _read(self, size: int) -> util.Bytes:
        pass

    @abc.abstractmethod
    async def _reset_input_buffer(self):
        pass


ConnectionCb = aio.AsyncCallable[[Connection], None]


async def serial_create(port: str,
                        **kwargs
                        ) -> Connection:
    endpoint = await serial.create(port, **kwargs)

    mlog.debug("serial endpoint opened: %s", endpoint.port)
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
        self._log_prefix = f'serial port {endpoint.port}'

    @property
    def async_group(self):
        return self._endpoint.async_group

    @property
    def log_prefix(self):
        return self._log_prefix

    async def _write(self, data):
        await self._endpoint.write(data)

    async def _read(self, size):
        return await self._endpoint.read(size)

    async def _drain(self):
        await self._endpoint.drain()

    async def _reset_input_buffer(self):
        return await self._endpoint.reset_input_buffer()


class _TcpConnection(Connection):

    def __init__(self, conn):
        self._conn = conn
        self._log_prefix = (
            f'tcp local ('
            f'{conn.info.local_addr.host}:{conn.info.local_addr.port}'
            f') remote ('
            f'{conn.info.remote_addr.host}:{conn.info.remote_addr.port})')

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def log_prefix(self):
        return self._log_prefix

    async def _write(self, data):
        await self._conn.write(data)

    async def _read(self, size):
        return await self._conn.readexactly(size)

    async def _drain(self):
        await self._conn.drain()

    async def _reset_input_buffer(self):
        return self._conn.reset_input_buffer()
