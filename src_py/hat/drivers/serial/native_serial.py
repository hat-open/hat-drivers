"""Implementation based on native serial communication"""

import asyncio
import contextlib
import functools
import logging
import sys

from hat import aio
from hat import util

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
    endpoint = Endpoint()
    endpoint._port = port
    endpoint._silent_interval = silent_interval
    endpoint._loop = asyncio.get_running_loop()
    endpoint._input_buffer = util.BytesBuffer()
    endpoint._input_cv = asyncio.Condition()
    endpoint._write_queue = aio.Queue()

    endpoint._serial = _native_serial.Serial(in_buff_size=0xFFFF,
                                             out_buff_size=0xFFFF)

    endpoint._close_cb_future = endpoint._loop.create_future()
    close_cb = endpoint._create_serial_cb(endpoint._close_cb_future)
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

            return self._input_buffer.read(size)

    async def write(self, data):
        future = self._loop.create_future()
        try:
            self._write_queue.put_nowait((data, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def drain(self):
        future = self._loop.create_future()
        try:
            self._write_queue.put_nowait((None, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def reset_input_buffer(self):
        async with self._input_cv:
            return self._input_buffer.clear()

    async def _on_close(self):
        self._serial.close()

        await self._close_cb_future

        async with self._input_cv:
            self._input_cv.notify_all()

        self._serial.set_close_cb(None)

    async def _read_loop(self):
        try:
            while True:
                with self._create_in_change_future() as change_future:

                    data = self._serial.read()

                    if not data:
                        await change_future
                        continue

                async with self._input_cv:
                    self._input_buffer.add(data)
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

                if data is None:
                    with self._create_drain_future() as drain_future:
                        self._serial.drain()

                        await drain_future

                else:
                    data = memoryview(data)
                    while data:
                        with self._create_out_change_future() as change_future:
                            result = self._serial.write(bytes(data))
                            if result < 0:
                                raise Exception('write error')

                            data = data[result:]

                            if data:
                                await change_future

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

    @contextlib.contextmanager
    def _create_in_change_future(self):
        with self._create_serial_future(self._serial.set_in_change_cb) as f:
            yield f

    @contextlib.contextmanager
    def _create_out_change_future(self):
        with self._create_serial_future(self._serial.set_out_change_cb) as f:
            yield f

    @contextlib.contextmanager
    def _create_drain_future(self):
        with self._create_serial_future(self._serial.set_drain_cb) as f:
            yield f

    @contextlib.contextmanager
    def _create_serial_future(self, serial_set_cb):
        future = self._loop.create_future()
        cb = self._create_serial_cb(future)
        serial_set_cb(cb)

        try:
            yield future

        finally:
            serial_set_cb(None)

    def _create_serial_cb(self, future):
        return functools.partial(self._loop.call_soon_threadsafe,
                                 _try_set_result, future, None)


def _try_set_result(future, result):
    if not future.done():
        future.set_result(result)
