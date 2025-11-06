from hat.drivers.common import *  # NOQA

import collections
import logging


from hat.drivers import serial
from hat.drivers.iec60870.link import common


def create_logger(logger: logging.Logger,
                  info: serial.EndpointInfo
                  ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870Link',
                      'name': info.name,
                      'port': info.port}}

    return logging.LoggerAdapter(logger, extra)


def create_connection_logger(logger: logging.Logger,
                             info: common.ConnectionInfo
                             ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec60870LinkConnection',
                      'name': info.name,
                      'port': info.port,
                      'address': info.address}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: serial.EndpointInfo):
        extra = {'meta': {'type': 'Iec60870Link',
                          'communication': True,
                          'name': info.name,
                          'port': info.port}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            frame: common.Frame | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if frame is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_frame(frame),
                            stacklevel=2)


def _format_frame(frame):
    segments = collections.deque()

    if isinstance(frame, common.ReqFrame):
        segments.append('Req')

        if frame.direction is not None:
            segments.append(f"direction={frame.direction.name}")

        if frame.frame_count_valid:
            segments.append(f"fcb={frame.frame_count_bit}")

        segments.append(f"function={frame.function.name}")
        segments.append(f"addr={frame.address}")
        segments.append(f"data=({frame.data.hex(' ')})")

    elif isinstance(frame, common.ResFrame):
        segments.append('Res')

        if frame.direction is not None:
            segments.append(f"direction={frame.direction.name}")

        if frame.access_demand:
            segments.append('access_demand')

        if frame.data_flow_control:
            segments.append('data_flow_control')

        segments.extend(f"function={frame.function.name}")
        segments.append(f"addr={frame.address}")
        segments.append(f"data=({frame.data.hex(' ')})")

    elif isinstance(frame, common.ShortFrame):
        segments.append('Res')
        segments.append('short')

    else:
        raise TypeError('unsupported frame type')

    return f"({' '.join(segments)})"
