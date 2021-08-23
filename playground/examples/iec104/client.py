import asyncio
from hat.drivers import iec104


addr = iec104.Address('127.0.0.1', 23231)

cmd = iec104.Command(action=iec104.Action.EXECUTE,
                     value=iec104.SingleValue.ON,
                     time=None,
                     asdu_address=123,
                     io_address=321,
                     qualifier=0)


async def main():
    while True:
        try:
            conn = await iec104.connect(addr)
        except Exception:
            print('connect failed - waithing for 5 seconds')
            await asyncio.sleep(5)
            continue
        conn.async_group.spawn(connection_loop, conn)
        await conn.wait_closed()


async def connection_loop(conn):
    print('starting connection loop')
    try:
        print('sending command')
        await conn.send_command(cmd)
        while True:
            data = await conn.receive()
            for i in data:
                print('>>', i)
    finally:
        conn.close()


if __name__ == '__main__':
    asyncio.run(main())
