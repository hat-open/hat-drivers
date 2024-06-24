import argparse
import asyncio
import contextlib
import sys

from hat import aio
from hat import json

from hat.drivers import snmp
from hat.drivers import udp


string_decode = 'utf-8'


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p', type=int, metavar='PORT', dest='port',
        default=161,
        help='agent UDP port, defaults to 161')
    parser.add_argument(
        '-v', choices=['1', '2c', '3'], metavar='VERSION', dest='version',
        default='2c',
        help='SNMP version, defaults to 2c (versions: 1, 2c, 3)')
    parser.add_argument(
        '--string-decode', choices=['utf-8', 'hex'],
        default='utf-8',
        help='way of representing string')

    group_v1_2c = parser.add_argument_group('version 1 or 2c specific')
    group_v1_2c.add_argument(
        '-c', type=str, metavar='COMMUNITY', dest='community',
        default='public',
        help="community, defaults to 'public'")

    group_v3 = parser.add_argument_group('version 3 specific')
    group_v3.add_argument(
        '-n', type=str, metavar='CONTEXT', dest='context_name',
        default='',
        help='context name, defaults to empty string')
    group_v3.add_argument(
        '-u', type=str, metavar='USER-NAME', dest='user_name',
        default='public',
        help="user security name, defaults to 'public'")
    group_v3.add_argument(
        '-E', metavar='ENGINE-ID', type=str, dest='context_engine_id',
        default='',
        help='context engineID, defaults to empty string')
    group_v3.add_argument(
        '-a', choices=['MD5', 'SHA'], metavar='PROTOCOL', dest='auth_protocol',
        default=None,
        help='use authentication (protocols: MD5, SHA)')
    group_v3.add_argument(
        '-A', type=str, metavar='PASSPHRASE', dest='auth_passphrase',
        default=None,
        help='authentication pass phrase')
    group_v3.add_argument(
        '-x', choices=['DES'], metavar='PROTOCOL', dest='priv_protocol',
        default=None,
        help='use privacy (protocols: DES)')
    group_v3.add_argument(
        '-X', type=str, metavar='PASSPHRASE', dest='priv_passphrase',
        default=None,
        help='privacy protocol pass phrase')

    parser.add_argument(
        'host', type=str, metavar='HOST',
        help='agent hostname')

    subparsers = parser.add_subparsers(
        dest='action', required=True,
        help='available snmp commands')

    subparser_get = subparsers.add_parser(
        'get',
        help='snmp get on specific oid')
    subparser_get.add_argument(
        'oid', type=str, metavar='OID',
        help='object id')

    subparser_getnext = subparsers.add_parser(
        'getnext',
        help='snmp get next on specific oid')
    subparser_getnext.add_argument(
        'oid', type=str, metavar='OID',
        help='object id')

    subparsers.add_parser(
        'walk',
        help='retrieve entire snmp device tree')

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    global string_decode
    string_decode = args.string_decode

    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args))


async def async_main(args):
    manager = await _create_manager(args)

    try:
        if args.action == 'get':
            results = _get(manager, args.oid)

        elif args.action == 'getnext':
            results = _get_next(manager, args.oid)

        elif args.action == 'walk':
            results = _walk(manager)

        else:
            raise Exception('unknown action')

        async for res in results:
            print(json.encode(res))

    finally:
        await aio.uncancellable(manager.async_close())


async def _create_manager(args):
    version = args.version
    if version == '1':
        return await snmp.create_v1_manager(
            remote_addr=udp.Address(
                host=args.host,
                port=args.port),
            community=args.community)

    if version == '2c':
        return await snmp.create_v2c_manager(
            remote_addr=udp.Address(
                host=args.host,
                port=args.port),
            community=args.community)

    if version == '3':
        return await snmp.create_v3_manager(
            remote_addr=udp.Address(
                host=args.host,
                port=args.port),
            context=snmp.Context(
                engine_id=args.context_engine_id,
                name=args.context_name) if args.context_engine_id else None,
            user=snmp.User(
                name=args.user_name,
                auth_type=(snmp.AuthType[args.auth_protocol]
                           if args.auth_protocol else None),
                auth_password=(args.auth_passphrase
                               if args.auth_protocol else None),
                priv_type=(snmp.PrivType[args.priv_protocol]
                           if args.priv_protocol else None),
                priv_password=(args.priv_passphrase
                               if args.priv_protocol else None)))

    raise Exception('unsupported version')


