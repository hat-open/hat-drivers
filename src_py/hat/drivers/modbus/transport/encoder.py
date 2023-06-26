import itertools
import struct

from hat import util

from hat.drivers.modbus.transport import common

try:
    from hat.drivers.modbus.transport import _encoder

except ImportError:
    _encoder = None


def get_next_adu_size(modbus_type: common.ModbusType,
                      direction: common.Direction,
                      data: util.Bytes
                      ) -> int:
    if modbus_type == common.ModbusType.TCP:
        return _get_next_tcp_adu_size(data)

    if modbus_type == common.ModbusType.RTU:
        return _get_next_rtu_adu_size(direction, data)

    if modbus_type == common.ModbusType.ASCII:
        return _get_next_ascii_adu_size(direction, data)

    raise ValueError("unsupported modbus type")


def decode_adu(modbus_type: common.ModbusType,
               direction: common.Direction,
               data: util.Bytes
               ) -> tuple[common.Adu, util.Bytes]:
    if modbus_type == common.ModbusType.TCP:
        return _decode_tcp_adu(direction, data)

    if modbus_type == common.ModbusType.RTU:
        return _decode_rtu_adu(direction, data)

    if modbus_type == common.ModbusType.ASCII:
        return _decode_ascii_adu(direction, data)

    raise ValueError("unsupported modbus type")


def encode_adu(adu: common.Adu) -> util.Bytes:
    if isinstance(adu, common.TcpAdu):
        return _encode_tcp_adu(adu)

    if isinstance(adu, common.RtuAdu):
        return _encode_rtu_adu(adu)

    if isinstance(adu, common.AsciiAdu):
        return _encode_ascii_adu(adu)

    raise ValueError("unsupported modbus type")


def _get_next_tcp_adu_size(data):
    if len(data) < 6:
        return 6

    length = int.from_bytes(data[4:6], 'big')
    return length + 6


def _get_next_rtu_adu_size(direction, data):
    if len(data) < 1:
        return 1

    pdu_size = _get_next_pdu_size(direction, data, 1)
    return pdu_size + 3


def _get_next_ascii_adu_size(direction, data):
    size = 0
    while size < len(data) and data[size] != ord(':'):
        size += 1

    if size >= len(data):
        return size + 1

    size += 1
    while size < len(data) and data[size:size+2] != b'\r\n':
        size += 2

    return size + 2


def _get_next_pdu_size(direction, data, offset):
    if direction == common.Direction.REQUEST:
        return _get_next_req_size(data, offset)

    if direction == common.Direction.RESPONSE:
        return _get_next_res_size(data, offset)

    raise ValueError('invalid direction')


def _get_next_req_size(data, offset):
    if len(data) < offset + 1:
        return 1

    fc = common.FunctionCode(data[offset])

    if fc in (common.FunctionCode.READ_COILS,
              common.FunctionCode.READ_DISCRETE_INPUTS,
              common.FunctionCode.READ_HOLDING_REGISTERS,
              common.FunctionCode.READ_INPUT_REGISTERS,
              common.FunctionCode.WRITE_SINGLE_COIL,
              common.FunctionCode.WRITE_SINGLE_REGISTER):
        return 5

    if fc in (common.FunctionCode.WRITE_MULTIPLE_COILS,
              common.FunctionCode.WRITE_MULTIPLE_REGISTER):
        if len(data) < offset + 6:
            return 6

        return data[offset + 5] + 6

    if fc == common.FunctionCode.MASK_WRITE_REGISTER:
        return 7

    if fc == common.FunctionCode.READ_FIFO_QUEUE:
        return 3

    raise ValueError("unsupported function code")


