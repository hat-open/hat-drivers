import logging

from hat import aio

from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import encoder
from hat.drivers.iec60870.link import logger


mlog: logging.Logger = logging.getLogger(__name__)


async def create(port: str,
                 address_size: common.AddressSize,
                 direction_valid: bool,
                 **kwargs
                 ) -> 'Endpoint':
    """Create serial endpoint

    Additional arguments are passed directly to `hat.drivers.serial.create`.

    """
    endpoint = await serial.create(port, **kwargs)

    return Endpoint(endpoint, address_size, direction_valid)


class Endpoint(aio.Resource):
    """Serial endpoint"""

    def __init__(self,
                 endpoint: serial.Endpoint,
                 address_size: common.AddressSize,
                 direction_valid: bool):
        self._endpoint = endpoint
        self._encoder = encoder.Encoder(address_size=address_size,
                                        direction_valid=direction_valid)
        self._data = memoryview(bytes())
        self._log = logger.create_logger(mlog, endpoint.info)
        self._comm_log = logger.CommunicationLogger(mlog, endpoint.info)

        self.async_group.spawn(aio.call_on_cancel, self._comm_log.log,
                               common.CommLogAction.CLOSE)
        self._comm_log.log(common.CommLogAction.OPEN)

    @property
    def async_group(self):
        """Async group"""
        return self._endpoint.async_group

    @property
    def info(self) -> serial.EndpointInfo:
        return self._endpoint.info

    async def receive(self) -> common.Frame:
        """Receive"""
        while True:
            try:
                size = self._encoder.get_next_frame_size(self._data)

            except Exception:
                self._data = self._data[1:]
                continue

            if len(self._data) < size:
                data = await self._endpoint.read(size - len(self._data))
                self._data = memoryview(b''.join([self._data, data]))
                continue

            try:
                data, self._data = self._data[:size], self._data[size:]
                msg = self._encoder.decode(data)

                self._comm_log.log(common.CommLogAction.RECEIVE, msg)

                return msg

            except Exception as e:
                self._log.error("error decoding message: %s", e, exc_info=e)

    async def send(self, msg: common.Frame):
        """Send"""
        data = self._encoder.encode(msg)

        self._comm_log.log(common.CommLogAction.SEND, msg)

        await self._endpoint.write(data)

    async def drain(self):
        """Drain"""
        await self._endpoint.drain()
