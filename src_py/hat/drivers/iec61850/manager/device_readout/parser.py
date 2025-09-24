from collections.abc import Collection, Iterable
import collections

from hat import asn1
from hat import json

from hat.drivers import tcp
from hat.drivers.iec61850.manager.device_readout import common


def get_device_conf(addr: tcp.Address,
                    tsel: int | None,
                    ssel: int | None,
                    psel: int | None,
                    ap_title: asn1.ObjectIdentifier | None,
                    ae_qualifier: int | None,
                    value_types: dict[common.RootDataRef,
                                      common.ValueType | None],
                    dataset_data_refs: dict[common.DatasetRef,
                                            Collection[common.DataRef]],
                    rcb_attr_values: dict[common.RcbRef,
                                          dict[common.RcbAttrType,
                                               common.RcbAttrValue]],
                    cmd_models: dict[common.CommandRef, common.ControlModel]
                    ) -> common.DeviceConf:
    updated_value_types = {
        ref: (_update_value_type(value_type) if value_type is not None
              else None)
        for ref, value_type in value_types.items()}

    return {
        'type': 'iec61850-device',
        'version': '1',
        'connection': _get_connection_conf(addr=addr,
                                           tsel=tsel,
                                           ssel=ssel,
                                           psel=psel,
                                           ap_title=ap_title,
                                           ae_qualifier=ae_qualifier),
        'value_types': list(_get_value_type_confs(updated_value_types)),
        'datasets': list(_get_dataset_confs(dataset_data_refs)),
        'rcbs': list(_get_rcb_confs(rcb_attr_values)),
        'data': list(_get_data_confs(value_types=updated_value_types,
                                     raw_value_types=value_types,
                                     dataset_data_refs=dataset_data_refs)),
        'commands': list(_get_command_confs(updated_value_types, cmd_models))}


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


def _get_value_type_confs(value_types: dict[common.RootDataRef,
                                            common.ValueType | None]
                          ) -> Iterable[json.Data]:
    for root_data_ref, value_type in value_types.items():
        yield {'logical_device': root_data_ref.logical_device,
               'logical_node': root_data_ref.logical_node,
               'fc': root_data_ref.fc,
               'name': root_data_ref.name,
               'type': (common.value_type_to_json(value_type)
                        if value_type is not None else None)}


def _get_dataset_confs(dataset_data_refs: dict[common.DatasetRef,
                                               Collection[common.DataRef]]
                       ) -> Iterable[json.Data]:
    for dataset_ref, data_refs in dataset_data_refs.items():
        yield {'ref': common.dataset_ref_to_json(dataset_ref),
               'values': [common.data_ref_to_json(data_ref)
                          for data_ref in data_refs]}


