from pathlib import Path
import argparse
import logging
import sys
import typing
import xml.etree.ElementTree

from hat import json

from hat.drivers.iec61850.manager import common


mlog: logging.Logger = logging.getLogger(__name__)


def create_argument_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser('file-readout')

    parser.add_argument(
        '--output', metavar='PATH', type=Path, default=Path('-'),
        help="output devices file path or - for stdout (default -)")

    parser.add_argument(
        'source', type=Path, default=Path('-'), nargs='?',
        help="input source file path or - for stdin (default -)")

    return parser


def main(args):
    source = args.source if args.source != Path('-') else sys.stdin

    device_confs = readout(source)

    if args.output == Path('-'):
        json.encode_stream(device_confs, sys.stdout)

    else:
        json.encode_file(device_confs, args.output)


def readout(source: typing.TextIO | Path
            ) -> dict[common.IedName, common.DeviceConf]:
    root_el = _read_xml(source)
    return {ied_name: device_conf
            for ied_name, device_conf in _parse_ieds(root_el)}


def _read_xml(source):
    it = xml.etree.ElementTree.iterparse(source)
    for _, el in it:
        prefix, has_namespace, postfix = el.tag.partition('}')
        if has_namespace:
            el.tag = postfix
    return it.root


def _parse_ieds(root_el):
    for ied_el in root_el.findall("./IED"):
        ied_name = ied_el.get('name')
        if ied_name == 'TEMPLATE':
            mlog.warning(
                "ied name is 'TEMPLATE': possible insufficient structure")

        uneditable_rcb = list(_parse_uneditable_rcb(ied_el))

        for ap_el in ied_el.findall("./AccessPoint"):
            if ap_el.find("./Server/LDevice") is None:
                continue

            yield ied_name, _parse_device(root_el=root_el,
                                          ap_el=ap_el,
                                          ied_name=ied_name,
                                          uneditable_rcb=uneditable_rcb)


def _parse_device(root_el, ap_el, ied_name, uneditable_rcb):
    ap_name = ap_el.get('name')
    datasets = []
    rcbs = []
    data = []
    commands = []
    value_types = []

    for ld_el in ap_el.findall("./Server/LDevice"):
        logical_device = _create_logical_device(ied_name, ld_el.get('inst'))
        for ln_el in ld_el:
            if ln_el.tag not in {'LN0', 'LN'}:
                continue

            logical_node = _create_logical_node(ln_el.get('prefix'),
                                                ln_el.get('lnClass'),
                                                ln_el.get('inst'))
            ln_type = ln_el.get('lnType')
            ln_type_el = root_el.find(f"./DataTypeTemplates/LNodeType"
                                      f"[@id='{ln_type}']")

            value_types.extend(_parse_value_types(
                root_el, ln_type_el, logical_device, logical_node))

            datasets.extend(_parse_datasets(
                ied_name, logical_device, logical_node, ln_el))

            rcbs.extend(_parse_rcbs(
                logical_device, logical_node, ln_el, uneditable_rcb))

            data.extend(_parse_data(root_el=root_el,
                                    ln_type_el=ln_type_el,
                                    ied_name=ied_name,
                                    ap_name=ap_name,
                                    logical_device=logical_device,
                                    logical_node=logical_node,
                                    datasets=datasets))

            commands.extend(_parse_commands(
                root_el, ln_el, ln_type_el, logical_device, logical_node))

    return {
        'connection': _parse_connection(root_el, ied_name, ap_name),
        'value_types': value_types,
        'datasets': datasets,
        'rcbs': rcbs,
        'data': data,
        'commands': commands}


def _parse_uneditable_rcb(ied_el):
    report_settings_el = ied_el.find('./Services/ReportSettings')

    if report_settings_el is None or report_settings_el.get('rptID') != 'Dyn':
        yield 'REPORT_ID'

    if report_settings_el is None or report_settings_el.get('datSet') != 'Dyn':
        yield 'DATASET'

    if (report_settings_el is None or
            report_settings_el.get('optFields') != 'Dyn'):
        yield 'OPTIONAL_FIELDS'

    if (report_settings_el is None or
            report_settings_el.get('bufTime') != 'Dyn'):
        yield 'BUFFER_TIME'

    if report_settings_el is None or report_settings_el.get('trgOps') != 'Dyn':
        yield 'TRIGGER_OPTIONS'

    if report_settings_el is None or report_settings_el.get('intgPd') != 'Dyn':
        yield 'INTEGRITY_PERIOD'


