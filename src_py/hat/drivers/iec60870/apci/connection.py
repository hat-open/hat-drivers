import asyncio
import itertools
import logging
import ssl
import typing

from hat import aio
from hat.drivers import tcp
from hat.drivers.iec60870.apci import common
from hat.drivers.iec60870.apci import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


ConnectionCb = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


class ConnectionDisabledError(ConnectionError):
    pass


async def connect(addr: tcp.Address,
                  response_timeout: float = 15,
                  supervisory_timeout: float = 10,
                  test_timeout: float = 20,
                  send_window_size: int = 12,
                  receive_window_size: int = 8,
                  ssl_ctx: typing.Optional[ssl.SSLContext] = None
                  ) -> 'Connection':
    """Connect to remote device

    Args:
        addr: remote server's address
        response_timeout: response timeout (t1) in seconds
        supervisory_timeout: supervisory timeout (t2) in seconds
        test_timeout: test timeout (t3) in seconds
        send_window_size: send window size (k)
        receive_window_size: receive window size (w)
        ssl_ctx: optional ssl context argument

    """
    conn = await tcp.connect(addr, ssl=ssl_ctx)

    try:
        _write_apdu(conn, common.APDUU(common.ApduFunction.STARTDT_ACT))
        await aio.wait_for(_wait_startdt_con(conn), response_timeout)

    except Exception:
        await aio.uncancellable(conn.async_close())
        raise

    return Connection(conn=conn,
                      always_enabled=True,
                      response_timeout=response_timeout,
                      supervisory_timeout=supervisory_timeout,
                      test_timeout=test_timeout,
                      send_window_size=send_window_size,
                      receive_window_size=receive_window_size)


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 2404),
                 response_timeout: float = 15,
                 supervisory_timeout: float = 10,
                 test_timeout: float = 20,
                 send_window_size: int = 12,
                 receive_window_size: int = 8,
                 ssl_ctx: typing.Optional[ssl.SSLContext] = None
                 ) -> 'Server':
    """Create new IEC104 slave and listen for incoming connections

    Args:
        connection_cb: new connection callback
        addr: listening socket address
        response_timeout: response timeout (t1) in seconds
        supervisory_timeout: supervisory timeout (t2) in seconds
        test_timeout: test timeout (t3) in seconds
        send_window_size: send window size (k)
        receive_window_size: receive window size (w)
        ssl_ctx: optional ssl context argument

    """
    server = Server()
    server._connection_cb = connection_cb
    server._response_timeout = response_timeout
    server._supervisory_timeout = supervisory_timeout
    server._test_timeout = test_timeout
    server._send_window_size = send_window_size
    server._receive_window_size = receive_window_size

    server._srv = await tcp.listen(server._on_connection, addr,
                                   bind_connections=True,
                                   ssl=ssl_ctx)

    return server


