from hat.drivers.snmp.common import *  # NOQA

import abc

from hat import aio

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
