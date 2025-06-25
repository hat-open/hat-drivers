import importlib.resources

import pytest

from hat import json
from hat import util

from hat.drivers.iec61850.manager.file_readout import readout


json_schema_id = "hat-drivers://iec61850/device.yaml"


@pytest.fixture(scope='session')
def validator(pytestconfig):
    json_schema_repo = json.create_schema_repository(
        pytestconfig.rootpath / 'schemas_json')
    return json.DefaultSchemaValidator(json_schema_repo)


def test_1(validator):
    with importlib.resources.open_text(__package__, 'test1.cid') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'Demo' in res
    device_json = res['Demo']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 6
    assert len(device_json['commands']) == 4
    assert len(device_json['data']) == 84
    writable_values = [j for i in device_json['data'] for j in i['values']
                       if j['writable']]
    assert len(writable_values) == 2

    ld = "DemoMeasurement"
    ln = "I3pMMXU1"
    do_name = "A"
    data = util.first(device_json['data'],
                      lambda i: i['ref'] == {
                           "logical_device": ld,
                           "logical_node": ln,
                           "names": [do_name]})
    assert data['cdc'] == 'WYE'

    for subdo_name in ["phsA", "phsB", "phsC"]:
        data = util.first(device_json['data'],
                          lambda i: i['ref'] == {
                               "logical_device": ld,
                               "logical_node": ln,
                               "names": [do_name, subdo_name]})
        assert data['cdc'] == 'CMV'


def test_2(validator):
    with importlib.resources.open_text(__package__, 'test2.cid') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'J01' in res
    device_json = res['J01']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 15
    assert len(device_json['commands']) == 2
    assert len(device_json['data']) == 256
    writable_values = [j for i in device_json['data'] for j in i['values']
                       if j['writable']]
    assert len(writable_values) == 0

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

    assert len(res) == 3
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'E1_7SA' in res
    assert res['E1_7SA']['connection']['host'] == '192.168.29.162'
    assert res['E1_7SA']['connection']['tsel'] == 1
    assert res['E1_7SA']['connection']['ssel'] == 1
    assert res['E1_7SA']['connection']['psel'] == 1
    assert res['E1_7SA']['connection']['ap_title'] == [1, 3, 9999, 23]
    assert res['E1_7SA']['connection']['ae_qualifier'] == 23

    assert 'E1_REL' in res
    assert res['E1_REL']['connection']['host'] == '192.168.29.163'
    assert res['E1_REL']['connection']['tsel'] == 1
    assert res['E1_REL']['connection']['ssel'] == 1
    assert res['E1_REL']['connection']['psel'] == 1
    assert res['E1_REL']['connection']['ap_title'] == [1, 3, 9999, 23]
    assert res['E1_REL']['connection']['ae_qualifier'] == 23

    assert 'LKKU' in res
    assert res['LKKU']['connection']['host'] == '10.228.34.150'
    assert res['LKKU']['connection']['tsel'] == 1
    assert res['LKKU']['connection']['ssel'] == 1
    assert res['LKKU']['connection']['psel'] == 1
    assert res['LKKU']['connection']['ap_title'] == [1, 3, 9999, 23]
    assert res['LKKU']['connection']['ae_qualifier'] == 23

    # verify a E1_REL dataset values
    assert len(res['E1_REL']['datasets']) == 5
    ds_staturg = util.first(res['E1_REL']['datasets'],
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

    assert len(res) == 2
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'E1_7SA' in res
    device_json = res['E1_7SA']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 42
    assert len(device_json['commands']) == 99
    assert len(device_json['data']) == 2050

    # indexed rcbs
    rcbs = [rcb_conf for rcb_conf in device_json['rcbs']
            if rcb_conf['report_id'] == "E1_7SA/Application/LLN0$BR$Report1"]
    assert len(rcbs) == 6
    assert [i['ref']['name'] for i in rcbs] == [
        f'Report10{i}' for i in range(1, 7)]

    assert 'E1_REL' in res
    device_json = res['E1_REL']
    assert len(device_json['datasets']) == 5
    assert len(device_json['rcbs']) == 32
    assert len(device_json['commands']) == 92
    assert len(device_json['data']) == 741


def test_5(validator):
    with importlib.resources.open_text(__package__, 'test5.scd') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'SIP' in res
    device_json = res['SIP']
    assert len(device_json['datasets']) == 2
    assert len(device_json['rcbs']) == 62
    assert len(device_json['commands']) == 48
    assert len(device_json['data']) == 935
    writable_values = [j for i in device_json['data'] for j in i['values']
                       if j['writable']]
    assert len(writable_values) == 77


def test_6(validator):
    with importlib.resources.open_text(__package__, 'test6.cid') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'X1_SACO' in res
    device_json = res['X1_SACO']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 15
    assert len(device_json['commands']) == 13
    assert len(device_json['data']) == 314
    writable_values = [j for i in device_json['data'] for j in i['values']
                       if j['writable']]
    assert len(writable_values) == 0