class Server(aio.Resource):
    """Server

    For creating new Server instances see `listen` coroutine.

    Closing server closes all incoming connections.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._srv.async_group

    @property
    def addresses(self) -> typing.List[tcp.Address]:
        """Listening addresses"""
        return self._srv.addresses

    async def _on_connection(self, conn):
        connection = Connection(conn=conn,
                                always_enabled=False,
                                response_timeout=self._response_timeout,
                                supervisory_timeout=self._supervisory_timeout,
                                test_timeout=self._test_timeout,
                                send_window_size=self._send_window_size,
                                receive_window_size=self._receive_window_size)

        try:
            await aio.call(self._connection_cb, connection)

        except BaseException:
            connection.close()
            raise


class Connection(aio.Resource):
    """Connection

    For creating new Connection instances see `connect` or `listen` coroutine.

    """

    def __init__(self,
                 conn: tcp.Connection,
                 always_enabled: bool,
                 response_timeout: float,
                 supervisory_timeout: float,
                 test_timeout: float,
                 send_window_size: int,
                 receive_window_size: int):
        self._conn = conn
        self._always_enabled = always_enabled
        self._is_enabled = always_enabled
        self._response_timeout = response_timeout
        self._supervisory_timeout = supervisory_timeout
        self._test_timeout = test_timeout
        self._send_window_size = send_window_size
        self._receive_window_size = receive_window_size
        self._receive_queue = aio.Queue()
        self._send_queue = aio.Queue()
        self._test_event = asyncio.Event()
        self._ssn = 0
        self._rsn = 0
        self._ack = 0
        self._w = 0
        self._supervisory_handle = None
        self._waiting_ack_handles = {}
        self._waiting_ack_cv = asyncio.Condition()

        self.async_group.spawn(self._read_loop)
        self.async_group.spawn(self._write_loop)
        self.async_group.spawn(self._test_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        """Connection info"""
        return self._conn.info

    def send(self, data: common.Bytes):
        """Send data

        Raises:
            ConnectionError

        """
        entry = _SendQueueEntry(data, None, False)
        try:
            self._send_queue.put_nowait(entry)

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send_wait_ack(self, data: common.Bytes):
        """Send data and wait for acknowledgement

        Raises:
            ConnectionDisabledError
            ConnectionError

        """
        entry = _SendQueueEntry(data, asyncio.Future(), True)
        try:
            self._send_queue.put_nowait(entry)
            await entry.future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def drain(self, wait_ack: bool = False):
        """Drain

        Raises:
            ConnectionError

        """
        entry = _SendQueueEntry(None, asyncio.Future(), wait_ack)
        try:
            self._send_queue.put_nowait(entry)
            await entry.future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def receive(self) -> common.Bytes:
        """Receive data

        Raises:
            ConnectionError

        """
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    def _on_response_timeout(self):
        mlog.warning("response timeout occured - closing connection")
        self.close()

    def _on_supervisory_timeout(self):
        self._supervisory_handle = None

        try:
            _write_apdu(self._conn, common.APDUS(self._rsn))
            self._w = 0

        except Exception as e:
            mlog.warning('supervisory timeout error: %s', e, exc_info=e)

    async def _read_loop(self):
        try:
            while True:
                apdu = await _read_apdu(self._conn)

                if isinstance(apdu, common.APDUU):
                    await self._process_apduu(apdu)

                elif isinstance(apdu, common.APDUS):
                    await self._process_apdus(apdu)

                elif isinstance(apdu, common.APDUI):
                    await self._process_apdui(apdu)

                else:
                    raise ValueError("unsupported APDU")

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            mlog.warning('read loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._receive_queue.close()

    async def _write_loop(self):
        entry = None

        try:
            while True:
                entry = await self._send_queue.get()

                if entry.data is None:
                    await self._conn.drain()
                    ssn = (self._ssn or 0x8000) - 1
                    handle = self._waiting_ack_handles.get(ssn)

                else:
                    handle = await self._write_apdui(entry.data)
                    if not handle and entry.future and not entry.future.done():
                        entry.future.set_exception(ConnectionDisabledError())

                if not entry.future:
                    continue

                if entry.wait_ack and handle and not entry.future.done():
                    self.async_group.spawn(self._wait_ack, handle,
                                           entry.future)
                    entry = None

                elif not entry.future.done():
                    entry.future.set_result(None)

        except (ConnectionError, aio.QueueClosedError):
            pass

        except Exception as e:
            mlog.warning('write loop error: %s', e, exc_info=e)

        finally:
            self.close()
            self._stop_supervisory_timeout()
            self._send_queue.close()

            for f in self._waiting_ack_handles.values():
                f.cancel()

            while True:
                if entry and entry.future and not entry.future.done():
                    entry.future.set_exception(ConnectionError())
                if self._send_queue.empty():
                    break
                entry = self._send_queue.get_nowait()

    async def _test_loop(self):
        # TODO: implement reset timeout on received frame (v2 5.2.)
        try:
            while True:
                await asyncio.sleep(self._test_timeout)

                self._test_event.clear()
                _write_apdu(self._conn,
                            common.APDUU(common.ApduFunction.TESTFR_ACT))

                await aio.wait_for(self._test_event.wait(),
                                   self._response_timeout)

        except Exception as e:
            mlog.warning('test loop error: %s', e, exc_info=e)

        finally:
            self.close()

    async def _process_apduu(self, apdu):
        if apdu.function == common.ApduFunction.STARTDT_ACT:
            self._is_enabled = True
            _write_apdu(self._conn,
                        common.APDUU(common.ApduFunction.STARTDT_CON))

        elif apdu.function == common.ApduFunction.STOPDT_ACT:
            if not self._always_enabled:
                _write_apdu(self._conn, common.APDUS(self._rsn))
                self._w = 0
                self._stop_supervisory_timeout()
                self._is_enabled = False
                _write_apdu(self._conn,
                            common.APDUU(common.ApduFunction.STOPDT_CON))

        elif apdu.function == common.ApduFunction.TESTFR_ACT:
            _write_apdu(self._conn,
                        common.APDUU(common.ApduFunction.TESTFR_CON))

        elif apdu.function == common.ApduFunction.TESTFR_CON:
            self._test_event.set()

    async def _process_apdus(self, apdu):
        await self._set_ack(apdu.rsn)

    async def _process_apdui(self, apdu):
        await self._set_ack(apdu.rsn)

        if apdu.ssn != self._rsn:
            raise Exception('missing apdu sequence number')

        self._rsn = (self._rsn + 1) % 0x8000
        self._start_supervisory_timeout()

        if apdu.data:
            self._receive_queue.put_nowait(apdu.data)

        self._w += 1
        if self._w >= self._receive_window_size:
            _write_apdu(self._conn, common.APDUS(self._rsn))
            self._w = 0
            self._stop_supervisory_timeout()

    async def _write_apdui(self, data):
        if self._ssn in self._waiting_ack_handles:
            raise Exception("can not reuse already registered ssn")

        async with self._waiting_ack_cv:
            await self._waiting_ack_cv.wait_for(
                lambda: (len(self._waiting_ack_handles) <
                         self._send_window_size))

        if not self._is_enabled:
            mlog.info("send data not enabled - discarding message")
            return

        _write_apdu(self._conn, common.APDUI(ssn=self._ssn,
                                             rsn=self._rsn,
                                             data=data))
        self._w = 0
        self._stop_supervisory_timeout()

        handle = asyncio.get_event_loop().call_later(self._response_timeout,
                                                     self._on_response_timeout)
        self._waiting_ack_handles[self._ssn] = handle
        self._ssn = (self._ssn + 1) % 0x8000
        return handle

    async def _wait_ack(self, handle, future):
        try:
            async with self._waiting_ack_cv:
                await self._waiting_ack_cv.wait_for(handle.cancelled)

            if not future.done():
                future.set_result(None)

        finally:
            if not future.done():
                future.set_exception(ConnectionError())

    async def _set_ack(self, ack):
        if ack >= self._ack:
            ssns = range(self._ack, ack)
        else:
            ssns = itertools.chain(range(self._ack, 0x8000), range(ack))

        for ssn in ssns:
            handle = self._waiting_ack_handles.pop(ssn, None)
            if not handle:
                raise Exception("received ack for unsent sequence number")
            handle.cancel()

        self._ack = ack
        async with self._waiting_ack_cv:
            self._waiting_ack_cv.notify_all()

    def _start_supervisory_timeout(self):
        if self._supervisory_handle:
            return

        self._supervisory_handle = asyncio.get_event_loop().call_later(
            self._supervisory_timeout, self._on_supervisory_timeout)

    def _stop_supervisory_timeout(self):
        if not self._supervisory_handle:
            return

        self._supervisory_handle.cancel()
        self._supervisory_handle = None


class _SendQueueEntry(typing.NamedTuple):
    data: typing.Optional[common.Bytes]
    future: typing.Optional[asyncio.Future]
    wait_ack: bool


async def _read_apdu(conn):
    data = bytearray()

    while True:
        size = encoder.get_next_apdu_size(data)
        if size <= len(data):
            break
        data.extend(await conn.readexactly(size - len(data)))

    return encoder.decode(memoryview(data))


def _write_apdu(conn, apdu):
    data = encoder.encode(apdu)
    conn.write(data)


async def _wait_startdt_con(conn):
    while True:
        req = await _read_apdu(conn)

        if not isinstance(req, common.APDUU):
            continue

        if req.function == common.ApduFunction.STARTDT_CON:
            return

        if req.function == common.ApduFunction.TESTFR_ACT:
            res = common.APDUU(common.ApduFunction.TESTFR_CON)
            _write_apdu(conn, res)
