import argparse
import sys

from hat.drivers.tls import l2
from hat.drivers.tls import l3
from hat.drivers.tls import l4


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--general-msgs', action='store_true')
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    data = memoryview(bytes.fromhex(sys.stdin.read()))
    while data:
        try:
            size = l2.get_next_frame_size(data)

        except Exception:
            data = data[1:]
            continue

        if size > len(data):
            break

        frame_data, data = data[:size], data[size:]

        print()

        write_l1(frame_data)

        try:
            frame = l2.decode(frame_data)

        except Exception as e:
            write_error(e)
            continue

        write_l2(frame)

        if isinstance(frame, l2.ShortFrame) or not frame.data:
            continue

        try:
            packet = l3.decode(frame.data)

        except Exception as e:
            write_error(e)
            continue

        write_l3(packet)

        try:
            if args.general_msgs:
                msg = l4.decode_general_msg(packet.data)

            else:
                msg = l4.decode_msg(packet.data)

        except Exception as e:
            write_error(e)
            continue

        write_l4(msg)


def write_error(e):
    print(">>> ERR")
    print(f"  {e}")


def write_l1(data):
    print(">>> L1")
    print("  Data")
    print(f"    {data.hex(' ')}")


def write_l2(frame):
    print(">>> L2")

    if isinstance(frame, l2.ShortFrame):
        print("  ShortFrame")

    elif isinstance(frame, l2.ReqFrame):
        print("  ReqFrame")
        print(f"    frame_count_bit: {frame.frame_count_bit}")
        print(f"    frame_count_valid: {frame.frame_count_valid}")
        print(f"    function: {frame.function.name}")
        print(f"    address: {frame.address}")
        print(f"    data: {frame.data.hex(' ')}")

    elif isinstance(frame, l2.ResFrame):
        print("  ResFrame")
        print(f"    access_demand: {frame.access_demand}")
        print(f"    data_flow_control: {frame.data_flow_control}")
        print(f"    function: {frame.function.name}")
        print(f"    address: {frame.address}")
        print(f"    data: {frame.data.hex(' ')}")

    else:
        raise TypeError('unsupported frame type')


def write_l3(packet):
    print(">>> L3")
    print("  Packet")
    print(f"    priority: {packet.priority.name}")
    print(f"    pointer: {packet.pointer}")
    print(f"    addresses: {packet.addresses}")
    print(f"    data: {packet.data.hex(' ')}")


def write_l4(msg):
    print(">>> L4")

    if isinstance(msg, l4.GeneralMsg):
        print("  GeneralMsg")
        print(f"    node: {msg.node}")

        msgs = msg.msgs

    else:
        msgs = [msg]

    for msg in msgs:
        if isinstance(msg, l4.ReqMsg):
            print("  ReqMsg")

        elif isinstance(msg, l4.ResMsg):
            print("  ResMsg")

        else:
            raise TypeError('unsupported msg type')

        identifier = (msg.identifier if isinstance(msg.identifier, int)
                      else msg.identifier.name)

        print(f"    function_group: {msg.function_group}")
        print(f"    identifier: {identifier}")
        print(f"    job_number: {msg.job_number}")

        for dt in msg.dts:
            print("    DT")
            print(f"      channel: {dt.channel}")
            print(f"      type: {dt.type}")
            print(f"      data: {dt.data.hex(' ')}")


if __name__ == '__main__':
    main()
