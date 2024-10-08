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
    async def create_master_slave(modbus_type, comm_type, read_cb=None,
                                  write_cb=None, write_mask_cb=None):
        srv = None

        if comm_type == CommType.TCP:
            slave_queue = aio.Queue()
            srv = await modbus.create_tcp_server(
                modbus_type, tcp_addr, slave_queue.put_nowait,
                read_cb, write_cb, write_mask_cb)
            master = await modbus.create_tcp_master(
                modbus_type, tcp_addr)
            slave = await slave_queue.get()

        elif comm_type == CommType.SERIAL:
            master = await modbus.create_serial_master(
                modbus_type, str(nullmodem[0]))
            slave = await modbus.create_serial_slave(
                modbus_type, str(nullmodem[1]), read_cb, write_cb,
                write_mask_cb)

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
        await modbus.create_tcp_master(modbus_type, tcp_addr)

    slave_queue = aio.Queue()
    srv = await modbus.create_tcp_server(modbus_type, tcp_addr,
                                         slave_queue.put_nowait)
    assert not srv.is_closed
    assert slave_queue.empty()

    masters = []
    slaves = []

    for _ in range(10):
        master = await modbus.create_tcp_master(modbus_type, tcp_addr)
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
        master = await modbus.create_tcp_master(modbus_type, tcp_addr)
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
    master = await modbus.create_serial_master(modbus_type, str(nullmodem[0]))
    slave = await modbus.create_serial_slave(modbus_type, str(nullmodem[1]))
    assert not master.is_closed
    assert not slave.is_closed
    await master.async_close()
    await slave.async_close()


@pytest.mark.parametrize("modbus_type", list(modbus.ModbusType))
@pytest.mark.parametrize("comm_type", comm_types)
@pytest.mark.parametrize(
    "device_id, data_type, start_address, quantity, result", [
        (1, modbus.DataType.COIL, 1, 1, [0]),
        (2, modbus.DataType.COIL, 1, 1, [1]),
        (3, modbus.DataType.COIL, 3, 4, [1, 0, 1, 0]),
        (4, modbus.DataType.DISCRETE_INPUT, 1, 1, [0]),
        (5, modbus.DataType.DISCRETE_INPUT, 1, 2, [1, 0]),
        (6, modbus.DataType.HOLDING_REGISTER, 1, 1, [0]),
        (7, modbus.DataType.HOLDING_REGISTER, 1, 4, [1, 255, 1234, 0xFFFF]),
        (8, modbus.DataType.INPUT_REGISTER, 1, 1, [0]),
        (9, modbus.DataType.INPUT_REGISTER, 1, 4, [1, 255, 1234, 0xFFFF]),
        (1, modbus.DataType.INPUT_REGISTER, 1, 4, [1, 255, 1234, 0xFFFF]),
        (1, modbus.DataType.QUEUE, 123, None, [1, 255, 1234, 0xFFFF]),
        (1, modbus.DataType.COIL, 1, 1, modbus.Error.INVALID_FUNCTION_CODE),
        (1, modbus.DataType.COIL, 1, 3, modbus.Error.INVALID_DATA_ADDRESS),
        (1, modbus.DataType.COIL, 1, 1, modbus.Error.INVALID_DATA_VALUE),
        (1, modbus.DataType.COIL, 1, 3, modbus.Error.FUNCTION_ERROR)
    ])
async def test_read(create_master_slave, modbus_type, comm_type,
                    device_id, data_type, start_address, quantity, result):
    read_queue = aio.Queue()

    async def on_read(slave, device_id, data_type, start_address, quantity):
        f = asyncio.Future()
        entry = device_id, data_type, start_address, quantity, f
        read_queue.put_nowait(entry)
        return await f

    async with create_master_slave(modbus_type, comm_type,
                                   read_cb=on_read) as (master, slave):

        read_future = asyncio.ensure_future(master.read(
            device_id, data_type, start_address, quantity))

        entry = await read_queue.get()
        assert entry[0] == device_id
        assert entry[1] == data_type
        assert entry[2] == start_address
        assert entry[3] == quantity
        entry[4].set_result(result)

        read_result = await read_future
        assert read_result == result


@pytest.mark.parametrize("modbus_type", list(modbus.ModbusType))
@pytest.mark.parametrize("comm_type", comm_types)
@pytest.mark.parametrize(
    "device_id, data_type, start_address, values, result", [
        (1, modbus.DataType.COIL, 1, [0], None),
        (2, modbus.DataType.COIL, 1, [1], None),
        (3, modbus.DataType.COIL, 3, [1, 0, 1, 0], None),
        (6, modbus.DataType.HOLDING_REGISTER, 1, [0], None),
        (7, modbus.DataType.HOLDING_REGISTER, 1, [1, 255, 1234, 0xFFFF], None),
        (1, modbus.DataType.COIL, 1, [0], modbus.Error.INVALID_FUNCTION_CODE),
        (1, modbus.DataType.COIL, 1, [0], modbus.Error.INVALID_DATA_ADDRESS),
        (1, modbus.DataType.COIL, 1, [0], modbus.Error.INVALID_DATA_VALUE),
        (1, modbus.DataType.COIL, 1, [0], modbus.Error.FUNCTION_ERROR)
    ])
async def test_write(create_master_slave, modbus_type, comm_type,
                     device_id, data_type, start_address, values, result):
    write_queue = aio.Queue()

    async def on_write(slave, device_id, data_type, start_address, values):
        f = asyncio.Future()
        entry = device_id, data_type, start_address, values, f
        write_queue.put_nowait(entry)
        return await f

    async with create_master_slave(modbus_type, comm_type,
                                   write_cb=on_write) as (master, slave):

        write_future = asyncio.ensure_future(master.write(
            device_id, data_type, start_address, values))

        entry = await write_queue.get()
        assert entry[0] == device_id
        assert entry[1] == data_type
        assert entry[2] == start_address
        assert entry[3] == values
        entry[4].set_result(result)

        read_result = await write_future
        assert read_result == result


@pytest.mark.parametrize("modbus_type", list(modbus.ModbusType))
@pytest.mark.parametrize("comm_type", comm_types)
@pytest.mark.parametrize("device_id, address, and_mask, or_mask", [
    (1, 1, 12, 21),
    (3, 5, 42, 24)
])
@pytest.mark.parametrize("result", [None, *modbus.Error])
async def test_write_mask(create_master_slave, modbus_type, comm_type,
                          device_id, address, and_mask, or_mask, result):
    write_mask_queue = aio.Queue()

    async def on_write_mask(slave, device_id, address, and_mask, or_mask):
        f = asyncio.Future()
        entry = device_id, address, and_mask, or_mask, f
        write_mask_queue.put_nowait(entry)
        return await f

    async with create_master_slave(
            modbus_type, comm_type,
            write_mask_cb=on_write_mask) as (master, slave):

        write_mask_future = asyncio.ensure_future(master.write_mask(
            device_id, address, and_mask, or_mask))

        entry = await write_mask_queue.get()
        assert entry[0] == device_id
        assert entry[1] == address
        assert entry[2] == and_mask
        assert entry[3] == or_mask
        entry[4].set_result(result)

        read_result = await write_mask_future
        assert read_result == result
