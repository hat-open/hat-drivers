import asyncio
import logging
import time
import typing

from hat import aio
from hat import util

from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import endpoint


mlog: logging.Logger = logging.getLogger(__name__)

ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['SlaveConnection'], None]

PollClass2Cb: typing.TypeAlias = aio.AsyncCallable[['SlaveConnection'],
                                                   util.Bytes | None]


async def create_slave(port: str,
                       addrs: typing.Iterable[common.Address],
                       *,
                       connection_cb: ConnectionCb | None = None,
                       poll_class2_cb: PollClass2Cb | None = None,
                       keep_alive_timeout: float = 30,
                       address_size: common.AddressSize = common.AddressSize.ONE,  # NOQA
                       silent_interval: float = 0.005,
                       **kwargs
                       ) -> 'Slave':
    """Create unbalanced slave

    Execution of `connection_cb` blocks slave's read/write loop.

    Additional arguments are passed directly to
    `hat.drivers.iec60870.link.endpoint.create`.

    """
    if address_size == common.AddressSize.ZERO:
        raise ValueError('unsupported address size')

    ep = await endpoint.create(port=port,
                               address_size=address_size,
                               direction_valid=False,
                               **kwargs)

    return Slave(ep, addrs, connection_cb, poll_class2_cb, keep_alive_timeout,
                 address_size, silent_interval)


class Slave(aio.Resource):

    def __init__(self,
                 endpoint: endpoint.Endpoint,
                 addrs: typing.Iterable[common.Address],
                 connection_cb: ConnectionCb,
                 poll_class2_cb: PollClass2Cb,
                 keep_alive_timeout: float,
                 address_size: common.AddressSize,
                 silent_interval: float):
        self._endpoint = endpoint
        self._connection_cb = connection_cb
        self._poll_class2_cb = poll_class2_cb
        self._keep_alive_timeout = keep_alive_timeout
        self._silent_interval = silent_interval
        self._broadcast_address = common.get_broadcast_address(address_size)
        self._conns = {addr: None for addr in addrs}

        self.async_group.spawn(self._read_write_loop)

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def _read_write_loop(self):
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

                    res, sent_cb = await conn._process(req)

                    if (req.address == self._broadcast_address or
                            req.function == common.ReqFunction.DATA_NO_RES):
                        continue

                    last_rw_delta = time.monotonic() - last_rw_time
                    sleep_duration = self._silent_interval - last_rw_delta
                    if sleep_duration > 0:
                        await asyncio.sleep(sleep_duration)

                    await self._endpoint.send(res)
                    last_rw_time = time.monotonic()

                    if sent_cb:
                        await aio.call(sent_cb)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.warning("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _get_connection(self, addr):
        if addr not in self._conns:
            return

        conn = self._conns[addr]
        if conn and conn.is_open:
            return conn

        conn = SlaveConnection(self, addr)
        self._conns[addr] = conn

        if self._connection_cb:
            await aio.call(self._connection_cb, conn)

        return conn


class SlaveConnection(aio.Resource):

    def __init__(self,
                 slave: Slave,
                 addr: common.Address):
        self._addr = addr
        self._loop = asyncio.get_running_loop()
        self._frame_count_bit = None
        self._res = None
        self._keep_alive_event = asyncio.Event()
        self._send_queue = aio.Queue()  # TODO limit queue size
        self._receive_queue = aio.Queue()  # TODO limit queue size
        self._poll_class2_cb = slave._poll_class2_cb
        self._async_group = slave.async_group.create_subgroup()

        self.async_group.spawn(aio.call_on_cancel, self._on_close)
        self.async_group.spawn(self._keep_alive_loop,
                               slave._keep_alive_timeout)

    @property
    def async_group(self):
        return self._async_group

    @property
    def address(self):
        return self._addr

    def send(self,
             data: util.Bytes,
             sent_cb: aio.AsyncCallable[[], None] | None = None):
        if not data:
            return

        try:
            self._send_queue.put_nowait((data, sent_cb))

        except aio.QueueClosedError:
            raise ConnectionError()

    async def receive(self) -> util.Bytes:
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    def _on_close(self):
        self._send_queue.close()
        self._receive_queue.close()

    async def _keep_alive_loop(self, timeout):
        try:
            while True:
                await aio.wait_for(self._keep_alive_event.wait(), timeout)
                self._keep_alive_event.clear()

        except asyncio.TimeoutError:
            mlog.warning('keep alive timeout')

        finally:
            self.close()

    async def _process(self, req):
        self._keep_alive_event.set()
        sent_cb = None

        if req.frame_count_valid:
            # TODO compare rest of request in case of same fcb
            if req.frame_count_bit == self._frame_count_bit:
                return self._res, sent_cb
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
            function = common.ResFunction.RES_NACK
            data = b''

        elif req.function == common.ReqFunction.REQ_STATUS:
            function = common.ResFunction.RES_STATUS
            data = b''

        elif req.function == common.ReqFunction.REQ_DATA_1:
            if self._send_queue.empty():
                function = common.ResFunction.RES_NACK
                data = b''
            else:
                function = common.ResFunction.RES_DATA
                data, sent_cb = self._send_queue.get_nowait()

        elif req.function == common.ReqFunction.REQ_DATA_2:
            if self._poll_class2_cb:
                data = await aio.call(self._poll_class2_cb, self)
            else:
                data = None
            if data is None:
                function = common.ResFunction.RES_NACK
                data = b''
            else:
                function = common.ResFunction.RES_DATA

        else:
            function = common.ResFunction.NOT_IMPLEMENTED
            data = b''

        access_demand = not self._send_queue.empty()

        if not access_demand and function in (common.ResFunction.ACK,
                                              common.ResFunction.RES_NACK):
            res = common.ShortFrame()

        else:
            res = common.ResFrame(direction=None,
                                  access_demand=access_demand,
                                  data_flow_control=False,
                                  function=function,
                                  address=self._addr,
                                  data=data)

        # TODO: remember response only if resend posible
        self._res = res

        return res, sent_cb
