"""Modbus slave"""

import logging
import typing

from hat import aio

from hat.drivers import serial
from hat.drivers import tcp
from hat.drivers.modbus import common
from hat.drivers.modbus import transport


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

SlaveCb: typing.TypeAlias = aio.AsyncCallable[['Slave'], None]
"""Slave callback"""

ReadCb: typing.TypeAlias = aio.AsyncCallable[['Slave',
                                              int,
                                              common.DataType,
                                              int,
                                              int | None
                                              ], list[int] | common.Error]
"""Read callback

Args:
    slave: slave instance
    device_id: device identifier
    data_type: data type
    start_address: staring address
    quantity: number of registers

Returns:
    list of register values or error

"""

WriteCb: typing.TypeAlias = aio.AsyncCallable[['Slave',
                                               int,
                                               common.DataType,
                                               int,
                                               list[int]
                                               ], common.Error | None]
"""Write callback

Args:
    slave: slave instance
    device_id: device identifier
    data_type: data type
    start_address: staring address
    values: register values

Returns:
    `None` on success or error

"""

WriteMaskCb: typing.TypeAlias = aio.AsyncCallable[['Slave',
                                                   int,
                                                   int,
                                                   int,
                                                   int
                                                   ], common.Error | None]
"""Write mask callback

Args:
    slave: slave instance
    device_id: device identifier
    address: address
    and_mask: and mask
    or_mask: or mask

Returns:
    `None` on success or error

"""


async def create_tcp_server(modbus_type: common.ModbusType,
                            addr: tcp.Address,
                            *,
                            slave_cb: SlaveCb | None = None,
                            read_cb: ReadCb | None = None,
                            write_cb: WriteCb | None = None,
                            write_mask_cb: WriteMaskCb | None = None,
                            **kwargs
                            ) -> tcp.Server:
    """Create TCP server

    Closing server closes all active associated slaves.

    Args:
        modbus_type: modbus type
        addr: local listening host address
        slave_cb: slave callback
        read_cb: read callback
        write_cb: write callback
        write_mask_cb: write mask callback
        kwargs: additional arguments used for creating TCP server
            (see `tcp.listen`)

    """

    async def on_connection(conn):
        if not conn.is_open:
            return

        log = tcp.create_logger_adapter(mlog, conn.info)
        log.debug("new incomming tcp connection")

        slave = Slave(link=transport.TcpLink(conn),
                      modbus_type=modbus_type,
                      read_cb=read_cb,
                      write_cb=write_cb,
                      write_mask_cb=write_mask_cb)

        try:
            if slave_cb:
                await aio.call(slave_cb, slave)

            await slave.wait_closing()

        except Exception as e:
            log.error("error in slave callback: %s", e, exc_info=e)

        finally:
            await aio.uncancellable(slave.async_close())

    server = await tcp.listen(on_connection, addr,
                              bind_connections=True,
                              **kwargs)

    log = tcp.create_logger_adapter(mlog, server.info)
    log.debug("tcp server listening")

    return server


