import pytest

from hat.drivers.snmp import key


@pytest.mark.parametrize('key_type, password, engine_id_hex, exp_key_hex', [
    # example from rfc3414 A.3.1
    (key.KeyType.MD5,
     'maplesyrup',
     '00 00 00 00 00 00 00 00 00 00 00 02',
     '52 6f 5e ed 9f cc e2 6f 89 64 c2 93 07 87 d8 2b'),
    # example from rfc3414 A.5.1
    (key.KeyType.MD5,
     'newsyrup',
     '00 00 00 00 00 00 00 00 00 00 00 02',
     '87 02 1d 7b d9 d1 01 ba 05 ea 6e 3b f9 d9 bd 4a'),
    # example from rfc3414 A.3.2
    (key.KeyType.SHA,
     'maplesyrup',
     '00 00 00 00 00 00 00 00 00 00 00 02',
     '66 95 fe bc 92 88 e3 62 82 23 5f c7 15 1f 12 84 97 b3 8f 3f'),
    # example from rfc3414 A.5.2
    (key.KeyType.SHA,
     'newsyrup',
     '00 00 00 00 00 00 00 00 00 00 00 02',
     '78 e2 dc ce 79 d5 94 03 b5 8c 1b ba a5 bf f4 63 91 f1 cd 25'),
    ])
def test_create_key(key_type, password, engine_id_hex, exp_key_hex):
    result_key = key.create_key(
        key_type=key_type,
        password=password,
        engine_id=bytes.fromhex(engine_id_hex))
    assert result_key.type == key_type
    assert result_key.data == bytes.fromhex(exp_key_hex)
