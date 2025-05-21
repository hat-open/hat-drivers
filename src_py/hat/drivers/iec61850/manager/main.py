import argparse
import sys

from hat.drivers.iec61850.manager import device_readout
from hat.drivers.iec61850.manager import file_readout


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action', required=True)

    device_readout.create_argument_parser(subparsers)
    file_readout.create_argument_parser(subparsers)

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.action == 'device-readout':
        device_readout.main(args)

    elif args.action == 'file-readout':
        file_readout.main(args)

    else:
        raise ValueError('unsupported action')


if __name__ == '__main__':
    sys.argv[0] = 'hat-iec61850-manager'
    main()
