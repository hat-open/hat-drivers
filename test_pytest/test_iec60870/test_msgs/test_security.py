import pytest

from hat.drivers.iec60870.msgs import iec104
from hat.drivers.iec60870.msgs.security import common
from hat.drivers.iec60870.msgs.security import encoder


def gen_causes(amount):
    causes = (common.CauseType.AUTHENTICATION,
              common.CauseType.SESSION_KEY_MAINTENANCE,
              common.CauseType.UPDATE_KEY_MAINTENANCE)
    is_negatives = (False, True, False, True)
    is_tests = (False, False, True, True)
    orig_addrs = (0, 255, 123, 13, 1)

    for _ in range(amount):
        for counter, cause_type in enumerate(causes):
            for is_neg, is_test, orig_addr in zip(is_negatives,
                                                  is_tests,
                                                  orig_addrs):
                yield common.Cause(type=cause_type,
                                   is_negative_confirm=is_neg,
                                   is_test=is_test,
                                   originator_address=orig_addr)


def gen_asdu_address(amount):
    addrs = (0, 255, 65535)
    for i in range(amount):
        yield addrs[i % len(addrs)]


def gen_io_address(amount):
    addrs = (0, 255, 16777215)
    for i in range(amount):
        yield addrs[i % len(addrs)]


def gen_sequence_numbers(amount):
    numbers = [0, 255, 4294967295]
    for i in range(amount):
        yield numbers[i % len(numbers)]


def gen_user_numbers(amount):
    usr_numbers = [0, 255, 65535]
    for i in range(amount):
        yield usr_numbers[i % (len(usr_numbers))]


def gen_mac_alg(amount):
    macs = [*common.MacAlgorithm, 8, 10]
    for i in range(amount):
        yield macs[i % len(macs)]


def gen_reason(amount):
    reasons = [0, 1, 255]
    for i in range(amount):
        yield reasons[i % len(reasons)]


def gen_role(amount):
    role = [*common.UserRole, 255, 65535]
    for i in range(amount):
        yield role[i % (len(role))]


def gen_role_expiry(amount):
    role = [0, 255, 65535]
    for i in range(amount):
        yield role[i % (len(role))]


def gen_bytes(amount):
    data = [b'1', b'22', b'6' * 65535]
    for i in range(amount):
        yield data[i % len(data)]


def gen_times(amount):
    samples = {'milliseconds': (0, 59999, 1234),
               'invalid': [True, False, True],
               'minutes': (0, 59, 30),
               'summer_time': [True, False, True],
               'hours': (0, 23, 12),
               'day_of_week': (1, 7, 3),
               'day_of_month': (1, 31, 13),
               'months': (1, 12, 6),
               'years': (0, 99, 50)}
    cnt = 0
    while True:
        for values in zip(*samples.values()):
            time_dict = dict(zip(samples.keys(), values))
            yield common.Time(**time_dict,
                              size=common.TimeSize.SEVEN)
            cnt += 1
            if cnt == amount:
                return


def gen_asdu_bytes(amount):
    iec104_encoder = iec104.encoder.Encoder()

    cause = iec104.common.Cause(
        type=iec104.common.CauseType.ACTIVATION,
        is_negative_confirm=False,
        is_test=False,
        originator_address=iec104.common.OriginatorAddress(2))

    io_element = iec104.common.IoElement_C_SC_NA(
        value=iec104.common.SingleValue.ON,
        select=False,
        qualifier=0)

    input_asdu = iec104.common.ASDU(
        type=iec104.common.AsduType.C_SC_NA,
        cause=cause,
        address=3,
        ios=[iec104.common.IO(address=5,
                              elements=[io_element],
                              time=None)])

    encoded_asdu = iec104_encoder.encode_asdu(input_asdu)
    return [encoded_asdu] * amount


def gen_key_wrap_algs(amount):
    kwas = [*common.KeyWrapAlgorithm, 8, 10]
    for i in range(amount):
        yield kwas[i % len(kwas)]


def gen_key_stats(amount):
    ksts = [*common.KeyStatus, 8, 10]
    for i in range(amount):
        yield ksts[i % len(ksts)]


def gen_operations(amount):
    operations = [*common.Operation, 8, 10]
    for i in range(amount):
        yield operations[i % len(operations)]


def gen_association_ids(amount):
    a_ids = [0, 255, 65535]
    for i in range(amount):
        yield a_ids[i % len(a_ids)]