def _parse_connection(root_el, ied_name, ap_name):
    conn_conf = {}
    connected_ap_el = root_el.find(f"./Communication/SubNetwork/ConnectedAP"
                                   f"[@iedName='{ied_name}']"
                                   f"[@apName='{ap_name}']")
    if connected_ap_el is None:
        return conn_conf

    for addr_p_el in connected_ap_el.find('./Address'):
        if addr_p_el.get('type') == 'IP':
            conn_conf['host'] = addr_p_el.text

        if addr_p_el.get('type') == 'OSI-TSEL':
            conn_conf['tsel'] = int(addr_p_el.text)

        if addr_p_el.get('type') == 'OSI-SSEL':
            conn_conf['ssel'] = int(addr_p_el.text)

        if addr_p_el.get('type') == 'OSI-PSEL':
            conn_conf['psel'] = int(addr_p_el.text)

        if addr_p_el.get('type') == 'OSI-AP-Title':
            conn_conf['ap_title'] = [int(i) for i in addr_p_el.text.split(',')]

        if addr_p_el.get('type') == 'OSI-AE-Qualifier':
            conn_conf['ae_qualifier'] = int(addr_p_el.text)

    return conn_conf


def _parse_value_types(root_el, ln_type_el, logical_device, logical_node):
    for do_el in ln_type_el:
        do_name = do_el.get('name')
        try:
            value_type_fc = _parse_value_type_fc(root_el, do_el)
            fcs = set(_get_all_fcs(value_type_fc))
            for fc in fcs:
                value_type = _get_value_type_for_fc(value_type_fc, fc)
                if value_type:
                    yield {'logical_device': logical_device,
                           'logical_node': logical_node,
                           'fc': fc,
                           'name': do_el.get('name'),
                           'type': value_type}

        except Exception as e:
            mlog.warning('value type %s/%s.%s ignored: %s',
                         logical_device, logical_node, do_name, e, exc_info=e)


def _parse_value_type_fc(root_el, node_el, is_array_element=False):
    basic_value_type = _get_basic_value_type(node_el)
    if basic_value_type:
        return basic_value_type

    type = node_el.get('type')
    btype = node_el.get('bType')
    fc = node_el.get('fc')
    node_type_el = root_el.find(f"./DataTypeTemplates/*"
                                f"[@id='{type}']")
    if node_type_el is None:
        mlog.warning('type %s ignored: not defined', type)
        return

    array_length = node_el.get('count')
    if array_length and not is_array_element:
        element_type = _parse_value_type_fc(
            root_el, node_el, is_array_element=True)
        if element_type is None:
            return

        return {'type': 'ARRAY',
                'element_type': element_type,
                'length': array_length,
                'fc': fc}

    if btype == 'Struct':
        elements = [{'type': _parse_value_type_fc(root_el, da_el),
                     'name': da_el.get('name'),
                     'fc': da_el.get('fc')}
                    for da_el in node_type_el]
        if any(el['type'] is None for el in elements):
            return

        return {'type': 'STRUCT',
                'elements': elements,
                'fc': fc}


def _get_all_fcs(value_type):
    if value_type is None:
        return

    if value_type.get('fc') is not None:
        yield value_type.get('fc')

    if 'elements' in value_type:
        for element_vt in value_type['elements']:
            yield from _get_all_fcs(element_vt)

    if 'element_type' in value_type:
        yield from _get_all_fcs(value_type['element_type'])


