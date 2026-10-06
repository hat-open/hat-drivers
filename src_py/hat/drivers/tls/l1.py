import abc
import asyncio
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import serial
from hat.drivers import net


mlog: logging.Logger = logging.getLogger(__name__)


LinkInfo: typing.TypeAlias = net.ConnectionInfo | serial.EndpointInfo


class Link(aio.Resource):

    @property
    @abc.abstractmethod
    async def info(self) -> LinkInfo:
        pass

    @abc.abstractmethod
    async def read(self, size: int) -> util.Bytes:
        pass

    @abc.abstractmethod
    async def write(self, data: util.Bytes):
        pass

    @abc.abstractmethod
    async def drain(self):
        pass


LinkCb: typing.TypeAlias = aio.AsyncCallable[[Link], None]

Endpoint: typing.TypeAlias = aio.Resource


async def create_net_server_endpoint(link_cb: LinkCb,
                                     addr: net.StreamAddress,
                                     *,
                                     bind_connections: bool = True,
                                     **kwargs
                                     ) -> Endpoint:
    """Create network server endpoint"""

    async def on_connection(conn):
        await _on_link(link_cb, _NetLink(conn))

    return await net.listen(on_connection, addr,
                            bind_connections=bind_connections,
                            **kwargs)


async def create_net_client_endpoint(link_cb: LinkCb,
                                     addr: net.StreamAddress,
                                     reconnect_delay: float,
                                     **kwargs
                                     ) -> Endpoint:
    """Create network client endpoint"""
    async_group = aio.Group()

    async def connection_loop():
        link = None

        try:
            while True:
                try:
                    link = _NetLink(await net.connect(addr, **kwargs))

                except Exception:
                    await asyncio.sleep(reconnect_delay)
                    continue

                link.async_group.spawn(_on_link, link_cb, link)

                await link.wait_closed()

        except Exception as e:
            mlog.error("net client endpoint error: %s", e, exc_info=e)

        finally:
            async_group.close()

            if link:
                await aio.uncancellable(link.async_close())

    async_group.spawn(connection_loop)
    return async_group


async def create_serial_endpoint(link_cb: LinkCb,
                                 port: str,
                                 reconnect_delay: float,
                                 **kwargs
                                 ) -> Endpoint:
    """Create serial endpoint"""
    async_group = aio.Group()

    async def connection_loop():
        link = None

        try:
            while True:
                try:
                    link = _SerialLink(await serial.create(port, **kwargs))

                except Exception:
                    await asyncio.sleep(reconnect_delay)
                    continue

                link.async_group.spawn(_on_link, link_cb, link)

                await link.wait_closed()

        except Exception as e:
            mlog.error("serial endpoint error: %s", e, exc_info=e)

        finally:
            async_group.close()

            if link:
                await aio.uncancellable(link.async_close())

    async_group.spawn(connection_loop)
    return async_group


class _NetLink(Link):

    def __init__(self, conn: net.Connection):
        self._conn = conn

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    @property
    def info(self) -> LinkInfo:
        return self._conn.info

    async def read(self, size: int) -> util.Bytes:
        return await self._conn.readexactly(size)

    async def write(self, data: util.Bytes):
        await self._conn.write(data)

    async def drain(self):
        await self._conn.drain()


class _SerialLink(Link):

    def __init__(self, endpoint: serial.Endpoint):
        self._endpoint = endpoint

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    @property
    def info(self) -> LinkInfo:
        return self._endpoint.info

    async def read(self, size: int) -> util.Bytes:
        return await self._endpoint.read(size)

    async def write(self, data: util.Bytes):
        await self._endpoint.write(data)

    async def drain(self):
        await self._endpoint.drain()


async def _on_link(link_cb: LinkCb,
                   link: Link):
    try:
        await aio.call(link_cb, link)

    except Exception as e:
        mlog.error('link callback error: %s', e, exc_info=e)
        link.close()
