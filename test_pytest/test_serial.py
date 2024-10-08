import asyncio
import sys

import pytest

from hat.drivers import serial


pytestmark = pytest.mark.skipif(sys.platform == 'win32',
                                reason="can't simulate serial")

implementations = [serial.native_serial,
                   serial.py_serial]


@pytest.mark.parametrize('impl', implementations)
async def test_create(nullmodem, impl):
    endpoint = await impl.create(port=str(nullmodem[0]))
    assert not endpoint.is_closed
    await endpoint.async_close()
    assert endpoint.is_closed


@pytest.mark.parametrize('impl', implementations)
async def test_read_write(nullmodem, impl):
    endpoint1 = await impl.create(port=str(nullmodem[0]))
    endpoint2 = await impl.create(port=str(nullmodem[1]))

    data = b'test1\x00'
    await endpoint1.write(data)
    await endpoint1.drain()
    assert data == await endpoint2.read(len(data))

    data = b'test2\x00'
    await endpoint2.write(data)
    await endpoint2.drain()
    assert data == await endpoint1.read(len(data))

    await endpoint1.async_close()
    await endpoint2.async_close()

    with pytest.raises(ConnectionError):
        await endpoint1.read(1)

    with pytest.raises(ConnectionError):
        await endpoint2.write(b'')


@pytest.mark.parametrize('impl', implementations)
async def test_close_while_reading(nullmodem, impl):
    endpoint = await impl.create(port=str(nullmodem[0]))

    read_future = asyncio.ensure_future(endpoint.read(1))

    await endpoint.async_close()

    with pytest.raises(ConnectionError):
        read_future.result()


@pytest.mark.parametrize('impl', implementations)
async def test_close_nullmodem(nullmodem, impl):
    endpoint = await impl.create(port=str(nullmodem[0]))

    read_future = asyncio.ensure_future(endpoint.read(1))

    nullmodem[2].terminate()

    with pytest.raises(ConnectionError):
        await read_future

    await endpoint.async_close()
