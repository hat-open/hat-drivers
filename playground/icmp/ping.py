import argparse
import asyncio
import contextlib

from hat import aio

from hat.drivers import icmp


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--local-host', type=str, metavar='HOST', default='0.0.0.0',
        help="local host name (default '0.0.0.0')")

    parser.add_argument(
        'remote_host', metavar='HOST',
        help='remote host name')

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args))


async def async_main(args):
    endpoint = await icmp.create_endpoint(args.local_host)

    try:
        await endpoint.ping(args.remote_host)

    finally:
        await aio.uncancellable(endpoint.async_close())


if __name__ == '__main__':
    main()
