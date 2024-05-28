import asyncio
import itertools
import logging

from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import encoder
from hat.drivers.snmp.manager import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_v2c_manager(remote_addr: udp.Address,
                             community: common.CommunityName = 'public'
                             ) -> common.Manager:
    """Create v2c manager"""
    endpoint = await udp.create(local_addr=None,
                                remote_addr=remote_addr)

    try:
        return V2CManager(endpoint=endpoint,
                          community=community)

    except BaseException:
        await aio.uncancellable(endpoint.async_close())
        raise


class V2CManager(common.Manager):

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
        return self._endpoint.async_group

    async def send(self, req: common.Request) -> common.Response:
        if not self.is_open:
            raise ConnectionError()

        if isinstance(req, common.GetDataReq):
            msg_type = encoder.v2c.MsgType.GET_REQUEST

        elif isinstance(req, common.GetNextDataReq):
            msg_type = encoder.v2c.MsgType.GET_NEXT_REQUEST

        elif isinstance(req, common.GetBulkDataReq):
            msg_type = encoder.v2c.MsgType.GET_BULK_REQUEST

        elif isinstance(req, common.SetDataReq):
            msg_type = encoder.v2c.MsgType.SET_REQUEST

        else:
            raise ValueError('unsupported request')

        request_id = next(self._next_request_ids)

        if isinstance(req, common.SetDataReq):
            data = req.data

        else:
            data = [common.UnspecifiedData(name=name) for name in req.names]

        if isinstance(req, common.GetBulkDataReq):
            pdu = encoder.v2c.BulkPdu(request_id=request_id,
                                      non_repeaters=0,
                                      max_repetitions=0,
                                      data=data)

        else:
            pdu = encoder.v2c.BasicPdu(
                request_id=request_id,
                error=common.Error(common.ErrorType.NO_ERROR, 0),
                data=data)

        msg = encoder.v2c.Msg(type=msg_type,
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

                    res = (msg.pdu.data
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
