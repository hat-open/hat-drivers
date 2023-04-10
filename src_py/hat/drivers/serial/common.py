import abc
import enum
import typing

from hat import aio


Bytes = typing.Union[bytes, bytearray, memoryview]


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


class Endpoint(aio.Resource):
    """Serial endpoint"""

    @property
    @abc.abstractmethod
    def port(self) -> str:
        """Port name"""

    @abc.abstractmethod
    async def read(self, size: int) -> Bytes:
        """Read

        Args:
            size: number of bytes to read

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def write(self, data: Bytes):
        """Write

        Raises:
            ConnectionError

        """

    @abc.abstractmethod
    async def reset_input_buffer(self) -> int:
        """Reset input buffer

        Returns number of bytes available in buffer immediately before
        buffer was cleared.

        Raises:
            ConnectionError

        """
