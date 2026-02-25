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
    conn = await iec104.connect(addr)
    print('connected')
    try:
        await connection_loop_4(conn)
    except ConnectionError:
        pass
    finally:
        print('disconnected')
        await conn.async_close()


async def connection_loop_1(conn):
    await conn.wait_closing()


async def connection_loop_2(conn):
    while True:
        data = await conn.receive()
        print('received data')
        for i in data:
            print('>>', i)


async def connection_loop_3(conn):
    result = await conn.interrogate(1)
    print('>>', result)


async def connection_loop_4(conn):
    cmd = iec104.Command(action=iec104.Action.EXECUTE,
                         value=iec104.SingleValue.ON,
                         time=None,
                         asdu_address=123,
                         io_address=321,
                         qualifier=0)
    result = await conn.send_command(cmd)
    print('>>', result)


if __name__ == '__main__':
    main()
