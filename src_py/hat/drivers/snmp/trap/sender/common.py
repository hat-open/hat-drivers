from hat.drivers.snmp.common import *  # NOQA

import abc
import logging

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp.common import Error, Inform, Trap


class TrapSender(aio.Resource):

    @abc.abstractmethod
    def send_trap(self, trap: Trap):
        """Send trap"""

    @abc.abstractmethod
    async def send_inform(self,
                          inform: Inform
                          ) -> Error | None:
        """Send inform"""


def create_logger_adapter(logger: logging.Logger,
                          communication: bool,
                          info: udp.EndpointInfo):
    extra = {'meta': {'type': 'SnmpTrapSender',
                      'communication': communication,
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': ({'host': info.remote_addr.host,
                                       'port': info.remote_addr.port}
                                      if info.remote_addr else None)}}

    return logging.LoggerAdapter(logger, extra)
