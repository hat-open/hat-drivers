import logging

from hat import aio

from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import encoder


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

    @property
    def async_group(self):
        """Async group"""
        return self._endpoint.async_group

    async def receive(self) -> common.Frame:
        """Receive"""
        while True:
            msg_bytes = bytearray()

            while True:
                try:
                    size = self._encoder.get_next_frame_size(msg_bytes)

                except Exception:
                    msg_bytes = msg_bytes[1:]
                    continue

                if len(msg_bytes) >= size:
                    break

                data = await self._endpoint.read(size - len(msg_bytes))
                msg_bytes.extend(data)

            try:
                return self._encoder.decode(memoryview(msg_bytes))

            except Exception as e:
                mlog.error("error decoding message: %s", e, exc_info=e)

    async def send(self, msg: common.Frame):
        """Send"""
        data = self._encoder.encode(msg)
        await self._endpoint.write(data)

    async def drain(self):
        """Drain"""
        await self._endpoint.drain()
