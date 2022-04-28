import logging
import typing

from hat import aio
from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


mlog: logging.Logger = logging.getLogger(__name__)
"""Module logger"""


async def create_listener(local_addr: udp.Address = udp.Address('0.0.0.0', 162)
                          ) -> 'Listener':
    """Create listener"""
    listener = Listener()
    listener._receive_queue = aio.Queue()

    listener._endpoint = await udp.create(local_addr=local_addr,
                                          remote_addr=None)

    listener.async_group.spawn(listener._receive_loop)

    return listener


class Listener(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._endpoint.async_group

    async def receive(self) -> typing.Tuple[common.Context,
                                            common.Trap,
                                            udp.Address]:
        """Receive trap

        For v1 and v2c, context's name is used as community name.

        """
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _receive_loop(self):
        try:
            while True:
                msg_bytes, addr = await self._udp.receive()

                try:
                    msg = encoder.decode(msg_bytes)

                except Exception as e:
                    mlog.warning("could not decode message from %s: %s",
                                 addr, e, exc_info=e)
                    continue

                if isinstance(msg, common.MsgV1):
                    context = common.Context(None, msg.community)

                elif isinstance(msg, common.MsgV2C):
                    context = common.Context(None, msg.community)

                elif isinstance(msg, common.MsgV3):
                    context = msg.context

                else:
                    raise ValueError('unsupported message type')

                print(msg)

                # if not isinstance(msg.pdu, common.TrapPdu):
                #     mlog.warning("received not trap pdu from %s", addr)
                #     continue

                # trap = common.Trap(oid=msg.pdu.enterprise,
                #                    timestamp=msg.pdu.timestamp,
                #                    data=msg.pdu.data)
                # self._receive_queue.put_nowait((context, trap, addr))

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._receive_queue.close()
