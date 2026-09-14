import typing

from hat import aio

from hat.drivers import net
from hat.drivers.mqtt.transport import common
from hat.drivers.mqtt.transport import encoder


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]


async def connect(addr: net.StreamAddress,
                  **kwargs
                  ) -> 'Connection':
    conn = await net.connect(addr, **kwargs)

    return Connection(conn)


async def listen(connection_cb: ConnectionCb,
                 addr: net.StreamAddress,
                 **kwargs
                 ) -> net.Server:

    async def on_connection(conn):
        await aio.call(connection_cb, Connection(conn))

    srv = await net.listen(on_connection, addr, **kwargs)

    return srv


class Connection(aio.Resource):

    def __init__(self, conn: net.Connection):
        self._conn = conn

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def info(self) -> net.ConnectionInfo:
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
