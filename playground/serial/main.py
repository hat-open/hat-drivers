import asyncio
import contextlib
import itertools
import argparse

from hat import aio

from hat.drivers import serial


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baudrate', type=int, default=9600)
    parser.add_argument('--bytesize', type=int, default=8,
                        choices=[5, 6, 7, 8])
    parser.add_argument('--parity', default='N',
                        choices=['N', 'E', 'O', 'M', 'S'])
    parser.add_argument('--stopbits', type=int, default=1,
                        choices=[1, 2])
    parser.add_argument('--xonxoff', action='store_true')
    parser.add_argument('--rtscts', action='store_true')
    parser.add_argument('--dsrdtr', action='store_true')
    parser.add_argument('port')
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args))


async def async_main(args):
    endpoint = await serial.create(port=args.port,
                                   baudrate=args.baudrate,
                                   bytesize=serial.ByteSize(args.bytesize),
                                   parity=serial.Parity(args.parity),
                                   stopbits=serial.StopBits(args.stopbits),
                                   xonxoff=args.xonxoff,
                                   rtscts=args.rtscts,
                                   dsrdtr=args.dsrdtr)

    endpoint.async_group.spawn(read_loop, endpoint)

    try:
        for i in itertools.count(0):
            await asyncio.sleep(1)

            print('>> sending', i % 0x100)
            await endpoint.write(bytes([i % 0x100]))

    except ConnectionError:
        pass

    finally:
        await aio.uncancellable(endpoint.async_close())


async def read_loop(endpoint):
    print('>> starting read loop')
    try:
        while True:
            data = await endpoint.read(1)
            print('>> received', data[0])

    except ConnectionError:
        pass

    finally:
        print('>> closing read loop')
        endpoint.close()


if __name__ == '__main__':
    main()