def _get_value_type_for_fc(value_type, fc):
    if isinstance(value_type, str):
        return value_type

    if value_type['type'] == 'ARRAY':
        if value_type['fc'] is not None and value_type['fc'] != fc:
            return

        element_type = _get_value_type_for_fc(value_type['element_type'], fc)
        if element_type:
            return {'type': 'ARRAY',
                    'element_type': element_type,
                    'length': value_type['length']}

    if value_type['type'] == 'STRUCT':
        if value_type['fc'] is not None and value_type['fc'] != fc:
            return

        elements = []
        for el in value_type['elements']:
            if el['fc'] is not None and el['fc'] != fc:
                continue

            element_type = _get_value_type_for_fc(el['type'], fc)
            if element_type is not None:
                elements.append({'name': el['name'],
                                 'type': element_type})
        if elements:
            return {'type': 'STRUCT',
                    'elements': elements}


def _parse_datasets(ied_name, logical_device, logical_node, ln_el):
    for dataset_el in ln_el.findall('./DataSet'):
        name = dataset_el.get('name')
        try:
            yield {
                'ref': {'logical_device': logical_device,
                        'logical_node': logical_node,
                        'name': name},
                'values': list(_parse_dataset_values(dataset_el, ied_name))}

        except Exception as e:
            mlog.warning('dataset %s ignored: %s', name, e, exc_info=e)


def _parse_dataset_values(dataset_el, ied_name):
    ds_name = dataset_el.get('name')
    for i, fcda_el in enumerate(dataset_el):
        if fcda_el.tag != 'FCDA':
            continue
        try:
            fc = fcda_el.get('fc')
            do_name = fcda_el.get('doName')
            da_name = fcda_el.get('daName')
            names = []
            if do_name:
                names.extend(_names_from_fcda_name(do_name))
            if da_name:
                names.extend(_names_from_fcda_name(da_name))
            yield {
                'logical_device': _create_logical_device(
                    ied_name, fcda_el.get('ldInst')),
                'logical_node': _create_logical_node(fcda_el.get('prefix'),
                                                     fcda_el.get('lnClass'),
                                                     fcda_el.get('lnInst')),
                'fc': fc,
                'names': names}

        except Exception as e:
            mlog.warning('dataset %s value at index %s ignored: %s',
                         ds_name, i, e, exc_info=e)


def _names_from_fcda_name(name):
    for i in name.split('.'):
        _, _, after = i.partition('(')
        if after:
            idx, _, _ = after.partition(')')
            yield int(idx)

        else:
            yield i


def _parse_rcbs(logical_device, logical_node, ln_el, uneditable_rcb):
    for rc_el in ln_el.findall('./ReportControl'):
        name = rc_el.get('name')
        try:
            yield from _parse_rcb(rc_el=rc_el,
                                  logical_device=logical_device,
                                  logical_node=logical_node,
                                  uneditable_rcb=uneditable_rcb)

        except Exception as e:
            mlog.warning('rcb %s ignored: %s', name, e, exc_info=e)


def _parse_rcb(rc_el, logical_device, logical_node, uneditable_rcb):
    name = rc_el.get('name')
    report_id = rc_el.get('rptID')
    dataset = rc_el.get('datSet')
    rcb_type = 'BUFFERED' if rc_el.get('buffered') == 'true' else 'UNBUFFERED'
    if not report_id:
        rcb_type_short = {'BUFFERED': 'BR',
                          'UNBUFFERED': 'RP'}[rcb_type]
        report_id = f"{logical_device}/{logical_node}.{rcb_type_short}.{name}"

    for rcb_name in _parse_rcb_names(rc_el):
        yield {
            'ref': {'logical_device': logical_device,
                    'logical_node': logical_node,
                    'type': rcb_type,
                    'name': rcb_name},
            'report_id': report_id,
            'dataset': {'logical_device': logical_device,
                        'logical_node': logical_node,
                        'name': dataset} if dataset else None,
            'conf_revision': int(rc_el.get('confRev')),
            'optional_fields': list(_parse_rcb_opt_flds(rc_el)),
            'buffer_time': int(rc_el.get('bufTime', '0')),
            'trigger_options': list(_parse_rcb_trg_ops(rc_el)),
            'integrity_period': int(rc_el.get('intgPd', '0')),
            'uneditable': uneditable_rcb}


