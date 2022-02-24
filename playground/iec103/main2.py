import asyncio
import contextlib
import sys

from hat import aio
from hat.drivers import serial
from hat.drivers.iec60870 import app
from hat.drivers.iec60870 import link


def main():
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():

    port = sys.argv[1]

    encoder = app.iec103.encoder.Encoder()

    endpoint = await link.endpoint.create(
        address_size=link.AddressSize.ONE,
        direction_valid=False,
        port=port,
        baudrate=19200,
        parity=serial.Parity.EVEN)

    while True:
        frame = await endpoint.receive()
        if frame.function not in (link.common.ReqFunction.DATA,
                                  link.common.ResFunction.RES_DATA):
            continue

        if not frame.data:
            continue

        # print('===', bytes(frame.data).hex(' '))

        asdu = encoder.decode_asdu(frame.data)
        if asdu.type == app.iec103.common.AsduType.MEASURANDS_2:
            continue

        print('+++', asdu)

    await endpoint.async_close()


if __name__ == '__main__':
    main()
