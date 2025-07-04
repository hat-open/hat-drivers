from collections.abc import Collection
import logging

from hat import aio
from hat import asn1
from hat import json

from hat.drivers import mms
from hat.drivers import tcp
from hat.drivers.iec61850 import encoder
from hat.drivers.iec61850.manager.device_readout import common
from hat.drivers.iec61850.manager.device_readout.parser import (get_cdc_data,
                                                                get_cdc_commands)  # NOQA
from hat.drivers.iec61850.manager.device_readout.client import Client


mlog: logging.Logger = logging.getLogger(__name__)


async def readout(addr: tcp.Address,
                  local_tsel: int | None = None,
                  remote_tsel: int | None = None,
                  local_ssel: int | None = None,
                  remote_ssel: int | None = None,
                  local_psel: int | None = None,
                  remote_psel: int | None = None,
                  local_ap_title: asn1.ObjectIdentifier | None = None,
                  remote_ap_title: asn1.ObjectIdentifier | None = None,
                  local_ae_qualifier: int | None = None,
                  remote_ae_qualifier: int | None = None,
                  local_detail_calling: int | None = None
                  ) -> common.DeviceConf:
    value_types: dict[common.RootDataRef, common.ValueType | None] = {}
    dataset_data_refs: dict[common.DatasetRef, Collection[common.DataRef]] = {}
    rcb_attr_values: dict[common.RcbRef, dict[common.RcbAttrType,
                                              common.RcbAttrValue]] = {}
    cmd_models: dict[common.CommandRef, common.ControlModel] = {}

    mlog.info('connecting to %s:%s...', addr.host, addr.port)
    conn = await mms.connect(addr=addr,
                             local_tsel=local_tsel,
                             remote_tsel=remote_tsel,
                             local_ssel=local_ssel,
                             remote_ssel=remote_ssel,
                             local_psel=local_psel,
                             remote_psel=remote_psel,
                             local_ap_title=local_ap_title,
                             remote_ap_title=remote_ap_title,
                             local_ae_qualifier=local_ae_qualifier,
                             remote_ae_qualifier=remote_ae_qualifier,
                             local_detail_calling=local_detail_calling)

    try:
        mlog.info('connected')
        client = Client(conn)

        mlog.info('getting logical devices...')
        logical_devices = await client.get_logical_devices()

        mlog.info('got %s logical devices', len(logical_devices))

        for logical_device in logical_devices:
            mlog.info('logical device %s: getting root data refs..',
                      logical_device)
            root_data_refs = await client.get_root_data_refs(logical_device)

            mlog.info('logical device %s: got %s root data refs',
                      logical_device, len(root_data_refs))

            for root_data_ref in root_data_refs:
                data_ref = common.DataRef(
                    logical_device=root_data_ref.logical_device,
                    logical_node=root_data_ref.logical_node,
                    fc=root_data_ref.fc,
                    names=(root_data_ref.name, ))
                data_ref_str = encoder.data_ref_to_str(data_ref)

                mlog.info('logical device %s: getting value type for %s...',
                          logical_device, data_ref_str)
                value_type = await client.get_value_type(data_ref)
                value_types[root_data_ref] = value_type

                mlog.info('logical device %s: got value type for %s',
                          logical_device, data_ref_str)

                if root_data_ref.fc == 'CO':
                    cmd_ref = common.CommandRef(
                        logical_device=root_data_ref.logical_device,
                        logical_node=root_data_ref.logical_node,
                        name=root_data_ref.name)

                    mlog.info('logical device %s: getting control model '
                              'for %s...',
                              logical_device, data_ref_str)
                    cmd_model = await client.get_control_model(cmd_ref)
                    cmd_models[cmd_ref] = cmd_model

                    mlog.info('logical device %s: got control model %s '
                              'for %s...',
                              logical_device, cmd_model.name, data_ref_str)

                elif root_data_ref.fc in ('BR', 'RP'):
                    rcb_ref = common.RcbRef(
                        logical_device=root_data_ref.logical_device,
                        logical_node=root_data_ref.logical_node,
                        type=common.RcbType(root_data_ref.fc),
                        name=root_data_ref.name)

                    mlog.info('logical device %s: getting rcb attr values '
                              'for %s...',
                              logical_device, data_ref_str)
                    attr_values = await client.get_rcb_attr_values(rcb_ref)
                    rcb_attr_values[rcb_ref] = attr_values

                    mlog.info('logical device %s: got rcb attr values '
                              'for %s...',
                              logical_device, data_ref_str)

            mlog.info('logical device %s: getting dataset refs..',
                      logical_device)
            dataset_refs = await client.get_dataset_refs(logical_device)

            mlog.info('logical device %s: got %s dataset refs',
                      logical_device, len(dataset_refs))

            for dataset_ref in dataset_refs:
                dataset_ref_str = encoder.dataset_ref_to_str(dataset_ref)

                mlog.info('logical device %s: getting data refs for %s...',
                          logical_device, dataset_ref_str)
                data_refs = await client.get_dataset_data_refs(dataset_ref)
                dataset_data_refs[dataset_ref] = data_refs

                mlog.info('logical device %s: got %s data refs for %s',
                          logical_device, len(data_refs), dataset_ref_str)

    finally:
        await aio.uncancellable(conn.async_close())

    cdc_data = get_cdc_data(value_types, dataset_data_refs)
    cdc_commands = get_cdc_commands(value_types, cmd_models)

    return {
        'connection': _get_connection_conf(addr=addr,
                                           tsel=remote_tsel,
                                           ssel=remote_ssel,
                                           psel=remote_psel,
                                           ap_title=remote_ap_title,
                                           ae_qualifier=remote_ae_qualifier),
        'value_types': _get_value_types_conf(value_types),
        'datasets': _get_datasets_conf(dataset_data_refs),
        'rcbs': _get_rcbs_conf(rcb_attr_values),
        'data': _get_data_conf(cdc_data),
        'commands': _get_commands_conf(cdc_commands)}