def _parse_rcb_names(rc_el):
    name = rc_el.get('name')
    rpt_enabled_el = rc_el.find('./RptEnabled')
    max_rcbs = 0
    if rpt_enabled_el is not None:
        max_rcbs = int(rpt_enabled_el.get('max', '1'))

    indexed = rc_el.get('indexed') != 'false'

    if indexed and max_rcbs > 1:
        for i in range(max_rcbs):
            yield f'{name}{i+1:02}'

    else:
        yield name


def _parse_data(root_el, ln_type_el, ied_name, ap_name, logical_device,
                logical_node, datasets):

    def parse_node(node_el, names):
        if not node_el.get('name'):
            return

        node_type = node_el.get('type')
        if not node_type:
            return

        names = [*names, node_el.get('name')]
        type_el = root_el.find(f"./DataTypeTemplates/*"
                               f"[@id='{node_type}']")
        if type_el is None:
            return

        cdc = type_el.get('cdc')
        if cdc:
            data_ref = {'logical_device': logical_device,
                        'logical_node': logical_node,
                        'names': names}
            yield {
                'ref': data_ref,
                'cdc': cdc if cdc in _cdc_builtin else None,
                'datasets': list(_get_data_datasets(data_ref, datasets)),
                'values': list(_get_data_values(root_el, type_el))}

        for nd_el in type_el:
            yield from parse_node(nd_el, names)

    for node_el in ln_type_el:
        name = node_el.get('name')
        try:
            yield from parse_node(node_el, [])

        except Exception as e:
            mlog.warning('data %s/%s.%s ignored: %s',
                         logical_device, logical_node, name, e, exc_info=e)


def _get_data_datasets(data_ref, datasets):
    data_datasets = []
    for dataset in datasets:
        for value in dataset['values']:
            if (data_ref['logical_device'] == value['logical_device'] and
                data_ref['logical_node'] == value['logical_node'] and
                data_ref['names'] ==
                    value['names'][:len(data_ref['names'])] and
                    dataset['ref'] not in data_datasets):
                data_datasets.append(dataset['ref'])
                yield dataset['ref']


def _get_data_values(root_el, type_el):
    cdc = type_el.get('cdc')
    attrs = {node_el.get('name'): node_el for node_el in type_el}
    writable = _get_cdc_writeable(cdc)
    for value_name in _get_cdc_value_names(type_el):
        if value_name not in attrs:
            continue

        value = {'name': value_name,
                 'writable': writable}
        node_el = attrs[value_name]
        node_btype = node_el.get('bType')
        node_type = node_el.get('type')
        if node_btype == 'Enum':
            value['enumerated'] = _parse_enumerated(root_el, node_type)

        yield value


def _parse_commands(root_el, ln_el, ln_type_el, logical_device, logical_node):
    for do_el in ln_type_el:
        do_name = do_el.get('name')
        do_type = do_el.get('type')

        do_type_el = root_el.find(f"./DataTypeTemplates/*"
                                  f"[@id='{do_type}']")
        cdc = do_type_el.get('cdc')
        if cdc not in {'SPC',
                       'DPC',
                       'INC',
                       'ENC',
                       'BSC',
                       'ISC',
                       'APC',
                       'BAC'}:
            continue

        try:
            model = _parse_command_model(ln_el, do_el, do_type_el)
            if model is None:
                continue

            oper_el = do_type_el.find("./DA[@name='Oper']")
            oper_type = oper_el.get('type')
            oper_type_el = root_el.find(f"./DataTypeTemplates/*"
                                        f"[@id='{oper_type}']")
            with_operate_time = (
                oper_type_el.find("./BDA[@name='operTm']") is not None)

            cmd = {
                'ref': {
                    'logical_device': logical_device,
                    'logical_node': logical_node,
                    'name': do_name},
                'model': model,
                'with_operate_time': with_operate_time,
                'cdc': cdc}

            ctl_val_el = oper_type_el.find("./BDA[@name='ctlVal']")
            if ctl_val_el.get('bType') == 'Enum':
                cmd['enumerated'] = _parse_enumerated(
                    root_el, ctl_val_el.get('type'))

            yield cmd

        except Exception as e:
            mlog.warning('command %s/%s.%s ignored: %s',
                         logical_device, logical_node, do_name, e, exc_info=e)


