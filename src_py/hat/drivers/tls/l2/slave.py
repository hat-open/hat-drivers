import asyncio
import logging
import time
import typing

from hat import aio
from hat import util

from hat.drivers.tls import l1
from hat.drivers.tls.l2 import common
from hat.drivers.tls.l2 import encoder


mlog: logging.Logger = logging.getLogger(__name__)

PollClass2Cb: typing.TypeAlias = aio.AsyncCallable[common.Connection,
                                                   util.Bytes | None]


class SlaveLink(aio.Resource):

    def __init__(self,
                 link: l1.Link,
                 *,
                 silent_interval: float = 0.005):
        self._link = link
        self._silent_interval = silent_interval
        self._loop = asyncio.get_running_loop()
        self._conns = {}
        self._data = memoryview(bytes())

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self):
        return self._link.async_group

    async def open_connection(self,
                              addr: common.Address,
                              *,
                              name: str | None = None,
                              poll_class2_cb: PollClass2Cb | None = None,
                              keep_alive_timeout: float = 30,
                              receive_queue_size: int = 1024,
                              send_queue_size: int = 1024
                              ) -> common.Connection:
        if addr >= common.broadcast_address:
            raise ValueError('unsupported address')

        if addr in self._conns:
            raise Exception('connection already exists')

        conn = _SlaveConnection()
        conn._poll_class2_cb = poll_class2_cb
        conn._loop = self._loop
        conn._active_future = self._loop.create_future()
        conn._frame_count_bit = None
        conn._res = None
        conn._keep_alive_event = asyncio.Event()
        conn._send_data_queue = aio.Queue(send_queue_size)
        conn._send_test_queue = aio.Queue(send_queue_size)
        conn._receive_queue = aio.Queue(receive_queue_size)
        conn._async_group = self.async_group.create_subgroup()
        conn._info = common.create_connection_info(name=name,
                                                   addr=addr,
                                                   info=self._link.info)

        conn.async_group.spawn(aio.call_on_cancel, conn._send_data_queue.close)
        conn.async_group.spawn(aio.call_on_cancel, conn._send_test_queue.close)
        conn.async_group.spawn(aio.call_on_cancel, conn._receive_queue.close)

        conn.async_group.spawn(aio.call_on_cancel, self._conns.pop, addr,
                               None)
        self._conns[addr] = conn

        try:
            await conn._active_future

            conn.async_group.spawn(conn._keep_alive_loop, keep_alive_timeout)

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise

        return conn

    async def _receive_loop(self):
        try:
            while True:
                req = await self._receive()
                last_rw_time = time.monotonic()

                if req.address == common.broadcast_address:
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

                    if (req.address == common.broadcast_address or
                            req.function == common.ReqFunction.SEND_DATA_NO_RES):  # NOQA
                        continue

                    last_rw_delta = time.monotonic() - last_rw_time
                    sleep_duration = self._silent_interval - last_rw_delta
                    if sleep_duration > 0:
                        await asyncio.sleep(sleep_duration)

                    await self._send(res)
                    last_rw_time = time.monotonic()

                    if sent_cb:
                        await aio.call(sent_cb)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.warning("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _receive(self):
        while True:
            try:
                size = encoder.get_next_frame_size(self._data)

            except Exception:
                self._data = self._data[1:]
                continue

            if len(self._data) < size:
                data = await self._link.read(size - len(self._data))
                self._data = memoryview(b''.join([self._data, data]))
                continue

            try:
                data, self._data = self._data[:size], self._data[size:]
                frame = encoder.decode_frame(data)

            except Exception as e:
                mlog.error("error decoding message: %s", e, exc_info=e)
                continue

            if isinstance(frame, common.ReqFrame):
                return frame

    async def _send(self, frame):
        data = encoder.encode_frame(frame)

        await self._link.write(data)
        await self._link.drain()


class _SlaveConnection(common.Connection):

    @property
    def async_group(self):
        return self._async_group

    @property
    def info(self):
        return self._info

    async def send(self, data, *, sent_cb=None, with_ack=True, test=False):
        if not data:
            return

        send_queue = self._send_test_queue if test else self._send_data_queue

        try:
            await send_queue.put((data, sent_cb))

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

        if req.function in [common.ReqFunction.RESET_UNIT,
                            common.ReqFunction.RESET_COMMUNICATION]:
            # TODO: clear self._send_data_queue/self._send_test_queue ???
            if not req.frame_count_valid:
                self._frame_count_bit = False

            function = common.ResFunction.ACK
            data = b''

        elif req.function in [common.ReqFunction.SEND_DATA,
                              common.ReqFunction.SEND_TEST,
                              common.ReqFunction.SEND_DATA_NO_RES]:
            if req.data:
                test = req.function == common.ReqFunction.SEND_TEST
                await self._receive_queue.put((req.data, test))

            function = common.ResFunction.ACK
            data = b''

        elif req.function == common.ReqFunction.REQ_STATUS:
            function = common.ResFunction.RES_STATUS
            data = b''

        elif req.function in (common.ReqFunction.REQ_DATA_1,
                              common.ReqFunction.REQ_DATA_2,
                              common.ReqFunction.REQ_DATA_1_OR_2):
            req_data_1 = req.function in (common.ReqFunction.REQ_DATA_1,
                                          common.ReqFunction.REQ_DATA_1_OR_2)
            req_data_2 = req.function in (common.ReqFunction.REQ_DATA_2,
                                          common.ReqFunction.REQ_DATA_1_OR_2)

            if req_data_1 and not self._send_data_queue.empty():
                data, sent_cb = self._send_data_queue.get_nowait()

            elif req_data_2 and self._poll_class2_cb:
                data = await aio.call(self._poll_class2_cb, self)

            else:
                data = None

            function = (common.ResFunction.RES_ACK if data is None else
                        common.ResFunction.RES_DATA)
            if data is None:
                data = b''

        elif req.function == common.ReqFunction.REQ_TEST:
            if not self._send_test_queue.empty():
                function = common.ResFunction.RES_TEST
                data, sent_cb = self._send_test_queue.get_nowait()

            else:
                function = common.ResFunction.RES_ACK
                data = b''

        else:
            function = common.ResFunction.RES_REJECT
            data = b''

        access_demand = not self._send_data_queue.empty()

        if not access_demand and function in (common.ResFunction.ACK,
                                              common.ResFunction.RES_ACK):
            res = common.ShortFrame()

        else:
            res = common.ResFrame(access_demand=access_demand,
                                  data_flow_control=False,
                                  function=function,
                                  address=self._info.addr,
                                  data=data)

        # TODO: remember response only if resend posible
        self._res = res

        return res, sent_cb
