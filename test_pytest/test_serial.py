import asyncio
import atexit
import subprocess
import sys
import time

import pytest

from hat.drivers import serial


pytestmark = pytest.mark.skipif(sys.platform == 'win32',
                                reason="can't simulate serial")


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


async def test_create(nullmodem):
    endpoint = await serial.create(port=str(nullmodem[0]),
                                   rtscts=True,
                                   dsrdtr=True)
    assert not endpoint.is_closed
    await endpoint.async_close()
    assert endpoint.is_closed


async def test_read_write(nullmodem):
    endpoint1 = await serial.create(port=str(nullmodem[0]),
                                    rtscts=True,
                                    dsrdtr=True)
    endpoint2 = await serial.create(port=str(nullmodem[1]),
                                    rtscts=True,
                                    dsrdtr=True)

    data = b'test1'
    await endpoint1.write(data)
    assert data == await endpoint2.read(len(data))

    data = b'test2'
    await endpoint2.write(data)
    assert data == await endpoint1.read(len(data))

    await endpoint1.async_close()
    await endpoint2.async_close()

    with pytest.raises(ConnectionError):
        await endpoint1.read(1)

    with pytest.raises(ConnectionError):
        await endpoint2.write(b'')


async def test_close_while_reading(nullmodem):
    endpoint = await serial.create(port=str(nullmodem[0]),
                                   rtscts=True,
                                   dsrdtr=True)

    read_future = asyncio.ensure_future(endpoint.read(1))

    await endpoint.async_close()

    with pytest.raises(ConnectionError):
        read_future.result()


async def test_close_nullmodem(nullmodem):
    endpoint = await serial.create(port=str(nullmodem[0]),
                                   rtscts=True,
                                   dsrdtr=True)

    read_future = asyncio.ensure_future(endpoint.read(1))
    write_future = asyncio.ensure_future(endpoint.write(b'123'))

    nullmodem[2].terminate()

    with pytest.raises(ConnectionError):
        await read_future

    with pytest.raises(ConnectionError):
        await write_future

    await endpoint.async_close()
