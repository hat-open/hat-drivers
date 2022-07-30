import asyncio
from hat.drivers import tcp
from hat.drivers.iec60870 import apci
from hat.drivers.iec60870 import iec104


addr = tcp.Address('127.0.0.1', 23231)

cmd = iec104.CommandMsg(
    is_test=False,
    originator_address=0,
    asdu_address=123,
    io_address=321,
    command=iec104.SingleCommand(
        value=iec104.SingleValue.ON,
        select=False,
        qualifier=0),
    is_negative_confirm=False,
    time=None,
    cause=iec104.CommandReqCause.ACTIVATION)


async def main():
    while True:
        try:
            conn = await apci.connect(addr)
            conn = iec104.Connection(conn)

        except Exception:
            print('connect failed - waithing for 5 seconds')
            await asyncio.sleep(5)
            continue

        print('>> connected')
        try:
            print('>> sending')
            conn.send([cmd])

            while True:
                msgs = await conn.receive()
                print('>> received', msgs)

        except ConnectionError:
            pass

        finally:
            print('>> disconnected')
            await conn.async_close()


if __name__ == '__main__':
    asyncio.run(main())
