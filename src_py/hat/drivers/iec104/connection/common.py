from hat.drivers.iec104.common import *  # NOQA

import logging

from hat.drivers import tcp


def create_logger_adapter(logger: logging.Logger,
                          communication: bool,
                          info: tcp.ConnectionInfo):
    extra = {'meta': {'type': 'Iec104Connection',
                      'communication': communication,
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(logger, extra)
