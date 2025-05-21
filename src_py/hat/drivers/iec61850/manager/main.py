import argparse
import logging.config
import sys

from hat.drivers.iec61850.manager import device_readout
from hat.drivers.iec61850.manager import file_readout


default_log_level: str = 'INFO'


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-level', metavar='LEVEL', default=default_log_level,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help=f"console log level (default {default_log_level})")

    subparsers = parser.add_subparsers(dest='action', required=True)
    device_readout.create_argument_parser(subparsers)
    file_readout.create_argument_parser(subparsers)

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'console_formater': {
                'format': '[%(asctime)s %(levelname)s %(name)s] %(message)s'}},
        'handlers': {
            'console_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'console_formater',
                'level': args.log_level}},
        'root': {
            'level': args.log_level,
            'handlers': ['console_handler']},
        'disable_existing_loggers': False})

    if args.action == 'device-readout':
        device_readout.main(args)

    elif args.action == 'file-readout':
        file_readout.main(args)

    else:
        raise ValueError('unsupported action')


if __name__ == '__main__':
    sys.argv[0] = 'hat-iec61850-manager'
    main()
