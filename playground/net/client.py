from pathlib import Path
import asyncio
import contextlib
import itertools

from hat import aio

from hat.drivers import net


addr = Path(__file__).parent / 'socket'
# addr = net.TcpAddress('127.0.0.1', 1234)


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    conn = await net.connect(addr)

    try:
        print('>> conn info', conn.info)

        conn.async_group.spawn(read_loop, conn)
        conn.async_group.spawn(write_loop, conn)

        await conn.wait_closing()

    finally:
        await aio.uncancellable(conn.async_close())


async def read_loop(conn):
    try:
        while True:
            data = await conn.read()
            print(data.decode())

    except ConnectionError:
        pass

    finally:
        conn.close()


async def write_loop(conn):
    try:
        for i in itertools.count(0):
            await conn.write(f'client {i}'.encode())
            await asyncio.sleep(1)

    except ConnectionError:
        pass

    finally:
        conn.close()


if __name__ == '__main__':
    main()