def _parse_command_model(ln_el, do_el, do_type_el):
    do_name = do_el.get('name')
    ctl_model_el = do_type_el.find("./DA[@name='ctlModel']")
    if ctl_model_el is None:
        return

    val_el = ln_el.find(f"./DOI[@name='{do_name}']"
                        f"/DAI[@name='ctlModel']"
                        f"/Val")
    if val_el is None:
        val_el = ctl_model_el.find('.Val')
    if val_el is None:
        return

    ctl_model = val_el.text
    if ctl_model is None or ctl_model == 'status-only':
        return

    model = {
        'direct-with-normal-security': 'DIRECT_WITH_NORMAL_SECURITY',
        'sbo-with-normal-security': 'SBO_WITH_NORMAL_SECURITY',
        'direct-with-enhanced-security':
            'DIRECT_WITH_ENHANCED_SECURITY',
        'sbo-with-enhanced-security': 'SBO_WITH_ENHANCED_SECURITY'
        }.get(ctl_model)
    if model is None:
        raise Exception(f'unknown control model {ctl_model}')

    return model


def _parse_rcb_opt_flds(rc_el):
    opt_fields_el = rc_el.find('./OptFields')

    if opt_fields_el is None or opt_fields_el.get('bufOvfl') != 'false':
        yield 'BUFFER_OVERFLOW'

    if opt_fields_el is None:
        return

    if opt_fields_el.get('seqNum') == 'true':
        yield 'SEQUENCE_NUMBER'

    if opt_fields_el.get('timeStamp') == 'true':
        yield 'REPORT_TIME_STAMP'

    if opt_fields_el.get('reasonCode') == 'true':
        yield 'REASON_FOR_INCLUSION'

    if opt_fields_el.get('dataSet') == 'true':
        yield 'DATA_SET_NAME'

    if opt_fields_el.get('dataRef') == 'true':
        yield 'DATA_REFERENCE'

    if opt_fields_el.get('entryID') == 'true':
        yield 'ENTRY_ID'

    if opt_fields_el.get('configRef') == 'true':
        yield 'CONF_REVISION'


def _parse_rcb_trg_ops(rc_el):
    trg_ops_el = rc_el.find('./TrgOps')
    if trg_ops_el is None or trg_ops_el.get('gi') != 'false':
        yield 'GENERAL_INTERROGATION'

    if trg_ops_el is None:
        return

    if trg_ops_el.get('dchg') == 'true':
        yield 'DATA_CHANGE'

    if trg_ops_el.get('qchg') == 'true':
        yield 'QUALITY_CHANGE'

    if trg_ops_el.get('dupd') == 'true':
        yield 'DATA_UPDATE'

    if trg_ops_el.get('period') == 'true':
        yield 'INTEGRITY'


