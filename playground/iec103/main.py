import asyncio
import contextlib
import datetime

from hat import aio
from hat.drivers import serial
from hat.drivers.iec60870 import link
from hat.drivers.iec60870 import iec103


def main():
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


def on_data(data):
    print('>>>', data)


def on_generic_data(data):
    print('>>>', data)


async def async_main():
    link_master = await link.unbalanced.create_master(
        port='/dev/ttyS1',
        baudrate=19200,
        parity=serial.Parity.EVEN)
    print("serial endpoint opened")

    link_conn = await link_master.connect(10)
    print("link connected")

    master = iec103.MasterConnection(link_conn,
                                     data_cb=on_data,
                                     generic_data_cb=on_generic_data)

    await asyncio.sleep(2)

    time = iec103.time_from_datetime(datetime.datetime.now())
    time = time._replace(hours=time.hours + 3)
    print('sending time', time)
    await master.time_sync(time=time, asdu_address=10)

    await asyncio.sleep(2)

    print('GI start')
    await master.interrogate(10)
    print('GI stop')

    await asyncio.sleep(5)

    print('sending command')
    value = iec103.DoubleValue.ON
    result = await master.send_command(10, iec103.IoAddress(216, 3), value)
    print('command response', result)

    await asyncio.Future()

    await master.async_close()
    await link_conn.async_close()
    await link_master.async_close()


if __name__ == '__main__':
    main()
