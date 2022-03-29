import asyncio
import itertools
import logging
import typing

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_master(context: common.Context,
                        remote_addr: udp.Address,
                        version: common.Version = common.Version.V2C
                        ) -> 'Master':
    """Create master

    For v1 and v2c, context's name is used as community name.

    """
    master = Master()
    master._context = context
    master._version = version
    master._receive_queue = None
    master._next_request_id = itertools.count(1)
    master._send_lock = asyncio.Lock()

    master._endpoint = await udp.create(local_addr=None,
                                        remote_addr=remote_addr)

    master._async_group.spawn(master._read_loop)

    return master


class Master(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._udp.async_group

    async def get_data(self,
                       names: typing.Iterable[common.ObjectIdentifier]
                       ) -> typing.Union[common.Error,
                                         typing.List[common.Data]]:
        """Get data"""
        data = [self._name_to_data(name)
                for name in names]
        return await self._send(common.MsgType.GET_REQUEST, data)

    async def get_next_data(self,
                            names: typing.Iterable[common.ObjectIdentifier]
                            ) -> typing.Union[common.Error,
                                              typing.List[common.Data]]:
        """Get next data"""
        data = [self._name_to_data(name)
                for name in names]
        return await self._send(common.MsgType.GET_NEXT_REQUEST, data)

    async def get_bulk_data(self,
                            names: typing.Iterable[common.ObjectIdentifier]
                            ) -> typing.Union[common.Error,
                                              typing.List[common.Data]]:
        """Get bulk data"""
        data = [self._name_to_data(name)
                for name in names]
        return await self._send(common.MsgType.GET_BULK_REQUEST, data)

    async def set_data(self,
                       data: typing.List[common.Data]
                       ) -> typing.Union[common.Error,
                                         typing.List[common.Data]]:
        """Set data"""
        return await self._send(common.MsgType.SET_REQUEST, data)

    async def inform(self,
                     data: typing.List[common.Data]
                     ) -> typing.Union[common.Error,
                                       typing.List[common.Data]]:
        """Inform"""
        return await self._send(common.MsgType.INFORM_REQUEST, data)

    async def _read_loop(self):
        try:
            while True:
                # TODO address
                msg_bytes, addr = await self._udp.receive()

                if self._receive_queue is None:
                    continue

                try:
                    msg = encoder.decode(msg_bytes)

                except Exception as e:
                    mlog.warning("could not decode message from %s: %s",
                                 addr, e, exc_info=e)
                    continue

                self._receive_queue.put_nowait(msg)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("read loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _send(self, msg_type, data):
        async with self._send_lock:
            pass
        # if msg_type == MsgType.GET_BULK_REQUEST:
        #     req_pdu = BulkPdu(request_id=self._request_id,
        #                       non_repeaters=0,
        #                       max_repetitions=0,
        #                       data=data)
        # else:
        #     req_pdu = BasicPdu(request_id=self._request_id,
        #                        error=Error(ErrorType.NO_ERROR, 0),
        #                        data=data)
        # req_msg = self._create_msg(msg_type, req_pdu)
        # req_msg_bytes = self._serializer.encode(req_msg)
        # self._request_id += 1

        # # TODO: resend, timeout, check request_id, ...
        # queue = util.Queue()
        # with self._response_cbs.register(queue.put_nowait):
        #     self._udp.send(req_msg_bytes)
        #     res_msg, _ = await queue.get()
        #     if res_msg.pdu.error.type != ErrorType.NO_ERROR:
        #         return res_msg.pdu.error
        #     return res_msg.pdu.data

    def _create_msg(self, msg_type, request_id, pdu):
        if self._version == common.Version.V1:
            return common.MsgV1(type=msg_type,
                                community=self._context.name,
                                pdu=pdu)

        if self._version == common.Version.V2C:
            return common.MsgV2C(type=msg_type,
                                 community=self._context.name,
                                 pdu=pdu)

        if self._version == common.Version.V3:
            return common.MsgV3(type=msg_type,
                                id=request_id,
                                reportable=False,
                                context=self._context,
                                pdu=pdu)

        raise ValueError('unsupported version')

    def _name_to_data(self, name):
        if self._version == common.Version.V1:
            return common.Data(type=common.DataType.EMPTY,
                               name=name,
                               value=None)

        if self._version == common.Version.V2C:
            return common.Data(type=common.DataType.UNSPECIFIED,
                               name=name,
                               value=None)

        if self._version == common.Version.V3:
            return common.Data(type=common.DataType.UNSPECIFIED,
                               name=name,
                               value=None)

        raise ValueError('unsupported version')
