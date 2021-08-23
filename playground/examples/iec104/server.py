import asyncio
from hat.drivers import iec104


addr = iec104.Address('127.0.0.1', 23231)


async def main():
    srv = await iec104.listen(on_connection, addr,
                              command_cb=on_command)
    try:
        await asyncio.Future()
    finally:
        await srv.async_close()


async def on_connection(conn):
    print('connected')
    try:
        i = 0
        while True:
            await asyncio.sleep(1)
            i += 1
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
    except ConnectionError:
        pass
    finally:
        print('disconnected')
        await conn.async_close()


async def on_command(conn, cmd):
    print('>> received command', cmd)
    return True


if __name__ == '__main__':
    asyncio.run(main())
