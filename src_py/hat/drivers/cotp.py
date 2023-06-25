"""Connection oriented transport protocol"""

import asyncio
import collections
import enum
import itertools
import logging
import math
import typing

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers import tpkt


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


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
    tpkt_conn = await tpkt.connect(addr, **kwargs)
    try:
        conn = await _create_outgoing_connection(tpkt_conn,
                                                 local_tsel, remote_tsel,
                                                 cotp_receive_queue_size,
                                                 cotp_send_queue_size)
        return conn

    except BaseException:
        await aio.uncancellable(tpkt_conn.async_close())
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
                conn = await _create_incomming_connection(
                    tpkt_conn, self._receive_queue_size, self._send_queue_size)

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
                tpdu = _decode(memoryview(tpdu_bytes))

                if isinstance(tpdu, _DR) or isinstance(tpdu, _ER):
                    mlog.info("received disconnect request / error")
                    break

                if not isinstance(tpdu, _DT):
                    continue

                data_queue.append(tpdu.data)

                if not tpdu.eot:
                    continue

                data = bytes(itertools.chain.from_iterable(data_queue))
                data_queue.clear()

                await self._receive_queue.put(data)

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

                        tpdu = _DT(eot=not data, data=single_data)
                        tpdu_bytes = _encode(tpdu)
                        await self._conn.send(tpdu_bytes)

                if future and not future.done():
                    future.set_result(None)

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


_next_srcs = ((i % 0xFFFF) + 1 for i in itertools.count(0))


async def _create_outgoing_connection(conn, local_tsel, remote_tsel,
                                      receive_queue_size, send_queue_size):
    cr_tpdu = _CR(src=next(_next_srcs),
                  cls=0,
                  calling_tsel=local_tsel,
                  called_tsel=remote_tsel,
                  max_tpdu=2048,
                  pref_max_tpdu=None)
    cr_tpdu_bytes = _encode(cr_tpdu)
    await conn.send(cr_tpdu_bytes)

    cc_tpdu_bytes = await conn.receive()
    cc_tpdu = _decode(memoryview(cc_tpdu_bytes))
    _validate_connect_response(cr_tpdu, cc_tpdu)

    max_tpdu = _calculate_max_tpdu(cr_tpdu, cc_tpdu)
    calling_tsel, called_tsel = _get_tsels(cr_tpdu, cc_tpdu)
    return Connection(conn, max_tpdu, calling_tsel, called_tsel,
                      receive_queue_size, send_queue_size)


async def _create_incomming_connection(conn, receive_queue_size,
                                       send_queue_size):
    cr_tpdu_bytes = await conn.receive()
    cr_tpdu = _decode(memoryview(cr_tpdu_bytes))
    _validate_connect_request(cr_tpdu)

    cc_tpdu = _CC(dst=cr_tpdu.src,
                  src=next(_next_srcs),
                  cls=0,
                  calling_tsel=cr_tpdu.calling_tsel,
                  called_tsel=cr_tpdu.called_tsel,
                  max_tpdu=_calculate_cc_max_tpdu(cr_tpdu),
                  pref_max_tpdu=None)
    cc_tpdu_bytes = _encode(cc_tpdu)
    await conn.send(cc_tpdu_bytes)

    max_tpdu = _calculate_max_tpdu(cr_tpdu, cc_tpdu)
    calling_tsel, called_tsel = _get_tsels(cr_tpdu, cc_tpdu)
    return Connection(conn, max_tpdu, called_tsel, calling_tsel,
                      receive_queue_size, send_queue_size)


class _TpduType(enum.Enum):
    DT = 0xF0
    CR = 0xE0
    CC = 0xD0
    DR = 0x80
    ER = 0x70


class _DT(typing.NamedTuple):
    """Data TPDU"""
    eot: bool
    """end of transmition flag"""
    data: memoryview


class _CR(typing.NamedTuple):
    """Connection request TPDU"""
    src: int
    """connection reference selectet by initiator of connection request"""
    cls: int
    """transport protocol class"""
    calling_tsel: int | None
    """calling transport selector"""
    called_tsel: int | None
    """responding transport selector"""
    max_tpdu: int
    """max tpdu size in octets"""
    pref_max_tpdu: int
    """preferred max tpdu size in octets"""


class _CC(typing.NamedTuple):
    """Connection confirm TPDU"""
    dst: int
    """connection reference selected by initiator of connection request"""
    src: int
    """connection reference selected by initiator of connection confirm"""
    cls: int
    """transport protocol class"""
    calling_tsel: int | None
    """calling transport selector"""
    called_tsel: int | None
    """responding transport selector"""
    max_tpdu: int
    """max tpdu size in octets"""
    pref_max_tpdu: int
    """preferred max tpdu size in octets"""


class _DR(typing.NamedTuple):
    """Disconnect request TPDU"""
    dst: int
    """connection reference selected by remote entity"""
    src: int
    """connection reference selected by initiator of disconnect request"""
    reason: int
    """reason for disconnection"""


class _ER(typing.NamedTuple):
    """Error TPDU"""
    dst: int
    """connection reference selected by remote entity"""
    cause: int
    """reject cause"""


