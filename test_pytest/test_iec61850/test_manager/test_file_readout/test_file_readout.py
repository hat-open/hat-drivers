import importlib.resources

import pytest

from hat import json
from hat import util

from hat.drivers.iec61850.manager.common import json_schema_repo
from hat.drivers.iec61850.manager.file_readout import readout


json_schema_id = "hat-drivers://iec61850/readout.yaml"


@pytest.fixture(scope='session')
def validator(pytestconfig):
    return json.DefaultSchemaValidator(json_schema_repo)


def test_1(validator):
    with importlib.resources.open_text(__package__, 'test1.cid') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 1

    assert 'Demo' in device_jsons
    device_json = device_jsons['Demo']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 6
    assert len(device_json['commands']) == 4
    assert len(device_json['data']) == 123
    writable_values = [i for i in device_json['data'] if i['writable']]
    assert len(writable_values) == 3
    assert len(device_json['value_types']) == 127

    # assert parent and child data exist for sub DO
    for subdo_name in ["phsA", "phsB", "phsC"]:
        data_parent = util.first(
            device_json['data'],
            lambda i: i['value'] == {
                "logical_device": "DemoMeasurement",
                "logical_node": "I3pMMXU1",
                "fc": "MX",
                "names": ["A", subdo_name, "cVal"]})
        assert data_parent
        assert len(data_parent['datasets']) == 1
        assert data_parent['quality'] == {
            "logical_device": "DemoMeasurement",
            "logical_node": "I3pMMXU1",
            "fc": "MX",
            "names": ["A", subdo_name, "q"]}
        assert data_parent['timestamp'] == {
            "logical_device": "DemoMeasurement",
            "logical_node": "I3pMMXU1",
            "fc": "MX",
            "names": ["A", subdo_name, "t"]}

        data_child = util.first(
            device_json['data'],
            lambda i: i['value'] == {
                "logical_device": "DemoMeasurement",
                "logical_node": "I3pMMXU1",
                "fc": "MX",
                "names": ["A", subdo_name, "cVal", "mag"]})
        assert data_child
        assert len(data_child['datasets']) == 1
        assert data_child['value_type'] == {
            'type': 'STRUCT', 'elements': [{'type': 'FLOAT', 'name': 'f'}]}
        assert data_child['datasets'] == data_parent['datasets']
        assert data_child['quality'] == data_parent['quality']
        assert data_child['timestamp'] == data_parent['timestamp']

        data_child = util.first(
            device_json['data'],
            lambda i: i['value'] == {
                "logical_device": "DemoMeasurement",
                "logical_node": "I3pMMXU1",
                "fc": "MX",
                "names": ["A", subdo_name, "cVal", "mag", "f"]})
        assert data_child
        assert len(data_child['datasets']) == 1
        assert data_child['value_type'] == 'FLOAT'
        assert data_child['datasets'] == data_parent['datasets']
        assert data_child['quality'] == data_parent['quality']
        assert data_child['timestamp'] == data_parent['timestamp']

    # different fcs on the same address are split
    value_types = [i for i in device_json['value_types']
                   if (i['logical_device'] == 'DemoMeasurement' and
                       i['logical_node'] == 'LLN0' and
                       i['name'] == 'Health')]
    assert len(value_types) == 2
    assert util.first(value_types, lambda i: i['fc'] == 'ST')
    assert util.first(value_types, lambda i: i['fc'] == 'DC')

    # command, data and control model on the same address
    value_types = [i for i in device_json['value_types']
                   if (i['logical_device'] == 'DemoProtCtrl' and
                       i['logical_node'] == 'Obj1CSWI4' and
                       i['name'] == 'Pos')]
    assert len(value_types) == 3
    st_value_type = util.first(value_types, lambda i: i['fc'] == 'ST')
    assert st_value_type['type']['type'] == 'STRUCT'
    assert len(st_value_type['type']['elements']) == 3
    assert ({'name': 'stVal', 'type': 'DOUBLE_POINT'} in
            st_value_type['type']['elements'])
    assert ({'name': 'q', 'type': 'QUALITY'} in
            st_value_type['type']['elements'])
    assert ({'name': 't', 'type': 'TIMESTAMP'} in
            st_value_type['type']['elements'])
    cf_value_type = util.first(value_types, lambda i: i['fc'] == 'CF')
    assert len(cf_value_type['type']['elements']) == 1
    assert ({'name': 'ctlModel', 'type': 'INTEGER'} in
            cf_value_type['type']['elements'])
    co_value_type = util.first(value_types, lambda i: i['fc'] == 'CO')
    assert len(co_value_type['type']['elements']) == 3
    assert util.first(co_value_type['type']['elements'],
                      lambda i: i['name'] == 'SBOw')
    assert util.first(co_value_type['type']['elements'],
                      lambda i: i['name'] == 'Oper')
    assert util.first(co_value_type['type']['elements'],
                      lambda i: i['name'] == 'Cancel')

    # rcb with rcbID=""
    rcbs = device_json['rcbs']
    assert rcbs[0]['report_id'] == ''
    assert rcbs[0]['ref']['name'] == 'brcb101'
    assert rcbs[1]['report_id'] == ''
    assert rcbs[1]['ref']['name'] == 'urcb101'

    # no dynamic rcb editable attributes
    assert 'dynamic' not in device_json


