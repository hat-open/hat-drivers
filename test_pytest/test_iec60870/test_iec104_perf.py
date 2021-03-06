import asyncio
import datetime

import pytest

from hat import aio
from hat import util
from hat.drivers import tcp
from hat.drivers.iec60870 import apci
from hat.drivers.iec60870 import iec104


pytestmark = pytest.mark.perf


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.mark.parametrize("window_size", [1, 10, 100])
@pytest.mark.parametrize("data_count", [1, 100, 10000])
async def test_data_sequence(duration, addr, window_size, data_count):

    msg = iec104.DataMsg(
        is_test=False,
        originator_address=0,
        asdu_address=123,
        io_address=321,
        data=iec104.DoubleData(
            value=iec104.DoubleValue.ON,
            quality=iec104.IndicationQuality(
                invalid=False,
                not_topical=False,
                substituted=False,
                blocked=False)),
        time=iec104.time_from_datetime(datetime.datetime.now()),
        cause=iec104.DataResCause.SPONTANEOUS)

    conn2_future = asyncio.Future()
    srv = await apci.listen(conn2_future.set_result, addr,
                            send_window_size=window_size + 1,
                            receive_window_size=window_size - 1)
    conn1 = await apci.connect(addr,
                               send_window_size=window_size + 1,
                               receive_window_size=window_size - 1)
    conn2 = await conn2_future

    conn1 = iec104.Connection(conn1)
    conn2 = iec104.Connection(conn2)

    with duration(f'data count: {data_count}; window_size: {window_size}'):
        for _ in range(data_count):
            conn1.send([msg])
            await conn2.receive()

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()


@pytest.mark.parametrize("window_size", [1, 10, 100])
@pytest.mark.parametrize("data_count", [1, 100, 10000])
async def test_data_paralel(duration, addr, window_size, data_count):

    msg = iec104.DataMsg(
        is_test=False,
        originator_address=0,
        asdu_address=123,
        io_address=321,
        data=iec104.DoubleData(
            value=iec104.DoubleValue.ON,
            quality=iec104.IndicationQuality(
                invalid=False,
                not_topical=False,
                substituted=False,
                blocked=False)),
        time=iec104.time_from_datetime(datetime.datetime.now()),
        cause=iec104.DataResCause.SPONTANEOUS)

    conn2_future = asyncio.Future()
    srv = await apci.listen(conn2_future.set_result, addr,
                            send_window_size=window_size + 1,
                            receive_window_size=window_size - 1)
    conn1 = await apci.connect(addr,
                               send_window_size=window_size + 1,
                               receive_window_size=window_size - 1)
    conn2 = await conn2_future

    conn1 = iec104.Connection(conn1)
    conn2 = iec104.Connection(conn2)

    async def producer(conn):
        for _ in range(data_count):
            conn.send([msg])

    async def consumer(conn):
        for _ in range(data_count):
            await conn.receive()

    async_group = aio.Group()
    with duration(f'data count: {data_count}; window_size: {window_size}'):
        async_group.spawn(producer, conn1)
        async_group.spawn(consumer, conn2)
        await async_group.async_close(cancel=False)

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()
