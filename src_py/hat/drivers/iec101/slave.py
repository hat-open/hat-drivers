import collections

from hat import aio

from hat.drivers.iec101 import common
from hat.drivers.iec101 import encoder
from hat.drivers.iec60870.link import unbalanced


class SlaveConnection(aio.Resource):

    def __init__(self,
                 conn: unbalanced.SlaveConnection,
                 cause_size: common.CauseSize,
                 asdu_address_size: common.AsduAddressSize,
                 io_address_size: common.IoAddressSize):
        self._conn = conn
        self._encoder = encoder.Encoder(cause_size=cause_size,
                                        asdu_address_size=asdu_address_size,
                                        io_address_size=io_address_size)

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def address(self) -> common.Address:
        return self._conn.address

    def send(self,
             msgs: list[common.Msg],
             sent_cb: aio.AsyncCallable[[], None] | None = None):
        data = collections.deque(self._encoder.encode(msgs))
        while data:
            i = data.popleft()
            self._conn.send(i, sent_cb=None if data else sent_cb)

    async def receive(self) -> list[common.Msg]:
        data = await self._conn.receive()
        return list(self._encoder.decode(data))
