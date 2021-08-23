import asyncio

from hat.drivers import tcp
from hat.drivers import modbus


address = tcp.Address('127.0.0.1', 1234)


async def main():
    master = await modbus.create_tcp_master(modbus.ModbusType.RTU,
                                            address)
    try:
        result = await master.read(device_id=1,
                                   data_type=modbus.DataType.COIL,
                                   start_address=123,
                                   quantity=3)
        print(result)
    finally:
        await master.async_close()


if __name__ == '__main__':
    asyncio.run(main())
