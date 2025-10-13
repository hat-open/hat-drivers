import asyncio
import collections
import contextlib
import functools
import logging
import time

from hat import aio

from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import endpoint


mlog: logging.Logger = logging.getLogger(__name__)


async def create_master_link(port: str,
                             address_size: common.AddressSize,
                             *,
                             silent_interval: float = 0.005,
                             send_queue_size: int = 1024,
                             **kwargs
                             ) -> 'MasterLink':
    """Create unbalanced master link

    Additional arguments are passed directly to
    `hat.drivers.iec60870.link.endpoint.create`.

    """
    if address_size == common.AddressSize.ZERO:
        raise ValueError('unsupported address size')

    link = MasterLink()
    link._silent_interval = silent_interval
    link._loop = asyncio.get_running_loop()
    link._send_queue = aio.Queue(send_queue_size)
    link._res_future = None
    link._broadcast_address = common.get_broadcast_address(address_size)

    link._endpoint = await endpoint.create(port=port,
                                           address_size=address_size,
                                           direction_valid=False,
                                           **kwargs)

    link._log = serial.create_logger_adapter(mlog, link._endpoint.info)

    link.async_group.spawn(link._send_loop)
    link.async_group.spawn(link._receive_loop)

    return link


class MasterLink(aio.Resource):

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def open_connection(self,
                              addr: common.Address,
                              *,
                              name: str | None = None,
                              response_timeout: float = 15,
                              send_retry_count: int = 3,
                              poll_class1_delay: float | None = 1,
                              poll_class2_delay: float | None = None,
                              send_queue_size: int = 1024,
                              receive_queue_size: int = 1024,
                              ) -> common.Connection:
        if addr >= self._broadcast_address:
            raise ValueError('unsupported address')

        conn = MasterConnection()
        conn._send_retry_count = send_retry_count
        conn._loop = self._loop
        conn._send_queue = aio.Queue(send_queue_size)
        conn._receive_queue = aio.Queue(receive_queue_size)
        conn._access_demand_event = asyncio.Event()
        conn._async_group = self.async_group.create_subgroup()
        conn._info = common.ConnectionInfo(name=name,
                                           port=self._endpoint.info.port,
                                           address=addr)
        conn._log = common.create_logger_adapter(mlog, conn._info)

        send = functools.partial(self._send, response_timeout)

        try:
            while True:
                with contextlib.suppress(asyncio.TimeoutError):
                    # req = common.ReqFrame(
                    #     direction=None,
                    #     frame_count_bit=False,
                    #     frame_count_valid=False,
                    #     function=common.ReqFunction.REQ_STATUS,
                    #     address=addr,
                    #     data=b'')
                    # res = await send(req)

                    # if res.function not in [common.ResFunction.ACK,
                    #                         common.ResFunction.RES_STATUS]:
                    #     continue

                    req = common.ReqFrame(
                        direction=None,
                        frame_count_bit=False,
                        frame_count_valid=False,
                        function=common.ReqFunction.RESET_LINK,
                        address=addr,
                        data=b'')
                    res = await send(req)

                    if (isinstance(res, common.ShortFrame) or
                            (isinstance(res, common.ResFrame) and
                             res.function == common.ResFunction.ACK)):
                        # TODO maybe delay?
                        break

            conn.async_group.spawn(conn._send_loop, send)

            if poll_class1_delay is not None:
                conn.async_group.spawn(conn._poll_loop_class1,
                                       poll_class1_delay)

            if poll_class2_delay is not None:
                conn.async_group.spawn(conn._poll_loop_class2,
                                       poll_class2_delay)

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
        try:
            while True:
                msg = await self._endpoint.receive()

                # TODO check msg is response

                if self._res_future and not self._res_future.done():
                    self._res_future.set_result(msg)

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("read loop error: %s", e, exc_info=e)

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

                self._log.debug("writing request %s", req.function.name)
                await self._endpoint.send(req)
                await self._endpoint.drain()

                if (req.address == self._broadcast_address or
                        req.function == common.ReqFunction.DATA_NO_RES):
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
            self._log.error("write loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())

                if self._send_queue.empty():
                    break

                future, _, __ = self._send_queue.get_nowait()


class MasterConnection(common.Connection):

    @property
    def async_group(self):
        return self._async_group

    @property
    def info(self):
        return self._info

    async def send(self, data, sent_cb=None):
        if not data:
            return

        future = self._loop.create_future()
        try:
            await self._send_queue.put(
                (future, common.ReqFunction.DATA, data))
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

    async def _poll_loop_class1(self, delay):
        try:
            while True:
                self._access_demand_event.clear()

                future = self._loop.create_future()
                await self._send_queue.put(
                    (future, common.ReqFunction.REQ_DATA_1,  b''))
                await future

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._access_demand_event.wait(), delay)

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            self._log.error("poll loop class 1 error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _poll_loop_class2(self, delay):
        try:
            while True:
                future = self._loop.create_future()
                await self._send_queue.put(
                    (future, common.ReqFunction.REQ_DATA_2,  b''))
                await future

                await asyncio.sleep(delay)

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            self._log.error("poll loop class 2 error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _send_loop(self, send):
        future = None
        frame_count_bit = False
        data_flow_control = False
        data_flow_queue = collections.deque()

        try:
            while True:
                if not data_flow_control and data_flow_queue:
                    future, function, data = data_flow_queue.popleft()

                else:
                    future, function, data = await self._send_queue.get()

                if data_flow_control and function == common.ReqFunction.DATA:
                    data_flow_queue.append((future, function, data))
                    continue

                frame_count_bit = not frame_count_bit
                req = common.ReqFrame(
                    direction=None,
                    frame_count_bit=frame_count_bit,
                    frame_count_valid=True,
                    function=function,
                    address=self._info.address,
                    data=data)

                retry_counter = 0
                while True:
                    with contextlib.suppress(asyncio.TimeoutError):
                        res = await send(req)
                        break

                    if retry_counter >= self._send_retry_count:
                        raise Exception('send retry count exceeded')

                    retry_counter += 1

                if isinstance(res, common.ResFrame) and res.access_demand:
                    self._access_demand_event.set()

                data_flow_control = (res.data_flow_control
                                     if isinstance(res, common.ResFrame)
                                     else False)

                # TODO
                # if data_flow_control and data:
                #     data_flow_queue.append((future, data))
                #     continue

                if future.done():
                    continue

                if isinstance(res, common.ShortFrame):
                    future.set_result(None)

                elif isinstance(res, common.ResFrame):
                    if res.function == common.ResFunction.RES_DATA:
                        if res.data:
                            self._receive_queue.put_nowait(res.data)

                        future.set_result(None)

                    elif res.function in (common.ResFunction.ACK,
                                          common.ResFunction.RES_NACK):
                        future.set_result(None)

                    else:
                        future.set_exception(
                            Exception(f'received {res.function.name}'))

                else:
                    future.set_exception(Exception('unexpected response'))

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("send loop error: %s", e, exc_info=e)

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
