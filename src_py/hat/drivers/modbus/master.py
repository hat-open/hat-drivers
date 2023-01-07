"""Modbus master"""

import asyncio
import itertools
import logging
import typing

from hat import aio

from hat.drivers import tcp
from hat.drivers.modbus import common
from hat.drivers.modbus import transport


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""

reset_input_buffer_delay: float = 0.5
"""Reset input buffer delay"""


async def create_tcp_master(modbus_type: common.ModbusType,
                            addr: tcp.Address,
                            **kwargs
                            ) -> 'Master':
    """Create TCP master

    Args:
        modbus_type: modbus type
        addr: remote host address
        kwargs: additional arguments used for creating TCP connection
            (see `tcp.connect`)

    """
    conn = await transport.tcp_connect(addr, **kwargs)
    return Master(modbus_type, conn)


async def create_serial_master(modbus_type: common.ModbusType,
                               port: str, *,
                               silent_interval: float = 0.005,
                               **kwargs
                               ) -> 'Master':
    """Create serial master

    Args:
        modbus_type: modbus type
        port: port name (see `serial.create`)
        silent_interval: silent interval (see `serial.create`)
        kwargs: additional arguments used for opening serial connection
            (see `serial.create`)

    """
    conn = await transport.serial_create(port,
                                         silent_interval=silent_interval,
                                         **kwargs)
    return Master(modbus_type, conn)


class Master(aio.Resource):
    """Modbus master"""

    def __init__(self,
                 conn: transport.Connection,
                 modbus_type: common.ModbusType):
        self._conn = conn
        self._modbus_type = modbus_type
        self._send_queue = aio.Queue()

        if modbus_type == common.ModbusType.TCP:
            self._next_transaction_ids = iter(i % 0x10000
                                              for i in itertools.count(1))

        self.async_group.spawn(self._send_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    async def read(self,
                   device_id: int,
                   data_type: common.DataType,
                   start_address: int,
                   quantity: int = 1
                   ) -> typing.Union[typing.List[int], common.Error]:
        """Read data from modbus device

        Argument `quantity` is ignored if `data_type` is `QUEUE`.

        Args:
            device_id: slave device identifier
            data_type: data type
            start_address: starting modbus data address
            quantity: number of data values

        Raises:
            ConnectionError

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
                    ) -> typing.Optional[common.Error]:
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
                         ) -> typing.Optional[common.Error]:
        """Write mask to modbus device HOLDING_REGISTER

        Args:
            device_id: slave device identifier
            address: modbus data address
            and_mask: and mask
            or_mask: or mask

        Raises:
            ConnectionError

        """
        req = transport.MaskWriteRegisterReq(address=address,
                                             and_mask=and_mask,
                                             or_mask=or_mask)

        res = await self._send(device_id, req)

        if isinstance(res, transport.ErrorRes):
            return res.error

        if isinstance(res, transport.MaskWriteRegisterRes):
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
            req_adu = transport.RtuAdu(device_id=device_id,
                                       pdu=req)

        else:
            raise ValueError("unsupported modbus type")

        future = asyncio.Future()
        try:
            self._send_queue.put_nowait((req_adu, future))
            res_adu = await future

        except aio.QueueClosedError:
            raise ConnectionError()

        if isinstance(res_adu, transport.TcpAdu):
            if res_adu.transaction_id != req_adu.transaction_id:
                raise Exception("invalid response transaction id")

        if res_adu.device_id != req_adu.device_id:
            raise Exception("invalid response device id")

        req_fc = transport.get_pdu_function_code(req_adu.pdu)
        res_fc = transport.get_pdu_function_code(res_adu.pdu)
        if req_fc != res_fc:
            raise Exception("invalid response function code")

        return res_adu.pdu

    async def _send_loop(self):
        future = None
        try:
            while True:
                with self.async_group.create_subgroup() as subgroup:
                    subgroup.spawn(self._reset_input_buffer_loop)

                    while not future or future.done():
                        req_adu, future = await self._send_queue.get()

                await self._reset_input_buffer()

                await self._conn.send(req_adu)

                res_adu = await self._conn.receive(
                    modbus_type=self._modbus_type,
                    direction=transport.Direction.RESPONSE)

                if future.done():
                    continue

                future.set_result(res_adu)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("error in send loop: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()

    async def _reset_input_buffer_loop(self):
        try:
            while True:
                await self._reset_input_buffer()
                await asyncio.sleep(reset_input_buffer_delay)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("error in reset input buffer loop: %s", e, exc_info=e)

    async def _reset_input_buffer(self):
        count = await self._reset_input_buffer()
        if not count:
            return
        mlog.debug("discarded %s bytes from input buffer", count)
