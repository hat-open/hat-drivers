import sys

import pytest

from hat.drivers import serial


pytestmark = [pytest.mark.skipif(sys.platform == 'win32',
                                 reason="can't simulate serial"),
              pytest.mark.perf]

implementations = [serial.native_serial,
                   serial.py_serial]


@pytest.mark.parametrize('impl', implementations)
@pytest.mark.parametrize("data_count", [1, 10, 100])
@pytest.mark.parametrize("data_size", [1, 10, 100])
async def test_read_write(duration, nullmodem, impl, data_count, data_size):
    endpoint1 = await impl.create(port=str(nullmodem[0]),
                                  rtscts=True,
                                  dsrdtr=True)
    endpoint2 = await impl.create(port=str(nullmodem[1]),
                                  rtscts=True,
                                  dsrdtr=True)

    data = b'x' * data_size
    with duration(f'implementation: {impl.__name__}; '
                  f'data_count: {data_count}; '
                  f'data_size: {data_size}'):
        for i in range(data_count):
            await endpoint1.write(data)
            await endpoint2.read(len(data))

    await endpoint1.async_close()
    await endpoint2.async_close()
