"""Asyncio UDP endpoint wrapper"""

import asyncio
import logging
import typing

from hat import aio
from hat import util


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


class Address(typing.NamedTuple):
    host: str
    port: int


class EndpointInfo(typing.NamedTuple):
    local_addr: Address
    remote_addr: Address | None


async def create(local_addr: Address | None = None,
                 remote_addr: Address | None = None,
                 queue_size: int = 0,
                 **kwargs
                 ) -> 'Endpoint':
    """Create new UDP endpoint

    Args:
        local_addr: local address
        remote_addr: remote address
        queue_size: receive queue max size
        kwargs: additional arguments passed to
            :meth:`asyncio.AbstractEventLoop.create_datagram_endpoint`

    """
    endpoint = Endpoint()
    endpoint._local_addr = local_addr
    endpoint._remote_addr = remote_addr
    endpoint._async_group = aio.Group()
    endpoint._queue = aio.Queue(queue_size)

    class Protocol(asyncio.DatagramProtocol):

        def connection_lost(self, exc):
            endpoint._async_group.close()

        def datagram_received(self, data, addr):
            try:
                endpoint._queue.put_nowait(
                    (data, Address(addr[0], addr[1])))

            except aio.QueueFullError:
                mlog.warning('receive queue full - dropping datagram')

    loop = asyncio.get_running_loop()
    endpoint._transport, endpoint._protocol = \
        await loop.create_datagram_endpoint(Protocol, local_addr, remote_addr,
                                            **kwargs)

    endpoint._async_group.spawn(aio.call_on_cancel, endpoint._transport.close)
    endpoint._async_group.spawn(aio.call_on_cancel, endpoint._queue.close)

    sockname = endpoint._transport.get_extra_info('sockname')
    peername = endpoint._transport.get_extra_info('peername')
    endpoint._info = EndpointInfo(
        local_addr=Address(sockname[0], sockname[1]),
        remote_addr=Address(peername[0], peername[1]) if peername else None)

    return endpoint


class Endpoint(aio.Resource):
    """UDP endpoint"""

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> EndpointInfo:
        """Endpoint info"""
        return self._info

    @property
    def empty(self) -> bool:
        """Is receive queue empty"""
        return self._queue.empty()

    def send(self,
             data: util.Bytes,
             remote_addr: Address | None = None):
        """Send datagram

        If `remote_addr` is not set, `remote_addr` passed to :func:`create`
        is used.

        """
        if not self.is_open:
            raise ConnectionError()

        self._transport.sendto(data, remote_addr or self._remote_addr)

    async def receive(self) -> tuple[util.Bytes, Address]:
        """Receive datagram"""
        try:
            data, addr = await self._queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

        return data, addr
