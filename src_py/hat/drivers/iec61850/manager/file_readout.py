from pathlib import Path
import argparse
import functools
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
            for ied_name, device_conf in _get_ieds(root_el)}


def _read_xml(source):
    it = xml.etree.ElementTree.iterparse(source)
    for _, el in it:
        prefix, has_namespace, postfix = el.tag.partition('}')
        if has_namespace:
            el.tag = postfix
    return it.root


def _get_ieds(root_el):
    for ied_el in root_el.findall("./IED"):
        ied_name = ied_el.get('name')
        if ied_name == 'TEMPLATE':
            mlog.warning(
                "ied name is 'TEMPLATE': possible insufficient structure")

        uneditable_rcb = list(_get_uneditable_rcb(ied_el))

        for ap_el in ied_el.findall("./AccessPoint"):
            if ap_el.find("./Server/LDevice") is None:
                continue

            mlog.info('IED %s', ied_name)
            yield ied_name, _get_device(root_el=root_el,
                                        ap_el=ap_el,
                                        ied_name=ied_name,
                                        uneditable_rcb=uneditable_rcb)


def _get_uneditable_rcb(ied_el):
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


def _get_device(root_el, ap_el, ied_name, uneditable_rcb):
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

            mlog.info('value types for %s/%s', logical_device, logical_node)
            value_types.extend(_get_value_types(
                root_el, ln_type_el, logical_device, logical_node))

            datasets.extend(_get_datasets(
                ied_name, logical_device, logical_node, ln_el))

            rcbs.extend(_get_rcbs(
                logical_device, logical_node, ln_el, uneditable_rcb))

            data.extend(_get_data(root_el=root_el,
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


def _get_value_types(root_el, ln_type_el, logical_device, logical_node):
    for do_el in ln_type_el:
        do_name = do_el.get('name')
        mlog.debug('value type %s/%s.%s',
                   logical_device, logical_node, do_name)
        try:
            value_type_fc = _get_value_type(root_el, do_el, with_fc=True)
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


def _get_datasets(ied_name, logical_device, logical_node, ln_el):
    for dataset_el in ln_el.findall('./DataSet'):
        name = dataset_el.get('name')
        mlog.info("dataset %s/%s.%s", logical_device, logical_node, name)
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


def _get_rcbs(logical_device, logical_node, ln_el, uneditable_rcb):
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
    rcb_type_short = {'BUFFERED': 'BR',
                      'UNBUFFERED': 'RP'}[rcb_type]
    if not report_id:
        report_id = f"{logical_device}/{logical_node}.{rcb_type_short}.{name}"
    mlog.info('rcb %s/%s.%s.%s',
              logical_device, logical_node, rcb_type_short, name)
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


def _get_data(root_el, ln_type_el, ied_name, ap_name, logical_device,
              logical_node, datasets):

    def parse_node(node_el, names, fc):
        if not node_el.get('name'):
            return

        type_el = _get_node_type_el(root_el, node_el)
        if type_el is None:
            return

        names = [*names, node_el.get('name')]
        fc = node_el.get('fc') or fc
        cdc = type_el.get('cdc')
        if cdc:
            yield from _get_data_confs_for_cdc(
                root_el, type_el, cdc, logical_device, logical_node, fc, names,
                datasets)

        for nd_el in type_el:
            yield from parse_node(nd_el, names, fc)

    for node_el in ln_type_el:
        name = node_el.get('name')
        mlog.info('data %s/%s.%s', logical_device, logical_node, name)
        try:
            yield from parse_node(node_el, [], None)

        except Exception as e:
            mlog.warning('data %s/%s.%s ignored: %s',
                         logical_device, logical_node, name, e, exc_info=e)


def _parse_commands(root_el, ln_el, ln_type_el, logical_device, logical_node):
    for do_el in ln_type_el:
        do_name = do_el.get('name')
        do_type_el = _get_node_type_el(root_el, do_el)
        if not do_type_el:
            continue

        # cdc = do_type_el.get('cdc')
        # if cdc not in {'SPC',
        #                'DPC',
        #                'INC',
        #                'ENC',
        #                'BSC',
        #                'ISC',
        #                'APC',
        #                'BAC'}:
        #     continue
        # commands filtered by Oper attribute and model, instead of cdc
        oper_el = do_type_el.find("./DA[@name='Oper']")
        if oper_el is None or oper_el.get('fc') != 'CO':
            continue

        mlog.info('command %s/%s.%s',
                  logical_device, logical_node, do_name)
        try:
            model = _parse_command_model(ln_el, do_el, do_type_el)
            if model is None:
                # TODO: log for status-only command model?
                continue

            oper_type_el = _get_node_type_el(root_el, oper_el)
            if oper_type_el is None:
                raise Exception('Oper type undefined')

            with_operate_time = (
                oper_type_el.find("./BDA[@name='operTm']") is not None)
            ctl_val_el = oper_type_el.find("./BDA[@name='ctlVal']")
            if ctl_val_el is None:
                raise Exception('no ctlVal attribute')

            value_type = _get_value_type(root_el, ctl_val_el)
            if value_type is None:
                raise Exception('no value type')

            cmd = {
                'ref': {
                    'logical_device': logical_device,
                    'logical_node': logical_node,
                    'name': do_name},
                'value_type': value_type,
                'model': model,
                'with_operate_time': with_operate_time}

            if ctl_val_el.get('bType') == 'Enum':
                cmd['enumerated'] = _parse_enumerated(
                    root_el, ctl_val_el.get('type'))

            yield cmd

        except Exception as e:
            mlog.warning('command %s/%s.%s ignored: %s',
                         logical_device, logical_node, do_name, e, exc_info=e)


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
            conn_conf['tsel'] = int(addr_p_el.text, 16)

        if addr_p_el.get('type') == 'OSI-SSEL':
            conn_conf['ssel'] = int(addr_p_el.text, 16)

        if addr_p_el.get('type') == 'OSI-PSEL':
            conn_conf['psel'] = int(addr_p_el.text, 16)

        if addr_p_el.get('type') == 'OSI-AP-Title':
            conn_conf['ap_title'] = [int(i) for i in addr_p_el.text.split(',')]

        if addr_p_el.get('type') == 'OSI-AE-Qualifier':
            conn_conf['ae_qualifier'] = int(addr_p_el.text)

    return conn_conf


def _get_value_type(root_el, node_el, is_array_element=False, with_fc=False):
    if node_el.tag == 'ProtNs':
        return

    fc = node_el.get('fc')
    value_type = _get_basic_value_type(node_el)
    if value_type:
        if with_fc:
            return {'type': value_type,
                    'fc': fc}
        else:
            return value_type

    array_length = node_el.get('count')
    if array_length and not is_array_element:
        element_type = _get_value_type(
            root_el, node_el, is_array_element=True, with_fc=with_fc)
        if element_type is None:
            return

        value_type = {'type': 'ARRAY',
                      'element_type': element_type,
                      'length': array_length}
        if with_fc:
            value_type['fc'] = fc
        return value_type

    node_type = node_el.get('type')
    node_btype = node_el.get('bType')
    if node_type is None:
        mlog.warning("attr 'type' does not exist for bType %s", node_btype)
        return

    node_type_el = _get_node_type_el(root_el, node_el)
    if node_type_el is None:
        mlog.warning("type %s not defined", )
        return

    elements = []
    for da_el in node_type_el:
        el_type = _get_value_type(root_el, da_el, with_fc=with_fc)
        if el_type is None:
            continue

        value_type = {'type': el_type,
                      'name': da_el.get('name')}
        if with_fc:
            value_type['fc'] = da_el.get('fc')
        elements.append(value_type)

    value_type = {'type': 'STRUCT',
                  'elements': elements}
    if with_fc:
        value_type['fc'] = fc
    return value_type


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
    if value_type['fc'] is not None and value_type['fc'] != fc:
        return

    if value_type['type'] == 'ARRAY':
        element_type = _get_value_type_for_fc(value_type['element_type'], fc)
        if element_type:
            return {'type': 'ARRAY',
                    'element_type': element_type,
                    'length': value_type['length']}

    elif value_type['type'] == 'STRUCT':
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

    elif isinstance(value_type['type'], str):
        return value_type['type']


def _get_node_type_el(root_el, node_el):
    node_type = node_el.get('type')
    if not node_type:
        return

    if node_el.tag in {'DO', 'SDO'}:
        type_tag = 'DOType'
    elif node_el.tag in {'DA', 'BDA'}:
        type_tag = 'DAType'
    else:
        mlog.warning('unexpected TAG %s', node_el.tag)
        type_tag = '*'
    return root_el.find(f"./DataTypeTemplates/{type_tag}"
                        f"[@id='{node_type}']")


def _names_from_fcda_name(name):
    for i in name.split('.'):
        _, _, after = i.partition('(')
        if after:
            idx, _, _ = after.partition(')')
            yield int(idx)

        else:
            yield i


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


def _parse_command_model(ln_el, do_el, do_type_el):
    do_name = do_el.get('name')
    ctl_model_el = do_type_el.find("./DA[@name='ctlModel']")
    if ctl_model_el is None:
        return

    model_map = {
        'direct-with-normal-security': 'DIRECT_WITH_NORMAL_SECURITY',
        'sbo-with-normal-security': 'SBO_WITH_NORMAL_SECURITY',
        'direct-with-enhanced-security': 'DIRECT_WITH_ENHANCED_SECURITY',
        'sbo-with-enhanced-security': 'SBO_WITH_ENHANCED_SECURITY',
        'status-only': None}
    val_el = ln_el.find(f"./DOI[@name='{do_name}']"
                        f"/DAI[@name='ctlModel']"
                        f"/Val")
    if val_el is None or val_el.text not in model_map:
        val_el = ctl_model_el.find('.Val')
    if val_el is None:
        return

    ctl_model = val_el.text
    if ctl_model is None or ctl_model == 'status-only':
        return

    model = model_map.get(ctl_model)
    if model is None:
        raise Exception('unexpected control model')

    return model


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

    if btype == "VisString65":
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


def _get_data_conf(root_el, type_el, logical_device, logical_node, fc,
                   names, datasets, value_name=None, quality_name=None,
                   timestamp_name=None, selected_name=None, writable=False,
                   quality_ref=None, timestamp_ref=None, selected_ref=None):
    da_name_el = {node_el.get('name'): node_el for node_el in type_el}
    if value_name and value_name not in da_name_el:
        return

    for value_da_el in type_el if not value_name else [da_name_el[value_name]]:
        da_name = value_da_el.get('name')
        if value_name and value_name != da_name:
            continue

        fc = value_da_el.get('fc') or fc
        btype = value_da_el.get('bType')
        if not value_name and (fc not in {'MX', 'ST', 'SP'} or
                               btype in {'Quality', 'Timestamp'}):
            continue
        # TODO check fc and value type for cdc?

        data_ref = {'logical_device': logical_device,
                    'logical_node': logical_node,
                    'fc': fc,
                    'names': names}
        value_type = _get_value_type(root_el, value_da_el)
        if value_type is None:
            raise Exception('no value type')

        value_ref = {**data_ref,
                     'names': [*data_ref['names'], da_name]}

        if quality_name:
            if (quality_name and
                quality_name in da_name_el and
                    da_name_el[quality_name].get('bType') == 'Quality'):
                quality_ref = {**data_ref,
                               'names': [*data_ref['names'], quality_name]}

        if timestamp_name:
            if (timestamp_name and
                timestamp_name in da_name_el and
                    da_name_el[timestamp_name].get('bType') == 'Timestamp'):
                timestamp_ref = {**data_ref,
                                 'names': [*data_ref['names'], timestamp_name]}

        if selected_name:
            if (selected_name and
                selected_name in da_name_el and
                    da_name_el[selected_name].get('bType') == 'BOOLEAN'):
                selected_ref = {**data_ref,
                                'names': [*data_ref['names'], selected_name]}

        data_conf = {
            'value': value_ref,
            'value_type': value_type,
            'datasets': list(_get_value_datasets(
                datasets, value_ref, quality_ref, timestamp_ref,
                selected_ref)),
            'writable': writable}
        if quality_ref:
            data_conf['quality'] = quality_ref

        if timestamp_ref:
            data_conf['timestamp'] = timestamp_ref

        if selected_ref:
            data_conf['selected'] = selected_ref

        if value_da_el.get('bType') == 'Enum':
            data_conf['enumerated'] = _parse_enumerated(
                root_el, value_da_el.get('type'))

        yield data_conf

        value_da_type = value_da_el.get('type')
        if not value_da_type or btype != 'Struct':
            return

        type_el = _get_node_type_el(root_el, value_da_el)
        if type_el is None:
            raise Exception('type undefined')

        names = [*data_ref['names'], da_name]
        yield from _get_data_conf(
            root_el, type_el, logical_device, logical_node, fc, names,
            datasets,
            writable=writable,
            quality_ref=quality_ref,
            timestamp_ref=timestamp_ref,
            selected_ref=selected_ref,)


def _get_value_datasets(datasets, value_ref, quality_ref, timestamp_ref,
                        selected_ref):
    for dataset in datasets:
        for ds_val_ref in dataset['values']:
            if _is_ref_in_dataset(ds_val_ref, value_ref):
                yield {
                    'ref': dataset['ref'],
                    'quality': (_is_ref_in_dataset(ds_val_ref, quality_ref)
                                if quality_ref else False),
                    'timestamp': (_is_ref_in_dataset(ds_val_ref, timestamp_ref)
                                  if timestamp_ref else False),
                    'selected': (_is_ref_in_dataset(ds_val_ref, selected_ref)
                                 if selected_ref else False)}


def _is_ref_in_dataset(ds_value_ref, ref):
    if ds_value_ref['logical_device'] != ref['logical_device']:
        return False

    if ds_value_ref['logical_node'] != ref['logical_node']:
        return False

    if ds_value_ref['fc'] != ref['fc']:
        return False

    if ds_value_ref['names'] == ref['names']:
        return True

    if len(ds_value_ref['names']) > len(ref['names']):
        return True

    return ref['names'][:len(ds_value_ref['names'])] == ds_value_ref['names']


def _get_data_confs_for_cdc(root_el, type_el, cdc,
                            logical_device, logical_node, fc, names, datasets):
    get_data_conf = functools.partial(
        _get_data_conf, root_el, type_el, logical_device, logical_node, fc,
        names, datasets)
    if cdc == 'SPS':
        yield from get_data_conf('stVal', 'q', 't')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'DPS':
        yield from get_data_conf('stVal', 'q', 't')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'INS':
        yield from get_data_conf('stVal', 'q', 't')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'ENS':
        yield from get_data_conf('stVal', 'q', 't')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'ACT':
        yield from get_data_conf('general', 'q', 't')
        yield from get_data_conf('phsA', 'q', 't')
        yield from get_data_conf('phsB', 'q', 't')
        yield from get_data_conf('phsC', 'q', 't')
        yield from get_data_conf('neut', 'q', 't')
        # 'originSrc'
        # 'operTmPhsA'
        # 'operTmPhsB'
        # 'operTmPhsC'
        return

    elif cdc == 'ACD':
        yield from get_data_conf('general', 'q', 't')
        yield from get_data_conf('dirGeneral', 'q', 't')
        yield from get_data_conf('phsA', 'q', 't')
        yield from get_data_conf('dirPhsA', 'q', 't')
        yield from get_data_conf('phsB', 'q', 't')
        yield from get_data_conf('dirPhsB', 'q', 't')
        yield from get_data_conf('phsC', 'q', 't')
        yield from get_data_conf('dirPhsC', 'q', 't')
        yield from get_data_conf('neut', 'q', 't')
        yield from get_data_conf('dirNeut', 'q', 't')
        return

    elif cdc == 'SEC':
        yield from get_data_conf('cnt', timestamp_name='t')
        yield from get_data_conf('sev')
        yield from get_data_conf('addr')
        yield from get_data_conf('addInfo')

    elif cdc == 'BCR':
        yield from get_data_conf('actVal', 'q', 't')
        yield from get_data_conf('frVal', 'q', 'frTm')

    elif cdc == 'HST':
        # 'hstVal'
        return

    elif cdc == 'VSS':
        yield from get_data_conf('stVal', 'q', 't')

    elif cdc == 'MV':
        yield from get_data_conf('instMag', 'q', 't')
        yield from get_data_conf('mag', 'q', 't')
        yield from get_data_conf('range', 'q', 't')
        yield from get_data_conf('subMag', 'subQ')

    elif cdc == 'CMV':
        yield from get_data_conf('instCVal', 'q')
        yield from get_data_conf('subCVal', 'subQ')
        yield from get_data_conf('cVal', 'q', 't')
        yield from get_data_conf('range', 'q')
        yield from get_data_conf('rangeAng', timestamp_name='t')

    elif cdc == 'SAV':
        yield from get_data_conf('instMag', 'q', 't')

    elif cdc == 'SPC':
        yield from get_data_conf('stVal', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'DPC':
        yield from get_data_conf('stVal', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'INC':
        yield from get_data_conf('stVal', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'ENC':
        yield from get_data_conf('stVal', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'BSC':
        yield from get_data_conf('valWTr', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'ISC':
        yield from get_data_conf('valWTr', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'APC':
        yield from get_data_conf('mxVal', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'BAC':
        yield from get_data_conf('mxVal', 'q', 't', 'stSeld')
        yield from get_data_conf('opOk', timestamp_name='tOpOk')
        yield from get_data_conf('subVal', 'subQ')

    elif cdc == 'SPG':
        yield from get_data_conf('setVal', writable=True)

    elif cdc == 'ING':
        yield from get_data_conf('setVal', writable=True)

    elif cdc == 'ENG':
        yield from get_data_conf('setVal', writable=True)

    elif cdc == 'ORG':
        yield from get_data_conf('intAddr', writable=True)
        yield from get_data_conf('tstEna', writable=True)
        # 'setSrcRef'
        # 'setTstRef'
        # 'setSrcCB'
        # 'setTstCB'

    elif cdc == 'TSG':
        yield from get_data_conf('setTm', writable=True)
        yield from get_data_conf('setCal', writable=True)

    elif cdc == 'CUG':
        # 'cur'
        return

    elif cdc == 'VSG':
        yield from get_data_conf('setVal', writable=True)

    elif cdc == 'ASG':
        yield from get_data_conf('setMag', writable=True)

    elif cdc == 'CURVE':
        yield from get_data_conf('setCharact', writable=True)
        yield from get_data_conf('setParA', writable=True)
        yield from get_data_conf('setParB', writable=True)
        yield from get_data_conf('setParC', writable=True)
        yield from get_data_conf('setParD', writable=True)
        yield from get_data_conf('setParE', writable=True)
        yield from get_data_conf('setParF', writable=True)

    elif cdc == 'CSG':
        yield from get_data_conf('pointZ', writable=True)
        yield from get_data_conf('numPts', writable=True)
        # yield 'crvPts'

    elif cdc == 'DPL':
        yield from get_data_conf('vendor')
        yield from get_data_conf('hwRev')
        yield from get_data_conf('swRev')
        yield from get_data_conf('serNum')
        yield from get_data_conf('model')
        yield from get_data_conf('location')
        yield from get_data_conf('name')
        yield from get_data_conf('owner')
        yield from get_data_conf('ePSName')
        yield from get_data_conf('primeOper')
        yield from get_data_conf('secondOper')
        yield from get_data_conf('latitude')
        yield from get_data_conf('longitude')
        yield from get_data_conf('altitude')
        yield from get_data_conf('mrID')
        yield from get_data_conf('d')
        yield from get_data_conf('dU')
        yield from get_data_conf('cdcNs')
        yield from get_data_conf('cdcName')
        yield from get_data_conf('dataNs')

    elif cdc == 'LPL':
        yield from get_data_conf('vendor')
        yield from get_data_conf('swRev')
        yield from get_data_conf('d')
        yield from get_data_conf('dU')
        yield from get_data_conf('configRev')
        yield from get_data_conf('paramRev')
        yield from get_data_conf('valRev')
        yield from get_data_conf('ldNs')
        yield from get_data_conf('lnNs')
        yield from get_data_conf('cdcNs')
        yield from get_data_conf('cdcName')
        yield from get_data_conf('dataNs')

    elif cdc == 'CSD':
        yield from get_data_conf('xUnits')
        yield from get_data_conf('xD')
        yield from get_data_conf('xDU')
        yield from get_data_conf('yUnits')
        yield from get_data_conf('yD')
        yield from get_data_conf('yDU')
        yield from get_data_conf('zUnits')
        yield from get_data_conf('zD')
        yield from get_data_conf('zDU')
        yield from get_data_conf('numPts')
        yield from get_data_conf('crvPts')
        yield from get_data_conf('d')
        yield from get_data_conf('dU')
        yield from get_data_conf('cdcNs')
        yield from get_data_conf('cdcName')
        yield from get_data_conf('dataNs')

    elif cdc in {'WYE',
                 'DEL',
                 'SEQ',
                 'HMV',
                 'HWYE',
                 'HDEL'}:
        return

    else:
        for da_el in type_el:
            fc = da_el.get('fc')
            btype = da_el.get('bType')
            if (fc in {'MX',
                       'ST',
                       'SP'} and
                    btype not in {'Quality',
                                  'Timestamp'}):
                yield from get_data_conf(da_el.get('name'), 'q', 't', 'stSeld')
