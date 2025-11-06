from hat.drivers.common import *  # NOQA

import abc
import enum
import logging
import typing

from hat import aio
from hat import util

from hat.drivers.common import CommLogAction


class ByteSize(enum.Enum):
    FIVEBITS = 5
    SIXBITS = 6
    SEVENBITS = 7
    EIGHTBITS = 8


class Parity(enum.Enum):
    NONE = 'N'
    EVEN = 'E'
    ODD = 'O'
    MARK = 'M'
    SPACE = 'S'


class StopBits(enum.Enum):
    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2


class EndpointInfo(typing.NamedTuple):
    name: str | None
    port: str


class Endpoint(aio.Resource):
    """Serial endpoint"""

    @property
    @abc.abstractmethod
    def info(self) -> EndpointInfo:
        """Endpoint info"""

    @abc.abstractmethod
    async def read(self, size: int) -> util.Bytes:
        """Read

        Args:
            size: number of bytes to read

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def write(self, data: util.Bytes):
        """Write

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def drain(self):
        """Drain output buffer

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def clear_input_buffer(self) -> int:
        """Reset input buffer

        Returns number of bytes available in buffer immediately before
        buffer was cleared.

        Raises:
            ConnectionError

        """


def create_logger(logger: logging.Logger,
                  info: EndpointInfo
                  ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'SerialEndpoint',
                      'name': info.name,
                      'port': info.port}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: EndpointInfo):
        extra = {'meta': {'type': 'UdpEndpoint',
                          'communication': True,
                          'name': info.name,
                          'port': info.port}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: CommLogAction,
            *data: util.Bytes):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if not data:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s (%s)',
                            action.value, ' '.join(i.hex(' ') for i in data),
                            stacklevel=2)
