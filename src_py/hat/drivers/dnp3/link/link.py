import asyncio
import logging
import typing

from hat import aio
from hat import util

from hat.drivers.dnp3.endpoint import Endpoint
from hat.drivers.dnp3.link import common
from hat.drivers.dnp3.link import encoder


mlog: logging.Logger = logging.getLogger(__name__)


async def create_link(endpoint: Endpoint,
                      local_addr: common.Address,
                      remote_addr: common.Address,
                      direction: common.Direction,
                      response_timeout: float,
                      retry_count: int,
                      *,
                      send_queue_size: int = 1024,
                      receive_queue_size: int = 1024
                      ) -> 'Link':
    link = Link()
    link._endpoint = endpoint
    link._local_addr = local_addr
    link._remote_addr = remote_addr
    link._direction = direction
    link._response_timeout = response_timeout
    link._retry_count = retry_count
    link._loop = asyncio.get_running_loop()
    link._primary_next_fcb = False
    link._secondary_expected_fcb = None
    link._send_queue = aio.Queue(send_queue_size)
    link._receive_queue = aio.Queue(receive_queue_size)

    try:
        link.async_group.spawn(link._send_loop)
        link.async_group.spawn(link._receive_loop)

        await link._send_req(
            function_code=common.PrimaryFunctionCode.RESET_LINK_STATES,
            destination=remote_addr,
            data=b'',
            retry_count=None,
            with_res=True)

    except BaseException:
        await aio.uncancellable(link.async_close())
        raise

    return link


class Link(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    async def send(self,
                   data: util.Bytes,
                   *,
                   confirmed: bool = False,
                   broadcast: bool = False):
        if confirmed and broadcast:
            raise Exception('confirmed and broadcast not valid')

        function_code = (
            common.PrimaryFunctionCode.CONFIRMED_USER_DATA if confirmed
            else common.PrimaryFunctionCode.UNCONFIRMED_USER_DATA)

        # TODO diferent broadcast address
        destination = 0xffff if broadcast else self._remote_addr

        await self._send_req(
            function_code=function_code,
            destination=destination,
            data=data,
            retry_count=self._retry_count,
            with_res=confirmed)

    async def receive(self) -> util.Bytes:
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _send_loop(self):
        try:
            while True:
                pass

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error('receive loop error: %s', e, exc_info=e)

        finally:
            self.close()

            self._send_queue.close()

    async def _receive_loop(self):
        try:
            while True:
                frame_bytes = b''

                while True:
                    next_frame_size = encoder.get_next_frame_size(frame_bytes)
                    if len(frame_bytes) >= next_frame_size:
                        break

                    data = await self._endpoint.read(
                        next_frame_size - len(frame_bytes))

                    buffer = bytearray(len(frame_bytes) + len(data))
                    buffer[:len(frame_bytes)] = frame_bytes
                    buffer[len(frame_bytes):] = data

                    frame_bytes = memoryview(buffer)

                frame = encoder.decode_frame(frame_bytes)

                if frame.direction == self._direction:
                    continue

                if 0xfffd <= frame.destination <= 0xffff:
                    if frame.function_code == common.PrimaryFunctionCode:
                        raise Exception('invalid function code for broadcast '
                                        'address')

                elif frame.destination not in (self._local_addr, 0xfffc):
                    continue

                if isinstance(frame, common.PrimaryFrame):
                    await self._process_primary_frame(frame)

                elif isinstance(frame, common.SecondaryFrame):
                    await self._process_secondary_frame(frame)

                else:
                    raise TypeError('unsupported frame type')

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error('receive loop error: %s', e, exc_info=e)

        finally:
            self.close()

            self._receive_queue.close()

    async def _process_primary_frame(self, frame):
        if frame.function_code in common.frame_count_valid_function_codes:
            pass

        if frame.function_code == common.PrimaryFunctionCode.RESET_LINK_STATES:
            pass

        elif frame.function_code == common.PrimaryFunctionCode.TEST_LINK_STATES:  # NOQA
            pass

        elif frame.function_code == common.PrimaryFunctionCode.CONFIRMED_USER_DATA:  # NOQA
            pass

        elif frame.function_code == common.PrimaryFunctionCode.UNCONFIRMED_USER_DATA:  # NOQA
            pass

        elif frame.function_code == common.PrimaryFunctionCode.REQUEST_LINK_STATUS:  # NOQA
            pass

        else:
            raise ValueError('unsupported function code')

    async def _process_secondary_frame(self, frame):
        if frame.function_code == common.SecondaryFunctionCode.ACK:
            pass

        elif frame.function_code == common.SecondaryFunctionCode.NACK:
            pass

        elif frame.function_code == common.SecondaryFunctionCode.LINK_STATUS:
            pass

        elif frame.function_code == common.SecondaryFunctionCode.NOT_SUPPORTED:
            pass

        else:
            raise ValueError('unsupported function code')

    async def _send_req(self, function_code, destination, data, retry_count,
                        with_res):
        future = self._loop.create_future() if with_res else None

        try:
            await self._send_queue.put(
                _SendQueueEntry(future=future,
                                function_code=function_code,
                                destination=destination,
                                data=data,
                                retry_count=retry_count))

        except aio.QueueClosedError:
            return ConnectionError()

        if future:
            await future

    async def _send_frame(self, frame):
        frame_bytes = encoder.encode_frame(frame)
        await self._endpoint.write(frame_bytes)


class _SendQueueEntry(typing.NamedTuple):
    future: asyncio.Future | None
    function_code: common.PrimaryFunctionCode
    destination: common.Address
    data: util.Bytes
    retry_count: int | None
