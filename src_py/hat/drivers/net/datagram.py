import asyncio
import enum
import functools
import logging
import socket
import typing

from hat import aio
from hat import json
from hat import util

from hat.drivers.net import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


class UdpAddress(typing.NamedTuple):
    host: str
    port: int


DatagramAddress: typing.TypeAlias = UdpAddress | common.UnixAddress


class UdpEndpointInfo(typing.NamedTuple):
    name: str | None
    local_addr: UdpAddress
    remote_addr: UdpAddress | None


class UnixEndpointInfo(typing.NamedTuple):
    name: str | None
    local_addr: common.UnixAddress | None
    remote_addr: common.UnixAddress | None


EndpointInfo: typing.TypeAlias = UdpEndpointInfo | UnixEndpointInfo


class DatagramType(enum.Enum):
    UDP = 0
    UNIX = 1


def endpoint_info_to_json(info: EndpointInfo) -> json.Data:
    if isinstance(info, UdpEndpointInfo):
        data = {'name': info.name,
                'local_addr': {'host': info.local_addr.host,
                               'port': info.local_addr.port}}

        if info.remote_addr is not None:
            data['remote_addr'] = {'host': info.remote_addr.host,
                                   'port': info.remote_addr.port}

        return data

    if isinstance(info, UnixEndpointInfo):
        data = {'name': info.name}

        if info.local_addr is not None:
            data['local_addr'] = str(info.local_addr)

        if info.remote_addr is not None:
            data['remote_addr'] = str(info.remote_addr)

        return data

    raise TypeError('unsupported info type')


async def create_endpoint(datagram_type: DatagramType = DatagramType.UDP,
                          local_addr: DatagramAddress | None = None,
                          remote_addr: DatagramAddress | None = None,
                          *,
                          name: str | None = None,
                          receive_queue_size: int = 0,
                          **kwargs
                          ) -> 'Endpoint':
    """Create new UDP or Unix Domain Socket endpoint

    Args:
        datagram_type: datagram protocol type
        local_addr: local address
        remote_addr: remote address
        name: endpoint name
        receive_queue_size: receive queue max size
        kwargs: additional arguments passed to
            `asyncio.AbstractEventLoop.create_datagram_endpoint`

    """
    loop = asyncio.get_running_loop()

    create_protocol = functools.partial(_Protocol, datagram_type, name,
                                        receive_queue_size)
    family = _get_address_family(datagram_type)

    if isinstance(local_addr, common.UnixAddress):
        local_addr = str(local_addr)

    if isinstance(remote_addr, common.UnixAddress):
        remote_addr = str(remote_addr)

    _, protocol = await loop.create_datagram_endpoint(create_protocol,
                                                      local_addr,
                                                      remote_addr,
                                                      family=family,
                                                      **kwargs)

    return _create_endpoint(protocol)


def _create_endpoint(protocol: '_Protocol') -> 'Endpoint':
    endpoint = Endpoint()
    endpoint._protocol = protocol
    endpoint._async_group = aio.Group()

    endpoint.async_group.spawn(aio.call_on_cancel, protocol.close)
    endpoint.async_group.spawn(aio.call_on_done, protocol.wait_closed(),
                               endpoint.close)

    return endpoint


class Endpoint(aio.Resource):
    """UDP or Unix Domain Socket endpoint"""

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> EndpointInfo:
        """Endpoint info"""
        return self._protocol.info

    @property
    def empty(self) -> bool:
        """Is receive queue empty"""
        return self._protocol.empty

    def send(self,
             data: util.Bytes,
             remote_addr: DatagramAddress | None = None):
        """Send datagram

        If `remote_addr` is not set, `remote_addr` passed to `create` is used.

        """
        if not self.is_open:
            raise ConnectionError()

        self._protocol.send(data, remote_addr)

    async def receive(self) -> tuple[util.Bytes, DatagramAddress | None]:
        """Receive datagram"""
        return await self._protocol.receive()


