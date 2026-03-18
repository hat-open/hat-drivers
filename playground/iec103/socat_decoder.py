import argparse
import datetime
import enum
import io
import sys
import typing

from hat.drivers.iec103.common import AsduTypeError
from hat.drivers.iec60870 import link
from hat.drivers.iec60870.encodings.iec103 import Encoder as Iec103Encoder
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


class Iec103Stream:

    def __init__(self,
                 stream: io.TextIOBase):
        self._stream = stream
        self._data = b''
        self._link_encoder = LinkEncoder(address_size=link.AddressSize.ONE,
                                         direction_valid=False)
        self._iec103_encoder = Iec103Encoder()

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

            try:
                asdu, _ = self._iec103_encoder.decode_asdu(frame.data)
            except AsduTypeError as e:
                self._stream.write(f"  ASDU type error: {e}\n")
                continue

            self._write_asdu(asdu)

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

    def _write_asdu(self, asdu):
        self._stream.write("  ASDU\n")
        self._stream.write(f"    type: {asdu.type}\n")
        self._stream.write(f"    cause: {asdu.cause}\n")
        self._stream.write(f"    address: {asdu.address}\n")

        for io_ in asdu.ios:
            self._stream.write("    IO\n")
            self._stream.write("      function_type: "
                               f"{io_.address.function_type}\n")
            self._stream.write("      information_number: "
                               f"{io_.address.information_number}\n")

            for el in io_.elements:
                self._stream.write(f"      {type(el).__name__}\n")
                for k, v in el._asdict().items():
                    self._stream.write(f"        {k}: {v}\n")


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-text', action='store_true')
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    in_stream = sys.stdin
    out_stream = sys.stdout

    socat_stream = SocatStream(stream=in_stream,
                               with_text=args.with_text)
    iec103_streams = {
        direction: Iec103Stream(stream=out_stream)
        for direction in Direction}

    while True:
        msg = socat_stream.read()
        if not msg:
            break

        out_stream.write(f"{msg.direction.value} {msg.timestamp}\n")
        out_stream.write(f"  {msg.data.hex(' ')}\n")

        iec103_streams[msg.direction].write(msg.data)

        out_stream.write("\n")


if __name__ == "__main__":
    main()
