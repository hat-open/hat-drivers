import logging

from hat.drivers import tcp
from hat.drivers.iec60870.apci import common


def create_server_logger(logger: logging.Logger,
                         name: str | None,
                         info: tcp.ServerInfo | None
                         ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870ApciServer',
                      'name': name}}

    if info is not None:
        extra['meta']['addresses'] = [{'host': addr.host,
                                       'port': addr.port}
                                      for addr in info.addresses]

    return logging.LoggerAdapter(logger, extra)


def create_connection_logger(logger: logging.Logger,
                             info: tcp.ConnectionInfo
                             ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870ApciConnection',
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: tcp.ConnectionInfo):
        extra = {'meta': {'type': 'Iec60870ApciTransport',
                          'communication': True,
                          'name': info.name,
                          'local_addr': {'host': info.local_addr.host,
                                         'port': info.local_addr.port},
                          'remote_addr': {'host': info.remote_addr.host,
                                          'port': info.remote_addr.port}}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            apdu: common.APDU | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if apdu is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_apdu(apdu),
                            stacklevel=2)


def _format_apdu(apdu):
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
