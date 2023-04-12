"""Implementation based on native serial communication"""

import asyncio
import logging
import sys
import functools

from hat import aio

from hat.drivers.serial import common
from hat.drivers.serial import _native_serial


if sys.platform == 'win32':
    raise ImportError('WIP')


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create(port, *,
                 baudrate=9600,
                 bytesize=common.ByteSize.EIGHTBITS,
                 parity=common.Parity.NONE,
                 stopbits=common.StopBits.ONE,
                 xonxoff=False,
                 rtscts=False,
                 dsrdtr=False,
                 silent_interval=0):
    loop = asyncio.get_running_loop()

    endpoint = Endpoint()
    endpoint._port = port
    endpoint._silent_interval = silent_interval
    endpoint._input_buffer = bytearray()
    endpoint._input_cv = asyncio.Condition()
    endpoint._write_queue = aio.Queue()

    endpoint._serial = _native_serial.Serial(in_buff_size=0xFFFF,
                                             out_buff_size=0xFFFF)

    endpoint._close_cb_future = loop.create_future()
    close_cb = _create_serial_cb(loop, endpoint._close_cb_future)
    endpoint._serial.set_close_cb(close_cb)

    endpoint._serial.open(
        port=port,
        baudrate=baudrate,
        bytesize=bytesize.value,
        parity=parity.value,
        stopbits=(2 if stopbits == common.StopBits.ONE_POINT_FIVE
                  else stopbits.value),
        xonxoff=xonxoff,
        rtscts=rtscts,
        dsrdtr=dsrdtr)

    endpoint._async_group = aio.Group()
    endpoint._async_group.spawn(aio.call_on_done,
                                asyncio.shield(endpoint._close_cb_future),
                                endpoint.close)
    endpoint._async_group.spawn(aio.call_on_cancel, endpoint._on_close)
    endpoint._async_group.spawn(endpoint._read_loop)
    endpoint._async_group.spawn(endpoint._write_loop)

    return endpoint


class Endpoint(common.Endpoint):

    @property
    def async_group(self):
        return self._async_group

    @property
    def port(self):
        return self._port

    async def read(self, size):
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

    async def write(self, data):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        try:
            self._write_queue.put_nowait((data, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def reset_input_buffer(self):
        async with self._input_cv:
            count = len(self._input_buffer)
            self._input_buffer = bytearray()
            return count

    async def _on_close(self):
        self._serial.close()

        await self._close_cb_future

        async with self._input_cv:
            self._input_cv.notify_all()

        self._serial.set_close_cb(None)

    async def _read_loop(self):
        try:
            loop = asyncio.get_running_loop()

            while True:
                in_cb_future = loop.create_future()
                in_cb = _create_serial_cb(loop, in_cb_future)
                self._serial.set_in_cb(in_cb)

                data = self._serial.read()

                if not data:
                    await in_cb_future
                    continue

                self._serial.set_in_cb(None)

                async with self._input_cv:
                    self._input_buffer.extend(data)
                    self._input_cv.notify_all()

        except Exception as e:
            mlog.warning('read loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._serial.set_in_cb(None)

    async def _write_loop(self):
        future = None
        try:
            loop = asyncio.get_running_loop()

            while True:
                data, future = await self._write_queue.get()

                data = memoryview(data)
                while data:
                    out_cb_future = loop.create_future()
                    out_cb = _create_serial_cb(loop, out_cb_future)
                    self._serial.set_out_cb(out_cb)

                    result = self._serial.write(bytes(data))
                    if result < 0:
                        raise Exception('write error')

                    data = data[result:]

                    await out_cb_future

                self._serial.set_out_cb(None)

                if not future.done():
                    future.set_result(None)

                await asyncio.sleep(self._silent_interval)

        except Exception as e:
            mlog.warning('write loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._write_queue.close()
            self._serial.set_out_cb(None)

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())
                if self._write_queue.empty():
                    break
                _, future = self._write_queue.get_nowait()


def _create_serial_cb(loop, future):
    return functools.partial(loop.call_soon_threadsafe, _try_set_result,
                             future, None)


def _try_set_result(future, result):
    if not future.done():
        future.set_result(result)
