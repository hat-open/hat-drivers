import asyncio
import collections
import itertools
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers import tpkt
from hat.drivers.cotp import common
from hat.drivers.cotp import encoder


mlog: logging.Logger = logging.getLogger(__name__)

_next_srcs = ((i % 0xFFFF) + 1 for i in itertools.count(0))


class ConnectionInfo(typing.NamedTuple):
    local_addr: tcp.Address
    local_tsel: int | None
    remote_addr: tcp.Address
    remote_tsel: int | None


ConnectionCb = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


async def connect(addr: tcp.Address,
                  *,
                  local_tsel: int | None = None,
                  remote_tsel: int | None = None,
                  cotp_receive_queue_size: int = 1024,
                  cotp_send_queue_size: int = 1024,
                  **kwargs
                  ) -> 'Connection':
    """Create new COTP connection

    Additional arguments are passed directly to `hat.drivers.tpkt.connect`.

    """
    conn = await tpkt.connect(addr, **kwargs)

    try:
        cr_tpdu = common.CR(src=next(_next_srcs),
                            cls=0,
                            calling_tsel=local_tsel,
                            called_tsel=remote_tsel,
                            max_tpdu=2048,
                            pref_max_tpdu=None)
        cr_tpdu_bytes = encoder.encode(cr_tpdu)
        await conn.send(cr_tpdu_bytes)

        cc_tpdu_bytes = await conn.receive()
        cc_tpdu = encoder.decode(memoryview(cc_tpdu_bytes))
        _validate_connect_response(cr_tpdu, cc_tpdu)

        max_tpdu = _calculate_max_tpdu(cr_tpdu, cc_tpdu)
        calling_tsel, called_tsel = _get_tsels(cr_tpdu, cc_tpdu)

        return Connection(conn, max_tpdu, calling_tsel, called_tsel,
                          cotp_receive_queue_size, cotp_send_queue_size)

    except BaseException:
        await aio.uncancellable(conn.async_close())
        raise


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 102),
                 *,
                 cotp_receive_queue_size: int = 1024,
                 cotp_send_queue_size: int = 1024,
                 **kwargs
                 ) -> 'Server':
    """Create new COTP listening server

    Additional arguments are passed directly to `hat.drivers.tpkt.listen`.

    """
    server = Server()
    server._connection_cb = connection_cb
    server._receive_queue_size = cotp_receive_queue_size
    server._send_queue_size = cotp_send_queue_size

    server._srv = await tpkt.listen(server._on_connection, addr, **kwargs)

    return server


