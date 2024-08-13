import logging

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp.trap.sender import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_v1_trap_sender(remote_addr: udp.Address,
                                community: common.CommunityName = 'public'
                                ) -> common.TrapSender:
    """Create v1 trap sender"""
    endpoint = await udp.create(local_addr=None,
                                remote_addr=remote_addr)

    try:
        return V1TrapSender(endpoint=endpoint,
                            community=community)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class V1TrapSender(common.TrapSender):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 community: common.CommunityName):
        self._endpoint = endpoint
        self._community = community
        self._addr = tuple(int(i)
                           for i in endpoint.info.local_addr.host.split('.'))

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    def send_trap(self, trap: common.Trap):
        """Send trap"""
        if not self.is_open:
            raise ConnectionError()

        pdu = encoder.v1.TrapPdu(enterprise=trap.oid,
                                 addr=self._addr,
                                 cause=trap.cause,
                                 timestamp=trap.timestamp,
                                 data=trap.data)

        msg = encoder.v1.Msg(type=encoder.v1.MsgType.TRAP,
                             community=self._community,
                             pdu=pdu)
        msg_bytes = encoder.encode(msg)

        self._endpoint.send(msg_bytes)

    async def send_inform(self,
                          inform: common.Inform
                          ) -> common.Error | None:
        """Send inform"""
        raise Exception('inform not supported')
