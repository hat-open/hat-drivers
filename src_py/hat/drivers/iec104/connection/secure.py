# TODO WIP

import asyncio
import logging
import typing

from hat import aio
from hat import util

from hat.drivers.iec104 import common
from hat.drivers.iec104 import encoder
from hat.drivers.iec60870 import apci


mlog: logging.Logger = logging.getLogger(__name__)


default_critical_functions = {common.Function.COMMAND,
                              common.Function.TEST,
                              common.Function.RESET,
                              common.Function.PARAMETER,
                              common.Function.PARAMETER_ACTIVATION}


class SecureConnection(common.Connection):

    def __init__(self,
                 conn: apci.Connection,
                 is_master: bool,
                 update_key: util.Bytes,
                 critical_functions: typing.Set[common.Function] = default_critical_functions):  # NOQA
        self._conn = conn
        self._is_master = is_master
        self._encoder = encoder.Encoder()
        self._send_queue = aio.Queue()
        self._receive_queue = aio.Queue()

        self.async_group.spawn(self._send_loop)
        self.async_group.spawn(self._receive_loop)

    @property
    def conn(self) -> apci.Connection:
        return self._conn

    async def send(self,
                   msgs: typing.List[common.Msg],
                   wait_ack: bool = False):
        try:
            for i, msg in enumerate(msgs):
                entry = (_SendQueueEntry(msg, asyncio.Future(), True)
                         if i == len(msgs) - 1
                         else _SendQueueEntry(msg, None, False))

                self._send_queue.put_nowait(entry)

                if entry.future:
                    await entry.future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def drain(self, wait_ack: bool = False):
        try:
            entry = _SendQueueEntry(None, asyncio.Future(), wait_ack)
            self._send_queue.put_nowait(entry)
            await entry.future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def receive(self) -> typing.List[common.Msg]:
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _send_loop(self):
        entry = None

        try:
            while True:
                pass

        except ConnectionError:
            pass

        except Exception as e:
            mlog.warning('send loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if entry and entry.future and not entry.future.done():
                    entry.future.set_exception(ConnectionError())
                if self._send_queue.empty():
                    break
                entry = self._send_queue.get_nowait()

    async def _receive_loop(self):
        try:
            while True:
                pass

        except ConnectionError:
            pass

        except Exception as e:
            mlog.warning('receive loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._receive_queue.close()


class _SendQueueEntry(typing.NamedTuple):
    msg: typing.Optional[common.Msg]
    future: typing.Optional[asyncio.Future]
    wait_ack: bool
