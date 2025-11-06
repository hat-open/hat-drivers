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
        self._comm_log = _CommunicationLogger(conn.info)

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


class _CommunicationLogger:

    def __init__(self, info: tcp.ConnectionInfo):
        extra = {'meta': {'type': 'Iec60870ApciTransport',
                          'communication': True,
                          'name': info.name,
                          'local_addr': {'host': info.local_addr.host,
                                         'port': info.local_addr.port},
                          'remote_addr': {'host': info.remote_addr.host,
                                          'port': info.remote_addr.port}}}

        self._log = logging.LoggerAdapter(mlog, extra)

    def log(self,
            action: common.CommLogAction,
            apdu: common.APDU | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if apdu is None:
            self._log.debug(action.value)

        else:
            self._log.debug('%s %s', action.value, _format_comm_log_apdu(apdu))


def _format_comm_log_apdu(apdu):
    if isinstance(apdu, common.APDUI):
        return (f"(APDUI "
                f"ssn={apdu.ssn} "
                f"rsn={apdu.rsn} "
                f"data=({apdu.data.hex(' ')}))")

    if isinstance(apdu, common.APDUS):
        return f"(APDUS rsn={apdu.rsn})"

    if isinstance(apdu, common.APDUU):
        return f"(APDUU function={apdu.function.name})"

    raise TypeError('unsupported apdu type')