def _get_basic_value_type(node):
    btype = node.get('bType')
    type = node.get('type')
    if btype == "BOOLEAN":
        return "BOOLEAN"

    if btype == "INT8":
        return "INTEGER"

    if btype == "INT16":
        return "INTEGER"

    if btype == "INT24":
        return "INTEGER"

    if btype == "INT32":
        return "INTEGER"

    if btype == "INT64":
        return "INTEGER"

    if btype == "INT128":
        return "INTEGER"

    if btype == "INT8U":
        return "UNSIGNED"

    if btype == "INT16U":
        return "UNSIGNED"

    if btype == "INT24U":
        return "UNSIGNED"

    if btype == "INT32U":
        return "UNSIGNED"

    if btype == "FLOAT32":
        return "FLOAT"

    if btype == "FLOAT64":
        return "FLOAT"

    if btype == "Enum":

        if type == "sev":
            return "SEVERITY"

        if type == "dir":
            return "DIRECTION"

        return "INTEGER"

    if btype == "Dbpos":
        return "DOUBLE_POINT"

    if btype == "Tcmd":
        return 'BINARY_CONTROL'

    if btype == "Quality":
        return "QUALITY"

    if btype == "Timestamp":
        return "TIMESTAMP"

    if btype == "VisString32":
        return "VISIBLE_STRING"

    if btype == "VisString64":
        return "VISIBLE_STRING"

    if btype == "VisString129":
        return "VISIBLE_STRING"

    if btype == "VisString255":
        return "VISIBLE_STRING"

    if btype == "Octet64":
        return "OCTET_STRING"

    if btype == "Unicode255":
        return "MMS_STRING"

    if btype == "Struct":

        if type == "AnalogueValue":
            return "ANALOGUE"

        if type == "Vector":
            return "VECTOR"

        if type == "ValWithTrans":
            return 'STEP_POSITION'

    if btype == "Check":
        return 'INTEGER'

    if btype == "OptFlds":
        return 'BIT_STRING'

    if btype == "ObjRef":
        return 'VISIBLE_STRING'

    if btype == "PhyComAddr":
        return {'type': 'STRUCT',
                'elements': [
                    {'name': 'Addr',
                     'type': 'OCTET_STRING'},
                    {'name': 'PRIORITY',
                     'type': 'UNSIGNED'},
                    {'name': 'VID',
                     'type': 'UNSIGNED'},
                    {'name': 'APPID',
                     'type': 'UNSIGNED'}]}

    if btype in {"EntryTime",
                 "Currency"}:
        mlog.warning('basic types EntryTime and Currency not supported:'
                     'respective DO has undefined type')

    # "TrgOps"
    # "OptFlds"
    # "SvOptFlds"


def _parse_enumerated(root_el, type_name):
    type_el = root_el.find(f"./DataTypeTemplates/EnumType"
                           f"[@id='{type_name}']")
    return {'name': type_el.get('id'),
            'values': [{'value': int(val_el.get('ord')),
                        'label': val_el.text}
                       for val_el in type_el if val_el.text]}


def _create_logical_device(ied_name, inst):
    return f"{ied_name}{inst}"


def _create_logical_node(prefix, ln_class, inst):
    return f"{prefix or ''}{ln_class}{inst or ''}"