def _get_rcb_confs(rcb_attr_values: dict[common.RcbRef,
                                         dict[common.RcbAttrType,
                                              common.RcbAttrValue]]
                   ) -> Iterable[json.Data]:
    for rcb_ref, attr_values in rcb_attr_values.items():
        yield {
            'ref': common.rcb_ref_to_json(rcb_ref),
            'report_id': attr_values[common.RcbAttrType.REPORT_ID],
            'dataset': (
               common.dataset_ref_to_json(
                    attr_values[common.RcbAttrType.DATASET])
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
            'integrity_period': attr_values[common.RcbAttrType.INTEGRITY_PERIOD]}  # NOQA


def _get_data_confs(value_types: dict[common.RootDataRef,
                                      common.ValueType | None],
                    raw_value_types: dict[common.RootDataRef,
                                          common.ValueType | None],
                    dataset_data_refs: dict[common.DatasetRef,
                                            Collection[common.DataRef]]
                    ) -> Iterable[json.Data]:
    for root_data_ref, value_type in value_types.items():
        if not isinstance(value_type, common.StructValueType):
            continue

        data_ref = common.DataRef(
            logical_device=root_data_ref.logical_device,
            logical_node=root_data_ref.logical_node,
            fc=root_data_ref.fc,
            names=(root_data_ref.name, ))

        yield from _get_struct_data_confs(data_ref=data_ref,
                                          struct_value_type=value_type,
                                          raw_value_types=raw_value_types,
                                          dataset_data_refs=dataset_data_refs)


def _get_command_confs(value_types: dict[common.RootDataRef,
                                         common.ValueType | None],
                       cmd_models: dict[common.CommandRef, common.ControlModel]
                       ) -> Iterable[json.Data]:
    for root_data_ref, value_type in value_types.items():
        if (root_data_ref.fc != 'CO' or
                not isinstance(value_type, common.StructValueType)):
            continue

        cmd_ref = common.CommandRef(
            logical_device=root_data_ref.logical_device,
            logical_node=root_data_ref.logical_node,
            name=root_data_ref.name)

        oper_value_type = next(
            (i for name, i in value_type.elements if name == 'Oper'),
            None)
        if not isinstance(oper_value_type, common.StructValueType):
            continue

        ctl_val_value_type = next(
            (i for name, i in oper_value_type.elements if name == 'ctlVal'),
            None)
        if not ctl_val_value_type:
            continue

        model = cmd_models.get(cmd_ref)
        if not model:
            continue

        with_operate_time = any(
            name == 'operTm' for name, _ in oper_value_type.elements)

        yield {'ref': common.command_ref_to_json(cmd_ref),
               'value_type': common.value_type_to_json(ctl_val_value_type),
               'model': model.name,
               'with_operate_time': with_operate_time}


def _get_struct_data_confs(data_ref: common.DataRef,
                           struct_value_type: common.StructValueType,
                           raw_value_types: dict[common.RootDataRef,
                                                 common.ValueType | None],
                           dataset_data_refs: dict[common.DatasetRef,
                                                   Collection[common.DataRef]]
                           ) -> Iterable[json.Data]:
    value_types = dict(struct_value_type.elements)

    for name, value_type in struct_value_type.elements:
        if isinstance(value_type, common.StructValueType):
            yield from _get_struct_data_confs(
                data_ref=data_ref._replace(
                    names=(*data_ref.names, name)),
                struct_value_type=value_type,
                raw_value_types=raw_value_types,
                dataset_data_refs=dataset_data_refs)

        elif isinstance(value_type, common.ArrayValueType):
            if isinstance(value_type.type, common.StructValueType):
                for i in range(value_type.length):
                    yield from _get_struct_data_confs(
                        data_ref=data_ref._replace(
                            names=(*data_ref.names, name, i)),
                        struct_value_type=value_type.type,
                        raw_value_types=raw_value_types,
                        dataset_data_refs=dataset_data_refs)

        else:
            value_ref = data_ref._replace(names=(*data_ref.names, name))
            quality_ref = None
            timestamp_ref = None
            selected_ref = None

            if data_ref.fc == 'ST':
                if name in {'q', 't', 'stSeld', 'frTm'}:
                    continue

                if name in {'stVal', 'valWTr'}:
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                    if value_types.get('t') == common.AcsiValueType.TIMESTAMP:
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 't'))

                    if value_types.get('stSeld') == common.BasicValueType.BOOLEAN:  # NOQA
                        selected_ref = data_ref._replace(
                            names=(*data_ref.names, 'stSeld'))

                if name in {'general', 'phsA', 'phsB', 'phsC', 'neut',
                            'dirGeneral', 'dirPhsA', 'dirPhsB', 'dirPhsC',
                            'dirNeut', 'actVal'}:
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                    if value_types.get('t') == common.AcsiValueType.TIMESTAMP:
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 't'))

                elif name == 'cnt':
                    if value_types.get('t') == common.AcsiValueType.TIMESTAMP:
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 't'))

                elif name == 'frVal':
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                    if value_types.get('frTm') == common.AcsiValueType.TIMESTAMP:  # NOQA
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 'frTm'))

            elif data_ref.fc == 'MX':
                if name in {'q', 't', 'stSeld'}:
                    continue

                if name in {'mag', 'range', 'cVal'}:
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                    if value_types.get('t') == common.AcsiValueType.TIMESTAMP:
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 't'))

                elif name == 'instMag':
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                    if 'mag' not in value_types:
                        if value_types.get('t') == common.AcsiValueType.TIMESTAMP:  # NOQA
                            timestamp_ref = data_ref._replace(
                                names=(*data_ref.names, 't'))

                elif name == 'instCVal':
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                elif name == 'mxVal':
                    if value_types.get('q') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'q'))

                    if value_types.get('t') == common.AcsiValueType.TIMESTAMP:
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 't'))

                    if value_types.get('stSeld') == common.BasicValueType.BOOLEAN:  # NOQA
                        selected_ref = data_ref._replace(
                            names=(*data_ref.names, 'stSeld'))

            elif data_ref.fc == 'SV':
                if name == 'subQ':
                    continue

                if name in {'subVal', 'subMag', 'subCVal'}:
                    if value_types.get('subQ') == common.AcsiValueType.QUALITY:
                        quality_ref = data_ref._replace(
                            names=(*data_ref.names, 'subQ'))

            elif data_ref.fc == 'OR':
                if name == 'tOpOk':
                    continue

                if name == 'opOk':
                    if value_types.get('tOpOk') == common.AcsiValueType.TIMESTAMP:  # NOQA
                        timestamp_ref = data_ref._replace(
                            names=(*data_ref.names, 'tOpOk'))

            sub_names_value_types = collections.deque([(tuple(), value_type)])

            if value_type == common.AcsiValueType.ANALOGUE:
                sub_names_value_types.extend([
                    (('i', ), common.BasicValueType.INTEGER),
                    (('f', ), common.BasicValueType.FLOAT)])

            elif value_type == common.AcsiValueType.VECTOR:
                sub_names_value_types.extend([
                    (('mag', ), common.AcsiValueType.ANALOGUE),
                    (('ang', ), common.AcsiValueType.ANALOGUE),
                    (('mag', 'i'), common.BasicValueType.INTEGER),
                    (('mag', 'f'), common.BasicValueType.FLOAT),
                    (('ang', 'i'), common.BasicValueType.INTEGER),
                    (('ang', 'f'), common.BasicValueType.FLOAT)])

            elif value_type == common.AcsiValueType.STEP_POSITION:
                sub_names_value_types.extend([
                    (('posVal', ), common.BasicValueType.INTEGER),
                    (('transInd', ), common.BasicValueType.BOOLEAN)])

            for sub_names, sub_value_type in sub_names_value_types:
                sub_value_ref = value_ref._replace(
                    names=(*value_ref.names, *sub_names))

                if _get_value_type(sub_value_ref, raw_value_types) is None:
                    continue

                yield _get_data_conf(value_ref=sub_value_ref,
                                     value_type=sub_value_type,
                                     quality_ref=quality_ref,
                                     timestamp_ref=timestamp_ref,
                                     selected_ref=selected_ref,
                                     dataset_data_refs=dataset_data_refs)


