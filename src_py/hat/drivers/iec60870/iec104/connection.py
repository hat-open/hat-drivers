import typing

from hat import aio

from hat.drivers.iec60870 import apci
from hat.drivers.iec60870.iec104 import common
from hat.drivers.iec60870.iec104 import encoder


class Connection(aio.Resource):

    def __init__(self, conn: apci.Connection):
        self._conn = conn
        self._encoder = encoder.Encoder()

    @property
    def async_group(self):
        return self._conn.async_group

    def send(self, msgs: typing.List[common.Msg]):
        for data in self._encoder.encode(msgs):
            self._conn.send(data)

    async def drain(self):
        await self._conn.drain()

    async def receive(self) -> typing.List[common.Msg]:
        data = await self._conn.receive()
        return list(self._encoder.decode(data))
