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

RequestCb: typing.TypeAlias = aio.AsyncCallable[['Slave', common.Request],
                                                common.Response | None]
"""Request callback"""


async def create_tcp_server(modbus_type: common.ModbusType,
                            addr: tcp.Address,
                            *,
                            slave_cb: SlaveCb | None = None,
                            request_cb: RequestCb | None = None,
                            **kwargs
                            ) -> tcp.Server:
    """Create TCP server

    Closing server closes all active associated slaves.

    Additional arguments are passed directly to `hat.drivers.tcp.connect`
    (`bind_connections` is set by this coroutine).

    Args:
        modbus_type: modbus type
        addr: local listening host address
        slave_cb: slave callback
        request_cb: request callback

    """

    async def on_connection(conn):
        if not conn.is_open:
            return

        log = _create_logger_adapter(conn.info)

        slave = Slave(link=transport.TcpLink(conn),
                      modbus_type=modbus_type,
                      request_cb=request_cb)

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

    return server


async def create_serial_slave(modbus_type: common.ModbusType,
                              port: str,
                              *,
                              request_cb: RequestCb | None = None,
                              silent_interval: float = 0.005,
                              **kwargs
                              ) -> 'Slave':
    """Create serial slave

    Additional arguments are passed directly to `hat.drivers.serial.create`.

    Args:
        modbus_type: modbus type
        port: port name (see `hat.drivers.serial.create`)
        request_cb: request callback
        silent_interval: silent interval (see `serial.create`)

    """
    endpoint = await serial.create(port,
                                   silent_interval=silent_interval,
                                   **kwargs)

    try:
        return Slave(link=transport.SerialLink(endpoint),
                     modbus_type=modbus_type,
                     request_cb=request_cb)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class Slave(aio.Resource):
    """Modbus slave"""

    def __init__(self,
                 link: transport.Link,
                 modbus_type: common.ModbusType,
                 request_cb: RequestCb | None = None):
        self._modbus_type = modbus_type
        self._request_cb = request_cb
        self._conn = transport.Connection(link)
        self._log = _create_logger_adapter(self._conn.info)

        self.async_group.spawn(self._receive_loop)

        self._log.debug('slave created')

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
                req_pdu = req_adu.pdu

                try:
                    self._log.debug("processing request (device_id %s): %s",
                                    device_id, req_pdu)
                    res_pdu = await self._process_request(device_id, req_pdu)

                except Exception as e:
                    self._log.warning("error processing request: %s", e,
                                      exc_info=e)
                    continue

                if res_pdu is None:
                    self._log.debug("skip sending response")
                    continue

                self._log.debug("sending response: %s", res_pdu)

                if self._modbus_type == common.ModbusType.TCP:
                    res_adu = transport.TcpAdu(
                        transaction_id=req_adu.transaction_id,
                        device_id=req_adu.device_id,
                        pdu=res_pdu)

                elif self._modbus_type == common.ModbusType.RTU:
                    res_adu = transport.RtuAdu(device_id=req_adu.device_id,
                                               pdu=res_pdu)

                elif self._modbus_type == common.ModbusType.ASCII:
                    res_adu = transport.AsciiAdu(device_id=req_adu.device_id,
                                                 pdu=res_pdu)

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

    async def _process_request(self, device_id, req_pdu):
        if self._request_cb is None:
            return

        if isinstance(req_pdu, transport.ReadCoilsReq):
            req = common.ReadReq(device_id=device_id,
                                 data_type=common.DataType.COIL,
                                 start_address=req_pdu.address,
                                 quantity=req_pdu.quantity)

        elif isinstance(req_pdu, transport.ReadDiscreteInputsReq):
            req = common.ReadReq(device_id=device_id,
                                 data_type=common.DataType.DISCRETE_INPUT,
                                 start_address=req_pdu.address,
                                 quantity=req_pdu.quantity)

        elif isinstance(req_pdu, transport.ReadHoldingRegistersReq):
            req = common.ReadReq(device_id=device_id,
                                 data_type=common.DataType.HOLDING_REGISTER,
                                 start_address=req_pdu.address,
                                 quantity=req_pdu.quantity)

        elif isinstance(req_pdu, transport.ReadInputRegistersReq):
            req = common.ReadReq(device_id=device_id,
                                 data_type=common.DataType.INPUT_REGISTER,
                                 start_address=req_pdu.address,
                                 quantity=req_pdu.quantity)

        elif isinstance(req_pdu, transport.WriteSingleCoilReq):
            req = common.WriteReq(device_id=device_id,
                                  data_type=common.DataType.COIL,
                                  start_address=req_pdu.address,
                                  values=[req_pdu.value])

        elif isinstance(req_pdu, transport.WriteSingleRegisterReq):
            req = common.WriteReq(device_id=device_id,
                                  data_type=common.DataType.HOLDING_REGISTER,
                                  start_address=req_pdu.address,
                                  values=[req_pdu.value])

        elif isinstance(req_pdu, transport.WriteMultipleCoilsReq):
            req = common.WriteReq(device_id=device_id,
                                  data_type=common.DataType.COIL,
                                  start_address=req_pdu.address,
                                  values=req_pdu.values)

        elif isinstance(req_pdu, transport.WriteMultipleRegistersReq):
            req = common.WriteReq(device_id=device_id,
                                  data_type=common.DataType.HOLDING_REGISTER,
                                  start_address=req_pdu.address,
                                  values=req_pdu.values)

        elif isinstance(req_pdu, transport.MaskWriteRegisterReq):
            req = common.WriteMaskReq(device_id=device_id,
                                      address=req_pdu.address,
                                      and_mask=req_pdu.and_mask,
                                      or_mask=req_pdu.or_mask)

        elif isinstance(req_pdu, transport.ReadFifoQueueReq):
            req = common.ReadReq(device_id=device_id,
                                 data_type=common.DataType.QUEUE,
                                 start_address=req_pdu.address,
                                 quantity=0)

        else:
            raise TypeError('unsupported request')

        res = await aio.call(self._request_cb, self, req)

        if res is None:
            return

        if isinstance(res, common.Error):
            return transport.ErrorRes(
                fc=transport.get_pdu_function_code(req_pdu),
                error=res)

        if isinstance(req_pdu, transport.ReadCoilsReq):
            return transport.ReadCoilsRes(values=res)

        if isinstance(req_pdu, transport.ReadDiscreteInputsReq):
            return transport.ReadDiscreteInputsRes(values=res)

        if isinstance(req_pdu, transport.ReadHoldingRegistersReq):
            return transport.ReadHoldingRegistersRes(values=res)

        if isinstance(req_pdu, transport.ReadInputRegistersReq):
            return transport.ReadInputRegistersRes(values=res)

        if isinstance(req_pdu, transport.WriteSingleCoilReq):
            return transport.WriteSingleCoilRes(address=req_pdu.address,
                                                value=req_pdu.value)

        if isinstance(req_pdu, transport.WriteSingleRegisterReq):
            return transport.WriteSingleRegisterRes(address=req_pdu.address,
                                                    value=req_pdu.value)

        if isinstance(req_pdu, transport.WriteMultipleCoilsReq):
            return transport.WriteMultipleCoilsRes(
                address=req_pdu.address,
                quantity=len(req_pdu.values))

        if isinstance(req_pdu, transport.WriteMultipleRegistersReq):
            return transport.WriteMultipleRegistersRes(
                address=req_pdu.address,
                quantity=len(req_pdu.values))

        if isinstance(req_pdu, transport.MaskWriteRegisterReq):
            return transport.MaskWriteRegisterRes(address=req_pdu.address,
                                                  and_mask=req_pdu.and_mask,
                                                  or_mask=req_pdu.or_mask)

        if isinstance(req_pdu, transport.ReadFifoQueueReq):
            return transport.ReadFifoQueueRes(values=res)

        raise TypeError('unsupported request')


def _create_logger_adapter(info):
    if isinstance(info, tcp.ConnectionInfo):
        extra = {'meta': {'type': 'ModbusTcpSlave',
                          'name': info.name,
                          'local_addr': {'host': info.local_addr.host,
                                         'port': info.local_addr.port},
                          'remote_addr': {'host': info.remote_addr.host,
                                          'port': info.remote_addr.port}}}

    elif isinstance(info, serial.EndpointInfo):
        extra = {'meta': {'type': 'ModbusSerialSlave',
                          'name': info.name,
                          'port': info.port}}

    else:
        raise TypeError('invalid info type')

    return logging.LoggerAdapter(mlog, extra)
