import logging

from hat import aio
from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link import encoder


mlog: logging.Logger = logging.getLogger(__name__)


async def create(address_size: common.AddressSize,
                 direction_valid: bool,
                 port: str,
                 baudrate: int = 9600,
                 bytesize: serial.ByteSize = serial.ByteSize.EIGHTBITS,
                 parity: serial.Parity = serial.Parity.NONE,
                 stopbits: serial.StopBits = serial.StopBits.ONE,
                 xonxoff: bool = False,
                 rtscts: bool = False,
                 dsrdtr: bool = False
                 ) -> 'Endpoint':
    endpoint = Endpoint()
    endpoint._encoder = encoder.Encoder(address_size=address_size,
                                        direction_valid=direction_valid)

    endpoint._conn = await serial.create(port=port,
                                         baudrate=baudrate,
                                         bytesize=bytesize,
                                         parity=parity,
                                         stopbits=stopbits,
                                         xonxoff=xonxoff,
                                         rtscts=rtscts,
                                         dsrdtr=dsrdtr)

    return endpoint


class Endpoint(aio.Resource):

    @property
    def async_group(self):
        return self._conn.async_group

    async def receive(self) -> common.Frame:
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

                data = await self._conn.read(size - len(msg_bytes))
                msg_bytes.extend(data)

            try:
                return self._encoder.decode(memoryview(msg_bytes))

            except Exception as e:
                mlog.error("error decoding message: %s", e, exc_info=e)

    async def send(self, msg: common.Frame):
        data = self._encoder.encode(msg)
        await self._conn.write(data)
