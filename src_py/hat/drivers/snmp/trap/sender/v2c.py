import asyncio
import itertools
import logging

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp.trap.sender import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_v2c_trap_sender(remote_addr: udp.Address,
                                 community: common.CommunityName = 'public'
                                 ) -> common.TrapSender:
    """Create v2c trap sender"""
    endpoint = await udp.create(local_addr=None,
                                remote_addr=remote_addr)

    try:
        return V2CTrapSender(endpoint=endpoint,
                             community=community)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class V2CTrapSender(common.TrapSender):

    def __init__(self,
                 endpoint: udp.Endpoint,
                 community: common.CommunityName):
        self._endpoint = endpoint
        self._community = community
        self._loop = asyncio.get_running_loop()
        self._receive_futures = {}
        self._next_request_ids = itertools.count(1)

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._endpoint.async_group

    def send_trap(self, trap: common.Trap):
        """Send trap"""
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_ids)

        error = common.Error(common.ErrorType.NO_ERROR, 0)
        data = [common.TimeTicksData(name=(1, 3, 6, 1, 2, 1, 1, 3, 0),
                                     value=trap.timestamp),
                common.ObjectIdData(name=(1, 3, 6, 1, 6, 3, 1, 1, 4, 1, 0),
                                    value=trap.oid),
                *trap.data]

        pdu = encoder.v2c.BasicPdu(request_id=request_id,
                                   error=error,
                                   data=data)

        msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.SNMPV2_TRAP,
                              community=self._community,
                              pdu=pdu)
        msg_bytes = encoder.encode(msg)

        self._endpoint.send(msg_bytes)

    async def send_inform(self,
                          inform: common.Inform
                          ) -> common.Error | None:
        """Send inform"""
        if not self.is_open:
            raise ConnectionError()

        request_id = next(self._next_request_ids)

        error = common.Error(common.ErrorType.NO_ERROR, 0)

        pdu = encoder.v2c.BasicPdu(request_id=request_id,
                                   error=error,
                                   data=inform.data)

        msg = encoder.v2c.Msg(type=encoder.v2c.MsgType.INFORM_REQUEST,
                              community=self._community,
                              pdu=pdu)
        msg_bytes = encoder.encode(msg)

        future = self._loop.create_future()
        self._receive_futures[request_id] = future
        try:
            self._endpoint.send(msg_bytes)
            return await future

        finally:
            del self._receive_futures[request_id]

    async def _receive_loop(self):
        try:
            while True:
                msg_bytes, addr = await self._endpoint.receive()

                # TODO check address

                try:
                    msg = encoder.decode(msg_bytes)

                    if not isinstance(msg, encoder.v2c.Msg):
                        raise Exception('invalid version')

                    if msg.type != encoder.v2c.MsgType.RESPONSE:
                        raise Exception('invalid response message type')

                    if msg.community != self._community:
                        raise Exception('invalid community')

                    res = (None
                           if msg.pdu.error.type == common.ErrorType.NO_ERROR
                           else msg.pdu.error)

                    future = self._receive_futures[msg.pdu.request_id]
                    if not future.done():
                        future.set_result(res)

                except Exception as e:
                    mlog.warning("dropping message from %s: %s",
                                 addr, e, exc_info=e)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

            for future in self._receive_futures.values():
                if not future.done():
                    future.set_exception(ConnectionError())
