from pathlib import Path
import asyncio
import contextlib

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
                                     local_addr=addr)

    try:
        conn.async_group.spawn(receive_loop, conn)

        await conn.wait_closing()

    finally:
        await aio.uncancellable(conn.async_close())


async def receive_loop(conn):
    try:
        while True:
            data, addr = await conn.receive()
            print(addr, data.hex(' '))

    except ConnectionError:
        pass

    finally:
        conn.close()


if __name__ == '__main__':
    main()
