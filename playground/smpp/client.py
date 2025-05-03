import argparse
import asyncio
import contextlib
import sys

from hat import aio

from hat.drivers import smpp
from hat.drivers import tcp


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--port', type=int, metavar='PORT', default=2775,
        help="remote TCP port (default 2775)")

    parser.add_argument(
        '--system-id', type=str, metavar='SYSTEM_ID', default='',
        help="local system id (default '')")

    parser.add_argument(
        '--password', type=str, metavar='PASSWORD', default='',
        help="password (default '')")

    parser.add_argument(
        '--msg', type=str, metavar='MESSAGE', default=None,
        help="message content (instead reading from stdin)")

    parser.add_argument(
        '--long-msg', action='store_true',
        help="send long message payload")

    parser.add_argument(
        '--priority', default='BULK', type=str,
        choices=[i.name for i in smpp.Priority],
        help="priority (default 'BULK')")

    parser.add_argument(
        'host', metavar='HOST',
        help='remote host name')

    parser.add_argument(
        'addr', metavar='ADDR',
        help='destination address')

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    msg_str = sys.stdin.read() if args.msg is None else args.msg
    msg_bytes = msg_str.encode('ascii')

    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args, msg_bytes))


async def async_main(args, msg_bytes):
    client = await smpp.connect(addr=tcp.Address(args.host, args.port),
                                system_id=args.system_id,
                                password=args.password)

    try:
        msg_id = await client.send_message(
            dst_addr=args.addr,
            msg=msg_bytes,
            short_message=not args.long_msg,
            priority=smpp.Priority[args.priority])
        print(msg_id.hex())

    finally:
        await aio.uncancellable(client.async_close())


if __name__ == '__main__':
    main()
