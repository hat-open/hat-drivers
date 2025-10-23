import collections
import logging
import typing

from hat.drivers.iec104 import encoder
from hat.drivers.iec104.connection import common
from hat.drivers.iec60870 import apci


mlog: logging.Logger = logging.getLogger(__name__)


class RegularConnection(common.Connection):

    def __init__(self, conn: apci.Connection):
        self._conn = conn
        self._encoder = encoder.Encoder()
        self._comm_log = common.create_logger_adapter(mlog, True, conn.info)

    @property
    def conn(self) -> apci.Connection:
        return self._conn

    async def send(self,
                   msgs: typing.List[common.Msg],
                   wait_ack: bool = False):
        self._comm_log.debug('sending %s', msgs)

        data = collections.deque(self._encoder.encode(msgs))
        while data:
            head = data.popleft()
            head_wait_ack = False if data else wait_ack
            await self._conn.send(head, head_wait_ack)

    async def drain(self, wait_ack: bool = False):
        await self._conn.drain(wait_ack)

    async def receive(self) -> typing.List[common.Msg]:
        data = await self._conn.receive()
        msgs = list(self._encoder.decode(data))

        self._comm_log.debug('received %s', msgs)

        return msgs