def _get_next_res_size(data, offset):
    if len(data) < offset + 1:
        return 1

    if data[offset] & 0x80:
        return 2

    fc = common.FunctionCode(data[offset])

    if fc in (common.FunctionCode.READ_COILS,
              common.FunctionCode.READ_DISCRETE_INPUTS,
              common.FunctionCode.READ_HOLDING_REGISTERS,
              common.FunctionCode.READ_INPUT_REGISTERS,
              common.FunctionCode.READ_FIFO_QUEUE):
        if len(data) < offset + 2:
            return 2

        return data[offset + 1] + 2

    if fc in (common.FunctionCode.WRITE_SINGLE_COIL,
              common.FunctionCode.WRITE_SINGLE_REGISTER,
              common.FunctionCode.WRITE_MULTIPLE_COILS,
              common.FunctionCode.WRITE_MULTIPLE_REGISTER):
        return 5

    if fc == common.FunctionCode.MASK_WRITE_REGISTER:
        return 7

    raise ValueError("unsupported function code")


def _decode_tcp_adu(direction, data):
    mbap_bytes, rest = data[:7], data[7:]
    transaction_id, identifier, length, device_id = struct.unpack(
        '>HHHB', mbap_bytes)

    if identifier:
        raise Exception('invalid protocol identifier')

    pdu_bytes, rest = rest[:length-1], rest[length-1:]
    pdu, _ = _decode_pdu(direction, pdu_bytes)

    adu = common.TcpAdu(transaction_id=transaction_id,
                        device_id=device_id,
                        pdu=pdu)
    return adu, rest


def _decode_rtu_adu(direction, data):
    device_id, rest = data[0], data[1:]
    pdu, rest = _decode_pdu(direction, rest)

    crc_bytes, rest = rest[:2], rest[2:]
    crc = int.from_bytes(crc_bytes, 'little')

    calculated_crc = _calculate_crc(data[:len(data)-len(rest)-2])
    if crc != calculated_crc:
        raise Exception("CRC didn't match received message")

    adu = common.RtuAdu(device_id=device_id, pdu=pdu)
    return adu, rest


def _decode_ascii_adu(direction, data):
    rest = data
    while True:
        i, rest = rest[0], rest[1:]
        if i == ord(':'):
            break

    adu_bytes = bytearray()
    while True:
        i, rest = rest[:2], rest[2:]
        if i == b'\r\n':
            break
        adu_bytes.append(int(str(i, 'ascii'), 16))

    device_id = adu_bytes[0]
    pdu, _ = _decode_pdu(direction, adu_bytes[1:])

    lrc = adu_bytes[-1]
    calculated_lrc = _calculate_lrc(adu_bytes[:-1])
    if lrc != calculated_lrc:
        raise Exception("LRC didn't match received message")

    adu = common.AsciiAdu(device_id=device_id, pdu=pdu)
    return adu, rest


def _decode_pdu(direction, data):
    if direction == common.Direction.REQUEST:
        return _decode_req(data)

    if direction == common.Direction.RESPONSE:
        return _decode_res(data)

    raise ValueError('invalid direction')


