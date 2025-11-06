"""Asyncio UDP endpoint wrapper"""

import asyncio
import functools
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


class Address(typing.NamedTuple):
    host: str
    port: int


class EndpointInfo(typing.NamedTuple):
    name: str | None
    local_addr: Address
    remote_addr: Address | None


async def create(local_addr: Address | None = None,
                 remote_addr: Address | None = None,
                 *,
                 name: str | None = None,
                 queue_size: int = 0,
                 **kwargs
                 ) -> 'Endpoint':
    """Create new UDP endpoint

    Args:
        local_addr: local address
        remote_addr: remote address
        name: endpoint name
        queue_size: receive queue max size
        kwargs: additional arguments passed to
            :meth:`asyncio.AbstractEventLoop.create_datagram_endpoint`

    """
    endpoint = Endpoint()
    endpoint._local_addr = local_addr
    endpoint._remote_addr = remote_addr
    endpoint._async_group = aio.Group()
    endpoint._queue = aio.Queue(queue_size)
    endpoint._transport = None
    endpoint._protocol = None
    endpoint._log = _create_logger(name, None)
    endpoint._comm_log = _CommunicationLogger(name, None)

    loop = asyncio.get_running_loop()
    create_protocol = functools.partial(Protocol, endpoint)
    endpoint._transport, endpoint._protocol = \
        await loop.create_datagram_endpoint(create_protocol, local_addr,
                                            remote_addr, **kwargs)

    try:
        endpoint._async_group.spawn(aio.call_on_cancel, endpoint._on_close)

        sockname = endpoint._transport.get_extra_info('sockname')
        peername = endpoint._transport.get_extra_info('peername')
        endpoint._info = EndpointInfo(
            name=name,
            local_addr=Address(sockname[0], sockname[1]),
            remote_addr=(Address(peername[0], peername[1])
                         if peername else None))

        endpoint._log = _create_logger(name, endpoint._info)
        endpoint._comm_log = _CommunicationLogger(name, endpoint._info)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise

    endpoint._comm_log.log(common.CommLogAction.OPEN)

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

        If `remote_addr` is not set, `remote_addr` passed to `create` is used.

        """
        if not self.is_open or not self._transport:
            raise ConnectionError()

        msg = data, (remote_addr or self._remote_addr)
        self._comm_log.log(common.CommLogAction.SEND, msg)

        self._transport.sendto(msg[0], msg[1])

    async def receive(self) -> tuple[util.Bytes, Address]:
        """Receive datagram"""
        try:
            data, addr = await self._queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

        return data, addr

    def _on_close(self):
        self._queue.close()

        if self._transport:
            self._transport.close()

        self._transport = None
        self._protocol = None

        self._comm_log.log(common.CommLogAction.CLOSE)


class Protocol(asyncio.DatagramProtocol):

    def __init__(self, endpoint: Endpoint):
        self._endpoint = endpoint

    def connection_lost(self, exc: Exception | None):
        self._endpoint._log.debug('connection lost')

        self._endpoint.close()

    def datagram_received(self, data: util.Bytes, addr: tuple):
        msg = data, Address(addr[0], addr[1])
        self._endpoint._comm_log.log(common.CommLogAction.RECEIVE, msg)

        try:
            self._endpoint._queue.put_nowait(msg)

        except aio.QueueFullError:
            self._endpoint._log.warning('receive queue full - '
                                        'dropping datagram')


def _create_logger(name, info):
    extra = {'meta': {'type': 'UdpEndpoint',
                      'name': name}}

    if info is not None:
        extra['meta']['local_addr'] = {'host': info.local_addr.host,
                                       'port': info.local_addr.port}

        if info.remote_addr is not None:
            extra['meta']['remote_addr'] = {'host': info.remote_addr.host,
                                            'port': info.remote_addr.port}

    return logging.LoggerAdapter(mlog, extra)


class _CommunicationLogger:

    def __init__(self,
                 name: str | None,
                 info: EndpointInfo | None):
        extra = {'meta': {'type': 'UdpEndpoint',
                          'communication': True,
                          'name': name}}

        if info is not None:
            extra['meta']['local_addr'] = {'host': info.local_addr.host,
                                           'port': info.local_addr.port}

            if info.remote_addr is not None:
                extra['meta']['remote_addr'] = {'host': info.remote_addr.host,
                                                'port': info.remote_addr.port}

        self._log = logging.LoggerAdapter(mlog, extra)

    def log(self,
            action: common.CommLogAction,
            msg: tuple[util.Bytes, Address] | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if msg is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s (data=(%s) remote=%s)',
                            action.value, msg[0].hex(' '), tuple(msg[1]),
                            stacklevel=2)
