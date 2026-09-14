from pathlib import Path
import asyncio
import contextlib
import itertools

from hat import aio

from hat.drivers import net


addr = Path(__file__).parent / 'socket'
# addr = net.UdpAddress('127.0.0.1', 1234)


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    conn = await net.create_endpoint(net.DatagramType.UNIX,
                                     remote_addr=addr)

    try:
        conn.async_group.spawn(send_loop, conn)

        await conn.wait_closing()

    finally:
        await aio.uncancellable(conn.async_close())


async def send_loop(conn):
    try:
        for i in itertools.count(0):
            conn.send(str(i).encode())
            await asyncio.sleep(1)

    except ConnectionError:
        pass

    finally:
        conn.close()


if __name__ == '__main__':
    main()