def _get_connection_conf(addr: tcp.Address,
                         tsel: int | None,
                         ssel: int | None,
                         psel: int | None,
                         ap_title: asn1.ObjectIdentifier | None,
                         ae_qualifier: int | None
                         ) -> json.Data:
    connection_conf = {'host': addr.host,
                       'port': addr.port}

    if tsel is not None:
        connection_conf['tsel'] = tsel

    if ssel is not None:
        connection_conf['ssel'] = ssel

    if psel is not None:
        connection_conf['psel'] = psel

    if ap_title is not None:
        connection_conf['ap_title'] = ap_title

    if ae_qualifier is not None:
        connection_conf['ae_qualifier'] = ae_qualifier

    return connection_conf


def _get_value_types_conf(value_types: dict[common.RootDataRef,
                                            common.ValueType | None]
                          ) -> json.Data:
    return [{'logical_device': root_data_ref.logical_device,
             'logical_node': root_data_ref.logical_node,
             'fc': root_data_ref.fc,
             'name': root_data_ref.name,
             'type': (_value_type_to_json(value_type) if value_type is not None
                      else None)}
            for root_data_ref, value_type in value_types.items()]


def _get_datasets_conf(dataset_data_refs: dict[common.DatasetRef,
                                               Collection[common.DataRef]]
                       ) -> json.Data:
    return [{'ref': _dataset_ref_to_json(dataset_ref),
             'values': [_data_ref_to_json(data_ref)
                        for data_ref in data_refs]}
            for dataset_ref, data_refs in dataset_data_refs.items()]


def _get_rcbs_conf(rcb_attr_values: dict[common.RcbRef,
                                         dict[common.RcbAttrType,
                                              common.RcbAttrValue]]
                   ) -> json.Data:
    return [
        {'ref': _rcb_ref_to_json(rcb_ref),
         'report_id': attr_values[common.RcbAttrType.REPORT_ID],
         'dataset': (
            _dataset_ref_to_json(attr_values[common.RcbAttrType.DATASET])
            if attr_values[common.RcbAttrType.DATASET] is not None
            else None),
         'conf_revision': attr_values[common.RcbAttrType.CONF_REVISION],
         'optional_fields': [
            i.name
            for i in attr_values[common.RcbAttrType.OPTIONAL_FIELDS]],
         'buffer_time': attr_values[common.RcbAttrType.BUFFER_TIME],
         'trigger_options': [
            i.name
            for i in attr_values[common.RcbAttrType.TRIGGER_OPTIONS]],
         'integrity_period': attr_values[common.RcbAttrType.INTEGRITY_PERIOD],
         'uneditable': []}
        for rcb_ref, attr_values in rcb_attr_values.items()]


def _get_data_conf(cdc_data: dict[common.CdcDataRef, common.CdcData]
                   ) -> json.Data:
    return [{'ref': _cdc_data_ref_to_json(i_ref),
             'cdc': (i.cdc.name if i.cdc else None),
             'values': [{'name': value.name,
                         'fc': value.fc,
                         'datasets': [_dataset_ref_to_json(ds)
                                      for ds in value.datasets],
                         'writable': value.writable}
                        for value in i.values]}
            for i_ref, i in cdc_data.items()]


def _get_commands_conf(cdc_commands: dict[common.CommandRef, common.CdcCommand]
                       ) -> json.Data:
    return [{'ref': _command_ref_to_json(cmd_ref),
             'model': cdc_cmd.model.name,
             'with_operate_time': cdc_cmd.with_operate_time,
             'cdc': cdc_cmd.cdc.name}
            for cmd_ref, cdc_cmd in cdc_commands.items()]


def _value_type_to_json(value_type: common.ValueType
                        ) -> json.Data:
    if isinstance(value_type, common.BasicValueType):
        return value_type.name

    if isinstance(value_type, common.AcsiValueType):
        return value_type.name

    if isinstance(value_type, common.ArrayValueType):
        return {'type': 'ARRAY',
                'element_type': _value_type_to_json(value_type.type),
                'length': value_type.length}

    if isinstance(value_type, common.StructValueType):
        return {'type': 'STRUCT',
                'elements': [{'name': i_name,
                              'type': _value_type_to_json(i_type)}
                             for i_name, i_type in value_type.elements]}

    raise TypeError('unsupported value type')


def _data_ref_to_json(ref: common.DataRef
                      ) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'fc': ref.fc,
            'names': list(ref.names)}


def _dataset_ref_to_json(ref: common.PersistedDatasetRef
                         ) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'name': ref.name}


def _rcb_ref_to_json(ref: common.RcbRef
                     ) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'type': ref.type.name,
            'name': ref.name}


def _command_ref_to_json(ref: common.CommandRef
                         ) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'name': ref.name}


def _cdc_data_ref_to_json(ref: common.CdcDataRef
                          ) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'names': list(ref.names)}
