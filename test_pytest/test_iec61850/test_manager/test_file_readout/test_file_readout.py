from pathlib import Path

from hat import json
from hat import util

from hat.drivers.iec61850.manager.file_readout import readout


package_path = Path(__file__).parent
device_schema_path = (Path(__file__).parents[4] /
                      'schemas_json/iec61850/device.yaml')
json_schema_repo = json.create_schema_repository(device_schema_path)
validator = json.DefaultSchemaValidator(json_schema_repo)
json_schema_id = "hat-drivers://iec61850/device.yaml"


def test_1():
    res = readout(package_path / 'test1.cid')

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


def test_2():
    res = readout(package_path / 'test2.cid')

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)

    assert 'J01' in res
    device_json = res['J01']
    assert len(device_json['datasets']) == 3
    assert len(device_json['rcbs']) == 15


def test_3():
    res = readout(package_path / 'test3.scd')

    assert len(res) == 3
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_4():
    res = readout(package_path / 'test4.scd')

    assert len(res) == 2
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_5():
    res = readout(package_path / 'test5.scd')

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_6():
    res = readout(package_path / 'test6.cid')

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)


def test_7():
    res = readout(package_path / 'test7.cid')

    assert len(res) == 1
    for device_name, device_json in res.items():
        validator.validate(json_schema_id, device_json)