def test_2(validator):
    with importlib.resources.open_text(__package__, 'test2.cid') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 1

    assert 'J01' in device_jsons
    device_json = device_jsons['J01']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 15
    assert len(device_json['commands']) == 2
    assert len(device_json['data']) == 369
    writable_values = [i for i in device_json['data'] if i['writable']]
    assert len(writable_values) == 0
    assert len(device_json['value_types']) == 515

    ds_conf = util.first(device_json['datasets'],
                         lambda i: i['ref'] == {
                            'logical_device': 'J01LD0',
                            'logical_node': 'LLN0',
                            'name': 'MeasFlt'})
    assert ds_conf
    value_conf = util.first(ds_conf['values'],
                            lambda i: i == {
                             'logical_device': 'J01LD1',
                             'logical_node': 'UMMXU204',
                             'fc': 'MX',
                             'names': ['PPV', 'phsAB', 'cVal', 'mag', 'f']})

    # indexed rcbs
    for name_pfx in ['rcbMeasFlt', 'rcbStatUrg', 'rcbStatNrml']:
        rcbs = [rcb_conf for rcb_conf in device_json['rcbs']
                if rcb_conf['report_id'] == f"J01LD0/LLN0$BR${name_pfx}"]
        assert len(rcbs) == 5
        assert [i['ref']['name'] for i in rcbs] == [
            f'{name_pfx}0{i}' for i in range(1, 6)]

    assert value_conf


