import asyncio
import collections
import contextlib
import logging

import pytest

from hat import aio
from hat.drivers.iec60870.link import endpoint, common
import hat.drivers.serial


class CatchLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.records = collections.deque()

    def emit(self, record):
        self.records.append(record)


@contextlib.contextmanager
def catchlog_queue(logger):
    handler = CatchLogHandler()
    logger.addHandler(handler)
    logger.propagate = False
    try:
        yield handler.records
    finally:
        logger.removeHandler(handler)
        logger.propagate = True


class SerialMock(aio.Resource):

    def __init__(self):
        self._async_group = aio.Group()
        self._read_queue = aio.Queue()
        self._write_queue = aio.Queue()

    @property
    def async_group(self):
        return self._async_group

    async def read(self, size):
        ret = bytearray()
        for _ in range(size):
            ret.append(await self._read_queue.get())
        return ret

    async def write(self, data):
        self._write_queue.put_nowait(data)

    def _set_bytes_for_read(self, data):
        for i in data:
            self._read_queue.put_nowait(i)


async def test_endpoint(monkeypatch):
    serial_queue = aio.Queue()

    async def create_serial_mock(
            port,
            baudrate=9600,
            bytesize=hat.drivers.serial.ByteSize.EIGHTBITS,
            parity=hat.drivers.serial.Parity.NONE,
            stopbits=hat.drivers.serial.StopBits.ONE,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            silent_interval=0):
        serial_conn = SerialMock()
        serial_queue.put_nowait(serial_conn)
        return serial_conn

    with monkeypatch.context() as ctx:
        ctx.setattr(hat.drivers.serial, 'create', create_serial_mock)
        # logger monkeypatched to capture log message
        my_endpoint = await endpoint.create(
            address_size=common.AddressSize.TWO,
            port='port',
            baudrate=1,
            bytesize=hat.drivers.serial.ByteSize.EIGHTBITS,
            parity=hat.drivers.serial.Parity.NONE,
            stopbits=hat.drivers.serial.StopBits.ONE,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False)

        serial_conn = await serial_queue.get()

        frame = common.ReqFrame(
            is_master=True,
            frame_count_bit=False,
            frame_count_valid=False,
            function=common.ReqFunction.REQ_DATA_1,
            address=123,
            data=b'\xab\x12')
        await my_endpoint.send(frame)
        frame_bytes = await serial_conn._write_queue.get()
        assert frame_bytes

        serial_conn._set_bytes_for_read(frame_bytes)
        frame_rec = await my_endpoint.receive()
        assert frame_rec == frame

        # broken frame ignored with error logging
        frame_bytes_broken = bytearray(frame_bytes)[:-1] + bytearray(b'\xe5')
        serial_conn._set_bytes_for_read(bytes(frame_bytes_broken))
        with catchlog_queue(endpoint.mlog) as log_queue:
            with pytest.raises(asyncio.TimeoutError):
                frame_rec = await asyncio.wait_for(my_endpoint.receive(), 0.1)
            record = log_queue.pop()
            assert record.levelno == logging.ERROR

        # unexpected initial bytes are ignored without logging
        serial_conn._set_bytes_for_read(b'\xab\x12')
        with catchlog_queue(endpoint.mlog) as log_queue:
            with pytest.raises(asyncio.TimeoutError):
                frame_rec = await asyncio.wait_for(my_endpoint.receive(), 0.1)
            assert not log_queue

        await my_endpoint.async_close()
        assert my_endpoint.is_closed
