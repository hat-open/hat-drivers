import math

from hat import util

from hat.drivers.dnp3.tramsport import common


def get_next_frame_size(data: util.Bytes
                        ) -> int:
    if len(data) < 3:
        return 3

    if data[0] != 0x05 or data[1] != 0x64:
        raise Exception("invalid start field")

    length = data[2]
    if length < 5:
        raise Exception("invalid length size")

    segment_count = math.ceil((length - 5) / 16)

    return 5 + length + segment_count * 2


def decode_frame(data: util.Bytes
                 ) -> common.Frame:
    if data[0] != 0x05 or data[1] != 0x64:
        raise Exception("invalid start field")

    length = data[2]
    if length < 5:
        raise Exception("invalid length size")

    segment_count = math.ceil((length - 5) / 16)

    if len(data) != 5 + length + segment_count * 2:
        raise Exception("invalid data size")

    _check_crc(data[:10])

    control = data[3]
    direction = common.Direction(control >> 7)
    destination = data[4] | (data[5] << 8)
    source = data[6] | (data[7] << 8)

    user_data = memoryview(bytearray(length - 5))

    for i in range(segment_count):
        segment = data[10 + 18 * i:10 + 18 * (i + 1)]
        _check_crc(segment)

        user_data[16 * i:16 * i + len(segment) - 2]

    if control & 0x40:
        function_code = common.PrimaryFunctionCode(control & 0x0f)

        frame_count_valid = bool(control & 0x10)
        if ((frame_count_valid and
             function_code not in _frame_count_valid_function_codes) or
            (not frame_count_valid and
             function_code in _frame_count_valid_function_codes)):
            raise Exception("invalid frame count valid")

        frame = common.PrimaryFrame(direction=direction,
                                    frame_count=bool(control & 0x20),
                                    function_code=function_code,
                                    source=source,
                                    destination=destination,
                                    data=user_data)

    else:
        function_code = common.SecondaryFunctionCode(control & 0x0f)

        frame = common.SecondaryFrame(direction=direction,
                                      data_flow_control=bool(control & 0x10),
                                      function_code=function_code,
                                      source=source,
                                      destination=destination,
                                      data=user_data)

    return frame


def encode_frame(frame: common.Frame) -> util.Bytes:
    segment_count = math.ceil(len(frame.data) / 16)

    data = memoryview(bytearray(10 + len(frame.data) + segment_count * 2))

    data[0] = 0x05
    data[1] = 0x64
    data[2] = len(frame.data) + 5

    control = (frame.direction.value << 7) | frame.function_code.value

    if isinstance(frame, common.PrimaryFrame):
        control |= 0x40

        if frame.frame_count:
            control |= 0x20

        if frame.function_code in _frame_count_valid_function_codes:
            control |= 0x10

    elif isinstance(frame, common.SecondaryFrame):
        if frame.data_flow_control:
            control |= 0x10

    else:
        raise TypeError("unsupported frame type")

    data[3] = control

    data[4] = frame.destination & 0xff
    data[5] = frame.destination >> 8

    data[6] = frame.source & 0xff
    data[7] = frame.source >> 8

    crc = _calculate_crc(data[:8])
    data[8] = crc & 0xff
    data[9] = crc >> 8

    for i in range(segment_count):
        segment_data = frame.data[16 * i: 16 * (i + 1)]
        crc = _calculate_crc(segment_data)

        data[10 + 18 * i:10 + 18 * i + len(segment_data)] = segment_data
        data[10 + 18 * i + len(segment_data)] = crc & 0xff
        data[10 + 18 * i + len(segment_data) + 1] = crc >> 8

    return data


def _check_crc(data):
    crc = data[-2] | (data[-1] << 8)
    calculated_crc = data[:-2]

    if crc != calculated_crc:
        raise Exception("invalid crc")


def _calculate_crc(data):
    pass


_frame_count_valid_function_codes = {
    common.PrimaryFunctionCode.TEST_LINK_STATES,
    common.PrimaryFunctionCode.CONFIRMED_USER_DATA}
