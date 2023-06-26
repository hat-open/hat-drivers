"""Asyncio serial communication driver"""

from hat.drivers.serial.common import (ByteSize,
                                       Parity,
                                       StopBits,
                                       Endpoint)

from hat.drivers.serial import py_serial

try:
    from hat.drivers.serial import native_serial

except ImportError:
    native_serial = None


__all__ = ['ByteSize',
           'Parity',
           'StopBits',
           'Endpoint',
           'create',
           'py_serial',
           'native_serial']


async def create(port: str, *,
                 baudrate: int = 9600,
                 bytesize: ByteSize = ByteSize.EIGHTBITS,
                 parity: Parity = Parity.NONE,
                 stopbits: StopBits = StopBits.ONE,
                 xonxoff: bool = False,
                 rtscts: bool = False,
                 dsrdtr: bool = False,
                 silent_interval: float = 0
                 ) -> Endpoint:
    """Open serial port

    Args:
        port: port name dependent of operating system
            (e.g. `/dev/ttyUSB0`, `COM3`, ...)
        baudrate: baud rate
        bytesize: number of data bits
        parity: parity checking
        stopbits: number of stop bits
        xonxoff: enable software flow control
        rtscts: enable hardware RTS/CTS flow control
        dsrdtr: enable hardware DSR/DTR flow control
        silent_interval: minimum time in seconds between writing two
            consecutive messages

    """
    impl = native_serial or py_serial
    return await impl.create(port=port,
                             baudrate=baudrate,
                             bytesize=bytesize,
                             parity=parity,
                             stopbits=stopbits,
                             xonxoff=xonxoff,
                             rtscts=rtscts,
                             dsrdtr=dsrdtr,
                             silent_interval=silent_interval)