def test_3(validator):
    with importlib.resources.open_text(__package__, 'test3.scd') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 3

    assert 'E1_7SA' in device_jsons
    assert device_jsons['E1_7SA']['connection']['host'] == '192.168.29.162'
    assert device_jsons['E1_7SA']['connection']['tsel'] == 1
    assert device_jsons['E1_7SA']['connection']['ssel'] == 1
    assert device_jsons['E1_7SA']['connection']['psel'] == 1
    assert device_jsons['E1_7SA']['connection']['ap_title'] == [1, 3, 9999, 23]
    assert device_jsons['E1_7SA']['connection']['ae_qualifier'] == 23

    assert 'E1_REL' in device_jsons
    assert device_jsons['E1_REL']['connection']['host'] == '192.168.29.163'
    assert device_jsons['E1_REL']['connection']['tsel'] == 1
    assert device_jsons['E1_REL']['connection']['ssel'] == 1
    assert device_jsons['E1_REL']['connection']['psel'] == 1
    assert device_jsons['E1_REL']['connection']['ap_title'] == [1, 3, 9999, 23]
    assert device_jsons['E1_REL']['connection']['ae_qualifier'] == 23

    assert 'LKKU' in device_jsons
    assert device_jsons['LKKU']['connection']['host'] == '10.228.34.150'
    assert device_jsons['LKKU']['connection']['tsel'] == 1
    assert device_jsons['LKKU']['connection']['ssel'] == 1
    assert device_jsons['LKKU']['connection']['psel'] == 1
    assert device_jsons['LKKU']['connection']['ap_title'] == [1, 3, 9999, 23]
    assert device_jsons['LKKU']['connection']['ae_qualifier'] == 23

    assert len(device_jsons['E1_7SA']['value_types']) == 4053
    assert len(device_jsons['E1_REL']['value_types']) == 1350
    assert len(device_jsons['LKKU']['value_types']) == 3

    # dynamic
    assert device_jsons['E1_7SA']['dynamic']['rcb_editable']['report_id']
    assert device_jsons['E1_7SA']['dynamic']['rcb_editable']['dataset']
    assert device_jsons['E1_7SA']['dynamic']['rcb_editable']['optional_fields']
    assert device_jsons['E1_7SA']['dynamic']['rcb_editable']['buffer_time']
    assert device_jsons['E1_7SA']['dynamic']['rcb_editable']['trigger_options']
    assert device_jsons['E1_7SA']['dynamic']['rcb_editable']['integrity_period']  # NOQA
    assert device_jsons['E1_7SA']['dynamic']['max_datasets'] == 30
    assert device_jsons['E1_7SA']['dynamic']['max_dataset_attributes'] == 60

    assert device_jsons['E1_REL']['dynamic']['rcb_editable']['report_id']
    assert not device_jsons['E1_REL']['dynamic']['rcb_editable']['dataset']
    assert device_jsons['E1_REL']['dynamic']['rcb_editable']['optional_fields']
    assert device_jsons['E1_REL']['dynamic']['rcb_editable']['buffer_time']
    assert device_jsons['E1_REL']['dynamic']['rcb_editable']['trigger_options']
    assert device_jsons['E1_REL']['dynamic']['rcb_editable']['integrity_period']  # NOQA
    assert 'max_datasets' not in device_jsons['E1_REL']['dynamic']
    assert 'max_dataset_attributes' not in device_jsons['E1_REL']['dynamic']

    assert device_jsons['LKKU']['dynamic']['rcb_editable']['report_id']
    assert device_jsons['LKKU']['dynamic']['rcb_editable']['dataset']
    assert device_jsons['LKKU']['dynamic']['rcb_editable']['optional_fields']
    assert device_jsons['LKKU']['dynamic']['rcb_editable']['buffer_time']
    assert device_jsons['LKKU']['dynamic']['rcb_editable']['trigger_options']
    assert device_jsons['LKKU']['dynamic']['rcb_editable']['integrity_period']
    assert 'max_datasets' not in device_jsons['LKKU']['dynamic']
    assert 'max_dataset_attributes' not in device_jsons['LKKU']['dynamic']

    # verify a E1_REL dataset values
    assert len(device_jsons['E1_REL']['datasets']) == 5
    ds_staturg = util.first(device_jsons['E1_REL']['datasets'],
                            lambda i: i['ref'] == {
                                'logical_device': 'E1_RELLD0',
                                'logical_node': 'LLN0',
                                'name': 'StatUrg'})
    assert len(ds_staturg['values']) == 107

    value = ds_staturg['values'][0]
    assert value['logical_device'] == 'E1_RELLD0'
    assert value['logical_node'] == 'DRPRDRE1'
    assert value['fc'] == 'ST'
    assert value['names'] == ['RcdMade']


