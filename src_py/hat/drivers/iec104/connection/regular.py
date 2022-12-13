import collections
import typing

from hat.drivers.iec104 import common
from hat.drivers.iec104 import encoder
from hat.drivers.iec60870 import apci


class RegularConnection(common.Connection):

    def __init__(self, conn: apci.Connection):
        self._conn = conn
        self._encoder = encoder.Encoder()

    @property
    def conn(self) -> apci.Connection:
        return self._conn

    def send(self, msgs: typing.List[common.Msg]):
        for data in self._encoder.encode(msgs):
            self._conn.send(data)

    async def send_wait_ack(self, msgs: typing.List[common.Msg]):
        data = collections.deque(self._encoder.encode(msgs))
        if not data:
            return

        last = data.pop()
        for i in data:
            self._conn.send(i)

        await self._conn.send_wait_ack(last)

    async def drain(self, wait_ack: bool = False):
        await self._conn.drain(wait_ack)

    async def receive(self) -> typing.List[common.Msg]:
        data = await self._conn.receive()
        return list(self._encoder.decode(data))
