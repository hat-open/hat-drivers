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


def test_3(validator):
    with importlib.resources.open_text(__package__, 'test3.scd') as f:
        res = readout(f)

    assert len(res) == 3
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_4(validator):
    with importlib.resources.open_text(__package__, 'test4.scd') as f:
        res = readout(f)

    assert len(res) == 2
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_5(validator):
    with importlib.resources.open_text(__package__, 'test5.scd') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_6(validator):
    with importlib.resources.open_text(__package__, 'test6.cid') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_7(validator):
    with importlib.resources.open_text(__package__, 'test7.cid') as f:
        res = readout(f)

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)