def _decode_req(data):
    fc, rest = common.FunctionCode(data[0]), data[1:]

    if fc == common.FunctionCode.READ_COILS:
        address, quantity = struct.unpack('>HH', rest[:4])
        rest = rest[4:]
        req = common.ReadCoilsReq(address=address,
                                  quantity=quantity)

    elif fc == common.FunctionCode.READ_DISCRETE_INPUTS:
        address, quantity = struct.unpack('>HH', rest[:4])
        rest = rest[4:]
        req = common.ReadDiscreteInputsReq(address=address,
                                           quantity=quantity)

    elif fc == common.FunctionCode.READ_HOLDING_REGISTERS:
        address, quantity = struct.unpack('>HH', rest[:4])
        rest = rest[4:]
        req = common.ReadHoldingRegistersReq(address=address,
                                             quantity=quantity)

    elif fc == common.FunctionCode.READ_INPUT_REGISTERS:
        address, quantity = struct.unpack('>HH', rest[:4])
        rest = rest[4:]
        req = common.ReadInputRegistersReq(address=address,
                                           quantity=quantity)

    elif fc == common.FunctionCode.WRITE_SINGLE_COIL:
        address, value = struct.unpack('>HH', rest[:4])
        rest = rest[4:]
        req = common.WriteSingleCoilReq(address=address,
                                        value=bool(value))

    elif fc == common.FunctionCode.WRITE_SINGLE_REGISTER:
        address, value = struct.unpack('>HH', rest[:4])
        rest = rest[4:]
        req = common.WriteSingleRegisterReq(address=address,
                                            value=value)

    elif fc == common.FunctionCode.WRITE_MULTIPLE_COILS:
        address, quantity, byte_count = struct.unpack('>HHB', rest[:5])
        values_bytes, rest = rest[5:byte_count+5], rest[byte_count+5:]
        values = [int(bool(values_bytes[i // 8] & (1 << (i % 8))))
                  for i in range(quantity)]
        req = common.WriteMultipleCoilsReq(address=address,
                                           values=values)

    elif fc == common.FunctionCode.WRITE_MULTIPLE_REGISTER:
        address, quantity, byte_count = struct.unpack('>HHB', rest[:5])
        values_bytes, rest = rest[5:byte_count+5], rest[byte_count+5:]
        values = [int.from_bytes(values_bytes[i*2:(i+1)*2], 'big')
                  for i in range(quantity)]
        req = common.WriteMultipleRegistersReq(address=address,
                                               values=values)

    elif fc == common.FunctionCode.MASK_WRITE_REGISTER:
        address, and_mask, or_mask = struct.unpack('>HHH', rest[:6])
        rest = rest[6:]
        req = common.MaskWriteRegisterReq(address=address,
                                          and_mask=and_mask,
                                          or_mask=or_mask)

    elif fc == common.FunctionCode.READ_FIFO_QUEUE:
        address, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        req = common.ReadFifoQueueReq(address=address)

    else:
        raise ValueError("unsupported function code")

    return req, rest


def _decode_res(data):
    fc, rest = common.FunctionCode(data[0] & 0x7F), data[1:]

    if data[0] & 0x80:
        error, rest = common.Error(rest[0]), rest[1:]
        res = common.ErrorRes(fc=fc, error=error)

    elif fc == common.FunctionCode.READ_COILS:
        byte_count = rest[0]
        values_bytes, rest = rest[1:byte_count+1], rest[byte_count+1:]
        values = list(itertools.chain.from_iterable(((i >> j) & 1
                                                     for j in range(8))
                                                    for i in values_bytes))
        res = common.ReadCoilsRes(values=values)

    elif fc == common.FunctionCode.READ_DISCRETE_INPUTS:
        byte_count = rest[0]
        values_bytes, rest = rest[1:byte_count+1], rest[byte_count+1:]
        values = list(itertools.chain.from_iterable(((i >> j) & 1
                                                     for j in range(8))
                                                    for i in values_bytes))
        res = common.ReadDiscreteInputsRes(values=values)

    elif fc == common.FunctionCode.READ_HOLDING_REGISTERS:
        byte_count = rest[0]
        if byte_count % 2:
            raise Exception('invalid number of bytes')
        values_bytes, rest = rest[1:byte_count+1], rest[byte_count+1:]
        values = [int.from_bytes(values_bytes[i*2:(i+1)*2], 'big')
                  for i in range(byte_count // 2)]
        res = common.ReadHoldingRegistersRes(values=values)

    elif fc == common.FunctionCode.READ_INPUT_REGISTERS:
        byte_count = rest[0]
        if byte_count % 2:
            raise Exception('invalid number of bytes')
        values_bytes, rest = rest[1:byte_count+1], rest[byte_count+1:]
        values = [int.from_bytes(values_bytes[i*2:(i+1)*2], 'big')
                  for i in range(byte_count // 2)]
        res = common.ReadInputRegistersRes(values=values)

    elif fc == common.FunctionCode.WRITE_SINGLE_COIL:
        address, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        value, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        value = 1 if value else 0
        res = common.WriteSingleCoilRes(address=address,
                                        value=value)

    elif fc == common.FunctionCode.WRITE_SINGLE_REGISTER:
        address, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        value, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        res = common.WriteSingleRegisterRes(address=address,
                                            value=value)

    elif fc == common.FunctionCode.WRITE_MULTIPLE_COILS:
        address, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        quantity, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        res = common.WriteMultipleCoilsRes(address=address,
                                           quantity=quantity)

    elif fc == common.FunctionCode.WRITE_MULTIPLE_REGISTER:
        address, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        quantity, rest = int.from_bytes(rest[:2], 'big'), rest[2:]
        res = common.WriteMultipleRegistersRes(address=address,
                                               quantity=quantity)

    elif fc == common.FunctionCode.MASK_WRITE_REGISTER:
        address, and_mask, or_mask = struct.unpack('>HHH', rest[:6])
        rest = rest[6:]
        res = common.MaskWriteRegisterRes(address=address,
                                          and_mask=and_mask,
                                          or_mask=or_mask)

    elif fc == common.FunctionCode.READ_FIFO_QUEUE:
        byte_count = rest[0]
        if byte_count % 2:
            raise Exception('invalid number of bytes')
        values_bytes, rest = rest[1:byte_count+1], rest[byte_count+1:]
        values = [int.from_bytes(values_bytes[i*2:(i+1)*2], 'big')
                  for i in range(byte_count // 2)]
        res = common.ReadFifoQueueRes(values=values)

    else:
        raise ValueError("unsupported function code")

    return res, rest


def _encode_tcp_adu(adu):
    pdu_bytes = bytes(_encode_pdu(adu.pdu))
    header_bytes = struct.pack('>HHHB',
                               adu.transaction_id,
                               0,
                               len(pdu_bytes) + 1,
                               adu.device_id)

    adu_bytes = bytes(itertools.chain(header_bytes, pdu_bytes))
    return adu_bytes


def _encode_rtu_adu(adu):
    adu_bytes = bytearray()
    adu_bytes.append(adu.device_id)
    adu_bytes.extend(_encode_pdu(adu.pdu))

    crc = _calculate_crc(adu_bytes)
    crc_bytes = crc.to_bytes(2, 'little')
    adu_bytes.extend(crc_bytes)

    return adu_bytes


def _encode_ascii_adu(adu):
    msg_bytes = bytearray()
    msg_bytes.append(adu.device_id)
    msg_bytes.extend(_encode_pdu(adu.pdu))

    lrc = _calculate_lrc(msg_bytes)
    msg_bytes.append(lrc)

    msg_ascii = bytearray(b':')
    for i in msg_bytes:
        msg_ascii.extend(f'{i:02X}'.encode('ascii'))
    msg_ascii.extend(b'\r\n')

    return msg_ascii


def _encode_pdu(pdu):
    if isinstance(pdu, common.Request):
        return _encode_req(pdu)

    if isinstance(pdu, common.Response):
        return _encode_res(pdu)

    raise ValueError('unsupported pdu data')


def _encode_req(req):
    if isinstance(req, common.ReadCoilsReq):
        yield common.FunctionCode.READ_COILS.value
        yield from struct.pack('>HH', req.address, req.quantity)

    elif isinstance(req, common.ReadDiscreteInputsReq):
        yield common.FunctionCode.READ_DISCRETE_INPUTS.value
        yield from struct.pack('>HH', req.address, req.quantity)

    elif isinstance(req, common.ReadHoldingRegistersReq):
        yield common.FunctionCode.READ_HOLDING_REGISTERS.value
        yield from struct.pack('>HH', req.address, req.quantity)

    elif isinstance(req, common.ReadInputRegistersReq):
        yield common.FunctionCode.READ_INPUT_REGISTERS.value
        yield from struct.pack('>HH', req.address, req.quantity)

    elif isinstance(req, common.WriteSingleCoilReq):
        yield common.FunctionCode.WRITE_SINGLE_COIL.value
        yield from struct.pack('>HH', req.address, 0xFF00 if req.value else 0)

    elif isinstance(req, common.WriteSingleRegisterReq):
        yield common.FunctionCode.WRITE_SINGLE_REGISTER.value
        yield from struct.pack('>HH', req.address, req.value)

    elif isinstance(req, common.WriteMultipleCoilsReq):
        yield common.FunctionCode.WRITE_MULTIPLE_COILS.value
        quantity = len(req.values)
        count = quantity // 8 + (1 if quantity % 8 else 0)
        yield from struct.pack('>HHB', req.address, quantity, count)
        for i in range(count):
            data_byte = 0
            for j in range(8):
                if len(req.values) > i * 8 + j and req.values[i * 8 + j]:
                    data_byte = data_byte | (1 << j)
            yield data_byte

    elif isinstance(req, common.WriteMultipleRegistersReq):
        yield common.FunctionCode.WRITE_MULTIPLE_REGISTER.value
        quantity = len(req.values)
        count = 2 * quantity
        yield from bytearray(struct.pack('>HHB', req.address, quantity, count))
        for i in range(count):
            yield (req.values[i // 2] >> (0 if i % 2 else 8)) & 0xFF

    elif isinstance(req, common.MaskWriteRegisterReq):
        yield common.FunctionCode.MASK_WRITE_REGISTER.value
        yield from struct.pack('>HHH', req.address, req.and_mask, req.or_mask)

    elif isinstance(req, common.ReadFifoQueueReq):
        yield common.FunctionCode.READ_FIFO_QUEUE.value
        yield from struct.pack('>H', req.address)

    else:
        raise ValueError('unsupported request type')


def _encode_res(res):
    if isinstance(res, common.ErrorRes):
        yield res.fc.value | 0x80
        yield res.error.value

    elif isinstance(res, common.ReadCoilsRes):
        yield common.FunctionCode.READ_COILS.value
        quantity = len(res.values)
        count = quantity // 8 + (1 if quantity % 8 else 0)
        yield count
        for i in range(count):
            data_byte = 0
            for j in range(8):
                if (len(res.values) > i * 8 + j and
                        res.values[i * 8 + j]):
                    data_byte = data_byte | (1 << j)
            yield data_byte

    elif isinstance(res, common.ReadDiscreteInputsRes):
        yield common.FunctionCode.READ_DISCRETE_INPUTS.value
        quantity = len(res.values)
        count = quantity // 8 + (1 if quantity % 8 else 0)
        yield count
        for i in range(count):
            data_byte = 0
            for j in range(8):
                if len(res.values) > i * 8 + j and res.values[i * 8 + j]:
                    data_byte = data_byte | (1 << j)
            yield data_byte

    elif isinstance(res, common.ReadHoldingRegistersRes):
        yield common.FunctionCode.READ_HOLDING_REGISTERS.value
        yield len(res.values) * 2
        for i in res.values:
            yield from [(i >> 8) & 0xFF, i & 0xFF]

    elif isinstance(res, common.ReadInputRegistersRes):
        yield common.FunctionCode.READ_INPUT_REGISTERS.value
        yield len(res.values) * 2
        for i in res.values:
            yield from [(i >> 8) & 0xFF, i & 0xFF]

    elif isinstance(res, common.WriteSingleCoilRes):
        yield common.FunctionCode.WRITE_SINGLE_COIL.value
        yield from struct.pack('>HH', res.address, 0xFF00 if res.value else 0)

    elif isinstance(res, common.WriteSingleRegisterRes):
        yield common.FunctionCode.WRITE_SINGLE_REGISTER.value
        yield from struct.pack('>HH', res.address, res.value)

    elif isinstance(res, common.WriteMultipleCoilsRes):
        yield common.FunctionCode.WRITE_MULTIPLE_COILS.value
        yield from struct.pack('>HH', res.address, res.quantity)

    elif isinstance(res, common.WriteMultipleRegistersRes):
        yield common.FunctionCode.WRITE_MULTIPLE_REGISTER.value
        yield from struct.pack('>HH', res.address, res.quantity)

    elif isinstance(res, common.MaskWriteRegisterRes):
        yield common.FunctionCode.MASK_WRITE_REGISTER.value
        yield from struct.pack('>HHH', res.address, res.and_mask, res.or_mask)

    elif isinstance(res, common.ReadFifoQueueRes):
        yield common.FunctionCode.READ_FIFO_QUEUE.value
        yield len(res.values) * 2
        for i in res.values:
            yield from [(i >> 8) & 0xFF, i & 0xFF]

    else:
        raise ValueError('unsupported request type')


def _calculate_crc(data):
    if _encoder:
        return _encoder.calculate_crc(data)

    crc = 0xFFFF
    for i in data:
        crc ^= i
        for _ in range(8):
            lsb = crc & 1
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc


def _calculate_lrc(data):
    return (~sum(data) + 1) & 0xFF
