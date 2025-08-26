import asyncio
import logging
import time
import typing

from hat import aio
from hat import util

from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import endpoint


mlog: logging.Logger = logging.getLogger(__name__)

PollClass2Cb: typing.TypeAlias = aio.AsyncCallable[common.Connection,
                                                   util.Bytes | None]


async def create_slave_link(port: str,
                            address_size: common.AddressSize,
                            *,
                            silent_interval: float = 0.005,
                            **kwargs
                            ) -> 'SlaveLink':
    """Create unbalanced slave link

    Additional arguments are passed directly to
    `hat.drivers.iec60870.link.endpoint.create`.

    """
    if address_size == common.AddressSize.ZERO:
        raise ValueError('unsupported address size')

    link = SlaveLink()
    link._silent_interval = silent_interval
    link._loop = asyncio.get_running_loop()
    link._conns = {}
    link._broadcast_address = common.get_broadcast_address(address_size)

    link._endpoint = await endpoint.create(port=port,
                                           address_size=address_size,
                                           direction_valid=False,
                                           **kwargs)

    link.async_group.spawn(link._receive_loop)

    return link


class SlaveLink(aio.Resource):

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def open_connection(self,
                              addr: common.Address,
                              *,
                              poll_class2_cb: PollClass2Cb | None = None,
                              keep_alive_timeout: float = 30,
                              receive_queue_size: int = 1024,
                              send_queue_size: int = 1024
                              ) -> common.Connection:
        if addr >= self._broadcast_address:
            raise ValueError('unsupported address')

        if addr in self._conns:
            raise Exception('connection already exists')

        conn = _SlaveConnection()
        conn._addr = addr
        conn._poll_class2_cb = poll_class2_cb
        conn._loop = self._loop
        conn._active_future = self._loop.create_future()
        conn._frame_count_bit = None
        conn._res = None
        conn._keep_alive_event = asyncio.Event()
        conn._send_queue = aio.Queue(send_queue_size)
        conn._receive_queue = aio.Queue(receive_queue_size)
        conn._async_group = self.async_group.create_subgroup()

        conn.async_group.spawn(aio.call_on_cancel, conn._send_queue.close)
        conn.async_group.spawn(aio.call_on_cancel, conn._receive_queue.close)

        conn.async_group.spawn(aio.call_on_cancel, self._conns.pop, addr,
                               None)
        self._conns[addr] = conn

        conn.async_group.spawn(self._keep_alive_loop, keep_alive_timeout)

        try:
            await conn._active_future

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise

        return conn

    async def _receive_loop(self):
        try:
            while True:
                req = await self._endpoint.receive()
                last_rw_time = time.monotonic()

                if not isinstance(req, common.ReqFrame):
                    continue

                if req.address == self._broadcast_address:
                    # TODO maybe filter conns that have active_future set
                    conns = list(self._conns.values())

                elif req.address in self._conns:
                    conns = [self._conns[req.address]]

                else:
                    continue

                for conn in conns:
                    if not conn.is_open:
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


class _SlaveConnection(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    @property
    def address(self):
        return self._addr

    def send(self, data, sent_cb=None):
        if not data:
            return

        try:
            await self._send_queue.put((data, sent_cb))

        except aio.QueueClosedError:
            raise ConnectionError()

    async def receive(self):
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

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

        if not self._active_future.done():
            self._active_future.set_result(None)

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
                await self._receive_queue.put(req.data)

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
