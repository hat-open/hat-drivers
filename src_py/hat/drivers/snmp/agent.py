import logging

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


# TODO maybe add version?
RequestCb = aio.AsyncCallable[[common.Context, common.Request],
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
                msg_bytes, addr = await self._endpoint.receive()

                # TODO: process msg

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
