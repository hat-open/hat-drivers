import logging

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


RequestCb = aio.AsyncCallable[[common.Version, common.Context, common.Request],
                              common.Response]


async def create_agent(request_cb: RequestCb,
                       local_addr: udp.Address = udp.Address('0.0.0.0', 161)
                       ) -> 'Agent':
    """Create agent"""
    agent = Agent()
    agent._request_cb = request_cb

    agent._endpoint = await udp.create(local_addr=local_addr,
                                       remote_addr=None)

    agent.async_group.spawn(agent._receive_loop)

    return agent


class Agent(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    async def _receive_loop(self):
        try:
            while True:
                req_msg_bytes, addr = await self._endpoint.receive()

                try:
                    req_msg = encoder.decode(req_msg_bytes)
                    version, context, request_id, data, req = _decode_req_msg(
                        req_msg)

                except Exception as e:
                    mlog.warning("dropping message from %s: %s",
                                 addr, e, exc_info=e)
                    continue

                try:
                    res = await aio.call(self._request_cb, version, context,
                                         req)
                    res_msg = _encode_res_msg(version, context, request_id,
                                              data, res)
                    res_msg_bytes = encoder.encode(res_msg)

                except Exception as e:
                    mlog.warning("error processing request: %s", e, exc_info=e)
                    res_msg = _encode_err_msg(version, context, request_id,
                                              data)
                    res_msg_bytes = encoder.encode(res_msg)

                self._endpoint.send(res_msg_bytes, addr)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()


def _decode_req_msg(msg):
    if isinstance(msg, encoder.v1.Msg):
        version = common.Version.V1

    elif isinstance(msg, encoder.v2c.Msg):
        version = common.Version.V2C

    elif isinstance(msg, encoder.v3.Msg):
        version = common.Version.V3

    else:
        raise ValueError('unsupported message')

    if version == common.Version.V1:
        if msg.type == encoder.v1.MsgType.GET_REQUEST:
            req = common.GetDataReq([i.name for i in msg.pdu.data])

        elif msg.type == encoder.v1.MsgType.GET_NEXT_REQUEST:
            req = common.GetNextDataReq([i.name for i in msg.pdu.data])

        elif msg.type == encoder.v1.MsgType.SET_REQUEST:
            req = common.SetDataReq(msg.pdu.data)

        else:
            raise ValueError('unsupported message type')

    else:
        if msg.type == encoder.v2c.MsgType.GET_REQUEST:
            req = common.GetDataReq([i.name for i in msg.pdu.data])

        elif msg.type == encoder.v2c.MsgType.GET_NEXT_REQUEST:
            req = common.GetNextDataReq([i.name for i in msg.pdu.data])

        elif msg.type == encoder.v2c.MsgType.GET_BULK_REQUEST:
            req = common.GetBulkDataReq([i.name for i in msg.pdu.data])

        elif msg.type == encoder.v2c.MsgType.SET_REQUEST:
            req = common.SetDataReq(msg.pdu.data)

        else:
            raise ValueError('unsupported message type')

    context = (msg.context if version == common.Version.V3 else
               common.Context(engine_id=None, name=msg.community))
    request_id = msg.pdu.request_id
    data = msg.pdu.data

    return version, context, request_id, data, req


def _encode_res_msg(version, context, request_id, data, res):
    if isinstance(res, common.Error):
        if (version == common.Version.V1 and
                res.type.value > common.ErrorType.GEN_ERR.value):
            error = res._replace(type=common.ErrorType.GEN_ERR)

        else:
            error = res

    else:
        error = common.Error(common.ErrorType.NO_ERROR, 0)
        data = res

    pdu = encoder.v1.BasicPdu(request_id=request_id,
                              error=error,
                              data=data)

    if version == common.Version.V1:
        return encoder.v1.Msg(type=encoder.v1.MsgType.GET_RESPONSE,
                              community=context.name,
                              pdu=pdu)

    if version == common.Version.V2C:
        return encoder.v2c.Msg(type=encoder.v2c.MsgType.RESPONSE,
                               community=context.name,
                               pdu=pdu)

    if version == common.Version.V3:
        return encoder.v3.Msg(type=encoder.v3.MsgType.RESPONSE,
                              id=request_id,
                              reportable=False,
                              context=context,
                              pdu=pdu)

    raise ValueError('unsupported version')


def _encode_err_msg(version, context, request_id, data):
    error = common.Error(common.ErrorType.GEN_ERR, 0)
    pdu = encoder.v1.BasicPdu(request_id=request_id,
                              error=error,
                              data=data)

    if version == common.Version.V1:
        return encoder.v1.Msg(type=encoder.v1.MsgType.GET_RESPONSE,
                              community=context.name,
                              pdu=pdu)

    if version == common.Version.V2C:
        return encoder.v2c.Msg(type=encoder.v2c.MsgType.RESPONSE,
                               community=context.name,
                               pdu=pdu)

    if version == common.Version.V3:
        return encoder.v3.Msg(type=encoder.v3.MsgType.RESPONSE,
                              id=request_id,
                              reportable=False,
                              context=context,
                              pdu=pdu)

    raise ValueError('unsupported version')
