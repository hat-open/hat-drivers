from hat.drivers.snmp.common import *  # NOQA

import abc

from hat import aio

from hat.drivers.snmp.common import Request, Response


class Manager(aio.Resource):

    @abc.abstractmethod
    async def send(self, req: Request) -> Response:
        """Send request and wait for response"""
