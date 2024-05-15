import argparse
import asyncio
import contextlib

from hat import aio
from hat import json
from hat.drivers import snmp
from hat.drivers import udp


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'host', type=str, metavar='HOST',
        help='agent host')
    parser.add_argument(
        'oid', type=str, metavar='OID',
        help='oid')

    parser.add_argument(
        '-p', '--port', type=int,
        default=161,
        help='agent port, defaults to 161')
    parser.add_argument(
        '-v', '--version', choices=['1', '2c', '3'],
        default='2c',
        help=('SNMP version: 1, 2c or 3, defaults to 2c'))

    group_v1_2c = parser.add_argument_group('Version 1 or 2c specific')
    group_v1_2c.add_argument(
        '-c', type=str, metavar='COMMUNITY', dest='community',
        default='public',
        help=("community, defaults to 'public'"))

    group_v3 = parser.add_argument_group('Version 3 specific')
    group_v3.add_argument(
        '-n', type=str, metavar='CONTEXT', dest='context_name',
        default='',
        help=('context name, defaults to empty string'))
    group_v3.add_argument(
        '-u', type=str, metavar='USER-NAME', dest='user_name',
        default='',
        help=('user security name, defaults to empty string'))
    group_v3.add_argument(
        '-E', metavar='ENGINE-ID', type=str, dest='context_engine_id',
        default='',
        help=('context engineID used for SNMPv3, defaults to empty string'))
    group_v3.add_argument(
        '-l', choices=['noAuthNoPriv', 'authNoPriv', 'authPriv'],
        metavar='LEVEL', dest='level',
        default=None,
        help=('authentication protocol'))
    group_v3.add_argument(
        '-a', choices=['md5', 'sha'], metavar='PROTOCOL', dest='auth_protocol',
        default=None,
        help=('authentication protocol'))
    group_v3.add_argument(
        '-A', type=str, metavar='PASSPHRASE', dest='auth_passphrase',
        default=None,
        help=('authentication protocol pass phrase'))
    group_v3.add_argument(
        '-x', choices=['des', 'aes'], metavar='PROTOCOL', dest='priv_protocol',
        default=None,
        help=('privacy protocol'))
    group_v3.add_argument(
        '-X', type=str, metavar='PASSPHRASE', dest='priv_passphrase',
        default=None,
        help=('privacy protocol pass phrase'))

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args))


async def async_main(args):
    version = args.version
    if version == '3':
        context = snmp.Context(
            engine_id=args.context_engine_id,
            name=args.context_name)
    else:
        context = snmp.Context(
            engine_id=None,
            name=args.community)

    manager = await snmp.create_manager(
                        context=context,
                        remote_addr=udp.Address(
                            host=args.host,
                            port=args.port),
                        version=snmp.Version[f"V{args.version.upper()}"])
    try:
        request = snmp.GetDataReq(names=[_oid_from_str(args.oid)])
        result = await manager.send(request)
        print(json.encode([_response_to_json(resp) for resp in result]))

    finally:
        await aio.uncancellable(manager.async_close())


def _response_to_json(response):
    if response is None:
        return

    if isinstance(response, snmp.Error):
        return f'ERROR {response.index}, {response.type.name}'

    if isinstance(response, snmp.Data):
        return {
            'name': _oid_to_str(response.name),
            'type': response.type.name,
            'value': response.value}

    raise Exception('unexpected response')


def _oid_from_str(oid_str):
    return tuple(int(i) for i in oid_str.split('.'))


def _oid_to_str(oid):
    return '.'.join(str(i) for i in oid)


if __name__ == '__main__':
    main()
