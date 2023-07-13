import collections
import contextlib
import enum
import itertools
import logging
import typing

from hat import util

from hat.drivers.iec60870.encodings import iec101
from hat.drivers.iec60870.encodings import iec104
from hat.drivers.iec60870.encodings.encoder import encode_time, decode_time
from hat.drivers.iec60870.encodings.security import common


mlog: logging.Logger = logging.getLogger(__name__)


ASDU: typing.TypeAlias = common.ASDU | iec101.ASDU | iec104.ASDU


class Encoder:

    def __init__(self, encoder: iec101.Encoder | iec104.Encoder):
        self._encoder = encoder
        self._buffer = None

    def decode_asdu(self,
                    asdu_bytes: util.Bytes
                    ) -> tuple[ASDU | None, util.Bytes]:
        asdu_type = asdu_bytes[0]
        with contextlib.suppress(ValueError):
            asdu_type = common.AsduType(asdu_type)

        if isinstance(asdu_type, common.AsduType):
            return self._decode_asdu(asdu_bytes, asdu_type)

        if self._buffer:
            mlog.warning('unsegmented asdu - discarding buffer')
            self._buffer = None

        return self._encoder.decode_asdu(asdu_bytes)

    def encode_asdu(self, asdu: ASDU) -> list[util.Bytes]:
        if isinstance(asdu, common.ASDU):
            return list(self._encode_asdu(asdu))

        return [self._encoder.encode_asdu(asdu)]

    def _decode_asdu(self, asdu_bytes, asdu_type):
        io_count, rest = _decode_io_count(asdu_bytes[1:], asdu_type)
        cause, rest = _decode_cause(rest, self._encoder.cause_size)
        asdu_address, rest = _decode_int(rest,
                                         self._encoder.asdu_address_size.value)

        ios = collections.deque()
        for _ in range(io_count):
            if asdu_type in _unsegmented_asdu_types:
                io, rest = self._decode_unsegmented_io(rest, asdu_type)

            else:
                io, rest = self._decode_segmented_io(rest, asdu_type, cause,
                                                     asdu_address)

            if io:
                ios.append(io)

        if asdu_type != common.AsduType.S_IT_TC and not ios:
            return None, rest

        asdu = common.ASDU(type=asdu_type,
                           cause=cause,
                           address=asdu_address,
                           ios=list(ios))
        return asdu, rest

    def _encode_asdu(self, asdu):
        identifier = collections.deque()
        identifier.append(asdu.type.value)
        identifier.append(len(asdu.ios))
        identifier.extend(_encode_cause(asdu.cause, self._encoder.cause_size))
        identifier.extend(_encode_int(asdu.address,
                                      self._encoder.asdu_address_size.value))

        parts = collections.deque()
        for io in asdu.ios:
            if io.address is not None:
                parts.append(
                    _encode_int(io.address,
                                self._encoder.io_address_size.value))

            parts.append(_encode_io_element(io.element, self._encoder))

            if io.time is not None:
                parts.append(encode_time(io.time, common.TimeSize.SEVEN))

        rest = itertools.chain.from_iterable(parts)

        if asdu.type in _unsegmented_asdu_types:
            yield bytes(itertools.chain(identifier, rest))

        else:
            first = True
            segment = 0
            rest = memoryview(bytes(rest))
            max_size = self._encoder.max_asdu_size - len(identifier) - 1

            while rest:
                data, rest = rest[:max_size], rest[max_size:]
                last = not rest

                yield bytes(itertools.chain(identifier,
                                            [(0x40 if first else 0) |
                                             (0x80 if last else 0) |
                                             segment],
                                            data))

                first = False
                segment = (segment + 1) % 64

    def _decode_unsegmented_io(self, io_bytes, asdu_type):
        if self._buffer:
            mlog.warning('unsegmented asdu - discarding buffer')
            self._buffer = None

        if asdu_type == common.AsduType.S_IT_TC:
            io_address, rest = _decode_int(
                io_bytes, self._encoder.io_address_size.value)
            element, rest = _decode_io_element(rest, self._encoder,
                                               asdu_type)
            time, rest = (decode_time(rest, common.TimeSize.SEVEN),
                          rest[7:])

        else:
            io_address = None
            element, rest = _decode_io_element(io_bytes, self._encoder,
                                               asdu_type)
            time = None

        io = common.IO(address=io_address,
                       element=element,
                       time=time)
        return io, rest

    def _decode_segmented_io(self, io_bytes, asdu_type, cause, asdu_address):
        first = bool(io_bytes[0] & 0x40)
        last = bool(io_bytes[0] & 0x80)
        segment = io_bytes[0] & 0x3f
        rest = io_bytes[1:]

        if first:
            if self._buffer:
                mlog.warning('new first segment - discarding buffer')

            self._buffer = _Buffer(asdu_type=asdu_type,
                                   cause=cause,
                                   asdu_address=asdu_address,
                                   prev_first=first,
                                   prev_segment=segment,
                                   prev_io_bytes=rest,
                                   all_io_bytes=rest)

        else:
            if not self._buffer:
                mlog.warning('empty buffer - discarding segment')
                return None, b''

            elif self._buffer.asdu_type != asdu_type:
                mlog.warning('asdu type not matching - '
                             'discarding segment and buffer')
                self._buffer = None
                return None, b''

            elif self._buffer.cause != cause:
                mlog.warning('cause not matching - '
                             'discarding segment and buffer')
                self._buffer = None
                return None, b''

            elif self._buffer.asdu_address != asdu_address:
                mlog.warning('asdu address not matching - '
                             'discarding segment and buffer')
                self._buffer = None
                return None, b''

            elif ((self._buffer.prev_segment + 1) % 64) != segment:
                if (self._buffer.prev_first == first and
                        self._buffer.prev_segment == segment and
                        self._buffer.prev_io_bytes == rest):
                    mlog.warning('duplicated segment - discarding segment')

                else:
                    mlog.warning('segment number not matching - '
                                 'discarding segment and buffer')
                    self._buffer = None

                return None, b''

            self._buffer = self._buffer._replace(
                prev_first=first,
                prev_segment=segment,
                prev_io_bytes=rest,
                all_io_bytes=itertools.chain(self._buffer.all_io_bytes, rest))

        if not last:
            return None, b''

        all_io_bytes = (self._buffer.all_io_bytes
                        if isinstance(self._buffer.all_io_bytes, memoryview)
                        else memoryview(bytes(self._buffer.all_io_bytes)))
        self._buffer = None

        element, rest = _decode_io_element(all_io_bytes, self._encoder,
                                           asdu_type)
        io = common.IO(address=None,
                       element=element,
                       time=None)
        return io, rest


