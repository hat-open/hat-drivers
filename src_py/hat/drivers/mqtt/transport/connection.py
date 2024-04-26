import typing

from hat import aio

from hat.drivers import tcp
from hat.drivers.mqtt.transport import common
from hat.drivers.mqtt.transport import encoder


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]


async def connect(addr: tcp.Address,
                  **kwargs
                  ) -> 'Connection':
    conn = await tcp.connect(addr, **kwargs)

    return Connection(conn)


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address,
                 **kwargs) -> tcp.Server:

    async def on_connection(conn):
        await aio.call(connection_cb, Connection(conn))

    srv = await tcp.listen(on_connection, addr, **kwargs)

    return srv


class Connection(aio.Resource):

    def __init__(self, conn: tcp.Connection):
        self._conn = conn

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        return self._conn.info

    async def send(self, packet: common.Packet):
        packet_bytes = encoder.encode_packet(packet)
        await self._conn.write(packet_bytes)

    async def receive(self) -> common.Packet:
        data = bytearray()

        while True:
            next_packet_size = encoder.get_next_packet_size(memoryview(data))
            remaining_len = next_packet_size - len(data)
            if remaining_len < 1:
                break

            remaining = await self._conn.readexactly(remaining_len)
            data.extend(remaining)

        return encoder.decode_packet(memoryview(data))
