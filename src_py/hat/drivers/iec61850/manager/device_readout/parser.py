from collections.abc import Collection

from hat.drivers.iec61850.manager.device_readout import common


def get_cdc_data(value_types: dict[common.RootDataRef,
                                   common.ValueType | None],
                 dataset_data_refs: dict[common.DatasetRef,
                                         Collection[common.DataRef]]
                 ) -> dict[common.CdcDataRef, common.CdcData]:
    # TODO
    pass


def get_cdc_commands(value_types: dict[common.RootDataRef,
                                       common.ValueType | None],
                     cmd_models: dict[common.CommandRef, common.ControlModel]
                     ) -> dict[common.CommandRef, common.CdcCommand]:
    cdc_commands = {}
    for root_data_ref, value_type in value_types.items():
        if root_data_ref.fc != 'CO' or value_type is None:
            continue

        cmd_ref = common.CommandRef(
            logical_device=root_data_ref.logical_device,
            logical_node=root_data_ref.logical_node,
            name=root_data_ref.name)
        co_value_type = value_type
        st_value_type = value_types.get(root_data_ref._replace(fc='ST'))
        if not st_value_type:
            continue

        cdc = _get_command_cdc(cmd_ref=cmd_ref,
                               co_value_type=co_value_type,
                               st_value_type=st_value_type)
        if cdc is None:
            continue

        cdc_commands[cmd_ref] = common.CdcCommand(
            cdc=cdc,
            model=cmd_models[cmd_ref],
            with_operate_time=(
                isinstance(value_type, common.StructValueType) and
                any(i == 'operTm' for i, _ in value_type.elements)))

    return cdc_commands


def _get_command_cdc(cmd_ref: common.CommandRef,
                     co_value_type: common.ValueType,
                     st_value_type: common.ValueType
                     ) -> common.Cdc | None:
    if (not isinstance(co_value_type, common.StructValueType) or
            not isinstance(st_value_type, common.StructValueType) or
            not co_value_type.elements or
            not st_value_type.elements):
        return

    ctl_val_name, ctl_val_value_type = next(iter(co_value_type.element))
    if ctl_val_name != 'ctlVal':
        return

    st_val_value_type = next((value_type
                              for name, value_type in st_value_type.elements
                              if name == 'stVal'),
                             None)

    if ctl_val_value_type == common.BasicValueType.BOOLEAN:
        if st_val_value_type == common.BasicValueType.BOOLEAN:
            return common.Cdc.SPC

        if st_val_value_type == common.BasicValueType.BIT_STRING:
            return common.Cdc.DPC

    elif ctl_val_value_type == common.BasicValueType.INTEGER:
        if st_val_value_type == common.BasicValueType.INTEGER:
            return common.Cdc.INC  # or ENC

        if any(i == 'valWTr' for i, _ in st_value_type.elements):
            return common.Cdc.ISC

    elif ctl_val_value_type == common.BasicValueType.BIT_STRING:
        if any(i == 'valWTr' for i, _ in st_value_type.elements):
            return common.Cdc.BSC

        if any(i == 'mxVal' for i, _ in st_value_type.elements):
            return common.Cdc.BAC

    elif ctl_val_value_type == common.AcsiValueType.ANALOGUE:
        return common.Cdc.APC
