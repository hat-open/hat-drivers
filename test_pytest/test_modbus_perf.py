import subprocess
import time
import atexit
import sys

import pytest

from hat import util
from hat.drivers import modbus
from hat.drivers import tcp


pytestmark = pytest.mark.perf


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.fixture
def nullmodem(request, tmp_path):
    path1 = tmp_path / '1'
    path2 = tmp_path / '2'
    p = subprocess.Popen(
        ['socat',
         f'pty,link={path1},raw,echo=0',
         f'pty,link={path2},raw,echo=0'])
    while not path1.exists() or not path2.exists():
        time.sleep(0.001)

    def finalizer():
        p.terminate()

    atexit.register(finalizer)
    request.addfinalizer(finalizer)
    return str(path1), str(path2), p


@pytest.mark.skipif(sys.platform == 'win32', reason="can't simulate serial")
@pytest.mark.parametrize("quantity", [1, 5, 10])
@pytest.mark.parametrize("count", [1, 100, 1000])
async def test_serial(profile, nullmodem, quantity, count):

    def on_read(slave, device_id, data_type, start_address, quantity):
        return list(range(quantity))

    slave = await modbus.create_serial_slave(modbus_type=modbus.ModbusType.RTU,
                                             port=nullmodem[0],
                                             read_cb=on_read,
                                             silent_interval=0)

    master = await modbus.create_serial_master(
        modbus_type=modbus.ModbusType.RTU,
        port=nullmodem[1],
        silent_interval=0)

    with profile(f'quantity_{quantity}_count_{count}'):
        for _ in range(count):
            await master.read(device_id=1,
                              data_type=modbus.DataType.HOLDING_REGISTER,
                              start_address=42,
                              quantity=quantity)

    await master.async_close()
    await slave.async_close()


@pytest.mark.parametrize("quantity", [1, 5, 10])
@pytest.mark.parametrize("count", [1, 100, 1000])
async def test_tcp(profile, addr, quantity, count):

    def on_read(slave, device_id, data_type, start_address, quantity):
        return list(range(quantity))

    server = await modbus.create_tcp_server(modbus_type=modbus.ModbusType.RTU,
                                            addr=addr,
                                            read_cb=on_read)

    master = await modbus.create_tcp_master(modbus_type=modbus.ModbusType.RTU,
                                            addr=addr)

    with profile(f'quantity_{quantity}_count_{count}'):
        for _ in range(count):
            await master.read(device_id=1,
                              data_type=modbus.DataType.HOLDING_REGISTER,
                              start_address=42,
                              quantity=quantity)

    await master.async_close()
    await server.async_close()
