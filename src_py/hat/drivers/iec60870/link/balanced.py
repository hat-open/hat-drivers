import asyncio
import collections
import contextlib
import functools
import logging

from hat import aio

from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import endpoint


mlog: logging.Logger = logging.getLogger(__name__)


async def create_balanced_link(port: str,
                               address_size: common.AddressSize,
                               *,
                               silent_interval: float = 0.005,
                               send_queue_size: int = 1024,
                               **kwargs
                               ) -> 'BalancedLink':
    link = BalancedLink()
    link._address_size = address_size
    link._loop = asyncio.get_running_loop()
    link._conns = {}
    link._res_future = None
    link._send_queue = aio.Queue(send_queue_size)

    link._endpoint = await endpoint.create(port=port,
                                           address_size=address_size,
                                           direction_valid=True,
                                           silent_interval=silent_interval,
                                           **kwargs)

    link._log = common.create_logger_adapter(mlog, False, link._endpoint.info)

    link.async_group.spawn(link._send_loop)
    link.async_group.spawn(link._receive_loop)

    return link


class BalancedLink(aio.Resource):

    @property
    def async_group(self):
        return self._endpoint.async_group

    async def open_connection(self,
                              direction: common.Direction,
                              addr: common.Address,
                              *,
                              name: str | None = None,
                              response_timeout: float = 15,
                              send_retry_count: int = 3,
                              status_delay: float = 5,
                              receive_queue_size: int = 1024,
                              send_queue_size: int = 1024
                              ) -> common.Connection:
        if addr >= (1 << (self._address_size.value * 8)):
            raise ValueError('unsupported address')

        conn_key = direction, addr
        if conn_key in self._conns:
            raise Exception('connection already exists')

        conn = BalancedConnection()
        conn._direction = direction
        conn._send_retry_count = send_retry_count
        conn._loop = self._loop
        conn._send_event = asyncio.Event()
        conn._receive_queue = aio.Queue(receive_queue_size)
        conn._send_queue = aio.Queue(send_queue_size)
        conn._frame_count_bit = None
        conn._res = None
        conn._async_group = self.async_group.create_subgroup()
        conn._info = common.ConnectionInfo(name=name,
                                           port=self._endpoint.info.port,
                                           address=addr)
        conn._log = common.create_connection_logger_adapter(mlog, conn._info)

        conn.async_group.spawn(aio.call_on_cancel, self._conns.pop, conn_key,
                               None)
        self._conns[conn_key] = conn

        send = functools.partial(self._send, response_timeout)

        try:
            while True:
                with contextlib.suppress(asyncio.TimeoutError):
                    # req = common.ReqFrame(
                    #     direction=direction,
                    #     frame_count_bit=False,
                    #     frame_count_valid=False,
                    #     function=common.ReqFunction.REQ_STATUS,
                    #     address=addr,
                    #     data=b'')
                    # res = await self._send(req)

                    # if res.function not in [common.ResFunction.ACK,
                    #                         common.ResFunction.RES_STATUS]:
                    #     continue

                    req = common.ReqFrame(
                        direction=direction,
                        frame_count_bit=False,
                        frame_count_valid=False,
                        function=common.ReqFunction.RESET_LINK,
                        address=addr,
                        data=b'')
                    res = await send(req)

                    if (isinstance(res, common.ShortFrame) or
                            (isinstance(res, common.ResFrame) and
                             res.function == common.ResFunction.ACK)):
                        break

            conn.async_group.spawn(conn._send_loop, send)
            conn.async_group.spawn(conn._status_loop, status_delay)

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

    async def _process(self, req):
        conn_key = _invert_direction(req.direction), req.address
        conn = self._conns.get(conn_key)
        if not conn or not conn.is_open:
            return

        res = await conn._process(req)

        if req.function == common.ReqFunction.DATA_NO_RES:
            return

        await self._endpoint.send(res)

    async def _receive_loop(self):
        try:
            while True:
                msg = await self._endpoint.receive()

                if isinstance(msg, common.ReqFrame):
                    await self._process(msg)

                elif isinstance(msg, (common.ResFrame, common.ShortFrame)):
                    if self._res_future and not self._res_future.done():
                        self._res_future.set_result(msg)

                else:
                    raise TypeError('unsupported frame type')

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _send_loop(self):
        future = None

        try:
            while True:
                future, response_timeout, req = await self._send_queue.get()
                if future.done():
                    continue

                self._res_future = self._loop.create_future()

                self._log.debug("writing request %s", req.function.name)
                await self._endpoint.send(req)
                await self._endpoint.drain()

                if req.function == common.ReqFunction.DATA_NO_RES:
                    res = None

                else:
                    try:
                        res = await aio.wait_for(self._res_future,
                                                 response_timeout)

                    except asyncio.TimeoutError as e:
                        if not future.done():
                            future.set_exception(e)

                if not future.done():
                    future.set_result(res)

                self._res_future = None

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("send loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_exception(ConnectionError())

                if self._send_queue.empty():
                    break

                future, _, __ = self._send_queue.get_nowait()


class BalancedConnection(common.Connection):

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
                    direction=self._direction,
                    frame_count_bit=frame_count_bit,
                    frame_count_valid=True,
                    function=function,
                    address=self._info.address,
                    data=data)

                retry_counter = 0
                while True:
                    self._send_event.set()

                    with contextlib.suppress(asyncio.TimeoutError):
                        res = await send(req)
                        break

                    if retry_counter >= self._send_retry_count:
                        raise Exception('send retry count exceeded')

                    retry_counter += 1

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
                    if res.function in (common.ResFunction.ACK,
                                        common.ResFunction.RES_STATUS):
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

    async def _status_loop(self, delay):
        try:
            while True:
                self._send_event.clear()

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._send_event.wait(), delay)
                    continue

                future = self._loop.create_future()
                await self._send_queue.put(
                    (future, common.ReqFunction.REQ_STATUS, b''))
                await future

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            self._log.error("status loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _process(self, req):
        if req.frame_count_valid:
            # TODO compare rest of request in case of same fcb
            if req.frame_count_bit == self._frame_count_bit:
                return self._res

            self._frame_count_bit = req.frame_count_bit

        if req.function in (common.ReqFunction.RESET_LINK,
                            common.ReqFunction.RESET_PROCESS):
            # TODO: clear self._send_queue ???
            if not req.frame_count_valid:
                self._frame_count_bit = False

            function = common.ResFunction.ACK
            data = b''

        elif req.function == common.ReqFunction.TEST:
            function = common.ResFunction.ACK
            data = b''

        elif req.function in [common.ReqFunction.DATA,
                              common.ReqFunction.DATA_NO_RES]:
            if req.data:
                await self._receive_queue.put(req.data)

            function = common.ResFunction.ACK
            data = b''

        elif req.function == common.ReqFunction.REQ_STATUS:
            function = common.ResFunction.RES_STATUS
            data = b''

        else:
            function = common.ResFunction.NOT_IMPLEMENTED
            data = b''

        if function == common.ResFunction.ACK:
            res = common.ShortFrame()

        else:
            res = common.ResFrame(direction=self._direction,
                                  access_demand=False,
                                  data_flow_control=False,
                                  function=function,
                                  address=self._info.address,
                                  data=data)

        # TODO: remember response only if resend posible
        self._res = res

        return res


def _invert_direction(direction):
    if direction == common.Direction.B_TO_A:
        return common.Direction.A_TO_B

    if direction == common.Direction.A_TO_B:
        return common.Direction.B_TO_A

    raise ValueError('unsupported direction')
