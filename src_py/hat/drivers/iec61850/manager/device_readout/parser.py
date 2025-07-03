from collections.abc import Collection
import collections

from hat.drivers.iec61850.manager.device_readout import common


def get_cdc_data(value_types: dict[common.RootDataRef,
                                   common.ValueType | None],
                 dataset_data_refs: dict[common.DatasetRef,
                                         Collection[common.DataRef]]
                 ) -> dict[common.CdcDataRef, common.CdcData]:
    parser = _CdcDataParser(value_types=value_types,
                            dataset_data_refs=dataset_data_refs)

    for root_data_ref, value_type in value_types.items():
        if not isinstance(value_type, common.StructValueType):
            continue

        cdc_data_ref = common.CdcDataRef(
            logical_device=root_data_ref.logical_device,
            logical_node=root_data_ref.logical_node,
            names=(root_data_ref.name, ))

        parser.parse(cdc_data_ref=cdc_data_ref,
                     struct_value_type=value_type)

    return parser.cdc_data


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


class _CdcDataParser:

    def __init__(self,
                 value_types: dict[common.RootDataRef,
                                   common.ValueType | None],
                 dataset_data_refs: dict[common.DatasetRef,
                                         Collection[common.DataRef]]):
        self._value_types = value_types
        self._dataset_data_refs = dataset_data_refs
        self._cdc_data = {}

    @property
    def cdc_data(self) -> dict[common.CdcDataRef, common.CdcData]:
        return self._cdc_data

    def parse(self,
              cdc_data_ref: common.CdcDataRef,
              struct_value_type: common.StructValueType):
        cdc_data = self._cdc_data.get(cdc_data_ref)
        if not cdc_data:
            cdc_data = common.CdcData(cdc=self._get_cdc(cdc_data_ref),
                                      values=collections.deque())
            self._cdc_data[cdc_data_ref] = cdc_data

        for name, value_type in struct_value_type.elements:
            if isinstance(value_type, common.StructValueType):
                self.parse(
                    cdc_data_ref=cdc_data_ref._replace(
                        names=(*cdc_data_ref.names, name)),
                    struct_value_type=value_type)

            elif isinstance(value_type, common.ArrayValueType):
                if isinstance(value_type.type, common.StructValueType):
                    for i in range(value_type.length):
                        self.parse(
                            cdc_data_ref=cdc_data_ref._replace(
                                names=(*cdc_data_ref.names, name, i)),
                            struct_value_type=value_type.type)

            elif value_type not in {common.AcsiValueType.QUALITY,
                                    common.AcsiValueType.TIMESTAMP}:
                cdc_data_value = common.CdcDataValue(
                    name=name,
                    datasets=self._get_datasets(cdc_data_ref, name),
                    writable=self._get_writable(cdc_data_ref, name))

                cdc_data.values.append(cdc_data_value)

    def _get_cdc(self, cdc_data_ref):
        value_types = {}

        for fc in ['ST', 'MX', 'CO', 'SP', 'SG', 'SE', 'DC']:
            fc_value_type = self._get_value_type(cdc_data_ref, fc)

            if isinstance(fc_value_type, common.StructValueType):
                value_types[fc] = {
                    name: value_type
                    for name, value_type in fc_value_type.elements}

            else:
                value_types[fc] = {}

        if 'ctlVal' in value_types['CO']:
            if value_types['CO']['ctlVal'] == common.BasicValueType.BOOLEAN:
                if value_types['ST'].get('stVal') == common.AcsiValueType.DOUBLE_POINT:  # NOQA
                    return common.Cdc.DPC

                return common.Cdc.SPC

            if value_types['CO']['ctlVal'] == common.BasicValueType.INTEGER:
                if value_types['ST'].get('stVal') == common.BasicValueType.INTEGER:  # NOQA
                    return common.Cdc.INC  # or ENC

                return common.Cdc.ISC


            if value_types['CO']['ctlVal'] == common.AcsiValueType.BINARY_CONTROL:  # NOQA
                if value_types['ST'].get('mxVal') == common.AcsiValueType.ANALOGUE:  # NOQA
                    return common.Cdc.BAC

                return common.Cdc.BSC

            if value_types['CO']['ctlVal'] == common.AcsiValueType.ANALOGUE:
                return common.Cdc.APC

            return

        if value_types['ST'].get('t') == common.AcsiValueType.TIMESTAMP:
            if value_types['ST'].get('q') == common.AcsiValueType.QUALITY:
                if 'stVal' in value_types['ST']:
                    if value_types['ST']['stVal'] == common.BasicValueType.BOOLEAN:  # NOQA
                        return common.Cdc.SPS

                    if value_types['ST']['stVal'] == common.AcsiValueType.DOUBLE_POINT:  # NOQA
                        return common.Cdc.DPS

                    if value_types['ST']['stVal'] == common.BasicValueType.INTEGER:  # NOQA
                        return common.Cdc.INS

                    if value_types['ST']['stVal'] == common.BasicValueType.VISIBLE_STRING:  # NOQA
                        return common.Cdc.VSS

                    return

                if 'general' in value_types['ST']:
                    if value_types['ST']['general'] == common.BasicValueType.BOOLEAN:  # NOQA
                        if 'dirGeneral' in value_types['ST']:
                            if value_types['ST']['dirGeneral'] == common.AcsiValueType.DIRECTION:  # NOQA
                                return common.Cdc.ACD

                            return

                        return common.Cdc.ACT

                    return

                if 'actVal' in value_types['ST']:
                    if value_types['ST']['actVal'] == common.BasicValueType.INTEGER:  # NOQA
                        return common.Cdc.BCR

                    return

                if 'hstVal' in value_types['ST']:
                    if (isinstance(value_types['ST']['hstVal'], common.ArrayValueType) and  # NOQA
                            value_types['ST']['hstVal'].type == common.BasicValueType.INTEGER):  # NOQA
                        return common.Cdc.HST

            if 'cnt' in value_types['ST']:
                if value_types['ST']['cnt'] == common.BasicValueType.INTEGER:
                    if value_types['ST'].get('sev') == common.BasicValueType.INTEGER:  # NOQA
                        return common.Cdc.SEC

                return

        if value_types['MX'].get('q') == common.AcsiValueType.QUALITY:
            if value_types['MX'].get('t') == common.AcsiValueType.TIMESTAMP:
                if 'mag' in value_types['MX']:
                    if value_types['MX']['mag'] == common.AcsiValueType.ANALOGUE:  # NOQA
                        return common.Cdc.MV

                    return

                if 'cVal' in value_types['MX']:
                    if value_types['MX']['cVal'] == common.AcsiValueType.VECTOR:  # NOQA
                        return common.Cdc.CMV

                    return

            if 'instMag' in value_types['MX']:
                if value_types['MX']['instMag'] == common.AcsiValueType.ANALOGUE:  # NOQA
                    return common.Cdc.SAV

                return

        for name in ['phsA', 'phsB', 'phsC', 'neut', 'net', 'res']:
            if name in value_types['MX']:
                if isinstance(value_types['MX'][name], common.StructValueType):
                    name_cdc = self._get_cdc(
                        cdc_data_ref._replace(
                            names=(*cdc_data_ref.names, name)))

                    if name_cdc == common.Cdc.CMV:
                        return common.Cdc.WYE

                return

        for name in ['phsAB', 'phsBC', 'phsCA']:
            if name in value_types['MX']:
                if isinstance(value_types['MX'][name], common.StructValueType):
                    name_cdc = self._get_cdc(
                        cdc_data_ref._replace(
                            names=(*cdc_data_ref.names, name)))

                    if name_cdc == common.Cdc.CMV:
                        return common.Cdc.DEL

                return

        if ('c1' in value_types['MX'] or
                'c2' in value_types['MX'] or
                'c3' in value_types['MX']):
            for name in ['c1', 'c2', 'c3']:
                if not isinstance(value_types['MX'][name], common.StructValueType): # NOQA
                    return

                name_cdc = self._get_cdc(
                    cdc_data_ref._replace(
                        names=(*cdc_data_ref.names, name)))

                if name_cdc != common.Cdc.CMV:
                    return

            return common.Cdc.SEQ

        if 'har' in value_types['MX']:
            if (isinstance(value_types['MX']['har'], common.ArrayValueType) and
                    isinstance(value_types['MX']['har'].type, common.StructValueType)):  # NOQA
                har_cdc = self._get_cdc(
                    cdc_data_ref._replace(
                        names=(*cdc_data_ref.names, 'har', 0)))

                if har_cdc == common.Cdc.CMV:
                    return common.Cdc.HMV

            return

        if 'phsAHar' in value_types['MX']:
            if (isinstance(value_types['MX']['phsAHar'], common.ArrayValueType) and  # NOQA
                    isinstance(value_types['MX']['phsAHar'].type, common.StructValueType)):  # NOQA
                phs_a_har_cdc = self._get_cdc(
                    cdc_data_ref._replace(
                        names=(*cdc_data_ref.names, 'phsAHar', 0)))

                if phs_a_har_cdc == common.Cdc.CMV:
                    return common.Cdc.HWYE

            return

        if 'phsABHar' in value_types['MX']:
            if (isinstance(value_types['MX']['phsABHar'], common.ArrayValueType) and  # NOQA
                    isinstance(value_types['MX']['phsABHar'].type, common.StructValueType)):  # NOQA
                phs_a_b_har_cdc = self._get_cdc(
                    cdc_data_ref._replace(
                        names=(*cdc_data_ref.names, 'phsABHar', 0)))

                if phs_a_b_har_cdc == common.Cdc.CMV:
                    return common.Cdc.HDEL

            return

        for fc in ['SP', 'SG', 'SE']:
            if 'setVal' in value_types[fc]:
                if value_types[fc]['setVal'] == common.BasicValueType.BOOLEAN:
                    return common.Cdc.SPG

                if value_types[fc]['setVal'] == common.BasicValueType.INTEGER:
                    return common.Cdc.ING  # or ENG

                if value_types[fc]['setVal'] == common.BasicValueType.VISIBLE_STRING:  # NOQA
                    return common.Cdc.VSG

                return

        if 'setSrcRef' in value_types['SP']:
            # TODO check type
            return common.Cdc.ORG

        for fc in ['SP', 'SG', 'SE']:
            for name in ['setTm', 'setCal']:
                if name in value_types[fc]:
                    # TODO check type
                    return common.Cdc.TSG

        for fc in ['SP', 'SG', 'SE']:
            if 'cur' in value_types[fc]:
                # TODO check type
                return common.Cdc.CUG

        for fc in ['SP', 'SG', 'SE']:
            if 'setMag' in value_types[fc]:
                if value_types[fc]['setMag'] == common.AcsiValueType.ANALOGUE:
                    return common.Cdc.ASG

                return

        for fc in ['SP', 'SG', 'SE']:
            for name in ['setCharact', 'setParA', 'setParB', 'setParC',
                         'setParD', 'setParE', 'setParF']:
                if name in value_types[fc]:
                    # TODO check type
                    return common.Cdc.CURVE

        for fc in ['SP', 'SG', 'SE']:
            for name in ['pointZ', 'numPts', 'crvPts']:
                if name in value_types[fc]:
                    # TODO check type
                    return common.Cdc.CSG

        if 'vendor' in value_types['DC']:
            if value_types['DC']['vendor'] == common.BasicValueType.VISIBLE_STRING:  # NOQA
                return common.Cdc.DPL  # or LPL

            return

        if any(name in value_types['DC'] for name in ['xUnits', 'xD',
                                                      'yUnits', 'yD',
                                                      'numPts', 'crvPts']):
            for name in ['xUnits', 'xD', 'yUnits', 'yD', 'numPts', 'crvPts']:
                if name not in value_types['DC']:
                    return

            return common.Cdc.CSD

    def _get_datasets(self, cdc_data_ref, name):
        # TODO
        return []

    def _get_writable(self, cdc_data_ref, name):
        # TODO
        return False

    def _get_value_type(self, cdc_data_ref, fc):
        if (not cdc_data_ref.names or
                not isinstance(cdc_data_ref.names[0], str)):
            return

        root_data_ref = common.RootDataRef(
            logical_device=cdc_data_ref.logical_device,
            logical_node=cdc_data_ref.logical_node,
            fc=fc,
            name=cdc_data_ref.names[0])

        value_type = self._value_types.get(root_data_ref)
        path = cdc_data_ref.names[1:]

        while value_type and path:
            name, path = path[0], path[1:]

            if (isinstance(name, str) and
                    isinstance(value_type, common.StructValueType)):
                value_type = next(
                    (v for k, v in value_type.elements if k == name),
                    None)

            elif (isinstance(name, int) and
                    isinstance(value_type, common.ArrayValueType)):
                value_type = value_type.type

            else:
                value_type = None

        return value_type


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
