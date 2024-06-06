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
        '-a', choices=['MD5', 'SHA'], metavar='PROTOCOL', dest='auth_protocol',
        default=None,
        help=('authentication protocol'))
    group_v3.add_argument(
        '-A', type=str, metavar='PASSPHRASE', dest='auth_passphrase',
        default=None,
        help=('authentication protocol pass phrase'))
    group_v3.add_argument(
        '-x', choices=['DES'], metavar='PROTOCOL', dest='priv_protocol',
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
    if version == '1':
        manager = await snmp.create_v1_manager(
            remote_addr=udp.Address(
                host=args.host,
                port=args.port),
            community=args.community)

    elif version == '2c':
        manager = await snmp.create_v2c_manager(
            remote_addr=udp.Address(
                host=args.host,
                port=args.port),
            community=args.community)
    elif version == '3':
        manager = await snmp.create_v3_manager(
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
    else:
        raise Exception('unsupported version')

    try:
        request = snmp.GetDataReq(names=[_oid_from_str(args.oid)])
        response = await manager.send(request)
        print(json.encode(_response_to_json(response)))

    finally:
        await aio.uncancellable(manager.async_close())


def _response_to_json(response):
    if response is None:
        return

    if isinstance(response, snmp.Error):
        return f'ERROR {response.index}, {response.type.name}'

    if not response:
        return 'ERROR empty response'

    resp_data = response[0]
    data_type = _data_type_from_response(response)

    if isinstance(resp_data,
                  (snmp.EmptyData,
                   snmp.UnspecifiedData,
                   snmp.NoSuchObjectData,
                   snmp.NoSuchInstanceData,
                   snmp.EndOfMibViewData)):
        return f'ERROR {data_type}'

    if isinstance(resp_data, snmp.Data):
        return {
            'name': _oid_to_str(resp_data.name),
            'type': data_type,
            'value': resp_data.value}

    raise Exception('unexpected response')


def _data_type_from_response(response):
    resp_data = response[0]
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
    main()
