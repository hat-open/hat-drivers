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

    parser.add_argument('--port', metavar='N', type=int, default=102)

    parser.add_argument('--local-tsel', metavar='N', type=int, default=None)
    parser.add_argument('--remote-tsel', metavar='N', type=int, default=None)

    parser.add_argument('--local-ssel', metavar='N', type=int, default=None)
    parser.add_argument('--remote-ssel', metavar='N', type=int, default=None)

    parser.add_argument('--local-psel', metavar='N', type=int, default=None)
    parser.add_argument('--remote-psel', metavar='N', type=int, default=None)

    parser.add_argument('--local-ap-title', metavar='OID',
                        type=(lambda x: tuple(x.split('.'))),
                        default=None)
    parser.add_argument('--remote-ap-title', metavar='OID',
                        type=(lambda x: tuple(x.split('.'))),
                        default=None)

    parser.add_argument('--local-ae-qualifier', metavar='N', type=int,
                        default=None)
    parser.add_argument('--remote-ae-qualifier', metavar='N', type=int,
                        default=None)

    parser.add_argument('--local-detail-calling', metavar='N', type=int,
                        default=None)

    parser.add_argument(
        '--output', metavar='PATH', type=Path, default=Path('-'),
        help="output devices file path or - for stdout (default -)")

    parser.add_argument('host')

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
