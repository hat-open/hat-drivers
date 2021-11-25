from hat.drivers import serial
from hat.drivers.iec60870.link import common
from hat.drivers.iec60870.link.connection import Connection


async def connect(is_master: bool,
                  port: str,
                  baudrate: int = 9600,
                  bytesize: serial.ByteSize = serial.ByteSize.EIGHTBITS,
                  parity: serial.Parity = serial.Parity.NONE,
                  stopbits: serial.StopBits = serial.StopBits.ONE,
                  xonxoff: bool = False,
                  rtscts: bool = False,
                  dsrdtr: bool = False,
                  silent_interval: float = 0,
                  address_size: common.AddressSize = common.AddressSize.ZERO,
                  addr: int = 0,
                  response_timeout: float = 15,
                  send_retry_count: int = 3
                  ) -> Connection:
    pass


class _Connection(Connection):

    @property
    def async_group(self):
        return self._async_group

    async def send(self, data: common.Bytes):
        pass

    async def receive(self) -> common.Bytes:
        pass