def _get_cdc_value_names(type_el):
    cdc = type_el.get('cdc')
    if cdc == 'SPS':
        yield 'stVal'
        return

    if cdc == 'DPS':
        yield 'stVal'
        return

    if cdc == 'INS':
        yield 'stVal'
        return

    if cdc == 'ENS':
        yield 'stVal'
        return

    if cdc == 'ACT':
        yield 'general'
        yield 'phsA'
        yield 'phsB'
        yield 'phsC'
        yield 'neut'
        # yield 'originSrc'
        # yield 'operTmPhsA'
        # yield 'operTmPhsB'
        # yield 'operTmPhsC'
        return

    if cdc == 'ACD':
        yield 'general'
        yield 'dirGeneral'
        yield 'phsA'
        yield 'dirPhsA'
        yield 'phsB'
        yield 'dirPhsB'
        yield 'phsC'
        yield 'dirPhsC'
        yield 'neut'
        yield 'dirNeut'
        return

    if cdc == 'SEC':
        yield 'cnt'
        yield 'sev'
        yield 'addr'
        yield 'addInfo'
        return

    if cdc == 'BCR':
        yield 'actVal'
        yield 'frVal'
        yield 'frTm'
        return

    if cdc == 'HST':
        # yield 'hstVal'
        return

    if cdc == 'VSS':
        yield 'stVal'
        return

    if cdc == 'MV':
        yield 'instMag'
        yield 'mag'
        yield 'range'
        return

    if cdc == 'CMV':
        yield 'instCVal'
        yield 'cVal'
        yield 'range'
        yield 'rangeAng'
        return

    if cdc == 'SAV':
        yield 'instMag'
        return

    if cdc == 'SPC':
        yield 'stVal'
        return

    if cdc == 'DPC':
        yield 'stVal'
        return

    if cdc == 'INC':
        yield 'stVal'
        return

    if cdc == 'ENC':
        yield 'stVal'
        return

    if cdc == 'BSC':
        yield 'valWTr'
        return

    if cdc == 'ISC':
        yield 'valWTr'
        return

    if cdc == 'APC':
        yield 'mxVal'
        return

    if cdc == 'BAC':
        yield 'mxVal'
        return

    if cdc == 'SPG':
        yield 'setVal'
        return

    if cdc == 'ING':
        yield 'setVal'
        return

    if cdc == 'ENG':
        yield 'setVal'
        return

    if cdc == 'ORG':
        # yield 'setSrcRef'
        # yield 'setTstRef'
        # yield 'setSrcCB'
        # yield 'setTstCB'
        yield 'intAddr'
        yield 'tstEna'
        return

    if cdc == 'TSG':
        yield 'setTm'
        yield 'setCal'
        return

    if cdc == 'CUG':
        # yield 'cur'
        return

    if cdc == 'VSG':
        yield 'setVal'
        return

    if cdc == 'ASG':
        yield 'setMag'
        return

    if cdc == 'CURVE':
        yield 'setCharact'
        yield 'setParA'
        yield 'setParB'
        yield 'setParC'
        yield 'setParD'
        yield 'setParE'
        yield 'setParF'
        return

    if cdc == 'CSG':
        yield 'pointZ'
        yield 'numPts'
        # yield 'crvPts'
        return

    if cdc == 'DPL':
        yield 'vendor'
        yield 'hwRev'
        yield 'swRev'
        yield 'serNum'
        yield 'model'
        yield 'location'
        yield 'name'
        yield 'owner'
        yield 'ePSName'
        yield 'primeOper'
        yield 'secondOper'
        yield 'latitude'
        yield 'longitude'
        yield 'altitude'
        yield 'mrID'
        yield 'd'
        yield 'dU'
        yield 'cdcNs'
        yield 'cdcName'
        yield 'dataNs'
        return

    if cdc == 'LPL':
        yield 'vendor'
        yield 'swRev'
        yield 'd'
        yield 'dU'
        yield 'configRev'
        yield 'paramRev'
        yield 'valRev'
        yield 'ldNs'
        yield 'lnNs'
        yield 'cdcNs'
        yield 'cdcName'
        yield 'dataNs'
        return

    if cdc == 'CSD':
        yield 'xUnits'
        yield 'xD'
        yield 'xDU'
        yield 'yUnits'
        yield 'yD'
        yield 'yDU'
        yield 'zUnits'
        yield 'zD'
        yield 'zDU'
        yield 'numPts'
        yield 'crvPts'
        yield 'd'
        yield 'dU'
        yield 'cdcNs'
        yield 'cdcName'
        yield 'dataNs'
        return

    if cdc in {'WYE',
               'DEL',
               'SEQ',
               'HMV',
               'HWYE',
               'HDEL'}:
        return

    for da_el in type_el:
        fc = da_el.get('fc')
        btype = da_el.get('bType')
        if (fc in {'MX',
                   'ST',
                   'SP'} and
                btype not in {'Quality',
                              'Timestamp'}):
            yield da_el.get('name')


def _get_cdc_writeable(cdc):
    if cdc in {'SPG',
               'ING',
               'ENG',
               'ORG',
               'TSG',
               'CUG',
               'VSG',
               'ASG',
               'CURVE',
               'CSG'}:
        return True

    return False


_cdc_builtin = {'SPS'
                'DPS',
                'INS',
                'ENS',
                'ACT',
                'ACD',
                'SEC',
                'BCR',
                'HST',
                'VSS',
                'MV',
                'CMV',
                'SAV',
                'SPC',
                'DPC',
                'INC',
                'ENC',
                'BSC',
                'ISC',
                'APC',
                'BAC',
                'SPG',
                'ING',
                'ENG',
                'ORG',
                'TSG',
                'CUG',
                'VSG',
                'ASG',
                'CURVE',
                'CSG',
                'DPL',
                'LPL',
                'CSD',
                'WYE',
                'DEL',
                'SEQ',
                'HMV',
                'HWYE',
                'HDEL'}
