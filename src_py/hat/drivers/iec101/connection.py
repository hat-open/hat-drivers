import collections
import logging

from hat import aio

from hat.drivers.iec101 import common
from hat.drivers.iec101 import encoder
from hat.drivers.iec101 import logger
from hat.drivers.iec60870 import link


mlog: logging.Logger = logging.getLogger(__name__)


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
        self._comm_log = logger.CommunicationLogger(mlog, conn.info)

        self.async_group.spawn(aio.call_on_cancel, self._comm_log.log,
                               common.CommLogAction.CLOSE)
        self._comm_log.log(common.CommLogAction.OPEN)

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    @property
    def info(self) -> link.ConnectionInfo:
        return self._conn.info

    async def send(self,
                   msgs: list[common.Msg],
                   sent_cb: aio.AsyncCallable[[], None] | None = None):
        self._comm_log.log(common.CommLogAction.SEND, msgs)

        data = collections.deque(self._encoder.encode(msgs))

        while data:
            i = data.popleft()
            await self._conn.send(i, sent_cb=None if data else sent_cb)

    async def receive(self) -> list[common.Msg]:
        data = await self._conn.receive()
        msgs = list(self._encoder.decode(data))

        self._comm_log.log(common.CommLogAction.RECEIVE, msgs)

        return msgs
