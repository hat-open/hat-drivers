import collections
import logging

from hat import aio

from hat.drivers.iec101 import common
from hat.drivers.iec101 import encoder
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
        self._comm_log = _create_logger_adapter(True, conn.info)

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    @property
    def info(self) -> link.ConnectionInfo:
        return self._conn.info

    async def send(self,
                   msgs: list[common.Msg],
                   sent_cb: aio.AsyncCallable[[], None] | None = None):
        self._comm_log.debug('sending %s', msgs)

        data = collections.deque(self._encoder.encode(msgs))

        while data:
            i = data.popleft()
            await self._conn.send(i, sent_cb=None if data else sent_cb)

    async def receive(self) -> list[common.Msg]:
        data = await self._conn.receive()
        msgs = list(self._encoder.decode(data))

        self._comm_log.debug('received %s', msgs)

        return msgs


def _create_logger_adapter(communication, info):
    extra = {'meta': {'type': 'Iec101Connection',
                      'communication': communication,
                      'name': info.name,
                      'port': info.port,
                      'address': info.address}}

    return logging.LoggerAdapter(mlog, extra)
