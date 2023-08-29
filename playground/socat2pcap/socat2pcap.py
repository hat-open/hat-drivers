import datetime
import enum
import io
import struct
import sys
import typing


class Direction(enum.Enum):
    A_TO_B = '>'
    B_TO_A = '<'


class Msg(typing.NamedTuple):
    direction: Direction
    timestamp: float
    data: bytes


def invert(direction: Direction) -> Direction:
    if direction == Direction.A_TO_B:
        return Direction.B_TO_A

    if direction == Direction.B_TO_A:
        return Direction.A_TO_B

    raise ValueError('unsupported direction')


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


class PcapStream:

    def __init__(self,
                 stream: io.RawIOBase):
        self._stream = stream
        self._addrs = {Direction.A_TO_B: 0x7f_00_00_01,
                       Direction.B_TO_A: 0x7f_00_00_01}
        self._ports = {Direction.A_TO_B: 1234,
                       Direction.B_TO_A: 4321}
        self._seqs = {Direction.A_TO_B: 0,
                      Direction.B_TO_A: 0}

        self._stream.write(struct.pack("IHHIIII",
                                       0xa1b2c3d4,  # magic number
                                       2,  # major version
                                       4,  # minor version
                                       0,  # reserved
                                       0,  # reserved
                                       0xffffffff,  # snap len
                                       101))  # link type - LINKTYPE_RAW
        self._stream.flush()

    def write(self, msg: Msg):
        seq = self._seqs[msg.direction]
        ack = self._seqs[invert(msg.direction)]

        tcp_len = 20 + len(msg.data)
        tcp_header = struct.pack(
            ">HHIIBBHHH",
            self._ports[msg.direction],  # src port
            self._ports[invert(msg.direction)],  # dst port
            seq,  # seq number
            ack,  # ack number
            0x50,  # data offset
            0,  # flags
            0xffff,  # window size
            0,  # checksum
            0)  # urgent pointer

        ip_len = 20 + tcp_len
        ip_header = struct.pack(
            ">BBHHHBBHLL",
            0x45,  # ipv4 + 5*32 bit header
            0,  # dscp + ecn
            ip_len,  # total length
            0,  # identification
            0,  # flag + fragment offset
            0xff,  # ttl
            6,  # protocol - tcp
            0,  # checksum
            self._addrs[msg.direction],  # src addr
            self._addrs[invert(msg.direction)])  # dst addr

        packet_header = struct.pack(
            "IIII",
            int(msg.timestamp),
            int((msg.timestamp - int(msg.timestamp)) * 1E6),
            ip_len,
            ip_len)

        self._stream.write(packet_header)
        self._stream.write(ip_header)
        self._stream.write(tcp_header)
        self._stream.write(msg.data)
        self._stream.flush()

        self._seqs[msg.direction] += len(msg.data)


def main():
    stdout, sys.stdout = sys.stdout.detach(), None

    socat = SocatStream(sys.stdin, True)
    pcap = PcapStream(stdout)

    while True:
        msg = socat.read()
        if not msg:
            break

        pcap.write(msg)


if __name__ == '__main__':
    main()
