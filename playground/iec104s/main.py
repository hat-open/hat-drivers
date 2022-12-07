import contextlib
import asyncio

from hat import aio


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    pass


if __name__ == '__main__':
    main()
