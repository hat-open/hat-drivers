import itertools

from hat import util

from hat.drivers.iec60870.link import common


class Encoder:

    def __init__(self,
                 address_size: common.AddressSize,
                 direction_valid: bool):
        self._address_size = address_size
        self._direction_valid = direction_valid

    def get_next_frame_size(self, data: util.Bytes) -> int:
        if not data or data[0] == 0xE5:
            return 1

        if data[0] == 0x10:
            return 4 + self._address_size.value

        if data[0] == 0x68:
            if len(data) < 4:
                return 4

            if data[1] != data[2]:
                raise Exception('length not matching')

            if data[3] != 0x68:
                raise Exception('invalid repeated start identifier')

            return data[1] + 6

        raise Exception('invalid start identifier')

    def decode(self, data: util.Bytes) -> common.Frame:
        if data[0] == 0xE5:
            return common.ShortFrame()

        if data[0] == 0x10:
            data = data[1:4 + self._address_size.value]

        elif data[0] == 0x68:
            if data[1] != data[2]:
                raise Exception('length not matching')

            if data[3] != 0x68:
                raise Exception('invalid repeated start identifier')

            data = data[4:data[1] + 6]

        else:
            raise Exception('invalid start identifier')

        if data[-1] != 0x16:
            raise Exception('invalid end identifier')

        if data[-2] != sum(data[:-2]) % 0x100:
            raise Exception('invalid crc')

        control_field = data[0]
        address_bytes = data[1:1+self._address_size.value]
        data = data[1+self._address_size.value:-2]

        direction = (common.Direction(control_field >> 7)
                     if self._direction_valid else None)
        address = (int.from_bytes(address_bytes, byteorder='little')
                   if self._address_size != common.AddressSize.ZERO
                   else None)

        if control_field & 0x40:
            frame_count_bit = bool(control_field & 0x20)
            frame_count_valid = bool(control_field & 0x10)
            function = common.ReqFunction(control_field & 0x0F)
            frame = common.ReqFrame(direction=direction,
                                    frame_count_bit=frame_count_bit,
                                    frame_count_valid=frame_count_valid,
                                    function=function,
                                    address=address,
                                    data=data)

        else:
            access_demand = bool(control_field & 0x20)
            data_flow_control = bool(control_field & 0x10)
            function = common.ResFunction(control_field & 0x0F)
            frame = common.ResFrame(direction=direction,
                                    access_demand=access_demand,
                                    data_flow_control=data_flow_control,
                                    function=function,
                                    address=address,
                                    data=data)

        return frame

    def encode(self, frame: common.Frame) -> util.Bytes:
        if isinstance(frame, common.ShortFrame):
            return b'\xE5'

        control_field = ((frame.direction.value << 7
                          if self._direction_valid else 0) |
                         frame.function.value)

        if isinstance(frame, common.ReqFrame):
            control_field = (control_field |
                             0x40 |
                             (0x20 if frame.frame_count_bit else 0x00) |
                             (0x10 if frame.frame_count_valid else 0x00))

        elif isinstance(frame, common.ResFrame):
            control_field = (control_field |
                             (0x20 if frame.access_demand else 0x00) |
                             (0x10 if frame.data_flow_control else 0x00))

        else:
            raise ValueError('unsupported frame type')

        address_bytes = (frame.address.to_bytes(self._address_size.value,
                                                byteorder='little')
                         if self._address_size != common.AddressSize.ZERO
                         else b'')

        data = [control_field, *address_bytes, *frame.data]
        crc = sum(data) % 0x100

        header = [0x68, len(data), len(data), 0x68] if frame.data else [0x10]
        footer = [crc, 0x16]

        return bytes(itertools.chain(header, data, footer))