_unsegmented_asdu_types = {common.AsduType.S_IT_TC,
                           common.AsduType.S_KR_NA}


class _Buffer(typing.NamedTuple):
    asdu_type: common.AsduType
    cause: common.Cause
    asdu_address: common.AsduAddress
    prev_first: bool
    prev_segment: int
    prev_io_bytes: util.Bytes
    all_io_bytes: typing.Iterable[int]


def _decode_io_count(qualifier_bytes, asdu_type):
    qualifier, rest = qualifier_bytes[0], qualifier_bytes[1:]

    if qualifier & 0x80:
        raise ValueError('invalid qualifier')

    if asdu_type != common.AsduType.S_IT_TC and qualifier != 1:
        raise ValueError('invalid io count')

    return qualifier, rest


def _decode_cause(cause_bytes, cause_size):
    cause, rest = _decode_int(cause_bytes, cause_size.value)
    cause = iec101.decode_cause(cause=cause,
                                cause_size=cause_size)

    cause_type = (cause.type.value if isinstance(cause.type, enum.Enum)
                  else cause.type)
    with contextlib.suppress(ValueError):
        cause_type = common.CauseType(cause_type)

    cause = common.Cause(type=cause_type,
                         is_negative_confirm=cause.is_negative_confirm,
                         is_test=cause.is_test,
                         originator_address=cause.originator_address)
    return cause, rest


def _encode_cause(cause, cause_size):
    cause_type = (cause.type.value if isinstance(cause.type, enum.Enum)
                  else cause.type)
    cause = iec101.Cause(type=cause_type,
                         is_negative_confirm=cause.is_negative_confirm,
                         is_test=cause.is_test,
                         originator_address=cause.originator_address)

    cause = iec101.encode_cause(cause, cause_size)
    return _encode_int(cause, cause_size.value)