class _Protocol(asyncio.DatagramProtocol):

    def __init__(self,
                 datagram_type: DatagramType,
                 name: str | None,
                 receive_queue_size: int):
        self._datagram_type = datagram_type
        self._name = name
        self._receive_queue = aio.Queue(receive_queue_size)
        self._closed = asyncio.Event()
        self._transport = None
        self._log = mlog
        self._comm_log = _CommunicationLogger(None)

    @property
    def info(self) -> EndpointInfo:
        return self._info

    @property
    def empty(self) -> bool:
        return self._receive_queue.empty()

    def connection_made(self, transport: asyncio.Transport):
        self._transport = transport
        self._info = _get_endpoint_info(self._datagram_type, self._name,
                                        transport)

        self._log = _create_logger(self._info)
        self._comm_log = _CommunicationLogger(self._info)

        self._comm_log.log(common.CommLogAction.OPEN)

    def connection_lost(self, exc: Exception | None):
        self._log.debug('connection lost')

        self._closed.set()
        self._comm_log.log(common.CommLogAction.CLOSE)

    def datagram_received(self, data: util.Bytes, addr: tuple | str | None):
        msg = data, addr

        self._comm_log.log(common.CommLogAction.RECEIVE, msg)

        try:
            self._receive_queue.put_nowait(msg)

        except aio.QueueFullError:
            self._log.warning('receive queue full - dropping datagram')

    def send(self,
             data: util.Bytes,
             remote_addr: DatagramAddress | None = None):
        if not self._transport:
            raise ConnectionError()

        if remote_addr is None:
            addr = None

        elif isinstance(remote_addr, UdpAddress):
            addr = tuple(remote_addr)

        elif isinstance(remote_addr, common.UnixAddress):
            addr = str(remote_addr)

        else:
            raise TypeError('unsupported address type')

        msg = data, addr
        self._comm_log.log(common.CommLogAction.SEND, msg)

        self._transport.sendto(msg[0], msg[1])

    async def receive(self) -> tuple[util.Bytes, DatagramAddress | None]:
        try:
            data, addr = await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

        if isinstance(addr, tuple):
            addr = UdpAddress(*addr)

        elif isinstance(addr, str):
            addr = common.UnixAddress(addr)

        return data, addr

    def close(self):
        self._receive_queue.close()

        if self._transport:
            self._transport.close()

        self._transport = None

    async def wait_closed(self):
        await self._closed.wait()


def _get_address_family(datagram_type: DatagramType) -> socket.AddressFamily:
    if datagram_type == DatagramType.UDP:
        return socket.AddressFamily.AF_UNSPEC

    if datagram_type == DatagramType.UNIX:
        return socket.AddressFamily.AF_UNIX

    raise ValueError('unsupported datagram type')


def _get_endpoint_info(datagram_type: DatagramType,
                       name: str | None,
                       transport: asyncio.Transport
                       ) -> EndpointInfo:
    sockname = transport.get_extra_info('sockname')
    peername = transport.get_extra_info('peername')

    if datagram_type == DatagramType.UDP:
        return UdpEndpointInfo(
            name=name,
            local_addr=UdpAddress(sockname[0], sockname[1]),
            remote_addr=(UdpAddress(peername[0], peername[1])
                         if peername else None))

    if datagram_type == DatagramType.UNIX:
        return UnixEndpointInfo(
            name=name,
            local_addr=(common.UnixAddress(sockname) if sockname else None),
            remote_addr=(common.UnixAddress(peername) if peername else None))

    raise ValueError('unsupported endpoint type')


def _create_logger(info: EndpointInfo) -> logging.LoggerAdapter:
    if isinstance(info, UdpEndpointInfo):
        meta_type = 'UdpEndpoint'

    elif isinstance(info, UnixEndpointInfo):
        meta_type = 'UnixEndpoint'

    else:
        raise TypeError('unsupported info type')

    extra = {'meta': {'type': meta_type,
                      **endpoint_info_to_json(info)}}

    return logging.LoggerAdapter(mlog, extra)


class _CommunicationLogger:

    def __init__(self, info: EndpointInfo | None):
        if info:
            self._log = _create_logger(info)
            self._log.extra['meta']['communication'] = True

        else:
            self._log = mlog

    def log(self,
            action: common.CommLogAction,
            msg: tuple[util.Bytes, tuple | str | None] | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if msg is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s (data=(%s) remote=%s)',
                            action.value, msg[0].hex(' '), msg[1],
                            stacklevel=2)