class Server(aio.Resource):
    """COTP listening server

    For creation of new instance see `listen` coroutine.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._srv.async_group

    @property
    def addresses(self) -> list[tcp.Address]:
        """Listening addresses"""
        return self._srv.addresses

    async def _on_connection(self, tpkt_conn):
        try:
            try:
                cr_tpdu_bytes = await tpkt_conn.receive()
                cr_tpdu = encoder.decode(memoryview(cr_tpdu_bytes))
                _validate_connect_request(cr_tpdu)

                cc_tpdu = common.CC(dst=cr_tpdu.src,
                                    src=next(_next_srcs),
                                    cls=0,
                                    calling_tsel=cr_tpdu.calling_tsel,
                                    called_tsel=cr_tpdu.called_tsel,
                                    max_tpdu=_calculate_cc_max_tpdu(cr_tpdu),
                                    pref_max_tpdu=None)
                cc_tpdu_bytes = encoder.encode(cc_tpdu)
                await tpkt_conn.send(cc_tpdu_bytes)

                max_tpdu = _calculate_max_tpdu(cr_tpdu, cc_tpdu)
                calling_tsel, called_tsel = _get_tsels(cr_tpdu, cc_tpdu)
                conn = Connection(tpkt_conn, max_tpdu,
                                  called_tsel, calling_tsel,
                                  self._receive_queue_size,
                                  self._send_queue_size)

            except BaseException:
                await aio.uncancellable(tpkt_conn.async_close())
                raise

            try:
                await aio.call(self._connection_cb, conn)

            except BaseException:
                await aio.uncancellable(conn.async_close())
                raise

        except Exception as e:
            mlog.error("error creating new incomming connection: %s", e,
                       exc_info=e)


class Connection(aio.Resource):
    """COTP connection

    For creation of new instance see `connect` or `listen`.

    """

    def __init__(self,
                 conn: tpkt.Connection,
                 max_tpdu: int,
                 local_tsel: int | None,
                 remote_tsel: int | None,
                 receive_queue_size: int,
                 send_queue_size: int):
        self._conn = conn
        self._max_tpdu = max_tpdu
        self._loop = asyncio.get_running_loop()
        self._info = ConnectionInfo(local_tsel=local_tsel,
                                    remote_tsel=remote_tsel,
                                    **conn.info._asdict())
        self._receive_queue = aio.Queue(receive_queue_size)
        self._send_queue = aio.Queue(send_queue_size)

        self.async_group.spawn(self._receive_loop)
        self.async_group.spawn(self._send_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> ConnectionInfo:
        """Connection info"""
        return self._info

    async def receive(self) -> util.Bytes:
        """Receive data"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send(self, data: util.Bytes):
        """Send data"""
        try:
            await self._send_queue.put((data, None))

        except aio.QueueClosedError:
            raise ConnectionError()

    async def drain(self):
        """Drain output buffer"""
        try:
            future = self._loop.create_future()
            await self._send_queue.put((None, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _receive_loop(self):
        try:
            data_queue = collections.deque()
            while True:
                tpdu_bytes = await self._conn.receive()
                tpdu = encoder.decode(memoryview(tpdu_bytes))

                if isinstance(tpdu, (common.DR, common.ER)):
                    mlog.info("received disconnect request / error")
                    break

                if not isinstance(tpdu, common.DT):
                    continue

                data_queue.append(tpdu.data)

                if not tpdu.eot:
                    continue

                data = bytes(itertools.chain.from_iterable(data_queue))
                data_queue.clear()

                await self._receive_queue.put(data)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._receive_queue.close()

    async def _send_loop(self):
        future = None
        try:
            while True:
                data, future = await self._send_queue.get()

                if data is None:
                    await self._conn.drain()

                else:
                    data = memoryview(data)
                    max_size = self._max_tpdu - 3

                    while data:
                        single_data, data = data[:max_size], data[max_size:]

                        tpdu = common.DT(eot=not data, data=single_data)
                        tpdu_bytes = encoder.encode(tpdu)
                        await self._conn.send(tpdu_bytes)

                if future and not future.done():
                    future.set_result(None)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("send loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_result(None)
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()


def _validate_connect_request(cr_tpdu):
    if not isinstance(cr_tpdu, common.CR):
        raise Exception("received message is not of type CR")

    if cr_tpdu.cls != 0:
        raise Exception(f"received class {cr_tpdu.cls} "
                        "(only class 0 is supported)")


def _validate_connect_response(cr_tpdu, cc_tpdu):
    if not isinstance(cc_tpdu, common.CC):
        raise Exception("received message is not of type CC")

    if (cr_tpdu.calling_tsel is not None and
            cc_tpdu.calling_tsel is not None and
            cr_tpdu.calling_tsel != cc_tpdu.calling_tsel):
        raise Exception(f"received calling tsel {cc_tpdu.calling_tsel} "
                        f"instead of {cr_tpdu.calling_tsel}")

    if (cr_tpdu.called_tsel is not None and
            cc_tpdu.called_tsel is not None and
            cr_tpdu.called_tsel != cc_tpdu.called_tsel):
        raise Exception(f"received calling tsel {cc_tpdu.called_tsel} "
                        f"instead of {cr_tpdu.called_tsel}")

    if cc_tpdu.dst != cr_tpdu.src:
        raise Exception("received message with invalid sequence number")

    if cc_tpdu.cls != 0:
        raise Exception(f"received class {cc_tpdu.cls} "
                        f"(only class 0 is supported)")


def _calculate_max_tpdu(cr_tpdu, cc_tpdu):

    # TODO not sure about standard's definition of this calculation

    if not cr_tpdu.max_tpdu and not cc_tpdu.max_tpdu:
        return 128

    elif cr_tpdu.max_tpdu and not cc_tpdu.max_tpdu:
        return cr_tpdu.max_tpdu

    return cc_tpdu.max_tpdu


def _calculate_cc_max_tpdu(cr_tpdu):

    # TODO not sure about standard's definition of this calculation

    if cr_tpdu.max_tpdu:
        return cr_tpdu.max_tpdu

    elif cr_tpdu.pref_max_tpdu:
        return cr_tpdu.pref_max_tpdu

    return 128


def _get_tsels(cr_tpdu, cc_tpdu):
    calling_tsel = (cr_tpdu.calling_tsel
                    if cr_tpdu.calling_tsel is not None
                    else cc_tpdu.calling_tsel)

    called_tsel = (cr_tpdu.called_tsel
                   if cr_tpdu.called_tsel is not None
                   else cc_tpdu.called_tsel)

    return calling_tsel, called_tsel