def _decode_io_element(io_bytes, encoder, asdu_type):
    if asdu_type == common.AsduType.S_IT_TC:
        association_id, rest = _decode_int(io_bytes, 2)
        value, rest = iec101.decode_binary_counter_value(rest)

        element = common.IoElement_S_IT_TC(association_id=association_id,
                                           value=value)
        return element, rest

    if asdu_type == common.AsduType.S_CH_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        mac_algorithm, rest = _decode_int(rest, 1)
        reason, rest = _decode_int(rest, 1)
        data_len, rest = _decode_int(rest, 2)
        data, rest = rest[:data_len], rest[data_len:]

        with contextlib.suppress(ValueError):
            mac_algorithm = common.MacAlgorithm(mac_algorithm)

        element = common.IoElement_S_CH_NA(sequence=sequence,
                                           user=user,
                                           mac_algorithm=mac_algorithm,
                                           reason=reason,
                                           data=data)
        return element, rest

    if asdu_type == common.AsduType.S_RP_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        mac_len, rest = _decode_int(rest, 2)
        mac, rest = rest[:mac_len], rest[mac_len:]

        element = common.IoElement_S_RP_NA(sequence=sequence,
                                           user=user,
                                           mac=mac)
        return element, rest

    if asdu_type == common.AsduType.S_AR_NA:
        _, rest = encoder.decode_asdu(io_bytes)
        asdu_len = len(io_bytes) - len(rest)
        asdu = io_bytes[:asdu_len]
        sequence, rest = _decode_int(rest, 4)
        user, rest = _decode_int(rest, 2)
        mac, rest = rest, b''

        element = common.IoElement_S_AR_NA(asdu=asdu,
                                           sequence=sequence,
                                           user=user,
                                           mac=mac)
        return element, rest

    if asdu_type == common.AsduType.S_KR_NA:
        user, rest = _decode_int(io_bytes, 2)

        element = common.IoElement_S_KR_NA(user=user)
        return element, rest

    if asdu_type == common.AsduType.S_KS_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        key_wrap_algorithm, rest = _decode_int(rest, 1)
        key_status, rest = _decode_int(rest, 1)
        mac_algorithm, rest = _decode_int(rest, 1)
        data_len, rest = _decode_int(rest, 2)
        data, rest = rest[:data_len], rest[data_len:]
        mac, rest = rest, b''

        with contextlib.suppress(ValueError):
            key_wrap_algorithm = common.KeyWrapAlgorithm(key_wrap_algorithm)

        with contextlib.suppress(ValueError):
            key_status = common.KeyStatus(key_status)

        with contextlib.suppress(ValueError):
            mac_algorithm = common.MacAlgorithm(mac_algorithm)

        element = common.IoElement_S_KS_NA(
            sequence=sequence,
            user=user,
            key_wrap_algorithm=key_wrap_algorithm,
            key_status=key_status,
            mac_algorithm=mac_algorithm,
            data=data,
            mac=mac)
        return element, rest

    if asdu_type == common.AsduType.S_KC_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        wrapped_key_len, rest = _decode_int(rest, 2)
        wrapped_key, rest = rest[:wrapped_key_len], rest[wrapped_key_len:]

        element = common.IoElement_S_KC_NA(sequence=sequence,
                                           user=user,
                                           wrapped_key=wrapped_key)
        return element, rest

    if asdu_type == common.AsduType.S_ER_NA:
        challenge_sequence, rest = _decode_int(io_bytes, 4)
        key_change_sequence, rest = _decode_int(rest, 4)
        user, rest = _decode_int(rest, 2)
        association_id, rest = _decode_int(rest, 2)
        code, rest = _decode_int(rest, 1)
        time, rest = decode_time(rest, common.TimeSize.SEVEN), rest[7:]
        text_len, rest = _decode_int(rest, 2)
        text, rest = rest[:text_len], rest[text_len:]

        with contextlib.suppress(ValueError):
            code = common.ErrorCode(code)

        element = common.IoElement_S_ER_NA(
            challenge_sequence=challenge_sequence,
            key_change_sequence=key_change_sequence,
            user=user,
            association_id=association_id,
            code=code,
            time=time,
            text=text)
        return element, rest

    if asdu_type == common.AsduType.S_UC_NA_X:
        key_change_method, rest = _decode_int(io_bytes, 1)
        data_len, rest = _decode_int(rest, 2)
        data, rest = rest[:data_len], rest[data_len:]

        with contextlib.suppress(ValueError):
            key_change_method = common.KeyChangeMethod(key_change_method)

        element = common.IoElement_S_UC_NA_X(
            key_change_method=key_change_method,
            data=data)
        return element, rest

    if asdu_type == common.AsduType.S_US_NA:
        key_change_method, rest = _decode_int(io_bytes, 1)
        operation, rest = _decode_int(rest, 1)
        sequence, rest = _decode_int(rest, 4)
        role, rest = _decode_int(rest, 2)
        role_expiry, rest = _decode_int(rest, 2)
        name_len, rest = _decode_int(rest, 2)
        public_key_len, rest = _decode_int(rest, 2)
        certification_len, rest = _decode_int(rest, 2)
        name, rest = rest[:name_len], rest[name_len:]
        public_key, rest = rest[:public_key_len], rest[public_key_len:]
        certification, rest = (rest[:certification_len],
                               rest[certification_len:])

        with contextlib.suppress(ValueError):
            key_change_method = common.KeyChangeMethod(key_change_method)

        with contextlib.suppress(ValueError):
            operation = common.Operation(operation)

        with contextlib.suppress(ValueError):
            role = common.UserRole(role)

        element = common.IoElement_S_US_NA(key_change_method=key_change_method,
                                           operation=operation,
                                           sequence=sequence,
                                           role=role,
                                           role_expiry=role_expiry,
                                           name=name,
                                           public_key=public_key,
                                           certification=certification)
        return element, rest

    if asdu_type == common.AsduType.S_UQ_NA:
        key_change_method, rest = _decode_int(io_bytes, 1)
        name_len, rest = _decode_int(rest, 2)
        data_len, rest = _decode_int(rest, 2)
        name, rest = rest[:name_len], rest[name_len:]
        data, rest = rest[:data_len], rest[data_len:]

        with contextlib.suppress(ValueError):
            key_change_method = common.KeyChangeMethod(key_change_method)

        element = common.IoElement_S_UQ_NA(key_change_method=key_change_method,
                                           name=name,
                                           data=data)
        return element, rest

    if asdu_type == common.AsduType.S_UR_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        data_len, rest = _decode_int(rest, 2)
        data, rest = rest[:data_len], rest[data_len:]

        element = common.IoElement_S_UR_NA(sequence=sequence,
                                           user=user,
                                           data=data)
        return element, rest

    if asdu_type == common.AsduType.S_UK_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        encrypted_update_key_len, rest = _decode_int(rest, 2)
        encrypted_update_key, rest = (rest[:encrypted_update_key_len],
                                      rest[encrypted_update_key_len:])
        mac, rest = rest, b''

        element = common.IoElement_S_UK_NA(
            sequence=sequence,
            user=user,
            encrypted_update_key=encrypted_update_key,
            mac=mac)
        return element, rest

    if asdu_type == common.AsduType.S_UA_NA:
        sequence, rest = _decode_int(io_bytes, 4)
        user, rest = _decode_int(rest, 2)
        encrypted_update_key_len, rest = _decode_int(rest, 2)
        encrypted_update_key, rest = (rest[:encrypted_update_key_len],
                                      rest[encrypted_update_key_len:])
        signature, rest = rest, b''

        element = common.IoElement_S_UA_NA(
            sequence=sequence,
            user=user,
            encrypted_update_key=encrypted_update_key,
            signature=signature)
        return element, rest

    if asdu_type == common.AsduType.S_UC_NA:
        mac, rest = io_bytes, b''

        element = common.IoElement_S_UC_NA(mac=mac)
        return element, rest

    raise ValueError('unsupported asdu type')


