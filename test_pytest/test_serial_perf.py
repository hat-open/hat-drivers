import atexit
import subprocess
import sys
import time

import pytest

from hat.drivers import serial


pytestmark = [pytest.mark.skipif(sys.platform == 'win32',
                                 reason="can't simulate serial"),
              pytest.mark.perf]


@pytest.fixture
def nullmodem(request, tmp_path):
    path1 = tmp_path / '1'
    path2 = tmp_path / '2'
    p = subprocess.Popen(
        ['socat',
         f'pty,link={path1},raw,echo=0',
         f'pty,link={path2},raw,echo=0'])
    while not path1.exists() or not path2.exists():
        time.sleep(0.001)

    def finalizer():
        p.terminate()

    atexit.register(finalizer)
    request.addfinalizer(finalizer)
    return path1, path2, p


@pytest.mark.parametrize("data_count", [1, 10, 100])
@pytest.mark.parametrize("data_size", [1, 10, 100])
async def test_read_write(duration, nullmodem, data_count, data_size):
    endpoint1 = await serial.create(port=str(nullmodem[0]),
                                    rtscts=True,
                                    dsrdtr=True)
    endpoint2 = await serial.create(port=str(nullmodem[1]),
                                    rtscts=True,
                                    dsrdtr=True)

    data = b'x' * data_size
    with duration(f'data_count: {data_count}; data_size: {data_size}'):
        for i in range(data_count):
            await endpoint1.write(data)
            await endpoint2.read(len(data))

    await endpoint1.async_close()
    await endpoint2.async_close()
