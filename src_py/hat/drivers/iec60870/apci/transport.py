import logging

from hat import aio

from hat.drivers import ssl
from hat.drivers import tcp
from hat.drivers.iec60870.apci import common
from hat.drivers.iec60870.apci import encoder


mlog: logging.Logger = logging.getLogger(__name__)


class Transport(aio.Resource):

    def __init__(self, conn: tcp.Connection):
        self._conn = conn
        self._comm_log = _create_logger_adapter(True, conn.info)

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

        self._comm_log.debug('received %s', apdu)

        return apdu

    async def write(self, apdu: common.APDU):
        self._comm_log.debug('sending %s', apdu)

        data = encoder.encode(apdu)
        await self._conn.write(data)


def _create_logger_adapter(communication, info):
    extra = {'meta': {'type': 'Iec60870ApciTransport',
                      'communication': communication,
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(mlog, extra)