def _encode_io_element(element, encoder):
    if isinstance(element, common.IoElement_S_IT_TC):
        yield from _encode_int(element.association_id, 2)
        yield from iec101.encode_binary_counter_value(element.value)

    elif isinstance(element, common.IoElement_S_CH_NA):
        mac_algorithm = (element.mac_algorithm.value
                         if isinstance(element.mac_algorithm, enum.Enum)
                         else element.mac_algorithm)

        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(mac_algorithm, 1)
        yield from _encode_int(element.reason, 1)
        yield from _encode_int(len(element.data), 2)
        yield from element.data

    elif isinstance(element, common.IoElement_S_RP_NA):
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(len(element.mac), 2)
        yield from element.mac

    elif isinstance(element, common.IoElement_S_AR_NA):
        yield from element.asdu
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from element.mac

    elif isinstance(element, common.IoElement_S_KR_NA):
        yield from _encode_int(element.user, 2)

    elif isinstance(element, common.IoElement_S_KS_NA):
        key_wrap_algorithm = (element.key_wrap_algorithm.value
                              if isinstance(element.key_wrap_algorithm, enum.Enum)  # NOQA
                              else element.key_wrap_algorithm)
        key_status = (element.key_status.value
                      if isinstance(element.key_status, enum.Enum)
                      else element.key_status)
        mac_algorithm = (element.mac_algorithm.value
                         if isinstance(element.mac_algorithm, enum.Enum)
                         else element.mac_algorithm)

        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(key_wrap_algorithm, 1)
        yield from _encode_int(key_status, 1)
        yield from _encode_int(mac_algorithm, 1)
        yield from _encode_int(len(element.data), 2)
        yield from element.data
        yield from element.mac

    elif isinstance(element, common.IoElement_S_KC_NA):
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(len(element.wrapped_key), 2)
        yield from element.wrapped_key

    elif isinstance(element, common.IoElement_S_ER_NA):
        code = (element.code.value if isinstance(element.code, enum.Enum)
                else element.code)

        yield from _encode_int(element.challenge_sequence, 4)
        yield from _encode_int(element.key_change_sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(element.association_id, 2)
        yield from _encode_int(code, 1)
        yield from encode_time(element.time, common.TimeSize.SEVEN)
        yield from _encode_int(len(element.text), 2)
        yield from element.text

    elif isinstance(element, common.IoElement_S_UC_NA_X):
        key_change_method = (element.key_change_method.value
                             if isinstance(element.key_change_method, enum.Enum)  # NOQA
                             else element.key_change_method)

        yield from _encode_int(key_change_method, 1)
        yield from _encode_int(len(element.data), 2)
        yield from element.data

    elif isinstance(element, common.IoElement_S_US_NA):
        key_change_method = (element.key_change_method.value
                             if isinstance(element.key_change_method, enum.Enum)  # NOQA
                             else element.key_change_method)
        operation = (element.operation.value
                     if isinstance(element.operation, enum.Enum)
                     else element.operation)
        role = (element.role.value if isinstance(element.role, enum.Enum)
                else element.role)

        yield from _encode_int(key_change_method, 1)
        yield from _encode_int(operation, 1)
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(role, 2)
        yield from _encode_int(element.role_expiry, 2)
        yield from _encode_int(len(element.name), 2)
        yield from _encode_int(len(element.public_key), 2)
        yield from _encode_int(len(element.certification), 2)
        yield from element.name
        yield from element.public_key
        yield from element.certification

    elif isinstance(element, common.IoElement_S_UQ_NA):
        key_change_method = (element.key_change_method.value
                             if isinstance(element.key_change_method, enum.Enum)  # NOQA
                             else element.key_change_method)

        yield from _encode_int(key_change_method, 1)
        yield from _encode_int(len(element.name), 2)
        yield from _encode_int(len(element.data), 2)
        yield from element.name
        yield from element.data

    elif isinstance(element, common.IoElement_S_UR_NA):
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(len(element.data), 2)
        yield from element.data

    elif isinstance(element, common.IoElement_S_UK_NA):
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(len(element.encrypted_update_key), 2)
        yield from element.encrypted_update_key
        yield from element.mac

    elif isinstance(element, common.IoElement_S_UA_NA):
        yield from _encode_int(element.sequence, 4)
        yield from _encode_int(element.user, 2)
        yield from _encode_int(len(element.encrypted_update_key), 2)
        yield from element.encrypted_update_key
        yield from element.signature

    elif isinstance(element, common.IoElement_S_UC_NA):
        yield from element.mac

    else:
        raise ValueError('unsupported io element')


def _decode_int(data, size):
    return int.from_bytes(data[:size], 'little'), data[size:]


def _encode_int(x, size):
    return x.to_bytes(size, 'little')
