import asyncio
import logging
import time
import typing

from hat import aio
from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import endpoint
from hat.drivers.iec60870.link.connection import (ConnectionCb,
                                                  Connection)


mlog: logging.Logger = logging.getLogger(__name__)


async def create_slave(port: str,
                       addrs: typing.Iterable[common.Address],
                       connection_cb: typing.Optional[ConnectionCb] = None,
                       baudrate: int = 9600,
                       bytesize: serial.ByteSize = serial.ByteSize.EIGHTBITS,
                       parity: serial.Parity = serial.Parity.NONE,
                       stopbits: serial.StopBits = serial.StopBits.ONE,
                       xonxoff: bool = False,
                       rtscts: bool = False,
                       dsrdtr: bool = False,
                       silent_interval: float = 0.005,
                       address_size: common.AddressSize = common.AddressSize.ONE,  # NOQA
                       keep_alive_timeout: float = 30
                       ) -> 'Slave':
    if address_size == common.AddressSize.ZERO:
        raise ValueError('unsupported address size')

    slave = Slave()
    slave._connection_cb = connection_cb
    slave._silent_interval = silent_interval
    slave._keep_alive_timeout = keep_alive_timeout
    slave._broadcast_address = common.get_broadcast_address(address_size)
    slave._conns = {addr: None for addr in addrs}

    slave._endpoint = await endpoint.create(address_size=address_size,
                                            direction_valid=False,
                                            port=port,
                                            baudrate=baudrate,
                                            bytesize=bytesize,
                                            parity=parity,
                                            stopbits=stopbits,
                                            xonxoff=xonxoff,
                                            rtscts=rtscts,
                                            dsrdtr=dsrdtr)

    slave.async_group.spawn(slave._read_write_loop)

    return slave


class Slave(aio.Resource):

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def _read_write_loop(self):
        future = None

        try:
            while True:
                req = await self._endpoint.receive()
                last_rw_time = time.monotonic()

                if not isinstance(req, common.ReqFrame):
                    continue

                addrs = (list(self._conns.keys())
                         if req.address == self._broadcast_address
                         else [req.address])

                for addr in addrs:
                    conn = await self._get_connection(addr)
                    if not conn or not conn.is_open:
                        continue

                    future, res = conn._process(req)

                    if (req.address == self._broadcast_address or
                            req.function == common.ReqFunction.DATA_NO_RES):
                        continue

                    last_rw_delta = time.monotonic() - last_rw_time
                    sleep_duration = self._silent_interval - last_rw_delta
                    if sleep_duration > 0:
                        await asyncio.sleep(sleep_duration)

                    await self._endpoint.send(res)
                    last_rw_time = time.monotonic()

                    if future and not future.done():
                        future.set_result(None)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.warning("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

            if future and not future.done():
                future.set_exception(ConnectionError())

    async def _get_connection(self, addr):
        if addr not in self._conns:
            return

        conn = self._conns[addr]
        if conn and conn.is_open:
            return conn

        conn = _SlaveConnection(self.async_group.create_subgroup(),
                                addr, self._keep_alive_timeout)
        self._conns[addr] = conn

        if self._connection_cb:
            await aio.call(self._connection_cb, conn)

        return conn


class _SlaveConnection(Connection):

    def __init__(self, async_group, addr, keep_alive_timeout):
        self._async_group = async_group
        self._addr = addr
        self._frame_count_bit = None
        self._res = None
        self._keep_alive_event = asyncio.Event()
        self._send_queue = aio.Queue()
        self._receive_queue = aio.Queue()

        self.async_group.spawn(aio.call_on_cancel, self._on_close)
        self.async_group.spawn(self._keep_alive_loop, keep_alive_timeout)

    @property
    def async_group(self):
        return self._async_group

    async def send(self, data: common.Bytes):
        if not data:
            return

        future = asyncio.Future()
        try:
            self._send_queue.put_nowait((future,  data))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def receive(self) -> common.Bytes:
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    def _on_close(self):
        self._send_queue.close()
        self._receive_queue.close()

        while not self._send_queue.empty():
            future, _ = self._send_queue.get_nowait()
            if future.done():
                continue
            future.set_exception(ConnectionError())

    async def _keep_alive_loop(self, timeout):
        try:
            while True:
                await aio.wait_for(self._keep_alive_event.wait(), timeout)
                self._keep_alive_event.clear()

        except asyncio.TimeoutError:
            mlog.warning('keep alive timeout')

        finally:
            self.close()

    def _process(self, req):
        self._keep_alive_event.set()
        future = None

        if req.frame_count_valid:
            # TODO compare rest of request in case of same fcb
            if req.frame_count_bit == self._frame_count_bit:
                return future, self._res
            self._frame_count_bit = req.frame_count_bit

        if req.function in [common.ReqFunction.RESET_LINK,
                            common.ReqFunction.RESET_PROCESS]:
            # TODO: clear self._send_queue ???
            if not req.frame_count_valid:
                self._frame_count_bit = False
            function = common.ResFunction.ACK
            data = b''

        elif req.function in [common.ReqFunction.DATA,
                              common.ReqFunction.DATA_NO_RES]:
            if req.data:
                self._receive_queue.put_nowait(req.data)
            function = common.ResFunction.ACK
            data = b''

        elif req.function == common.ReqFunction.REQ_ACCESS_DEMAND:
            function = common.ResFunction.ACK
            data = b''

        elif req.function == common.ReqFunction.REQ_STATUS:
            function = common.ResFunction.RES_STATUS
            data = b''

        elif req.function in [common.ReqFunction.REQ_DATA_1,
                              common.ReqFunction.REQ_DATA_2]:
            if self._send_queue.empty():
                function = common.ResFunction.ACK
                data = b''
            else:
                function = common.ResFunction.RES_DATA
                future, data = self._send_queue.get_nowait()

        else:
            function = common.ResFunction.NOT_IMPLEMENTED
            data = b''

        # TODO: remember response only if resend posible
        self._res = common.ResFrame(
            direction=None,
            access_demand=not self._send_queue.empty(),
            data_flow_control=False,
            function=function,
            address=self._addr,
            data=data)

        return future, self._res