def gen_err_codes(amount):
    err_codes = [*common.ErrorCode, 20, 30]
    for i in range(amount):
        yield err_codes[i % len(err_codes)]


def gen_key_change_methods(amount):
    kcms = [*common.KeyChangeMethod, 50, 51]
    for i in range(amount):
        yield kcms[i % len(kcms)]


def gen_binary_counter_values(amount):
    for i in range(amount):
        yield common.BinaryCounterValue(i)


def assert_encode_decode(asdu_type, cause, asdu_address, io_element,
                         io_address=None, time=None):
    secure_encoder = encoder.Encoder(iec104.encoder.Encoder())

    input_asdu = common.ASDU(type=asdu_type,
                             cause=cause,
                             address=asdu_address,
                             ios=[common.IO(address=io_address,
                                            element=io_element,
                                            time=time)])

    asdu_encoded = secure_encoder.encode_asdu(input_asdu)
    assert asdu_encoded

    for i, encoded in enumerate(asdu_encoded):
        asdu_decoded, _ = secure_encoder.decode_asdu(encoded)
        if i != len(asdu_encoded) - 1:
            assert asdu_decoded is None
        else:
            assert asdu_decoded is not None

    assert input_asdu == asdu_decoded


@pytest.mark.parametrize(
    'association_id, value, cause, asdu_address, io_address, time',
    zip(gen_association_ids(3),
        gen_binary_counter_values(3),
        gen_causes(3),
        gen_asdu_address(3),
        gen_io_address(3),
        gen_times(3)))
def test_s_it_tc(association_id, value, cause, asdu_address, io_address, time):
    asdu_type = common.AsduType.S_IT_TC

    io_element = common.IoElement_S_IT_TC(association_id=association_id,
                                          value=value)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element,
                         io_address=io_address,
                         time=time)


