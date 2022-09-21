import pytest

from hat.drivers.pnetgateway import common
from hat.drivers.pnetgateway import encoder


@pytest.mark.parametrize("data", [
    common.Data(key='key',
                value=123,
                quality=common.Quality.GOOD,
                timestamp=123456,
                type=common.DataType.NUMERIC,
                source=common.Source.REMOTE_SRC)
])
def test_encode_decode_data(data):
    encoded_data = encoder.data_to_json(data)
    decoded_data = encoder.data_from_json(encoded_data)
    assert data == decoded_data


@pytest.mark.parametrize("change", [
    common.Change(key='key',
                  value=123,
                  quality=common.Quality.GOOD,
                  timestamp=123456,
                  source=common.Source.REMOTE_SRC),
    common.Change(key='key',
                  value=None,
                  quality=None,
                  timestamp=None,
                  source=None)
])
def test_encode_decode_change(change):
    encoded_change = encoder.change_to_json(change)
    decoded_change = encoder.change_from_json(encoded_change)
    assert change == decoded_change


@pytest.mark.parametrize("command", [
    common.Command(key='key',
                   value=123)
])
def test_encode_decode_command(command):
    encoded_command = encoder.command_to_json(command)
    decoded_command = encoder.command_from_json(encoded_command)
    assert command == decoded_command
