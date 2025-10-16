"""Modbus master"""

import asyncio
import itertools
import logging
import typing

from hat import aio

from hat.drivers import tcp
from hat.drivers import serial
from hat.drivers.modbus import common
from hat.drivers.modbus import transport


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_tcp_master(modbus_type: common.ModbusType,
                            addr: tcp.Address,
                            *,
                            response_timeout: float | None = None,
                            **kwargs
                            ) -> 'Master':
    """Create TCP master

    Args:
        modbus_type: modbus type
        addr: remote host address
        response_timeout: response timeout in seconds
        kwargs: additional arguments used for creating TCP connection
            (see `tcp.connect`)

    """
    conn = await tcp.connect(addr, **kwargs)

    try:
        return Master(link=transport.TcpLink(conn),
                      modbus_type=modbus_type,
                      response_timeout=response_timeout)

    except BaseException:
        await aio.uncancellable(conn.async_close())
        raise


async def create_serial_master(modbus_type: common.ModbusType,
                               port: str,
                               *,
                               silent_interval: float = 0.005,
                               response_timeout: float | None = None,
                               **kwargs
                               ) -> 'Master':
    """Create serial master

    Args:
        modbus_type: modbus type
        port: port name (see `serial.create`)
        silent_interval: silent interval (see `serial.create`)
        response_timeout: response timeout in seconds
        kwargs: additional arguments used for opening serial connection
            (see `serial.create`)

    """
    endpoint = await serial.create(port,
                                   silent_interval=silent_interval,
                                   **kwargs)

    try:
        return Master(link=transport.SerialLink(endpoint),
                      modbus_type=modbus_type,
                      response_timeout=response_timeout)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class Master(aio.Resource):
    """Modbus master"""

    def __init__(self,
                 link: transport.Link,
                 modbus_type: common.ModbusType,
                 response_timeout: float | None):
        self._modbus_type = modbus_type
        self._response_timeout = response_timeout
        self._conn = transport.Connection(link)
        self._send_queue = aio.Queue()
        self._log = _create_logger_adapter(self._conn.info)

        if modbus_type == common.ModbusType.TCP:
            self._next_transaction_ids = iter(i % 0x10000
                                              for i in itertools.count(1))

        self.async_group.spawn(self._send_loop)

        self._log.debug('master created')

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo | serial.EndpointInfo:
        """Connection or endpoint info"""
        return self._conn.info

    async def read(self,
                   device_id: int,
                   data_type: common.DataType,
                   start_address: int,
                   quantity: int = 1
                   ) -> list[int] | common.Error:
        """Read data from modbus device

        Argument `quantity` is ignored if `data_type` is `QUEUE`.

        Args:
            device_id: slave device identifier
            data_type: data type
            start_address: starting modbus data address
            quantity: number of data values

        Raises:
            ConnectionError
            TimeoutError

        """
        if device_id == 0:
            raise ValueError('unsupported device id')

        if data_type == common.DataType.COIL:
            req = transport.ReadCoilsReq(address=start_address,
                                         quantity=quantity)

        elif data_type == common.DataType.DISCRETE_INPUT:
            req = transport.ReadDiscreteInputsReq(address=start_address,
                                                  quantity=quantity)

        elif data_type == common.DataType.HOLDING_REGISTER:
            req = transport.ReadHoldingRegistersReq(address=start_address,
                                                    quantity=quantity)

        elif data_type == common.DataType.INPUT_REGISTER:
            req = transport.ReadInputRegistersReq(address=start_address,
                                                  quantity=quantity)

        elif data_type == common.DataType.QUEUE:
            req = transport.ReadFifoQueueReq(address=start_address)

        else:
            raise ValueError('unsupported data type')

        res = await self._send(device_id, req)

        if isinstance(res, transport.ErrorRes):
            return res.error

        if isinstance(res, (transport.ReadCoilsRes,
                            transport.ReadDiscreteInputsRes,
                            transport.ReadHoldingRegistersRes,
                            transport.ReadInputRegistersRes)):
            return res.values[:quantity]

        if isinstance(res, transport.ReadFifoQueueRes):
            return res.values

        raise ValueError("unsupported response pdu")

    async def write(self,
                    device_id: int,
                    data_type: common.DataType,
                    start_address: int,
                    values: typing.List[int]
                    ) -> common.Error | None:
        """Write data to modbus device

        Data types `DISCRETE_INPUT`, `INPUT_REGISTER` and `QUEUE` are not
        supported.

        Args:
            device_id: slave device identifier
            data_type: data type
            start_address: starting modbus data address
            values: values

        Raises:
            ConnectionError
            TimeoutError

        """
        if data_type == common.DataType.COIL:
            if len(values) == 1:
                req = transport.WriteSingleCoilReq(address=start_address,
                                                   value=values[0])

            else:
                req = transport.WriteMultipleCoilsReq(address=start_address,
                                                      values=values)

        elif data_type == common.DataType.HOLDING_REGISTER:
            if len(values) == 1:
                req = transport.WriteSingleRegisterReq(address=start_address,
                                                       value=values[0])

            else:
                req = transport.WriteMultipleRegistersReq(
                    address=start_address,
                    values=values)

        else:
            raise ValueError('unsupported data type')

        res = await self._send(device_id, req)

        if isinstance(res, transport.ErrorRes):
            return res.error

        if not isinstance(res, (transport.WriteSingleCoilRes,
                                transport.WriteMultipleCoilsRes,
                                transport.WriteSingleRegisterRes,
                                transport.WriteMultipleRegistersRes)):
            raise ValueError("unsupported response pdu")

        if (res.address != start_address):
            raise Exception("invalid response pdu address")

        if isinstance(res, (transport.WriteSingleCoilRes,
                            transport.WriteSingleRegisterRes)):
            if (res.value != values[0]):
                raise Exception("invalid response pdu value")

        if isinstance(res, (transport.WriteMultipleCoilsRes,
                            transport.WriteMultipleRegistersRes)):
            if (res.quantity != len(values)):
                raise Exception("invalid response pdu quantity")

    async def write_mask(self,
                         device_id: int,
                         address: int,
                         and_mask: int,
                         or_mask: int
                         ) -> common.Error | None:
        """Write mask to modbus device HOLDING_REGISTER

        Args:
            device_id: slave device identifier
            address: modbus data address
            and_mask: and mask
            or_mask: or mask

        Raises:
            ConnectionError
            TimeoutError

        """
        req = transport.MaskWriteRegisterReq(address=address,
                                             and_mask=and_mask,
                                             or_mask=or_mask)

        res = await self._send(device_id, req)

        if isinstance(res, transport.ErrorRes):
            return res.error

        if not isinstance(res, transport.MaskWriteRegisterRes):
            raise ValueError("unsupported response pdu")

        if (res.address != address):
            raise Exception("invalid response pdu address")

        if (res.and_mask != and_mask):
            raise Exception("invalid response pdu and mask")

        if (res.or_mask != or_mask):
            raise Exception("invalid response pdu or mask")

    async def _send(self, device_id, req):
        if self._modbus_type == common.ModbusType.TCP:
            req_adu = transport.TcpAdu(
                transaction_id=next(self._next_transaction_ids),
                device_id=device_id,
                pdu=req)

        elif self._modbus_type == common.ModbusType.RTU:
            req_adu = transport.RtuAdu(device_id=device_id,
                                       pdu=req)

        elif self._modbus_type == common.ModbusType.ASCII:
            req_adu = transport.AsciiAdu(device_id=device_id,
                                         pdu=req)

        else:
            raise ValueError("unsupported modbus type")

        future = asyncio.Future()
        try:
            self._send_queue.put_nowait((req_adu, future))
            res_adu = await future

        except aio.QueueClosedError:
            raise ConnectionError()

        return res_adu.pdu

    async def _receive(self, req_adu):
        while True:
            res_adu = await self._conn.receive(self._modbus_type,
                                               transport.Direction.RESPONSE)

            if isinstance(res_adu, transport.TcpAdu):
                if res_adu.transaction_id != req_adu.transaction_id:
                    self._log.warning("discarding response adu: "
                                      "invalid response transaction id")
                    continue

            if res_adu.device_id != req_adu.device_id:
                self._log.warning("discarding response adu: "
                                  "invalid response device id")
                continue

            req_fc = transport.get_pdu_function_code(req_adu.pdu)
            res_fc = transport.get_pdu_function_code(res_adu.pdu)
            if req_fc != res_fc:
                self._log.warning("discarding response adu: "
                                  "invalid response function code")
                continue

            return res_adu

    async def _send_loop(self):
        self._log.debug("starting master send loop")
        future = None
        try:
            while self.is_open:
                # req_adu, future = await self._send_queue.get()

                async with self.async_group.create_subgroup() as subgroup:
                    subgroup.spawn(self._clear_input_buffer_loop)
                    self._log.debug("started discarding incomming data")

                    while not future or future.done():
                        req_adu, future = await self._send_queue.get()

                await self._clear_input_buffer()
                self._log.debug("stopped discarding incomming data")

                await self._conn.send(req_adu)
                await self._conn.drain()

                async with self.async_group.create_subgroup(
                        log_exceptions=False) as subgroup:
                    receive_task = subgroup.spawn(self._receive, req_adu)

                    await asyncio.wait([receive_task, future],
                                       timeout=self._response_timeout,
                                       return_when=asyncio.FIRST_COMPLETED)

                    if future.done():
                        continue

                    if receive_task.done():
                        future.set_result(receive_task.result())

                    else:
                        future.set_exception(TimeoutError())

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("error in send loop: %s", e, exc_info=e)

        finally:
            self._log.debug("stopping master send loop")
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()

    async def _clear_input_buffer_loop(self):
        try:
            while True:
                await self._clear_input_buffer()

                await self._conn.read_byte()
                self._log.debug("discarded 1 byte from input buffer")

        except ConnectionError:
            self.close()

        except Exception as e:
            self._log.error("error in reset input buffer loop: %s", e,
                            exc_info=e)
            self.close()

    async def _clear_input_buffer(self):
        count = await self._conn.clear_input_buffer()
        if not count:
            return
        self._log.debug("discarded %s bytes from input buffer", count)


def _create_logger_adapter(info):
    if isinstance(info, tcp.ConnectionInfo):
        extra = {'meta': {'type': 'ModbusTcpMaster',
                          'name': info.name,
                          'local_addr': {'host': info.local_addr.host,
                                         'port': info.local_addr.port},
                          'remote_addr': {'host': info.remote_addr.host,
                                          'port': info.remote_addr.port}}}

    elif isinstance(info, serial.EndpointInfo):
        extra = {'meta': {'type': 'ModbusSerialMaster',
                          'name': info.name,
                          'port': info.port}}

    else:
        raise TypeError('invalid info type')

    return logging.LoggerAdapter(mlog, extra)
