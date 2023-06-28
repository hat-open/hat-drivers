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

    async def send(self,
                   msgs: typing.List[common.Msg],
                   wait_ack: bool = False):
        data = collections.deque(self._encoder.encode(msgs))
        while data:
            head = data.popleft()
            head_wait_ack = False if data else wait_ack
            await self._conn.send(head, head_wait_ack)

    async def drain(self, wait_ack: bool = False):
        await self._conn.drain(wait_ack)

    async def receive(self) -> typing.List[common.Msg]:
        data = await self._conn.receive()
        return list(self._encoder.decode(data))
