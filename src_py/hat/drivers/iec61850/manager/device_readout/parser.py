from collections.abc import Collection

from hat.drivers.iec61850.manager.device_readout import common


def get_cdc_data(value_types: dict[common.DataRef,
                                   common.ValueType | None],
                 dataset_data_refs: dict[common.DatasetRef,
                                         Collection[common.DataRef]]
                 ) -> dict[common.CdcDataRef, common.CdcData]:
    pass


def get_cdc_commands(value_types: dict[common.DataRef,
                                       common.ValueType | None],
                     cmd_models: dict[common.CommandRef, common.ControlModel]
                     ) -> dict[common.CommandRef, common.CdcCommand]:
    cdc_commands = {}
    for data_ref, value_type in value_types.items():
        if data_ref.fc != 'CO' or value_type is None:
            continue

        cdc = _command_cdc_from_value_type(value_type)
        if cdc is None:
            continue

        cmd_ref = common.CommandRef(logical_device=data_ref.logical_device,
                                    logical_node=data_ref.logical_node,
                                    name=data_ref.names[0])

        cdc_commands[cmd_ref] = common.CdcCommand(
            cdc=cdc,
            model=cmd_models[cmd_ref],
            with_operate_time=(
                isinstance(value_type, common.StructValueType) and
                any(i == 'operTm' for i, _ in value_type.elements)))

    return cdc_commands


def update_value_types(value_types: dict[common.DataRef,
                                         common.ValueType | None],
                       cdc_data: dict[common.CdcDataRef, common.CdcData]
                       ) -> dict[common.DataRef,
                                 common.ValueType | None]:
    pass


def _command_cdc_from_value_type(value_type: common.ValueType
                                 ) -> common.Cdc | None:
    pass