def _validate_connect_request(cr_tpdu):
    if not isinstance(cr_tpdu, _CR):
        raise Exception("received message is not of type CR")

    if cr_tpdu.cls != 0:
        raise Exception(f"received class {cr_tpdu.cls} "
                        "(only class 0 is supported)")


def _validate_connect_response(cr_tpdu, cc_tpdu):
    if not isinstance(cc_tpdu, _CC):
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


def _encode(tpdu):
    if isinstance(tpdu, _DT):
        tpdu_type = _TpduType.DT

    elif isinstance(tpdu, _CR):
        tpdu_type = _TpduType.CR

    elif isinstance(tpdu, _CC):
        tpdu_type = _TpduType.CC

    elif isinstance(tpdu, _DR):
        tpdu_type = _TpduType.DR

    elif isinstance(tpdu, _ER):
        tpdu_type = _TpduType.ER

    else:
        raise ValueError('invalid tpdu')

    header = collections.deque()
    header.append(tpdu_type.value)

    if tpdu_type == _TpduType.DT:
        header.append(0x80 if tpdu.eot else 0)
        return bytes(itertools.chain([len(header)], header, tpdu.data))

    if tpdu_type == _TpduType.CR:
        header.extend([0, 0])

    else:
        header.extend(tpdu.dst.to_bytes(2, 'big'))

    if tpdu_type == _TpduType.ER:
        header.append(tpdu.cause)

    else:
        header.extend(tpdu.src.to_bytes(2, 'big'))

    if tpdu_type == _TpduType.DR:
        header.append(tpdu.reason)

    elif tpdu_type == _TpduType.CR or tpdu_type == _TpduType.CC:
        header.append(tpdu.cls << 4)

        if tpdu.calling_tsel is not None:
            header.append(0xC1)
            header.append(2)
            header.extend(tpdu.calling_tsel.to_bytes(2, 'big'))

        if tpdu.called_tsel is not None:
            header.append(0xC2)
            header.append(2)
            header.extend(tpdu.called_tsel.to_bytes(2, 'big'))

        if tpdu.max_tpdu is not None:
            header.append(0xC0)
            header.append(1)
            header.append(tpdu.max_tpdu.bit_length() - 1)

        if tpdu.pref_max_tpdu is not None:
            pref_max_tpdu_data = _uint_to_bebytes(tpdu.pref_max_tpdu // 128)
            header.append(0xC0)
            header.append(len(pref_max_tpdu_data))
            header.extend(pref_max_tpdu_data)

    return bytes(itertools.chain([len(header)], header))


def _decode(data):
    length_indicator = data[0]
    if length_indicator >= len(data) or length_indicator > 254:
        raise ValueError("invalid length indicator")

    header = data[:length_indicator + 1]
    tpdu_data = data[length_indicator + 1:]
    tpdu_type = _TpduType(header[1] & 0xF0)

    if tpdu_type == _TpduType.DT:
        eot = bool(header[2] & 0x80)
        return _DT(eot=eot,
                   data=tpdu_data)

    if tpdu_type in (_TpduType.CR, _TpduType.CC, _TpduType.DR):
        src = (header[4] << 8) | header[5]

    if tpdu_type in (_TpduType.CC, _TpduType.DR, _TpduType.ER):
        dst = (header[2] << 8) | header[3]

    if tpdu_type in (_TpduType.CR, _TpduType.CC):
        cls = header[6] >> 4
        calling_tsel = None
        called_tsel = None
        max_tpdu = None
        pref_max_tpdu = None
        vp_data = header[7:]
        while vp_data:
            k, v, vp_data = (vp_data[0],
                             vp_data[2:2 + vp_data[1]],
                             vp_data[2 + vp_data[1]:])
            if k == 0xC1:
                calling_tsel = _bebytes_to_uint(v)
            elif k == 0xC2:
                called_tsel = _bebytes_to_uint(v)
            elif k == 0xC0:
                max_tpdu = 1 << v[0]
            elif k == 0xF0:
                pref_max_tpdu = 128 * _bebytes_to_uint(v)

    if tpdu_type == _TpduType.CR:
        return _CR(src=src,
                   cls=cls,
                   calling_tsel=calling_tsel,
                   called_tsel=called_tsel,
                   max_tpdu=max_tpdu,
                   pref_max_tpdu=pref_max_tpdu)

    if tpdu_type == _TpduType.CC:
        return _CC(dst=dst,
                   src=src,
                   cls=cls,
                   calling_tsel=calling_tsel,
                   called_tsel=called_tsel,
                   max_tpdu=max_tpdu,
                   pref_max_tpdu=pref_max_tpdu)

    if tpdu_type == _TpduType.DR:
        reason = header[6]
        return _DR(dst=dst,
                   src=src,
                   reason=reason)

    if tpdu_type == _TpduType.ER:
        cause = header[4]
        return _ER(dst=dst,
                   cause=cause)

    raise ValueError("invalid tpdu code")


def _bebytes_to_uint(b):
    return int.from_bytes(b, 'big')


def _uint_to_bebytes(x):
    bytes_len = max(math.ceil(x.bit_length() / 8), 1)
    return x.to_bytes(bytes_len, 'big')
