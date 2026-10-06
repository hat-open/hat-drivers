import asyncio
import collections
import contextlib
import functools
import logging
import time

from hat import aio

from hat.drivers.tls import l1
from hat.drivers.tls.l2 import common
from hat.drivers.tls.l2 import encoder


mlog: logging.Logger = logging.getLogger(__name__)


class MasterLink(aio.Resource):

    def __init__(self,
                 link: l1.Link,
                 *,
                 silent_interval: float = 0.005,
                 send_queue_size: int = 1024):
        self._link = link
        self._silent_interval = silent_interval
        self._loop = asyncio.get_running_loop()
        self._send_queue = aio.Queue(send_queue_size)
        self._res_future = None

        self.async_group.spawn(self._send_loop)
        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self):
        return self._link.async_group

    async def open_connection(self,
                              addr: common.Address,
                              *,
                              name: str | None = None,
                              response_timeout: float = 0.1,
                              send_retry_count: int = 3,
                              poll_data_delay: float | None = 1,
                              poll_test_delay: float | None = None,
                              send_queue_size: int = 1024,
                              receive_queue_size: int = 1024,
                              connect_delay: float = 1,
                              reset_unit: bool = True
                              ) -> common.Connection:
        if addr >= common.broadcast_address:
            raise ValueError('unsupported address')

        conn = _MasterConnection()
        conn._send_retry_count = send_retry_count
        conn._loop = self._loop
        conn._send_queue = aio.Queue(send_queue_size)
        conn._receive_queue = aio.Queue(receive_queue_size)
        conn._access_demand_event = asyncio.Event()
        conn._async_group = self.async_group.create_subgroup()
        conn._info = common.create_connection_info(name=name,
                                                   addr=addr,
                                                   info=self._link.info)

        send = functools.partial(self._send, response_timeout)

        try:
            while True:
                try:
                    req = common.ReqFrame(
                        frame_count_bit=False,
                        frame_count_valid=False,
                        function=common.ReqFunction.REQ_STATUS,
                        address=addr,
                        data=b'')
                    res = await send(req)

                    if res.function != common.ResFunction.RES_STATUS:
                        await asyncio.sleep(connect_delay)
                        continue

                    req = common.ReqFrame(
                        frame_count_bit=False,
                        frame_count_valid=False,
                        function=(common.ReqFunction.RESET_UNIT if reset_unit
                                  else common.ReqFunction.RESET_COMMUNICATION),
                        address=addr,
                        data=b'')
                    res = await send(req)

                    if isinstance(res, common.ShortMsg):
                        data_flow_control = False
                        break

                    elif (isinstance(res, common.ResMsg) and
                            res.function == common.ResFunction.ACK):
                        data_flow_control = res.data_flow_control
                        break

                    else:
                        await asyncio.sleep(connect_delay)

                except asyncio.TimeoutError:
                    await asyncio.sleep(connect_delay)

            conn.async_group.spawn(conn._send_loop, send, data_flow_control)

            if poll_data_delay is not None:
                conn.async_group.spawn(conn._poll_data_loop, poll_data_delay)

            if poll_test_delay is not None:
                conn.async_group.spawn(conn._poll_test_loop, poll_test_delay)

            # TODO spawn status loop if polling is disabled

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise

        return conn

    async def _send(self, response_timeout, req):
        future = self._loop.create_future()
        try:
            await self._send_queue.put((future, response_timeout, req))
            return await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _receive_loop(self):
        data = memoryview(bytes())

        try:
            while True:
                try:
                    size = encoder.get_next_frame_size(data)

                except Exception:
                    data = data[1:]
                    continue

                if len(data) < size:
                    result = await self._link.read(size - len(self._data))
                    data = memoryview(b''.join([data, result]))
                    continue

                try:
                    frame_data, data = data[:size], data[size:]
                    frame = encoder.decode(frame_data)

                except Exception as e:
                    mlog.error("error decoding message: %s", e, exc_info=e)

                # TODO check frame is response

                if self._res_future and not self._res_future.done():
                    self._res_future.set_result(frame)

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _send_loop(self):
        future = None
        last_read_time = None

        try:
            while True:
                future, response_timeout, req = await self._send_queue.get()
                if future.done():
                    continue

                last_read_delta = (time.monotonic() - last_read_time
                                   if last_read_time is not None
                                   else self._silent_interval)
                sleep_duration = self._silent_interval - last_read_delta
                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)

                self._res_future = self._loop.create_future()

                mlog.debug("writing request %s", req.function.name)
                req_bytes = encoder.encode(req)
                await self._link.write(req_bytes)
                await self._link.drain()

                if req.function == common.ReqFunction.SEND_DATA_NO_RES:
                    res = None
                    last_read_time = time.monotonic()

                else:
                    try:
                        res = await aio.wait_for(self._res_future,
                                                 response_timeout)
                        last_read_time = time.monotonic()

                    except asyncio.TimeoutError as e:
                        if not future.done():
                            future.set_exception(e)

                if not future.done():
                    future.set_result(res)

                self._res_future = None

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("send loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())

                if self._send_queue.empty():
                    break

                future, _, __ = self._send_queue.get_nowait()


class _MasterConnection(common.Connection):

    @property
    def async_group(self):
        return self._async_group

    @property
    def info(self):
        return self._info

    async def send(self, data, *, sent_cb=None, with_ack=True, test=False):
        if not data:
            return

        function = (common.ReqFunction.SEND_TEST if test else
                    common.ReqFunction.SEND_DATA if with_ack else
                    common.ReqFunction.SEND_DATA_NO_RES)

        future = self._loop.create_future()
        try:
            await self._send_queue.put((future, function, data))
            await future

            if sent_cb:
                await aio.call(sent_cb)

        except aio.QueueClosedError:
            raise ConnectionError()

    async def receive(self):
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _poll_data_loop(self, delay):
        try:
            while True:
                self._access_demand_event.clear()

                future = self._loop.create_future()
                await self._send_queue.put(
                    (future, common.ReqFunction.REQ_DATA_1_OR_2,  b''))
                await future

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._access_demand_event.wait(), delay)

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            mlog.error("poll data loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _poll_test_loop(self, delay):
        try:
            while True:
                future = self._loop.create_future()
                await self._send_queue.put(
                    (future, common.ReqFunction.REQ_TEST,  b''))
                await future

                await asyncio.sleep(delay)

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            mlog.error("poll test loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _send_loop(self, send, data_flow_control):
        future = None
        frame_count_bit = False
        data_flow_queue = collections.deque()

        try:
            while True:
                if not data_flow_control and data_flow_queue:
                    future, function, data = data_flow_queue.popleft()

                else:
                    future, function, data = await self._send_queue.get()

                if data_flow_control and function in (common.ReqFunction.SEND_DATA,  # NOQA
                                                      common.ReqFunction.SEND_TEST):  # NOQA
                    data_flow_queue.append((future, function, data))
                    continue

                if function == common.ReqFunction.SEND_DATA_NO_RES:
                    req = common.ReqFrame(
                        frame_count_bit=False,
                        frame_count_valid=False,
                        function=function,
                        address=self._info.addr,
                        data=data)

                    await send(req)

                    if not future.done():
                        future.set_result(None)

                    continue

                frame_count_bit = not frame_count_bit
                req = common.ReqFrame(
                    frame_count_bit=frame_count_bit,
                    frame_count_valid=True,
                    function=function,
                    address=self._info.addr,
                    data=data)

                retry_counter = 0
                while True:
                    with contextlib.suppress(asyncio.TimeoutError):
                        res = await send(req)
                        break

                    if retry_counter > self._send_retry_count:
                        raise Exception('send retry count exceeded')

                    retry_counter += 1

                if isinstance(res, common.ResMsg) and res.access_demand:
                    self._access_demand_event.set()

                data_flow_control = (res.data_flow_control
                                     if isinstance(res, common.ResMsg)
                                     else False)

                # TODO
                # if data_flow_control and data:
                #     data_flow_queue.append_left((future, function, data))
                #     continue

                if future.done():
                    continue

                if isinstance(res, common.ShortMsg):
                    future.set_result(None)

                elif isinstance(res, common.ResFrame):
                    if res.function in (common.ResFunction.RES_DATA,
                                        common.ResFunction.RES_TEST):
                        if res.data:
                            test = res.function == common.ResFunction.RES_TEST
                            await self._receive_queue.put((data, test))

                        future.set_result(None)

                    elif res.function == common.ResFunction.RES_ACK:
                        future.set_result(None)

                    else:
                        future.set_exception(
                            Exception(f'received {res.function.name}'))

                else:
                    future.set_exception(Exception('unexpected response'))

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("send loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()
            self._receive_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())

                if self._send_queue.empty():
                    break

                future, _, __ = self._send_queue.get_nowait()

            while data_flow_queue:
                future, _, __ = data_flow_queue.popleft()
                if not future.done():
                    future.set_exception(ConnectionError())
