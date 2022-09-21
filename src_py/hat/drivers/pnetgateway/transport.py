from hat import aio
from hat import json
from hat.drivers import tcp


class Transport(aio.Resource):

    def __init__(self, conn: tcp.Connection):
        self._conn = conn

    @property
    def async_group(self):
        return self._conn.async_group

    async def receive(self) -> json.Data:
        size_bytes = await self._conn.readexactly(4)
        size = int.from_bytes(size_bytes, 'big')
        msg_bytes = await self._conn.readexactly(size)
        msg_str = msg_bytes.decode('utf-8')
        msg = json.decode(msg_str)
        return msg

    def send(self, msg: json.Data):
        msg_str = json.encode(msg)
        msg_bytes = msg_str.encode('utf-8')
        size = len(msg_bytes)
        size_bytes = size.to_bytes(4, 'big')
        self._conn.write(size_bytes + msg_bytes)
