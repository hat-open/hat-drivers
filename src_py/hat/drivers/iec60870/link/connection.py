import abc
import typing

from hat import aio
from hat import util


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]


class Connection(aio.Resource):

    @abc.abstractmethod
    async def send(self, data: util.Bytes):
        pass

    @abc.abstractmethod
    async def receive(self) -> util.Bytes:
        pass