@pytest.mark.parametrize(
    'seq_number, usr_number, mac_alg, reason, data, cause, asdu_address',
    zip(gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_mac_alg(3),
        gen_reason(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_ch_na(seq_number, usr_number, mac_alg, reason, data, cause,
                 asdu_address):
    asdu_type = common.AsduType.S_CH_NA

    io_element = common.IoElement_S_CH_NA(sequence=seq_number,
                                          user=usr_number,
                                          mac_algorithm=mac_alg,
                                          reason=reason,
                                          data=data)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'seq_number, usr_number, mac_value, cause, asdu_address',
    zip(gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_rp_na(seq_number, usr_number, mac_value, cause, asdu_address):
    asdu_type = common.AsduType.S_RP_NA

    io_element = common.IoElement_S_RP_NA(sequence=seq_number,
                                          user=usr_number,
                                          mac=mac_value)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'asdu_bytes, seq_number, usr_number, mac_value, cause, asdu_address',
    zip(gen_asdu_bytes(3),
        gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_ar_na(asdu_bytes, seq_number, usr_number, mac_value, cause,
                 asdu_address):
    asdu_type = common.AsduType.S_AR_NA

    io_element = common.IoElement_S_AR_NA(asdu=asdu_bytes,
                                          sequence=usr_number,
                                          user=usr_number,
                                          mac=mac_value)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'usr_number, cause, asdu_address',
    zip(gen_user_numbers(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_kr_na(usr_number, cause, asdu_address):
    asdu_type = common.AsduType.S_KR_NA

    io_element = common.IoElement_S_KR_NA(user=usr_number)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'seq_number, usr_number, key_wrap_alg, key_status, mac_alg, data, '
    'mac_value, cause, asdu_address',
    zip(gen_sequence_numbers(8),
        gen_user_numbers(8),
        gen_key_wrap_algs(8),
        gen_key_stats(8),
        gen_mac_alg(8),
        gen_bytes(8),
        gen_bytes(8),
        gen_causes(8),
        gen_asdu_address(8)))
def test_s_ks_na(seq_number, usr_number, key_wrap_alg, key_status, mac_alg,
                 data, mac_value, cause, asdu_address):
    asdu_type = common.AsduType.S_KS_NA

    io_element = common.IoElement_S_KS_NA(sequence=seq_number,
                                          user=usr_number,
                                          key_wrap_algorithm=key_wrap_alg,
                                          key_status=key_status,
                                          mac_algorithm=mac_alg,
                                          data=data,
                                          mac=mac_value)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'seq_number, usr_number, wrapped_key, cause, asdu_address',
    zip(gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_kc_na(seq_number, usr_number, wrapped_key, cause, asdu_address):
    asdu_type = common.AsduType.S_KC_NA

    io_element = common.IoElement_S_KC_NA(sequence=seq_number,
                                          user=usr_number,
                                          wrapped_key=wrapped_key)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'chall_seq, key_ch_seq, usr_number, association_id, err_code, io_time, '
    'text, cause, asdu_address',
    zip(gen_sequence_numbers(10),
        gen_sequence_numbers(10),
        gen_user_numbers(10),
        gen_association_ids(10),
        gen_err_codes(10),
        gen_times(10),
        gen_bytes(10),
        gen_causes(10),
        gen_asdu_address(10)))
def test_s_er_na(chall_seq, key_ch_seq, usr_number, association_id, err_code,
                 io_time, text, cause, asdu_address):
    asdu_type = common.AsduType.S_ER_NA

    io_element = common.IoElement_S_ER_NA(challenge_sequence=chall_seq,
                                          key_change_sequence=key_ch_seq,
                                          user=usr_number,
                                          association_id=association_id,
                                          code=err_code,
                                          time=io_time,
                                          text=text)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'key_ch_method, data, cause, asdu_address',
    zip(gen_key_change_methods(10),
        gen_bytes(10),
        gen_causes(10),
        gen_asdu_address(10)))
def test_s_uc_na_x(key_ch_method, data, cause, asdu_address):
    asdu_type = common.AsduType.S_UC_NA_X

    io_element = common.IoElement_S_UC_NA_X(key_change_method=key_ch_method,
                                            data=data)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'key_ch_method, operation, sequence, role, role_expiry, name, public_key, '
    'certification, cause, asdu_address',
    zip(gen_key_change_methods(3),
        gen_operations(3),
        gen_sequence_numbers(3),
        gen_role(3),
        gen_role_expiry(3),
        gen_bytes(3),
        gen_bytes(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_us_na(key_ch_method, operation, sequence, role, role_expiry, name,
                 public_key, certification, cause, asdu_address):
    asdu_type = common.AsduType.S_US_NA

    io_element = common.IoElement_S_US_NA(key_change_method=key_ch_method,
                                          operation=operation,
                                          sequence=sequence,
                                          role=role,
                                          role_expiry=role_expiry,
                                          name=name,
                                          public_key=public_key,
                                          certification=certification)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'key_ch_method, name, data, cause, asdu_address',
    zip(gen_key_change_methods(3),
        gen_bytes(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_uq_na(key_ch_method, name, data, cause, asdu_address):
    asdu_type = common.AsduType.S_UQ_NA

    io_element = common.IoElement_S_UQ_NA(key_change_method=key_ch_method,
                                          name=name,
                                          data=data)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'sequence_number, usr_number, data, cause, asdu_address',
    zip(gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_ur_na(sequence_number, usr_number, data, cause, asdu_address):
    asdu_type = common.AsduType.S_UR_NA

    io_element = common.IoElement_S_UR_NA(sequence=sequence_number,
                                          user=usr_number,
                                          data=data)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'sequence_number, usr_number, update_key, mac_bytes, cause, asdu_address',
    zip(gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_bytes(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_uk_na(sequence_number, usr_number, update_key, mac_bytes,
                 cause, asdu_address):
    asdu_type = common.AsduType.S_UK_NA

    io_element = common.IoElement_S_UK_NA(sequence=sequence_number,
                                          user=usr_number,
                                          encrypted_update_key=update_key,
                                          mac=mac_bytes)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'sequence_number, usr_number, update_key, signature, cause, asdu_address',
    zip(gen_sequence_numbers(3),
        gen_user_numbers(3),
        gen_bytes(3),
        gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_ua_na(sequence_number, usr_number, update_key, signature,
                 cause, asdu_address):
    asdu_type = common.AsduType.S_UA_NA

    io_element = common.IoElement_S_UA_NA(sequence=sequence_number,
                                          user=usr_number,
                                          encrypted_update_key=update_key,
                                          signature=signature)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)


@pytest.mark.parametrize(
    'mac_bytes, cause, asdu_address',
    zip(gen_bytes(3),
        gen_causes(3),
        gen_asdu_address(3)))
def test_s_uc_na(mac_bytes, cause, asdu_address):
    asdu_type = common.AsduType.S_UC_NA

    io_element = common.IoElement_S_UC_NA(mac=mac_bytes)

    assert_encode_decode(asdu_type, cause, asdu_address, io_element)
