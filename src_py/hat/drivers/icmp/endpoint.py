import asyncio
import itertools
import logging
import math
import socket
import sys
import uuid

from hat import aio

from hat.drivers.icmp import common
from hat.drivers.icmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)


async def create_endpoint(local_host: str = '0.0.0.0') -> 'Endpoint':
    loop = asyncio.get_running_loop()
    local_addr = await _get_host_addr(loop, local_host)

    endpoint = Endpoint()
    endpoint._async_group = aio.Group()
    endpoint._loop = loop
    endpoint._echo_data = _echo_data_iter()
    endpoint._echo_futures = {}

    endpoint._socket = _create_socket(local_addr)

    endpoint.async_group.spawn(endpoint._receive_loop)

    return endpoint


class Endpoint(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._async_group

    async def ping(self, remote_host: str):
        if not self.is_open:
            raise ConnectionError()

        addr = await _get_host_addr(self._loop, remote_host)

        if not self.is_open:
            raise ConnectionError()

        data = next(self._echo_data)

        # on linux, echo message identifier is chaged to
        # `self._socket.getsockname()[1]`
        req = common.EchoMsg(is_reply=False,
                             identifier=1,
                             sequence_number=1,
                             data=data)
        req_bytes = encoder.encode_msg(req)

        future = self._loop.create_future()

        try:
            self._echo_futures[data] = future

            if sys.version_info[:2] >= (3, 11):
                await self._loop.sock_sendto(self._socket, req_bytes, addr)

            else:
                self._socket.sendto(req_bytes, addr)

            await future

        finally:
            self._echo_futures.pop(data)

    async def _receive_loop(self):
        try:
            while True:
                msg_bytes = await self._loop.sock_recv(self._socket, 1024)

                try:
                    msg = encoder.decode_msg(memoryview(msg_bytes))

                except Exception as e:
                    mlog.warning("error decoding message: %s", e, exc_info=e)
                    continue

                if isinstance(msg, common.EchoMsg):
                    self._process_echo_msg(msg)

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

            for future in self._echo_futures.values():
                if not future.done():
                    future.set_exception(ConnectionError())

            self._socket.close()

    def _process_echo_msg(self, msg):
        if not msg.is_reply:
            return

        # TODO check identifier and sequence number

        data = bytes(msg.data)

        future = self._echo_futures.get(data)
        if not future or future.done():
            return

        future.set_result(None)


def _create_socket(local_addr):
    s = socket.socket(family=socket.AF_INET,
                      type=socket.SOCK_DGRAM,
                      proto=socket.IPPROTO_ICMP)

    try:
        s.setblocking(False)
        s.bind(local_addr)

    except Exception:
        s.close()
        raise

    return s


async def _get_host_addr(loop, host):
    infos = await loop.getaddrinfo(host, None,
                                   family=socket.AF_INET,
                                   proto=socket.IPPROTO_ICMP)

    if not infos:
        raise Exception("could not resolve host addr")

    return infos[0][4]


def _echo_data_iter():
    prefix = uuid.uuid1().bytes

    for i in itertools.count(1):
        i_size = math.ceil(i.bit_length() / 8)

        yield prefix + i.to_bytes(i_size, 'big')