def test_4(validator):
    with importlib.resources.open_text(__package__, 'test4.scd') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 2

    assert 'E1_7SA' in device_jsons
    device_json = device_jsons['E1_7SA']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 37
    assert len(device_json['commands']) == 100
    assert len(device_json['data']) == 3632
    assert len(device_json['value_types']) == 4109

    assert device_json['dynamic']['max_datasets'] == 30
    assert device_json['dynamic']['max_dataset_attributes'] == 60
    assert device_json['dynamic']['rcb_editable']['report_id']
    assert device_json['dynamic']['rcb_editable']['dataset']
    assert device_json['dynamic']['rcb_editable']['optional_fields']
    assert device_json['dynamic']['rcb_editable']['buffer_time']
    assert device_json['dynamic']['rcb_editable']['trigger_options']
    assert device_json['dynamic']['rcb_editable']['integrity_period']

    # indexed rcb with max=6
    rcbs = [rcb_conf for rcb_conf in device_json['rcbs']
            if rcb_conf['report_id'] == "E1_7SA/Application/LLN0$BR$Report1"]
    assert len(rcbs) == 6
    assert [i['ref']['name'] for i in rcbs] == [
        f'Report10{i}' for i in range(1, 7)]

    # indexed rcb with max=1
    rcbs = [rcb_conf for rcb_conf in device_json['rcbs']
            if rcb_conf['report_id'] == "E1_7SA/Application/LLN0$RP$Report2"]
    assert len(rcbs) == 1
    assert rcbs[0]['ref']['name'] == 'Report201'

    # subVal data value with subQ quality
    data_conf = util.first(
        device_json['data'],
        lambda i: i["value"] == {
                    "logical_device": "E1_7SALn1_ProcessMonitor",
                    "logical_node": "PROM_RSSR1",
                    "fc": "SV",
                    "names": ["DisCntrOpn",
                              "subVal"]})
    assert data_conf
    assert data_conf['quality'] == {
        **data_conf['value'],
        'names': [*data_conf['value']['names'][:-1], 'subQ']}

    assert 'E1_REL' in device_jsons
    device_json = device_jsons['E1_REL']
    assert len(device_json['datasets']) == 5
    assert len(device_json['rcbs']) == 32
    assert len(device_json['commands']) == 92
    assert len(device_json['data']) == 1342
    assert len(device_json['value_types']) == 1350

    # command, data and control model on the same address
    value_types = [i for i in device_json['value_types']
                   if (i['logical_device'] == 'E1_RELSES_1' and
                       i['logical_node'] == 'LLN0' and
                       i['name'] == 'Mod')]
    assert len(value_types) == 4
    co_value_type = util.first(value_types, lambda i: i['fc'] == 'CO')
    assert len(co_value_type['type']['elements']) == 1
    el_oper = co_value_type['type']['elements'][0]
    assert el_oper == {'name': 'Oper',
                       'type': {'elements': [{'name': 'ctlVal',
                                              'type': 'INTEGER'},
                                             {'name': 'origin',
                                              'type': {'elements': [
                                                {'name': 'orCat',
                                                 'type': 'INTEGER'},
                                                {'name': 'orIdent',
                                                 'type': 'OCTET_STRING'}],
                                               'type': 'STRUCT'}},
                                             {'name': 'ctlNum',
                                              'type': 'UNSIGNED'},
                                             {'name': 'T',
                                              'type': 'TIMESTAMP'},
                                             {'name': 'Test',
                                              'type': 'BOOLEAN'},
                                             {'name': 'Check',
                                              'type': 'INTEGER'}],
                                'type': 'STRUCT'}}

    # data values in multiple datasets
    data_conf = util.first(
        device_json['data'],
        lambda i: i['value'] == {'logical_device': 'E1_RELLD0',
                                 'logical_node': 'ECPSCH1',
                                 'fc': 'ST',
                                 'names': ['ProTx', 'stVal']})
    assert data_conf
    assert len(data_conf['datasets']) == 2
    assert data_conf['datasets'] == [
        {'ref': {'logical_device': 'E1_RELLD0',
                 'logical_node': 'LLN0',
                 'name': 'StatUrg'},
         'quality': True,
         'selected': False,
         'timestamp': True},
        {'ref': {'logical_device': 'E1_RELLD0',
                 'logical_node': 'LLN0',
                 'name': 'StatUrg_A'},
         'quality': True,
         'selected': False,
         'timestamp': True}]


def test_5(validator):
    with importlib.resources.open_text(__package__, 'test5.scd') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 1

    assert 'SIP' in device_jsons
    device_json = device_jsons['SIP']
    assert len(device_json['datasets']) == 2
    assert len(device_json['rcbs']) == 62
    assert len(device_json['commands']) == 48
    assert len(device_json['data']) == 1990
    writable_values = [i for i in device_json['data'] if i['writable']]
    assert len(writable_values) == 77
    assert len(device_json['value_types']) == 1363


def test_6(validator):
    with importlib.resources.open_text(__package__, 'test6.cid') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 1

    assert 'X1_SACO' in device_jsons
    device_json = device_jsons['X1_SACO']

    assert 'max_datasets' not in device_json['dynamic']
    assert 'max_dataset_attributes' not in device_json['dynamic']

    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 15
    assert len(device_json['commands']) == 13
    assert len(device_json['data']) == 409
    writable_values = [i for i in device_json['data'] if i['writable']]
    assert len(writable_values) == 0
    assert len(device_json['value_types']) == 655


