import asyncio
import contextlib
import enum
import sys

import pytest

from hat import aio
from hat import util

from hat.drivers import modbus
from hat.drivers import serial
from hat.drivers import tcp


CommType = enum.Enum('CommType', ['TCP', 'SERIAL'])


if sys.platform == 'win32':
    comm_types = [CommType.TCP]
else:
    comm_types = [CommType.TCP,
                  CommType.SERIAL]


@pytest.fixture
def tcp_addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.fixture
async def patch_serial_read_timeout(monkeypatch):
    monkeypatch.setattr(serial.py_serial, 'read_timeout', 0.01)


@pytest.fixture
async def create_master_slave(tcp_addr, nullmodem, patch_serial_read_timeout):

    @contextlib.asynccontextmanager
    async def create_master_slave(modbus_type, comm_type, request_cb=None):
        srv = None

        if comm_type == CommType.TCP:
            slave_queue = aio.Queue()
            srv = await modbus.create_tcp_server(
                modbus_type=modbus_type,
                addr=tcp_addr,
                slave_cb=slave_queue.put_nowait,
                request_cb=request_cb)
            master = await modbus.create_tcp_master(
                modbus_type=modbus_type,
                addr=tcp_addr)
            slave = await slave_queue.get()

        elif comm_type == CommType.SERIAL:
            master = await modbus.create_serial_master(
                modbus_type=modbus_type,
                port=str(nullmodem[0]))
            slave = await modbus.create_serial_slave(
                modbus_type=modbus_type,
                port=str(nullmodem[1]),
                request_cb=request_cb)

        else:
            raise ValueError()

        try:
            yield master, slave

        finally:
            await master.async_close()
            await slave.async_close()
            if srv:
                await srv.async_close()

    return create_master_slave


@pytest.mark.parametrize("modbus_type", list(modbus.ModbusType))
async def test_create_tcp(tcp_addr, modbus_type):
    with pytest.raises(Exception):
        await modbus.create_tcp_master(modbus_type=modbus_type,
                                       addr=tcp_addr)

    slave_queue = aio.Queue()
    srv = await modbus.create_tcp_server(modbus_type=modbus_type,
                                         addr=tcp_addr,
                                         slave_cb=slave_queue.put_nowait)
    assert not srv.is_closed
    assert slave_queue.empty()

    masters = []
    slaves = []

    for _ in range(10):
        master = await modbus.create_tcp_master(modbus_type=modbus_type,
                                                addr=tcp_addr)
        assert not master.is_closed
        masters.append(master)

        slave = await asyncio.wait_for(slave_queue.get(), 0.1)
        assert not slave.is_closed
        slaves.append(slave)

    for master, slave in zip(masters, slaves):
        assert not master.is_closed
        assert not slave.is_closed

        await master.async_close()
        assert master.is_closed
        await asyncio.wait_for(slave.wait_closed(), 0.1)

    masters = []
    slaves = []

    for _ in range(10):
        master = await modbus.create_tcp_master(modbus_type=modbus_type,
                                                addr=tcp_addr)
        assert not master.is_closed
        masters.append(master)

        slave = await asyncio.wait_for(slave_queue.get(), 0.1)
        assert not slave.is_closed
        slaves.append(slave)

    await srv.async_close()

    for master, slave in zip(masters, slaves):
        await asyncio.wait_for(slave.wait_closed(), 0.1)
        await master.async_close()


@pytest.mark.skipif(sys.platform == 'win32', reason="can't simulate serial")
@pytest.mark.parametrize("modbus_type", list(modbus.ModbusType))
async def test_create_serial(nullmodem, modbus_type,
                             patch_serial_read_timeout):
    master = await modbus.create_serial_master(modbus_type=modbus_type,
                                               port=str(nullmodem[0]))
    slave = await modbus.create_serial_slave(modbus_type=modbus_type,
                                             port=str(nullmodem[1]))
    assert not master.is_closed
    assert not slave.is_closed
    await master.async_close()
    await slave.async_close()


