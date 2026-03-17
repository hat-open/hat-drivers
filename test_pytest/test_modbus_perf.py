import sys

import pytest

from hat import util
from hat.drivers import modbus
from hat.drivers import tcp


pytestmark = pytest.mark.perf


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.mark.skipif(sys.platform == 'win32', reason="can't simulate serial")
@pytest.mark.parametrize("quantity", [1, 5, 10])
@pytest.mark.parametrize("count", [1, 100, 1000])
async def test_serial(profile, nullmodem, quantity, count):

    def on_request(slave, req):
        return list(range(quantity))

    slave = await modbus.create_serial_slave(modbus_type=modbus.ModbusType.RTU,
                                             port=str(nullmodem[0]),
                                             request_cb=on_request,
                                             silent_interval=0)

    master = await modbus.create_serial_master(
        modbus_type=modbus.ModbusType.RTU,
        port=str(nullmodem[1]),
        silent_interval=0)

    with profile(f'quantity_{quantity}_count_{count}'):
        for _ in range(count):
            await master.send(
                modbus.ReadReq(device_id=1,
                               data_type=modbus.DataType.HOLDING_REGISTER,
                               start_address=42,
                               quantity=quantity))

    await master.async_close()
    await slave.async_close()


@pytest.mark.parametrize("quantity", [1, 5, 10])
@pytest.mark.parametrize("count", [1, 100, 1000])
async def test_tcp(profile, addr, quantity, count):

    def on_request(slave, req):
        return list(range(quantity))

    server = await modbus.create_tcp_server(modbus_type=modbus.ModbusType.RTU,
                                            addr=addr,
                                            request_cb=on_request)

    master = await modbus.create_tcp_master(modbus_type=modbus.ModbusType.RTU,
                                            addr=addr)

    with profile(f'quantity_{quantity}_count_{count}'):
        for _ in range(count):
            await master.send(
                modbus.ReadReq(device_id=1,
                               data_type=modbus.DataType.HOLDING_REGISTER,
                               start_address=42,
                               quantity=quantity))

    await master.async_close()
    await server.async_close()
