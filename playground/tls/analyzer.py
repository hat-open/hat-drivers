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
            size = l2.get_next_msg_size(data)

        except Exception:
            data = data[1:]
            continue

        if size > len(data):
            break

        msg_data, data = data[:size], data[size:]

        print()

        write_l1(msg_data)

        try:
            l2_msg = l2.decode(msg_data)

        except Exception as e:
            write_error(e)
            continue

        write_l2(l2_msg)

        if isinstance(l2_msg, l2.ShortMsg) or not l2_msg.data:
            continue

        try:
            l3_msg = l3.decode(l2_msg.data)

        except Exception as e:
            write_error(e)
            continue

        write_l3(l3_msg)

        try:
            if args.general_msgs:
                l4_msg = l4.decode_general_msg(l3_msg.data)

            else:
                l4_msg = l4.decode_msg(l3_msg.data)

        except Exception as e:
            write_error(e)
            continue

        write_l4(l4_msg)


def write_error(e):
    print(">>> ERR")
    print(f"  {e}")


def write_l1(data):
    print(">>> L1")
    print(f"  {data.hex(' ')}")


def write_l2(msg):
    print(">>> L2")

    if isinstance(msg, l2.ShortMsg):
        print("  ShortMsg")

    elif isinstance(msg, l2.ReqMsg):
        print("  ReqMsg")
        print(f"    frame_count: {msg.frame_count}")
        print(f"    frame_count_valid: {msg.frame_count_valid}")
        print(f"    function: {msg.function.name}")
        print(f"    address: {msg.address}")
        print(f"    data: {msg.data.hex(' ')}")

    elif isinstance(msg, l2.ResMsg):
        print("  ReqMsg")
        print(f"    access_demand: {msg.access_demand}")
        print(f"    data_flow_control: {msg.data_flow_control}")
        print(f"    function: {msg.function.name}")
        print(f"    address: {msg.address}")
        print(f"    data: {msg.data.hex(' ')}")

    else:
        raise TypeError('unsupported msg type')


def write_l3(msg):
    print(">>> L3")
    print(f"  priority: {msg.priority.name}")
    print(f"  pointer: {msg.pointer}")
    print(f"  addresses: {msg.addresses}")
    print(f"  data: {msg.data.hex(' ')}")


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
