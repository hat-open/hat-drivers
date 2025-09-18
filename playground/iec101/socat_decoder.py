import argparse
import datetime
import enum
import io
import sys
import typing

from hat.drivers import iec101
from hat.drivers.iec101.encoder import Encoder as Iec101Encoder
from hat.drivers.iec60870.link.encoder import Encoder as LinkEncoder
from hat.drivers.iec60870.link.common import ShortFrame


class Direction(enum.Enum):
    A_TO_B = '>'
    B_TO_A = '<'


class Msg(typing.NamedTuple):
    direction: Direction
    timestamp: float
    data: bytes


class SocatStream:

    def __init__(self,
                 stream: io.TextIOBase,
                 with_text: bool):
        self._stream = stream
        self._with_text = with_text

    def read(self) -> Msg | None:
        line = self._stream.readline()
        if not line:
            return

        direction = Direction(line[0])
        timestamp = datetime.datetime(year=int(line[2:6]),
                                      month=int(line[7:9]),
                                      day=int(line[10:12]),
                                      hour=int(line[13:15]),
                                      minute=int(line[16:18]),
                                      second=int(line[19:21]),
                                      microsecond=int(line[22:28])).timestamp()

        if not self._with_text:
            line = self._stream.readline()
            if not line:
                return

            data = bytes.fromhex(line)

        else:
            data = b''
            while True:
                line = self._stream.readline()
                if not line:
                    return

                if line.startswith('--'):
                    break

                data += bytes.fromhex(line[:48])

        return Msg(direction=direction,
                   timestamp=timestamp,
                   data=data)


class Iec101Stream:

    def __init__(self,
                 stream: io.TextIOBase,
                 balanced: bool,
                 address_size: iec101.AddressSize,
                 cause_size: iec101.CauseSize,
                 asdu_address_size: iec101.AsduAddressSize,
                 io_address_size: iec101.IoAddressSize):
        self._stream = stream
        self._data = b''
        self._link_encoder = LinkEncoder(address_size=address_size,
                                         direction_valid=balanced)
        self._iec101_encoder = Iec101Encoder(
            cause_size=cause_size,
            asdu_address_size=asdu_address_size,
            io_address_size=io_address_size)

    def write(self, data: bytes):
        self._data += data

        while True:
            size = self._link_encoder.get_next_frame_size(self._data)
            if len(self._data) < size:
                break

            data, self._data = self._data[:size], self._data[size:]

            frame = self._link_encoder.decode(data)
            self._write_frame(frame)

            if isinstance(frame, ShortFrame) or not frame.data:
                continue

            msgs = self._iec101_encoder.decode(frame.data)
            for msg in msgs:
                self._write_msg(msg)

    def _write_frame(self, frame):
        self._stream.write(f"{type(frame).__name__}\n")

        for i in ['direction',
                  'frame_count_bit',
                  'frame_count_valid',
                  'access_demand',
                  'data_flow_control',
                  'function',
                  'address']:
            if hasattr(frame, i):
                self._stream.write(f"  {i}: {getattr(frame, i)}\n")

    def _write_msg(self, msg):
        self._stream.write(f"  {type(msg).__name__}\n")

        for i in ['is_test',
                  'originator_address',
                  'asdu_address',
                  'io_address',
                  'time',
                  'request',
                  'freeze',
                  'is_negative_confirm',
                  'param_change',
                  'qualifier',
                  'cause']:
            if hasattr(msg, i):
                self._stream.write(f"    {i}: {getattr(msg, i)}\n")

        if hasattr(msg, 'data'):
            self._write_data(msg.data)

        if hasattr(msg, 'command'):
            self._write_command(msg.command)

        if hasattr(msg, 'parameter'):
            self._write_parameter(msg.parameter)

    def _write_data(self, data):
        self._stream.write(f"    {type(data).__name__}\n")

        for i in ['value',
                  'quality',
                  'elapsed_time',
                  'duration_time',
                  'operating_time']:
            if hasattr(data, i):
                self._stream.write(f"      {i}: {getattr(data, i)}\n")

    def _write_command(self, cmd):
        self._stream.write(f"    {type(cmd).__name__}\n")

        for i in ['value',
                  'select',
                  'qualifier']:
            if hasattr(cmd, i):
                self._stream.write(f"      {i}: {getattr(cmd, i)}\n")

    def _write_parameter(self, param):
        self._stream.write(f"    {type(param).__name__}\n")

        for i in ['value',
                  'qualifier']:
            if hasattr(param, i):
                self._stream.write(f"      {i}: {getattr(param, i)}\n")


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-text', action='store_true')
    parser.add_argument('--balanced', action='store_true')
    parser.add_argument('--address-size', metavar='N', type=int, default=2)
    parser.add_argument('--cause-size', metavar='N', type=int, default=2)
    parser.add_argument('--asdu-address-size', metavar='N', type=int,
                        default=2)
    parser.add_argument('--io-address-size', metavar='N', type=int, default=3)
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    in_stream = sys.stdin
    out_stream = sys.stdout

    socat_stream = SocatStream(stream=in_stream,
                               with_text=args.with_text)
    iec101_streams = {
        direction: Iec101Stream(
            stream=out_stream,
            balanced=args.balanced,
            address_size=iec101.AddressSize(args.address_size),
            cause_size=iec101.CauseSize(args.cause_size),
            asdu_address_size=iec101.AsduAddressSize(args.asdu_address_size),
            io_address_size=iec101.IoAddressSize(args.io_address_size))
        for direction in Direction}

    while True:
        msg = socat_stream.read()
        if not msg:
            break

        out_stream.write(f"{msg.direction.value} {msg.timestamp}\n")
        out_stream.write(f"  {msg.data.hex(' ')}\n")

        iec101_streams[msg.direction].write(msg.data)

        out_stream.write("\n")


if __name__ == "__main__":
    main()
