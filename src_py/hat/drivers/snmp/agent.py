import logging

from hat import aio
from hat.drivers import udp


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_agent(local_addr: udp.Address = udp.Address('0.0.0.0', 161)
                       ) -> 'Agent':
    """Create agent"""
    agent = Agent()

    agent._endpoint = await udp.create(local_addr=local_addr,
                                       remote_addr=None)

    return agent


class Agent(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group