async def create_serial_slave(modbus_type: common.ModbusType,
                              port: str,
                              *,
                              read_cb: ReadCb | None = None,
                              write_cb: WriteCb | None = None,
                              write_mask_cb: WriteMaskCb | None = None,
                              silent_interval: float = 0.005,
                              **kwargs
                              ) -> 'Slave':
    """Create serial slave

    Args:
        modbus_type: modbus type
        port: port name (see `serial.create`)
        read_cb: read callback
        write_cb: write callback
        write_mask_cb: write mask callback
        silent_interval: silent interval (see `serial.create`)
        kwargs: additional arguments used for opening serial connection
            (see `serial.create`)

    """
    endpoint = await serial.create(port,
                                   silent_interval=silent_interval,
                                   **kwargs)

    try:
        log = serial.create_logger_adapter(mlog, endpoint.info)
        log.debug("serial endpoint opened")

        return Slave(link=transport.SerialLink(endpoint),
                     modbus_type=modbus_type,
                     read_cb=read_cb,
                     write_cb=write_cb,
                     write_mask_cb=write_mask_cb)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class Slave(aio.Resource):
    """Modbus slave"""

    def __init__(self,
                 link: transport.Link,
                 modbus_type: common.ModbusType,
                 read_cb: ReadCb | None = None,
                 write_cb: WriteCb | None = None,
                 write_mask_cb: WriteMaskCb | None = None):
        self._modbus_type = modbus_type
        self._read_cb = read_cb
        self._write_cb = write_cb
        self._write_mask_cb = write_mask_cb
        self._conn = transport.Connection(link)
        self._log = common.create_logger_adapter(mlog, self._conn.info)

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo | serial.EndpointInfo:
        """Connection or endpoint info"""
        return self._conn.info

    async def _receive_loop(self):
        self._log.debug("starting slave receive loop")
        try:
            while True:
                try:
                    self._log.debug("waiting for request")
                    req_adu = await self._conn.receive(
                        modbus_type=self._modbus_type,
                        direction=transport.Direction.REQUEST)

                except ConnectionError:
                    break

                except Exception as e:
                    self._log.warning("error receiving request: %s", e,
                                      exc_info=e)
                    continue

                device_id = req_adu.device_id
                req = req_adu.pdu

                try:
                    self._log.debug("processing request (device_id %s): %s",
                                    device_id, req)
                    res = await self._process_request(device_id, req)

                except Exception as e:
                    self._log.warning("error processing request: %s", e,
                                      exc_info=e)
                    continue

                if device_id == 0:
                    self._log.debug(
                        "skip sending response (broadcast request): %s", res)
                    continue

                self._log.debug("sending response: %s", res)

                if self._modbus_type == common.ModbusType.TCP:
                    res_adu = transport.TcpAdu(
                        transaction_id=req_adu.transaction_id,
                        device_id=req_adu.device_id,
                        pdu=res)

                elif self._modbus_type == common.ModbusType.RTU:
                    res_adu = transport.RtuAdu(device_id=req_adu.device_id,
                                               pdu=res)

                elif self._modbus_type == common.ModbusType.ASCII:
                    res_adu = transport.AsciiAdu(device_id=req_adu.device_id,
                                                 pdu=res)

                else:
                    raise ValueError("invalid modbus type")

                try:
                    await self._conn.send(res_adu)

                except ConnectionError:
                    break

                except Exception as e:
                    self._log.warning("error sending response: %s", e,
                                      exc_info=e)
                    continue

        except Exception as e:
            self._log.error("receive loop error: %s", e, exc_info=e)

        finally:
            self._log.debug("closing slave receive loop")
            self.close()

    async def _process_request(self, device_id, req):
        if isinstance(req, transport.ReadCoilsReq):
            result = await self._call_read_cb(
                device_id=device_id,
                data_type=common.DataType.COIL,
                start_address=req.address,
                quantity=req.quantity)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.READ_COILS,
                    error=result)

            return transport.ReadCoilsRes(values=result)

        if isinstance(req, transport.ReadDiscreteInputsReq):
            result = await self._call_read_cb(
                device_id=device_id,
                data_type=common.DataType.DISCRETE_INPUT,
                start_address=req.address,
                quantity=req.quantity)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.READ_DISCRETE_INPUTS,
                    error=result)

            return transport.ReadDiscreteInputsRes(values=result)

        if isinstance(req, transport.ReadHoldingRegistersReq):
            result = await self._call_read_cb(
                device_id=device_id,
                data_type=common.DataType.HOLDING_REGISTER,
                start_address=req.address,
                quantity=req.quantity)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.READ_HOLDING_REGISTERS,
                    error=result)

            return transport.ReadHoldingRegistersRes(values=result)

        if isinstance(req, transport.ReadInputRegistersReq):
            result = await self._call_read_cb(
                device_id=device_id,
                data_type=common.DataType.INPUT_REGISTER,
                start_address=req.address,
                quantity=req.quantity)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.READ_INPUT_REGISTERS,
                    error=result)

            return transport.ReadInputRegistersRes(values=result)

        if isinstance(req, transport.WriteSingleCoilReq):
            result = await self._call_write_cb(
                device_id=device_id,
                data_type=common.DataType.COIL,
                start_address=req.address,
                values=[req.value])

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.WRITE_SINGLE_COIL,
                    error=result)

            return transport.WriteSingleCoilRes(address=req.address,
                                                value=req.value)

        if isinstance(req, transport.WriteSingleRegisterReq):
            result = await self._call_write_cb(
                device_id=device_id,
                data_type=common.DataType.HOLDING_REGISTER,
                start_address=req.address,
                values=[req.value])

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.WRITE_SINGLE_REGISTER,
                    error=result)

            return transport.WriteSingleRegisterRes(address=req.address,
                                                    value=req.value)

        if isinstance(req, transport.WriteMultipleCoilsReq):
            result = await self._call_write_cb(
                device_id=device_id,
                data_type=common.DataType.COIL,
                start_address=req.address,
                values=req.values)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.WRITE_MULTIPLE_COILS,
                    error=result)

            return transport.WriteMultipleCoilsRes(address=req.address,
                                                   quantity=len(req.values))

        if isinstance(req, transport.WriteMultipleRegistersReq):
            result = await self._call_write_cb(
                device_id=device_id,
                data_type=common.DataType.HOLDING_REGISTER,
                start_address=req.address,
                values=req.values)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.WRITE_MULTIPLE_REGISTER,
                    error=result)

            return transport.WriteMultipleRegistersRes(
                address=req.address,
                quantity=len(req.values))

        if isinstance(req, transport.MaskWriteRegisterReq):
            result = await self._call_write_mask_cb(
                device_id=device_id,
                address=req.address,
                and_mask=req.and_mask,
                or_mask=req.or_mask)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.MASK_WRITE_REGISTER,
                    error=result)

            return transport.MaskWriteRegisterRes(address=req.address,
                                                  and_mask=req.and_mask,
                                                  or_mask=req.or_mask)

        if isinstance(req, transport.ReadFifoQueueReq):
            result = await self._call_read_cb(
                device_id=device_id,
                data_type=common.DataType.QUEUE,
                start_address=req.address,
                quantity=None)

            if isinstance(result, common.Error):
                return transport.ErrorRes(
                    fc=transport.FunctionCode.READ_FIFO_QUEUE,
                    error=result)

            return transport.ReadFifoQueueRes(values=result)

        return transport.ErrorRes(fc=transport.get_pdu_function_code(req),
                                  error=common.Error.INVALID_FUNCTION_CODE)

    async def _call_read_cb(self, device_id, data_type, start_address,
                            quantity):
        if not self._read_cb:
            self._log.debug("read callback not defined")
            return common.Error.FUNCTION_ERROR

        try:
            return await aio.call(self._read_cb, self, device_id, data_type,
                                  start_address, quantity)

        except Exception as e:
            self._log.warning("error in read callback: %s", e,
                              exc_info=e)
            return common.Error.FUNCTION_ERROR

    async def _call_write_cb(self, device_id, data_type, start_address,
                             values):
        if not self._write_cb:
            self._log.debug("write callback not defined")
            return common.Error.FUNCTION_ERROR

        try:
            return await aio.call(self._write_cb, self, device_id, data_type,
                                  start_address, values)

        except Exception as e:
            self._log.warning("error in write callback: %s", e,
                              exc_info=e)
            return common.Error.FUNCTION_ERROR

    async def _call_write_mask_cb(self, device_id, address, and_mask,
                                  or_mask):
        if not self._write_mask_cb:
            self._log.debug("write mask callback not defined")
            return common.Error.FUNCTION_ERROR

        try:
            return await aio.call(self._write_mask_cb, self, device_id,
                                  address, and_mask, or_mask)

        except Exception as e:
            self._log.warning("error in write mask callback: %s", e,
                              exc_info=e)
            return common.Error.FUNCTION_ERROR
