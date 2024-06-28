import asyncio
import contextlib

from hat import aio

from hat.drivers import mms
from hat.drivers import tcp


def main():
    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    addr = tcp.Address('10.13.40.11', 102)

    conn = await mms.connect(addr,
                             local_tsel=1,
                             remote_tsel=1,
                             local_ssel=1,
                             remote_ssel=1,
                             local_psel=1,
                             remote_psel=1)

    try:
        await asyncio.sleep(10)

    finally:
        await aio.uncancellable(conn.async_close())


if __name__ == '__main__':
    main()
