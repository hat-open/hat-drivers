import collections
import logging

from hat.drivers.icmp import common


def create_logger(logger: logging.Logger,
                  info: common.EndpointInfo
                  ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'IcmpEndpoint',
                      'name': info.name,
                      'local_host': info.local_host}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: common.EndpointInfo):
        extra = {'meta': {'type': 'IcmpEndpoint',
                          'communication': True,
                          'name': info.name,
                          'local_host': info.local_host}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            msg: common.Msg | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if msg is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_msg(msg),
                            stacklevel=2)


def _format_msg(msg):
    segments = collections.deque()

    if isinstance(msg, common.EchoMsg):
        segments.append('Echo')
        segments.append(f"is_reply={msg.is_reply}")
        segments.append(f"identifier={msg.identifier}")
        segments.append(f"sequence_number={msg.sequence_number}")
        segments.append(f"data=({msg.data.hex(' ')})")

    else:
        raise TypeError('unsupported message type')

    return _format_segments(segments)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
