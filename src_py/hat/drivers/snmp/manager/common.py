from hat.drivers.snmp.common import *  # NOQA

import abc
import logging

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp.common import Request, Response


class Manager(aio.Resource):

    @abc.abstractmethod
    async def send(self, req: Request) -> Response:
        """Send request and wait for response"""


def create_logger_adapter(logger: logging.Logger,
                          info: udp.EndpointInfo):
    extra = {'meta': {'type': 'SnmpManager',
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': ({'host': info.remote_addr.host,
                                       'port': info.remote_addr.port}
                                      if info.remote_addr else None)}}

    return logging.LoggerAdapter(logger, extra)
