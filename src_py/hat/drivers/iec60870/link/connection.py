import abc

from hat import aio
from hat.drivers.iec60870.link import common


ConnectionCb = aio.AsyncCallable[['Connection'], None]


class Connection(aio.Resource):

    @abc.abstractmethod
    async def send(self, data: common.Bytes):
        pass

    @abc.abstractmethod
    async def receive(self) -> common.Bytes:
        pass
