import traceback

import click

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


@click.command()
@click.option('-v', '--version', default='v1',
              type=click.Choice(['v1', 'v2c', 'v3'], case_sensitive=False),
              help='SNMP version')
@click.option('-h', '--host', required=True, help='remote host address')
@click.option('-p', '--port', default=161, type=int, help='remote port')
@click.option('-c', '--community', default='public', help='SNMP community')
@click.option('-o', '--outputs', default=['results'],
              type=click.Choice(['results', 'errors', 'info'],
                                case_sensitive=False), multiple=True,
              help='different outputs (multiple outputs possible)')
def main(version, host, port, community, outputs):
    aio.init_asyncio()
    aio.run_asyncio(async_main(version, host, port, community,
                               outputs))


async def async_main(version, host, port, community, outputs):
    if version.lower() == 'v1':
        await walk_v1(host, port, community, outputs)
    if version.lower() == 'v2c':
        await walk_v2c(host, port, community, outputs)
    if version.lower() == 'v3':
        await walk_v3(host, port, community, outputs)


def output(outputs, msg):
    error_type = msg.pdu.error.type
    if error_type is not common.ErrorType.NO_ERROR:
        if 'errors' in outputs:
            print(msg.pdu.error)
        return
    for data in msg.pdu.data:
        data_name = '.'.join(str(i) for i in data.name)
        data_type = data.type.name
        data_value = {
                common.DataType.OBJECT_ID: lambda: '.'.join(
                    str(i) for i in data.value),
                common.DataType.IP_ADDRESS: lambda: '.'.join(
                    str(i) for i in data.value)
            }.get(data.type, lambda: data.value)()
        if 'results' in outputs:
            print(f'oid: {data_name}, type: {data_type}, value: {data_value}')


def record_info(info, msg):
    error_type = msg.pdu.error.type
    if error_type is not common.ErrorType.NO_ERROR:
        et_str = error_type.name
        count = info['errors'].get(et_str, 0)
        info['errors'].update({et_str: count + 1})
        return

    data_count = len(msg.pdu.data)
    dc_str = str(data_count)
    count = info['data_count'].get(dc_str, 0)
    info['data_count'].update({dc_str: count + 1})

    for data in msg.pdu.data:
        data_type = data.type.name
        count = info['data_types'].get(data_type, 0)
        info['data_types'].update({data_type: count + 1})


def output_info(outputs, info):
    if 'info' in outputs:
        print(info)


async def walk_v1(host, port, community, outputs):
    endpoint = await udp.create(local_addr=None,
                                remote_addr=(host, port))
    request_id = 0
    name = (0, 0)
    info = {'data_count': {}, 'data_types': {}, 'errors': {}}
    while True:
        data = common.Data(type=common.DataType.EMPTY,
                           name=name,
                           value=None)
        pdu = encoder.v1.BasicPdu(request_id=request_id,
                                  error=common.Error(
                                      type=common.ErrorType.NO_ERROR,
                                      index=0),
                                  data=[data])
        req_msg = encoder.v1.Msg(type=encoder.v1.MsgType.GET_NEXT_REQUEST,
                                 community=community,
                                 pdu=pdu)
        req_msg_bytes = encoder.encode(req_msg)
        endpoint.send(req_msg_bytes)
        res_msg_bytes, addr = await endpoint.receive()
        try:
            res_msg = encoder.decode(res_msg_bytes)
            record_info(info, res_msg)
            output(outputs, res_msg)
            error_type = res_msg.pdu.error.type
            if error_type is not common.ErrorType.NO_ERROR:
                break
            name = res_msg.pdu.data[-1].name
            request_id += 1
        except Exception:
            print(traceback.format_exec())
            break
    output_info(outputs, info)
    await endpoint.async_close()


async def walk_v2c(host, port, community, outputs):
    endpoint = await udp.create(local_addr=None,
                                remote_addr=(host, port))
    name = (0, 0)
    request_id = 0
    max_repetitions = 10
    info = {'data_count': {}, 'data_types': {}, 'errors': {}}
    while True:
        data = common.Data(type=common.DataType.UNSPECIFIED,
                           name=name,
                           value=None)
        pdu = encoder.v2c.BulkPdu(request_id=request_id,
                                  non_repeaters=0,
                                  max_repetitions=max_repetitions,
                                  data=[data])
        req_msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.GET_BULK_REQUEST,
                                  community=community,
                                  pdu=pdu)
        req_msg_bytes = encoder.encode(req_msg)
        endpoint.send(req_msg_bytes)
        res_msg_bytes, addr = await endpoint.receive()
        try:
            res_msg = encoder.decode(res_msg_bytes)
            record_info(info, res_msg)
            output(outputs, res_msg)
            error_type = res_msg.pdu.error.type
            if error_type is not common.ErrorType.NO_ERROR:
                break
            data_type = res_msg.pdu.data[-1].type
            if data_type is common.DataType.END_OF_MIB_VIEW:
                break
            if len(res_msg.pdu.data) == max_repetitions:
                max_repetitions += 10
            elif max_repetitions > 2:
                max_repetitions -= 1
            name = res_msg.pdu.data[-1].name
            request_id += 1
        except Exception:
            print(traceback.format_exec())
            break
    output_info(outputs, info)
    await endpoint.async_close()


async def walk_v3(host, port, community, outputs):
    print('Not implemented!')


if __name__ == '__main__':
    main()
