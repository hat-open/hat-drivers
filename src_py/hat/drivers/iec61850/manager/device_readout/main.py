from pathlib import Path
import argparse
import asyncio
import contextlib
import logging
import sys

from hat import aio
from hat import json

from hat.drivers import tcp
from hat.drivers.iec61850.manager.device_readout.readout import readout


mlog: logging.Logger = logging.getLogger(__name__)


def create_argument_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser('device-readout')

    parser.add_argument(
        '--port', metavar='N', type=int, default=102,
        help="remote TCP port (default 102)")

    parser.add_argument(
        '--local-tsel', metavar='N', type=int, default=1, nargs='?',
        help="local tsel (if set without argument, tsel is not used) "
             "(default 1)")

    parser.add_argument(
        '--remote-tsel', metavar='N', type=int, default=1, nargs='?',
        help="remote tsel (if set without argument, tsel is not used) "
             "(default 1)")

    parser.add_argument(
        '--local-ssel', metavar='N', type=int, default=1, nargs='?',
        help="local ssel (if set without argument, ssel is not used) "
             "(default 1)")

    parser.add_argument(
        '--remote-ssel', metavar='N', type=int, default=1, nargs='?',
        help="remote ssel (if set without argument, ssel is not used) "
             "(default 1)")

    parser.add_argument(
        '--local-psel', metavar='N', type=int, default=1, nargs='?',
        help="local psel (if set without argument, psel is not used) "
             "(default 1)")

    parser.add_argument(
        '--remote-psel', metavar='N', type=int, default=1, nargs='?',
        help="remote psel (if set without argument, psel is not used) "
             "(default 1)")

    parser.add_argument(
        '--local-ap-title', metavar='OID', default=None,
        type=(lambda x: tuple(int(i) for i in x.split('.'))),
        help="local AP title (default not set)")

    parser.add_argument(
        '--remote-ap-title', metavar='OID', default=None,
        type=(lambda x: tuple(int(i) for i in x.split('.'))),
        help="remote AP title (default not set)")

    parser.add_argument(
        '--local-ae-qualifier', metavar='N', type=int, default=None,
        help="local AE qualifier (default not set)")

    parser.add_argument(
        '--remote-ae-qualifier', metavar='N', type=int, default=None,
        help="remote AE qualifier (default not set)")

    parser.add_argument(
        '--local-detail-calling', metavar='N', type=int, default=None,
        help="local detail calling (default not set)")

    parser.add_argument(
        '--output', metavar='PATH', type=Path, default=Path('-'),
        help="output devices file path or - for stdout (default -)")

    parser.add_argument(
        'host',
        help="remote host name or IP address")

    return parser


def main(args):
    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args))


async def async_main(args):
    try:
        device_conf = await readout(
            addr=tcp.Address(args.host, args.port),
            local_tsel=args.local_tsel,
            remote_tsel=args.remote_tsel,
            local_ssel=args.local_ssel,
            remote_ssel=args.remote_ssel,
            local_psel=args.local_psel,
            remote_psel=args.remote_psel,
            local_ap_title=args.local_ap_title,
            remote_ap_title=args.remote_ap_title,
            local_ae_qualifier=args.local_ae_qualifier,
            remote_ae_qualifier=args.remote_ae_qualifier,
            local_detail_calling=args.local_detail_calling)

    except Exception as e:
        mlog.error('readout error: %s', e, exc_info=e)
        return

    try:
        if args.output == Path('-'):
            json.encode_stream(device_conf, sys.stdout)

        else:
            json.encode_file(device_conf, args.output)

    except Exception as e:
        mlog.error('write output error: %s', e, exc_info=e)
