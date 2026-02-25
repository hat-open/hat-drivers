import asyncio
import contextlib

from hat import aio
from hat.drivers import iec104


addr = iec104.Address('127.0.0.1', 23231)


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    srv = await iec104.listen(on_connection, addr,
                              interrogate_cb=on_interrogate,
                              counter_interrogate_cb=on_counter_interrogate,
                              command_cb=on_command)
    try:
        await asyncio.Future()
    finally:
        await srv.async_close()


async def on_connection(conn):
    print('connected')
    try:
        await connection_loop_3(conn)
    except ConnectionError:
        pass
    finally:
        print('disconnected')
        await conn.async_close()


async def connection_loop_1(conn):
    await conn.wait_closing()


async def connection_loop_2(conn):
    for i in range(10):
        data = iec104.Data(value=iec104.ScaledValue(i),
                           quality=iec104.Quality(invalid=False,
                                                  not_topical=False,
                                                  substituted=False,
                                                  blocked=False,
                                                  overflow=False),
                           time=None,
                           asdu_address=123,
                           io_address=321,
                           cause=iec104.Cause.SPONTANEOUS,
                           is_test=False)
        conn.notify_data_change([data])
        await asyncio.sleep(1)


async def connection_loop_3(conn):
    await conn.wait_closing()


async def connection_loop_4(conn):
    await conn.wait_closing()


async def on_interrogate(conn, asdu_address):
    data = iec104.Data(value=iec104.DoubleValue.ON,
                       quality=iec104.Quality(invalid=False,
                                              not_topical=False,
                                              substituted=False,
                                              blocked=False,
                                              overflow=False),
                       time=None,
                       asdu_address=asdu_address,
                       io_address=321,
                       cause=iec104.Cause.INTERROGATED_STATION,
                       is_test=False)
    return [data]


async def on_counter_interrogate(conn, asdu_address):
    return None


async def on_command(conn, cmd):
    print('on command')
    print('>> cmd', cmd)
    return False

if __name__ == '__main__':
    main()
