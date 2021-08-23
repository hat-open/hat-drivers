import asyncio

from hat.drivers import tcp
from hat.drivers import modbus


address = tcp.Address('127.0.0.1', 1234)


async def main():
    server = await modbus.create_tcp_server(modbus.ModbusType.RTU,
                                            address,
                                            slave_cb=on_slave,
                                            read_cb=on_read)
    try:
        await server.wait_closing()
    finally:
        await server.async_close()


async def on_slave(slave):
    print('connected')
    try:
        await slave.wait_closing()
    finally:
        print('disconneted')
        await slave.async_close()


async def on_read(slave, device_id, data_type, start_address, quantity):
    print('read request')
    return [i % 2 for i in range(quantity)]


if __name__ == '__main__':
    asyncio.run(main())
