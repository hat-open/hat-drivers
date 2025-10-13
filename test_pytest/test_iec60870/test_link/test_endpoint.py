import asyncio
import collections
import contextlib
import logging

import pytest

from hat import aio

from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import endpoint
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


@pytest.fixture
async def serial_mock_queue(monkeypatch):
    serial_queue = aio.Queue()

    async def create_serial_mock(*args, **kwargs):
        serial_mock = SerialMock()
        serial_queue.put_nowait((serial_mock, kwargs))
        return serial_mock

    monkeypatch.setattr(hat.drivers.serial, 'create', create_serial_mock)
    return serial_queue


class SerialMock(aio.Resource):

    def __init__(self):
        self._async_group = aio.Group()
        self._read_queue = aio.Queue()
        self._write_queue = aio.Queue()

    @property
    def async_group(self):
        return self._async_group

    @property
    def info(self):
        return serial.EndpointInfo(name=None,
                                   port='')

    async def read(self, size):
        ret = bytearray()
        while len(ret) < size:
            ret.append(await self._read_queue.get())
        return ret

    async def write(self, data):
        self._write_queue.put_nowait(data)

    async def drain(self):
        pass

    def _set_bytes_for_read(self, data):
        for i in data:
            self._read_queue.put_nowait(i)


def replace_byte_at_idx(data, index, byte):
    return data[:index] + byte + data[index + 1:]


async def test_endpoint(serial_mock_queue):
    serial_kwargs_in = dict(
        baudrate=1,
        bytesize=hat.drivers.serial.ByteSize.EIGHTBITS,
        parity=hat.drivers.serial.Parity.NONE,
        stopbits=hat.drivers.serial.StopBits.ONE,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False)
    my_endpoint = await endpoint.create(
        port='port',
        address_size=common.AddressSize.TWO,
        direction_valid=True,
        **serial_kwargs_in)

    serial_conn, serial_kwargs = await serial_mock_queue.get()
    assert isinstance(serial_conn, SerialMock)
    assert serial_kwargs_in == serial_kwargs

    frame = common.ReqFrame(
        direction=common.Direction.B_TO_A,
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

    my_endpoint.close()
    await my_endpoint.wait_closed()
    assert my_endpoint.is_closed


def data_bytes_frames_received_log():
    noise = b'\x00\x01\xab\xff'
    short = b'\xe5'
    fixed = b'\x10\x49\x01\x4a\x16'
    variable = b'\x68\x05\x05\x68\x43\x70\xab\xff\x12\x6f\x16'
    yield (noise, 0, 0)
    yield (short, 1, 0)
    yield (noise + short + noise + short + short, 3, 0)

    yield (noise + fixed + noise, 1, 0)
    yield (noise + fixed + noise + fixed, 2, 0)
    yield (noise + variable + noise + variable + noise, 2, 0)
    fixed_invalid_end = replace_byte_at_idx(fixed, len(fixed) - 1, b'\xab')
    yield (fixed_invalid_end, 0, 1)
    fixed_invalid_crc = replace_byte_at_idx(fixed, len(fixed) - 2, b'\x4b')
    yield (fixed_invalid_crc, 0, 1)
    fixed_invalid_start = replace_byte_at_idx(fixed, 0, b'\x09')
    yield (fixed_invalid_start, 0, 0)
    yield (fixed_invalid_crc + fixed_invalid_end + fixed, 1, 2)
    yield (fixed_invalid_start + fixed, 1, 0)

    yield (variable, 1, 0)
    yield (noise + variable + noise + variable, 2, 0)
    variable_invalid_end = replace_byte_at_idx(
        variable, len(variable) - 1, b'\xab')
    yield (variable_invalid_end, 0, 1)
    variable_invalid_crc = replace_byte_at_idx(
        variable, len(variable) - 2, b'\x6e')
    yield (variable_invalid_crc, 0, 1)
    yield (variable_invalid_crc + noise + variable_invalid_end +
           noise + variable_invalid_crc, 0, 3)
    variable_invalid_length = replace_byte_at_idx(variable, 1, b'\x06')
    yield (variable_invalid_length, 0, 0)
    yield (variable_invalid_length + noise + variable, 1, 0)
    variable_invalid_start = replace_byte_at_idx(variable, 0, b'\x67')
    yield (variable_invalid_start, 0, 0)
    variable_invalid_repeated_start = replace_byte_at_idx(variable, 3, b'\x67')
    yield (variable_invalid_repeated_start, 0, 0)
    yield (noise + variable_invalid_start +
           noise + variable_invalid_repeated_start +
           noise + variable_invalid_crc +
           noise + variable +
           noise + variable_invalid_length, 1, 1)

    data_bytes = (noise + variable +
                  noise + fixed +
                  noise + fixed_invalid_crc +
                  noise + fixed_invalid_start +
                  noise + variable_invalid_end +
                  variable)
    yield (data_bytes, 3, 2)


@pytest.mark.parametrize("data_bytes, frames_received, logs",
                         data_bytes_frames_received_log())
async def test_endpoint_receive_noise(
        serial_mock_queue, data_bytes, frames_received, logs):
    my_endpoint = await endpoint.create(
        port='abc',
        address_size=common.AddressSize.ONE,
        direction_valid=None)

    serial_conn, _ = await serial_mock_queue.get()

    # broken frame ignored with error logging
    # frame_bytes_broken = bytearray(frame_bytes)[:-1] + bytearray(b'\xe5')
    serial_conn._set_bytes_for_read(data_bytes)
    with catchlog_queue(endpoint.mlog) as log_queue:
        if frames_received:
            # received expected number of frames
            for _ in range(frames_received):
                frame = await my_endpoint.receive()
                assert isinstance(frame, (common.ReqFrame,
                                          common.ResFrame,
                                          common.ShortFrame))
        else:
            # no frame is expected
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(my_endpoint.receive(), 0.1)
        # assert expected logging
        if logs:
            # expected error log message
            for _ in range(logs):
                record = log_queue.pop()
                assert record.levelno == logging.ERROR
        else:
            # no logging expected
            assert not log_queue

    await my_endpoint.async_close()
    assert my_endpoint.is_closed
