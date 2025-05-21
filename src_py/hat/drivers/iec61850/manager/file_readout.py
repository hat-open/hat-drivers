from pathlib import Path
import argparse
import logging
import sys
import typing

from hat import json

from hat.drivers.iec61850.manager import common


mlog: logging.Logger = logging.getLogger(__name__)


def create_argument_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser('file-readout')

    parser.add_argument(
        '--output', metavar='PATH', type=Path, default=Path('-'),
        help="output devices file path or - for stdout (default -)")

    parser.add_argument(
        'source', type=Path, default=Path('-'), nargs='?',
        help="input source file path or - for stdin (default -)")

    return parser


def main(args):
    source = args.source if args.source != Path('-') else sys.stdin

    device_confs = readout(source)

    if args.output == Path('-'):
        json.encode_stream(device_confs, sys.stdout)

    else:
        json.encode_file(device_confs, args.output)


def readout(source: typing.TextIO | Path
            ) -> dict[common.IedName, common.DeviceConf]:
    pass
