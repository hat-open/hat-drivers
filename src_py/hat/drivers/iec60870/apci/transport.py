import logging

from hat import aio

from hat.drivers import ssl
from hat.drivers import tcp
from hat.drivers.iec60870.apci import common
from hat.drivers.iec60870.apci import encoder
from hat.drivers.iec60870.apci import logger


mlog: logging.Logger = logging.getLogger(__name__)


class Transport(aio.Resource):

    def __init__(self, conn: tcp.Connection):
        self._conn = conn
        self._comm_log = logger.CommunicationLogger(mlog, conn.info)

        self.async_group.spawn(aio.call_on_cancel, self._comm_log.log,
                               common.CommLogAction.CLOSE)
        self._comm_log.log(common.CommLogAction.OPEN)

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        return self._conn.info

    @property
    def ssl_object(self) -> ssl.SSLObject | ssl.SSLSocket | None:
        return self._conn.ssl_object

    async def drain(self):
        await self._conn.drain()

    async def read(self) -> common.APDU:
        data = bytearray()

        while True:
            size = encoder.get_next_apdu_size(data)
            if size <= len(data):
                break
            data.extend(await self._conn.readexactly(size - len(data)))

        apdu = encoder.decode(memoryview(data))

        self._comm_log.log(common.CommLogAction.RECEIVE, apdu)

        return apdu

    async def write(self, apdu: common.APDU):
        data = encoder.encode(apdu)

        self._comm_log.log(common.CommLogAction.SEND, apdu)

        await self._conn.write(data)
