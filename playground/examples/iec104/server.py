import asyncio
from hat.drivers import tcp
from hat.drivers import iec104


addr = tcp.Address('127.0.0.1', 23231)


async def main():
    srv = await iec104.listen(on_connection, addr)

    try:
        await asyncio.Future()

    finally:
        await srv.async_close()


async def on_connection(conn):
    print('>> connected')
    try:
        conn.async_group.spawn(send_loop, conn)
        conn.async_group.spawn(receive_loop, conn)

        await conn.wait_closing()

    finally:
        print('>> disconnected')
        await conn.async_close()


async def send_loop(conn):
    try:
        i = 0
        while True:
            await asyncio.sleep(1)

            i += 1
            msg = iec104.DataMsg(
                is_test=False,
                originator_address=0,
                asdu_address=123,
                io_address=321,
                data=iec104.ScaledData(
                    value=iec104.ScaledValue(i),
                    quality=iec104.MeasurementQuality(
                        invalid=False,
                        not_topical=False,
                        substituted=False,
                        blocked=False,
                        overflow=False)),
                time=None,
                cause=iec104.DataResCause.SPONTANEOUS)

            print('>> sending')
            conn.send([msg])

    except ConnectionError:
        pass

    finally:
        conn.close()


async def receive_loop(conn):
    try:
        while True:
            msgs = await conn.receive()
            print('>> received', msgs)

    except ConnectionError:
        pass

    finally:
        conn.close()


if __name__ == '__main__':
    asyncio.run(main())
