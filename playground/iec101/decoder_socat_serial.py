from pathlib import Path
import click
import contextlib
import sys

from hat.drivers.iec60870 import iec101
from hat.drivers.iec60870 import link
from hat.drivers.iec60870.app.iec101.encoder import Encoder as EncoderApp
from hat.drivers.iec60870.iec101.encoder import Encoder
from hat.drivers.iec60870.link.encoder import Encoder as EncoderLink


def decode(in_bytes):
    encoder = Encoder(
        cause_size=iec101.CauseSize.ONE,
        asdu_address_size=iec101.AsduAddressSize.ONE,
        io_address_size=iec101.IoAddressSize.TWO)

    encoder_app = EncoderApp(
        cause_size=iec101.CauseSize.ONE,
        asdu_address_size=iec101.AsduAddressSize.ONE,
        io_address_size=iec101.IoAddressSize.TWO)

    encoder_link = EncoderLink(
        address_size=link.AddressSize.ONE,
        direction_valid=True)

    data_bytes = bytearray.fromhex(in_bytes)
    frame = encoder_link.decode(data_bytes)
    yield f"{frame}"
    if frame.data:
        asdu = encoder_app.decode_asdu(frame.data)
        yield f"\t{asdu}"
        for msg in encoder.decode(frame.data):
            yield f"\t{msg}"


@click.command()
@click.argument('input-path', default=Path('-'), type=Path)
@click.option('-o', '--output-path', default=Path('-'), type=Path)
def main(input_path, output_path):
    bytes_str = ''
    out_lines = []
    stream = (sys.stdin if input_path == Path('-')
              else open(input_path, 'r', encoding='utf-8'))
    with contextlib.closing(stream):
        while True:
            line = stream.readline()
            if not line:
                break
            if line[0] in ['-', '<', '>']:
                out_lines.append(line)
                continue
            bytes_str += line.split('    ')[0].strip()
            try:
                for i in decode(bytes_str):
                    out_lines.extend((i, "\n"))
                bytes_str = ''
            except Exception:
                pass

    stream = (sys.stdout if output_path == Path('-')
              else open(output_path, 'w'))
    with contextlib.closing(stream):
        stream.writelines(out_lines)


if __name__ == "__main__":
    sys.exit(main())
