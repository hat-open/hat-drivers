import asyncio
import contextlib

from pprint import pprint

from hat import aio
from hat.drivers import cdt


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


def on_event(name, data):
    print('>>>', name)
    pprint(data)


async def async_main():
    conn = await cdt.connect('127.0.0.1', 22222)

    conn.register_event_cb(on_event)

    target = await cdt.createTarget(conn)
    session = await target.attach()
    runtime = cdt.Runtime(session)

    await runtime.enable()

    res = await runtime.evaluate('JSON.stringify([1, 2, 3, 4])')
    pprint(res)

    await target.close()

    await conn.async_close()


if __name__ == '__main__':
    main()
