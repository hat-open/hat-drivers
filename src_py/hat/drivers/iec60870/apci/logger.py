import collections
import logging

from hat.drivers import net
from hat.drivers.iec60870.apci import common


def create_server_logger(logger: logging.Logger,
                         info: net.ServerInfo
                         ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870ApciServer',
                      **net.server_info_to_json(info)}}

    return logging.LoggerAdapter(logger, extra)


def create_connection_logger(logger: logging.Logger,
                             info: net.ConnectionInfo
                             ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870ApciConnection',
                      **net.connection_info_to_json(info)}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: net.ConnectionInfo):
        self._log = create_connection_logger(logger=logger,
                                             info=info)
        self._log.extra['meta']['communication'] = True

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
    segments = collections.deque()

    segments.append(type(apdu).__name__)

    if isinstance(apdu, common.APDUI):
        segments.append(f"ssn={apdu.ssn}")
        segments.append(f"rsn={apdu.rsn}")
        segments.append(f"data=({apdu.data.hex(' ')})")

    elif isinstance(apdu, common.APDUS):
        segments.append(f"rsn={apdu.rsn}")

    elif isinstance(apdu, common.APDUU):
        segments.append(f"function={apdu.function.name}")

    else:
        raise TypeError('unsupported apdu type')

    return _format_segments(segments)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
