import click
from pathlib import Path
import sys

from hat.drivers.iec60870 import iec101
from hat.drivers.iec60870.iec101.encoder import Encoder
from hat.drivers.iec60870.app.iec101.encoder import Encoder as EncoderApp
from hat.drivers.iec60870.link.encoder import Encoder as EncoderLink
from hat.drivers.iec60870 import link


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
@click.option('--in-file', default=None, type=Path, required=True)
@click.option('--out-file', default=None, type=Path, required=False)
def main(in_file, out_file):

    bytes_str = ''
    out_lines = []
    with open(in_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line[0] != ' ':
                out_lines.append(line)
                continue
            bytes_str += line.split('    ')[0].strip()
            try:
                for i in decode(bytes_str):
                    out_lines.append(i)
                    out_lines.append("\n")
                bytes_str = ''
            except Exception:
                pass

    if out_file:
        with open(out_file, 'w') as f:
            f.writelines(out_lines)
    else:
        for i in out_lines:
            print(i)


if __name__ == "__main__":
    sys.exit(main())