@pytest.mark.parametrize("modbus_type", list(modbus.ModbusType))
@pytest.mark.parametrize("comm_type", comm_types)
@pytest.mark.parametrize("req, res", [
    (modbus.ReadReq(device_id=1,
                    data_type=modbus.DataType.COIL,
                    start_address=1,
                    quantity=1),
     [0]),

    (modbus.ReadReq(device_id=2,
                    data_type=modbus.DataType.COIL,
                    start_address=1,
                    quantity=1),
     [1]),

    (modbus.ReadReq(device_id=3,
                    data_type=modbus.DataType.COIL,
                    start_address=3,
                    quantity=4),
     [1, 0, 1, 0]),

    (modbus.ReadReq(device_id=4,
                    data_type=modbus.DataType.DISCRETE_INPUT,
                    start_address=1,
                    quantity=1),
     [0]),

    (modbus.ReadReq(device_id=5,
                    data_type=modbus.DataType.DISCRETE_INPUT,
                    start_address=1,
                    quantity=2),
     [1, 0]),

    (modbus.ReadReq(device_id=6,
                    data_type=modbus.DataType.HOLDING_REGISTER,
                    start_address=1,
                    quantity=1),
     [0]),

    (modbus.ReadReq(device_id=7,
                    data_type=modbus.DataType.HOLDING_REGISTER,
                    start_address=1,
                    quantity=4),
     [1, 255, 1234, 0xFFFF]),

    (modbus.ReadReq(device_id=8,
                    data_type=modbus.DataType.INPUT_REGISTER,
                    start_address=1,
                    quantity=1),
     [0]),

    (modbus.ReadReq(device_id=9,
                    data_type=modbus.DataType.INPUT_REGISTER,
                    start_address=1,
                    quantity=4),
     [1, 255, 1234, 0xFFFF]),

    (modbus.ReadReq(device_id=10,
                    data_type=modbus.DataType.QUEUE,
                    start_address=123,
                    quantity=0),
     [1, 255, 1234, 0xFFFF]),

    (modbus.ReadReq(device_id=11,
                    data_type=modbus.DataType.COIL,
                    start_address=1,
                    quantity=1),
     modbus.Error.INVALID_FUNCTION_CODE),

    (modbus.ReadReq(device_id=12,
                    data_type=modbus.DataType.COIL,
                    start_address=1,
                    quantity=3),
     modbus.Error.INVALID_DATA_ADDRESS),

    (modbus.ReadReq(device_id=13,
                    data_type=modbus.DataType.COIL,
                    start_address=1,
                    quantity=1),
     modbus.Error.INVALID_DATA_VALUE),

    (modbus.ReadReq(device_id=14,
                    data_type=modbus.DataType.COIL,
                    start_address=1,
                    quantity=3),
     modbus.Error.FUNCTION_ERROR),

    (modbus.WriteReq(device_id=1,
                     data_type=modbus.DataType.COIL,
                     start_address=1,
                     values=[0]),
     modbus.Success()),

    (modbus.WriteReq(device_id=2,
                     data_type=modbus.DataType.COIL,
                     start_address=1,
                     values=[1]),
     modbus.Success()),

    (modbus.WriteReq(device_id=3,
                     data_type=modbus.DataType.COIL,
                     start_address=3,
                     values=[1, 0, 1, 0]),
     modbus.Success()),

    (modbus.WriteReq(device_id=4,
                     data_type=modbus.DataType.HOLDING_REGISTER,
                     start_address=1,
                     values=[0]),
     modbus.Success()),

    (modbus.WriteReq(device_id=5,
                     data_type=modbus.DataType.HOLDING_REGISTER,
                     start_address=1,
                     values=[1, 255, 1234, 0xFFFF]),
     modbus.Success()),

    (modbus.WriteReq(device_id=6,
                     data_type=modbus.DataType.COIL,
                     start_address=1,
                     values=[0]),
     modbus.Error.INVALID_FUNCTION_CODE),

    (modbus.WriteReq(device_id=7,
                     data_type=modbus.DataType.COIL,
                     start_address=1,
                     values=[0]),
     modbus.Error.INVALID_DATA_ADDRESS),

    (modbus.WriteReq(device_id=8,
                     data_type=modbus.DataType.COIL,
                     start_address=1,
                     values=[0]),
     modbus.Error.INVALID_DATA_VALUE),

    (modbus.WriteReq(device_id=9,
                     data_type=modbus.DataType.COIL,
                     start_address=1,
                     values=[0]),
     modbus.Error.FUNCTION_ERROR),

    (modbus.WriteMaskReq(device_id=1,
                         address=1,
                         and_mask=12,
                         or_mask=21),
     modbus.Success()),

    (modbus.WriteMaskReq(device_id=3,
                         address=5,
                         and_mask=42,
                         or_mask=24),
     modbus.Success())
    ])
async def test_send(create_master_slave, modbus_type, comm_type, req, res):

    async def on_request(slave, r):
        assert req == r
        return res

    async with create_master_slave(modbus_type, comm_type,
                                   on_request) as (master, slave):
        result = await master.send(req)
        assert result == res
