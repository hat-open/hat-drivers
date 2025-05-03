import asyncio
import contextlib

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.smpp import common
from hat.drivers.smpp import transport


async def connect(addr: tcp.Address,
                  system_id: str = '',
                  password: str = '',
                  close_timeout: float = 1,
                  enquire_link_delay: float | None = None,
                  enquire_link_timeout: float = 10
                  ) -> 'Client':
    client = Client()
    client._async_group = aio.Group()
    client._equire_link_event = asyncio.Event()
    client._bound = False

    conn = await tcp.connect(addr)
    client._conn = transport.Connection(
        conn=conn,
        request_cb=client._on_request,
        notification_cb=client._on_notification)

    try:
        client.async_group.spawn(aio.call_on_cancel, client._on_close,
                                 close_timeout)
        client.async_group.spawn(aio.call_on_done, conn.wait_closing(),
                                 client.close)

        req = transport.BindReq(
            bind_type=transport.BindType.TRANSCEIVER,
            system_id=system_id,
            password=password,
            system_type='',
            interface_version=0x34,
            addr_ton=transport.TypeOfNumber.UNKNOWN,
            addr_npi=transport.NumericPlanIndicator.UNKNOWN,
            address_range='')
        await client._send(req)

        client._bound = True

        if enquire_link_delay is not None:
            client.async_group.spawn(client._enquire_link_loop,
                                     enquire_link_delay, enquire_link_timeout)

    except BaseException:
        await aio.uncancellable(client.async_close())
        raise

    return client


class Client(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._async_group

    async def send_message(self,
                           dst_addr: str,
                           msg: util.Bytes,
                           *,
                           short_message: bool = True,
                           priority: common.Priority = common.Priority.BULK,
                           udhi: bool = False,
                           dst_ton: common.TypeOfNumber = common.TypeOfNumber.UNKNOWN,  # NOQA
                           src_ton: common.TypeOfNumber = common.TypeOfNumber.UNKNOWN,  # NOQA
                           src_addr: str = '',
                           data_coding: common.DataCoding = common.DataCoding.DEFAULT  # NOQA
                           ) -> common.MessageId:
        optional_params = {}
        gsm_features = set()

        if not short_message:
            optional_params[transport.OptionalParamTag.MESSAGE_PAYLOAD] = msg

        if udhi:
            gsm_features.add(transport.GsmFeature.UDHI)

        req = transport.SubmitSmReq(
            service_type='',
            source_addr_ton=src_ton,
            source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
            source_addr=src_addr,
            dest_addr_ton=dst_ton,
            dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
            destination_addr=dst_addr,
            esm_class=transport.EsmClass(
                messaging_mode=transport.MessagingMode.DEFAULT,
                message_type=transport.MessageType.DEFAULT,
                gsm_features=gsm_features),
            protocol_id=0,
            priority_flag=priority,
            schedule_delivery_time=None,
            validity_period=None,
            registered_delivery=transport.RegisteredDelivery(
                delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
                acknowledgements=set(),
                intermediate_notification=False),
            replace_if_present_flag=False,
            data_coding=data_coding,
            sm_default_msg_id=0,
            short_message=(msg if short_message else b''),
            optional_params=optional_params)

        res = await self._send(req)

        return res.message_id

    async def _on_close(self, timeout):
        if self._bound:
            with contextlib.suppress(Exception):
                await aio.wait_for(self._conn.send(transport.UnbindReq()),
                                   timeout)

        await self._conn.async_close()

    async def _on_request(self, req):
        self._equire_link_event.set()

        if isinstance(req, transport.UnbindReq):
            self._bound = False
            self.async_group.spawn(aio.call, self.close)
            return transport.UnbindRes()

        if isinstance(req, transport.DataSmReq):
            # TODO
            return transport.CommandStatus.ESME_RINVCMDID

        if isinstance(req, transport.DeliverSmReq):
            # TODO
            return transport.DeliverSmRes()

        if isinstance(req, transport.EnquireLinkReq):
            return transport.EnquireLinkRes()

        return transport.CommandStatus.ESME_RINVCMDID

    async def _on_notification(self, notification):
        self._equire_link_event.set()

        if isinstance(notification, transport.OutbindNotification):
            # TODO
            pass

        if isinstance(notification, transport.AlertNotification):
            # TODO
            pass

    async def _enquire_link_loop(self, delay, timeout):
        try:
            while True:
                self._equire_link_event.clear()

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._equire_link_event.wait(), delay)
                    continue

                if self._bound:
                    await aio.wait_for(
                        self._conn.send(transport.EnquireLinkReq()), timeout)

        except ConnectionError:
            pass

        except asyncio.TimeoutError:
            pass

        except Exception:
            pass

        finally:
            self.close()

    async def _send(self, req):
        res = await self._conn.send(req)
        self._equire_link_event.set()

        if isinstance(res, transport.CommandStatus):
            error_str = transport.command_status_descriptions[res]
            raise Exception(f'command error response: {error_str}')

        return res
