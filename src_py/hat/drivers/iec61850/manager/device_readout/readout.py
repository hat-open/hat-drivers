from collections.abc import Collection
import logging

from hat import aio
from hat import asn1

from hat.drivers import mms
from hat.drivers import tcp
from hat.drivers.iec61850 import encoder
from hat.drivers.iec61850.manager.device_readout import common
from hat.drivers.iec61850.manager.device_readout.parser import get_device_conf
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

    return get_device_conf(addr=addr,
                           tsel=remote_tsel,
                           ssel=remote_ssel,
                           psel=remote_psel,
                           ap_title=remote_ap_title,
                           ae_qualifier=remote_ae_qualifier,
                           value_types=value_types,
                           dataset_data_refs=dataset_data_refs,
                           rcb_attr_values=rcb_attr_values,
                           cmd_models=cmd_models)