def test_7(validator):
    with importlib.resources.open_text(__package__, 'test7.icd') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 1

    device_json = device_jsons['E3_TAPCON']

    assert device_json['dynamic']['max_datasets'] == 35
    assert device_json['dynamic']['max_dataset_attributes'] == 200
    assert device_json['dynamic']['rcb_editable']['report_id']
    assert device_json['dynamic']['rcb_editable']['dataset']
    assert device_json['dynamic']['rcb_editable']['optional_fields']
    assert device_json['dynamic']['rcb_editable']['buffer_time']
    assert device_json['dynamic']['rcb_editable']['trigger_options']
    assert device_json['dynamic']['rcb_editable']['integrity_period']

    # assert value types with different fc
    value_types = [i for i in device_json['value_types']
                   if i['logical_device'] == 'E3_TAPCONE3_TAP' and
                   i['logical_node'] == 'LLN0' and
                   i['name'] == 'Mod']
    assert len(value_types) == 3
    assert util.first(value_types, lambda i: i['fc'] == 'ST')
    assert util.first(value_types, lambda i: i['fc'] == 'CF')
    assert util.first(value_types, lambda i: i['fc'] == 'DC')

    # assert value type valWTr of type STEP_POSITION
    value_type_tap_changer = util.first(
        device_json['value_types'],
        lambda i: i['logical_device'] == 'E3_TAPCONE3_TAP' and
        i['logical_node'] == 'ATCC1' and
        i['fc'] == 'ST' and
        i['name'] == 'TapChg')
    assert value_type_tap_changer
    assert value_type_tap_changer['type']['type'] == 'STRUCT'
    assert value_type_tap_changer['type']['elements'][0] == {
        "name": "valWTr",
        "type": "STEP_POSITION"}
    value_type_tap_changer = util.first(
        device_json['value_types'],
        lambda i: i['logical_device'] == 'E3_TAPCONE3_TAP' and
        i['logical_node'] == 'ATCC1' and
        i['fc'] == 'CF' and
        i['name'] == 'TapChg')
    assert value_type_tap_changer

    # assert corresponding data valWTr of type STEP_POSITION
    data_conf = util.first(
        device_json['data'],
        lambda i: i["value"] == {
            "logical_device": "E3_TAPCONE3_TAP",
            "logical_node": "ATCC1",
            "fc": "ST",
            "names": ["TapChg",
                      "valWTr"]})
    assert data_conf
    assert data_conf['value_type'] == 'STEP_POSITION'
    assert data_conf['datasets']
    assert data_conf['quality']
    assert data_conf['timestamp']

    # assert sub-data for STEP_POSITION
    data_conf = util.first(
        device_json['data'],
        lambda i: i["value"] == {
            "logical_device": "E3_TAPCONE3_TAP",
            "logical_node": "ATCC1",
            "fc": "ST",
            "names": ["TapChg",
                      "valWTr",
                      "posVal"]})
    assert data_conf
    assert data_conf['value_type'] == 'INTEGER'


def test_8(validator):
    # File contains structs with count=0, which should not be defined as
    # arrays. This test verifies that no array elements are defined.
    with importlib.resources.open_text(__package__, 'test8.icd') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_jsons = {device_json['ied_name']: device_json
                    for device_json in res['devices']}

    assert len(device_jsons) == 1

    device_json = device_jsons['AA1RTUA02']

    assert len(device_json['value_types']) == 3726

    def _get_all_array_types(vt):
        if not isinstance(vt, dict):
            return

        if vt['type'] == 'ARRAY':
            yield vt

        if vt['type'] == 'STRUCT':
            for i in vt['elements']:
                yield from _get_all_array_types(i['type'])

    for i in device_json['value_types']:
        assert not list(_get_all_array_types(i['type']))


def test_9(validator):
    # File doesn't have rcbs defined with ReportControl but only with Private
    with importlib.resources.open_text(__package__, 'test9.cid') as f:
        res = readout(f)

    validator.validate(json_schema_id, res)

    device_json = res['devices'][0]

    assert len(device_json['rcbs']) == 134