class _EndOfMib(Exception):
    """End of Mib exception"""


async def _get(manager, oid):
    request = snmp.GetDataReq(names=[_oid_from_str(oid)])
    response = await manager.send(request)
    for i in _response_to_json(response):
        yield i


async def _get_next(manager, oid):
    request = snmp.GetNextDataReq(names=[_oid_from_str(oid)])
    response = await manager.send(request)
    for i in _response_to_json(response):
        yield i


async def _walk(manager):
    next_name = (0, 0)
    with contextlib.suppress(_EndOfMib):
        while True:
            request = snmp.GetNextDataReq(names=[next_name])
            response = await manager.send(request)
            for i in _response_to_json(response):
                yield i

            next_name = response[-1].name


def _response_to_json(response):
    if not response:
        raise Exception('ERROR: no data')

    if isinstance(response, snmp.Error):
        raise Exception(f'ERROR {response.index}, {response.type.name}')

    for resp_data in response:
        if isinstance(resp_data,
                      snmp.EndOfMibViewData):
            raise _EndOfMib()

        if isinstance(resp_data,
                      (snmp.EmptyData,
                       snmp.UnspecifiedData,
                       snmp.NoSuchObjectData,
                       snmp.NoSuchInstanceData)):
            data_type = _data_type_from_data(resp_data)
            raise Exception(f'ERROR on {resp_data.name} {data_type}')

        if isinstance(resp_data, snmp.Data):
            yield _data_to_json(resp_data)

        else:
            raise Exception('unexpected response data')


def _data_to_json(data):
    return {
        'name': _oid_to_str(data.name),
        'type': _data_type_from_data(data),
        'value': _value_to_json(data)}


def _value_to_json(data):
    if isinstance(data, snmp.StringData):
        if string_decode == 'utf-8':
            return str(data.value, encoding='utf-8', errors='replace')

        return data.value.hex()

    if isinstance(data, snmp.ArbitraryData):
        return data.value.hex()

    if isinstance(data, (snmp.ObjectIdData, snmp.IpAddressData)):
        return _oid_to_str(data.value)

    return data.value


def _data_type_from_data(resp_data):
    if isinstance(resp_data, snmp.IntegerData):
        return 'INTEGER'
    if isinstance(resp_data, snmp.UnsignedData):
        return 'UNSIGNED'
    if isinstance(resp_data, snmp.CounterData):
        return 'COUNTER'
    if isinstance(resp_data, snmp.BigCounterData):
        return 'BIG_COUNTER'
    if isinstance(resp_data, snmp.TimeTicksData):
        return 'TIME_TICKS'
    if isinstance(resp_data, snmp.StringData):
        return 'STRING'
    if isinstance(resp_data, snmp.ObjectIdData):
        return 'OBJECT_ID'
    if isinstance(resp_data, snmp.IpAddressData):
        return 'IP_ADDRESS'
    if isinstance(resp_data, snmp.ArbitraryData):
        return 'ARBITRARY'

    if isinstance(resp_data, snmp.EmptyData):
        return 'EMPTY'
    if isinstance(resp_data, snmp.UnspecifiedData):
        return 'UNSPECIFIED'
    if isinstance(resp_data, snmp.NoSuchObjectData):
        return 'NO_SUCH_OBJECT'
    if isinstance(resp_data, snmp.NoSuchInstanceData):
        return 'NO_SUCH_INSTANCE'
    if isinstance(resp_data, snmp.EndOfMibViewData):
        return 'END_OF_MIB_VIEW'

    raise Exception('unexpected data type')


def _oid_from_str(oid_str):
    return tuple(int(i) for i in oid_str.split('.'))


def _oid_to_str(oid):
    return '.'.join(str(i) for i in oid)


if __name__ == '__main__':
    sys.argv[0] = 'hat-snmp-manager'
    main()