def _get_data_conf(value_ref: common.DataRef,
                   value_type: common.ValueType,
                   quality_ref: common.DataRef | None,
                   timestamp_ref: common.DataRef | None,
                   selected_ref: common.DataRef | None,
                   dataset_data_refs: dict[common.DatasetRef,
                                           Collection[common.DataRef]]):
    datasets = _get_data_dataset_confs(
        value_ref, quality_ref, timestamp_ref, selected_ref,
        dataset_data_refs)

    writable = value_ref.fc in {'SP', 'SG', 'SE'}

    data_conf = {
        'value': common.data_ref_to_json(value_ref),
        'value_type': common.value_type_to_json(value_type),
        'datasets': list(datasets),
        'writable': writable}

    if quality_ref:
        data_conf['quality'] = common.data_ref_to_json(quality_ref)

    if timestamp_ref:
        data_conf['timestamp'] = common.data_ref_to_json(
            timestamp_ref)

    if selected_ref:
        data_conf['selected'] = common.data_ref_to_json(
            selected_ref)

    return data_conf


def _get_data_dataset_confs(value_ref: common.DataRef,
                            quality_ref: common.DataRef | None,
                            timestamp_ref: common.DataRef | None,
                            selected_ref: common.DataRef | None,
                            dataset_data_refs: dict[common.DatasetRef,
                                                    Collection[common.DataRef]]
                            ) -> Iterable[json.Data]:
    for dataset_ref, data_refs in dataset_data_refs.items():
        if not _is_ref_in_dataset(value_ref, data_refs):
            continue

        yield {'ref': common.dataset_ref_to_json(dataset_ref),
               'quality': bool(quality_ref and
                               _is_ref_in_dataset(quality_ref, data_refs)),
               'timestamp': bool(timestamp_ref and
                                 _is_ref_in_dataset(timestamp_ref, data_refs)),
               'selected': bool(selected_ref and
                                _is_ref_in_dataset(selected_ref, data_refs))}


