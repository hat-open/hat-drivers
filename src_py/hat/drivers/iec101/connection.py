import typing

from hat import aio

from hat.drivers.iec101 import common
from hat.drivers.iec101 import encoder
from hat.drivers.iec60870 import link


class Connection(aio.Resource):

    def __init__(self,
                 conn: link.Connection,
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

    async def send(self, msgs: typing.List[common.Msg]):
        for data in self._encoder.encode(msgs):
            await self._conn.send(data)

    async def receive(self) -> typing.List[common.Msg]:
        data = await self._conn.receive()
        return list(self._encoder.decode(data))
