"""Asyncio wrapper for serial communication

.. warning::

    implementation is based on read with timeout for periodical checking
    if connection is closed by user - better way of canceling active read
    operation is needed

"""

import asyncio
import enum
import logging
import typing

import serial

from hat import aio


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

read_timeout: float = 0.5
"""Read timeout"""


Bytes = typing.Union[bytes, bytearray, memoryview]


class ByteSize(enum.Enum):
    FIVEBITS = serial.FIVEBITS
    SIXBITS = serial.SIXBITS
    SEVENBITS = serial.SEVENBITS
    EIGHTBITS = serial.EIGHTBITS


class Parity(enum.Enum):
    NONE = serial.PARITY_NONE
    EVEN = serial.PARITY_EVEN
    ODD = serial.PARITY_ODD
    MARK = serial.PARITY_MARK
    SPACE = serial.PARITY_SPACE


class StopBits(enum.Enum):
    ONE = serial.STOPBITS_ONE
    ONE_POINT_FIVE = serial.STOPBITS_ONE_POINT_FIVE
    TWO = serial.STOPBITS_TWO


async def create(port: str, *,
                 baudrate: int = 9600,
                 bytesize: ByteSize = ByteSize.EIGHTBITS,
                 parity: Parity = Parity.NONE,
                 stopbits: StopBits = StopBits.ONE,
                 xonxoff: bool = False,
                 rtscts: bool = False,
                 dsrdtr: bool = False,
                 silent_interval: float = 0
                 ) -> 'Endpoint':
    """Open serial port

    Args:
        port: port name dependent of operating system
            (e.g. `/dev/ttyUSB0`, `COM3`, ...)
        baudrate: baud rate
        bytesize: number of data bits
        parity: parity checking
        stopbits: number of stop bits
        xonxoff: enable software flow control
        rtscts: enable hardware RTS/CTS flow control
        dsrdtr: enable hardware DSR/DTR flow control
        silent_interval: minimum time in seconds between writing two
            consecutive messages

    """
    endpoint = Endpoint()
    endpoint._port = port
    endpoint._silent_interval = silent_interval
    endpoint._input_buffer = bytearray()
    endpoint._input_cv = asyncio.Condition()
    endpoint._write_queue = aio.Queue()
    endpoint._executor = aio.create_executor()

    endpoint._serial = await endpoint._executor(
        serial.Serial,
        port=port,
        baudrate=baudrate,
        bytesize=bytesize.value,
        parity=parity.value,
        stopbits=stopbits.value,
        xonxoff=xonxoff,
        rtscts=rtscts,
        dsrdtr=dsrdtr,
        timeout=read_timeout)

    endpoint._async_group = aio.Group()
    endpoint._async_group.spawn(aio.call_on_cancel, endpoint._on_close)
    endpoint._async_group.spawn(endpoint._read_loop)
    endpoint._async_group.spawn(endpoint._write_loop)

    return endpoint


class Endpoint(aio.Resource):
    """Serial endpoint

    For creating new instances see `create` coroutine.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def port(self) -> str:
        """Port name"""
        return self._port

    async def read(self, size: int) -> Bytes:
        """Read

        Args:
            size: number of bytes to read

        Raises:
            ConnectionError

        """
        async with self._input_cv:
            while len(self._input_buffer) < size:
                if not self.is_open:
                    raise ConnectionError()
                await self._input_cv.wait()

            if size < 1:
                return b''

            buffer = memoryview(self._input_buffer)
            data, self._input_buffer = buffer[:size], bytearray(buffer[size:])
            return data

    async def write(self, data: Bytes):
        """Write

        Raises:
            ConnectionError

        """
        future = asyncio.Future()
        try:
            self._write_queue.put_nowait((data, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def reset_input_buffer(self) -> int:
        """Reset input buffer

        Returns number of bytes available in buffer immediately before
        buffer was cleared.

        Raises:
            ConnectionError

        """
        async with self._input_cv:
            count = len(self._input_buffer)
            self._input_buffer = bytearray()
            return count

    async def _on_close(self):
        await self._executor(self._ext_close)

        async with self._input_cv:
            self._input_cv.notify_all()

    async def _read_loop(self):
        try:
            while True:
                data_head = await self._executor(self._ext_read, 1)
                if not data_head:
                    continue

                data_rest = await self._executor(self._ext_read, -1)

                async with self._input_cv:
                    self._input_buffer.extend(data_head)
                    if data_rest:
                        self._input_buffer.extend(data_rest)

                    self._input_cv.notify_all()

        except Exception as e:
            mlog.warning('read loop error: %s', e, exc_info=e)

        finally:
            self.close()

    async def _write_loop(self):
        future = None
        try:
            while True:
                data, future = await self._write_queue.get()

                await self._executor(self._ext_write, data)

                if not future.done():
                    future.set_result(None)

                await asyncio.sleep(self._silent_interval)

        except Exception as e:
            mlog.warning('write loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._write_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())
                if self._write_queue.empty():
                    break
                _, future = self._write_queue.get_nowait()

    def _ext_close(self):
        self._serial.close()

    def _ext_read(self, n=-1):
        if n < 0:
            n = self._serial.in_waiting

        if n < 1:
            return b''

        return self._serial.read(n)

    def _ext_write(self, data):
        self._serial.write(data)
        self._serial.flush()