def _is_ref_in_dataset(ref: common.DataRef,
                       data_refs: Collection[common.DataRef]
                       ) -> bool:
    for data_ref in data_refs:
        if (ref.logical_device != data_ref.logical_device or
                ref.logical_node != data_ref.logical_node or
                ref.fc != data_ref.fc):
            continue

        if (len(ref.names) < len(data_ref.names) or
                any(i != j for i, j in zip(ref.names, data_ref.names))):
            continue

        return True

    return False


def _update_value_type(value_type: common.ValueType
                       ) -> common.ValueType:
    if isinstance(value_type, common.ArrayValueType):
        return value_type._replace(type=_update_value_type(value_type.type))

    if isinstance(value_type, common.StructValueType):
        return common.StructValueType([
            (i_name,
             _update_struct_element_type(i_name, _update_value_type(i_type)))
            for i_name, i_type in value_type.elements])

    return value_type


def _update_struct_element_type(name: str,
                                value_type: common.ValueType
                                ) -> common.ValueType:
    if value_type == common.BasicValueType.BIT_STRING:
        if name in {'q', 'subQ'}:
            return common.AcsiValueType.QUALITY

        if name in {'stVal', 'subVal'}:
            return common.AcsiValueType.DOUBLE_POINT

        if name == 'ctlVal':
            return common.AcsiValueType.BINARY_CONTROL

    elif value_type == common.BasicValueType.INTEGER:
        if name in {'dirGeneral', 'dirPhsA', 'dirPhsB', 'dirPhsC', 'dirNeut'}:
            return common.AcsiValueType.DIRECTION

        if name == 'sev':
            return common.AcsiValueType.SEVERITY

    elif isinstance(value_type, common.StructValueType):
        if name in {'instMag', 'mag', 'subMag', 'min', 'max', 'mxVal',
                    'subVal', 'minVal', 'maxVal', 'stepSize', 'ctlVal',
                    'setMag'}:
            if 1 <= len(value_type.elements) <= 2:
                elements = list(value_type.elements)

                if (elements == [('i', common.BasicValueType.INTEGER)] or
                        elements == [('f', common.BasicValueType.FLOAT)] or
                        elements == [('i', common.BasicValueType.INTEGER),
                                     ('f', common.BasicValueType.FLOAT)]):
                    return common.AcsiValueType.ANALOGUE

        if name in {'instCVal', 'cVal', 'subCVal'}:
            if 1 <= len(value_type.elements) <= 2:
                elements = list(value_type.elements)

                if (elements == [('mag', common.AcsiValueType.ANALOGUE)] or
                        elements == [('mag', common.AcsiValueType.ANALOGUE),
                                     ('ang', common.AcsiValueType.ANALOGUE)]):
                    return common.AcsiValueType.VECTOR

        if name in {'valWTr', 'subVal'}:
            if 1 <= len(value_type.elements) <= 2:
                elements = list(value_type.elements)

                if (elements == [('posVal', common.BasicValueType.INTEGER)] or
                        elements == [('posVal', common.BasicValueType.INTEGER),
                                     ('transInd', common.BasicValueType.BOOLEAN)]):  # NOQA
                    return common.AcsiValueType.STEP_POSITION

    return value_type


def _get_value_type(ref: common.DataRef,
                    value_types: dict[common.RootDataRef,
                                      common.ValueType | None]
                    ) -> common.ValueType | None:
    if not ref.names:
        return

    name, names = ref.names[0], ref.names[1:]
    if not isinstance(name, str):
        return

    value_type = value_types.get(
        common.RootDataRef(logical_device=ref.logical_device,
                           logical_node=ref.logical_node,
                           fc=ref.fc,
                           name=name))

    while value_type is not None and names:
        name, names = names[0], names[1:]

        if isinstance(name, int):
            if not isinstance(value_type, common.ArrayValueType):
                return

            value_type = value_type.type

        elif isinstance(name, str):
            if not isinstance(value_type, common.StructValueType):
                return

            value_type = next((i_type
                               for i_name, i_type in value_type.elements
                               if i_name == name),
                              None)

        else:
            raise TypeError('unsupported name type')

    return value_type
