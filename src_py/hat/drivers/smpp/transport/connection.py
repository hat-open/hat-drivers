import asyncio
import itertools
import logging
import typing

from hat import aio

from hat.drivers import tcp
from hat.drivers.smpp.transport import common
from hat.drivers.smpp.transport import encoder


mlog: logging.Logger = logging.getLogger(__name__)

RequestCb: typing.TypeAlias = aio.AsyncCallable[
    [common.Request],
    common.Response | common.CommandStatus]

NotificationCb: typing.TypeAlias = aio.AsyncCallable[
    [common.Notification],
    None]


class Connection(aio.Resource):

    def __init__(self,
                 conn: tcp.Connection,
                 request_cb: RequestCb | None,
                 notification_cb: NotificationCb | None):
        self._conn = conn
        self._request_cb = request_cb
        self._notification_cb = notification_cb
        self._loop = asyncio.get_running_loop()
        self._next_sequence_number = ((i % 0x7ffffffe) + 1
                                      for i in itertools.count(0))
        self._sequence_number_futures = {}

        if self.is_open:
            self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    async def send(self,
                   request: common.Request
                   ) -> common.Response | common.CommandStatus:
        if not self.is_open:
            raise ConnectionError()

        sequence_number = next(self._next_sequence_number)
        if sequence_number in self._sequence_number_futures:
            raise Exception('sequence number in use')

        future = self._loop.create_future()
        self._sequence_number_futures[sequence_number] = future

        try:
            await self._send(command_id=_get_request_command_id(request),
                             command_status=common.CommandStatus.ESME_ROK,
                             sequence_number=sequence_number,
                             body=request)

            return await future

        finally:
            self._sequence_number_futures.pop(sequence_number)

    async def notify(self, notification: common.Notification):
        if not self.is_open:
            raise ConnectionError()

        sequence_number = next(self._next_sequence_number)
        if sequence_number in self._sequence_number_futures:
            raise Exception('sequence number in use')

        await self._send(command_id=_get_notification_command_id(notification),
                         command_status=common.CommandStatus.ESME_ROK,
                         sequence_number=sequence_number,
                         body=notification)

    async def _receive_loop(self):
        try:
            while True:
                header_bytes = await self._conn.readexactly(
                    encoder.header_length)

                try:
                    header = encoder.decode_header(header_bytes)

                except encoder.CommandStatusError as e:
                    sequence_number = encoder.decode_sequence_number(
                        header_bytes)

                    await self._send(command_id=encoder.GENERIC_NACK,
                                     command_status=e.command_status,
                                     sequence_number=sequence_number,
                                     body=None)

                    raise

                body_bytes = await self._conn.readexactly(
                    header.command_length - encoder.header_length)

                if header.command_id in _request_command_ids:
                    await self._process_request(header=header,
                                                body_bytes=body_bytes)

                elif header.command_id in _response_command_ids:
                    self._process_response(header=header,
                                           body_bytes=body_bytes)

                elif header.command_id in _notification_command_ids:
                    await self._process_notification(header=header,
                                                     body_bytes=body_bytes)

                else:
                    raise Exception('invalid command id')

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error('receive loop error: %s', e, exc_info=e)

        finally:
            self.close()

            for future in self._sequence_number_futures.values():
                if not future.done():
                    future.cancel()

    async def _process_request(self, header, body_bytes):
        if not self._request_cb:
            res_command_status = common.CommandStatus.ESME_RINVCMDID

        elif header.command_status != common.CommandStatus.ESME_ROK:
            res_command_status = common.CommandStatus.ESME_RUNKNOWNERR

        else:
            try:
                req = encoder.decode_body(header.command_id, body_bytes)
                res_command_status = common.CommandStatus.ESME_ROK

            except encoder.CommandStatusError as e:
                res_command_status = e.command_status

            except Exception:
                res_command_status = common.CommandStatus.ESME_RUNKNOWNERR

        if res_command_status == common.CommandStatus.ESME_ROK:
            try:
                res = await aio.call(self._request_cb, req)

                if isinstance(res, common.CommandStatus):
                    if res == common.CommandStatus.ESME_ROK:
                        res_command_status = common.CommandStatus.ESME_RSYSERR

                    else:
                        res_command_status = res

                    res = None

            except Exception:
                res_command_status = common.CommandStatus.ESME_RSYSERR
                res = None

        else:
            res = None

        res_command_id = encoder.CommandId(header.command_id.value |
                                           0x80000000)

        if res is not None and _get_response_command_id(res) != res_command_id:
            res_command_status = common.CommandStatus.ESME_RSYSERR
            res = None

        await self._send(command_id=res_command_id,
                         command_status=res_command_status,
                         sequence_number=header.sequence_number,
                         body=res)

    def _process_response(self, header, body_bytes):
        future = self._sequence_number_futures.get(header.sequence_number)
        if not future or future.done():
            return

        if header.command_status != common.CommandStatus.ESME_ROK:
            future.set_result(header.command_status)
            return

        try:
            res = encoder.decode_body(header.command_id, body_bytes)

        except Exception:
            future.set_result(common.CommandStatus.ESME_RUNKNOWNERR)
            return

        future.set_result(res)

    async def _process_notification(self, header, body_bytes):
        if not self._notification_cb:
            return

        try:
            notification = encoder.decode_body(header.command_id, body_bytes)
            await aio.call(self._notification_cb, notification)

        except Exception:
            return

    async def _send(self, command_id, command_status, sequence_number, body):
        body_bytes = encoder.encode_body(body) if body is not None else b''

        header = encoder.Header(
            command_length=encoder.header_length + len(body_bytes),
            command_id=command_id,
            command_status=command_status,
            sequence_number=sequence_number)
        header_bytes = encoder.encode_header(header)

        pdu_bytes = bytearray(len(header_bytes) + len(body_bytes))
        pdu_bytes[:len(header_bytes)] = header_bytes
        pdu_bytes[len(header_bytes):] = body_bytes

        await self._conn.write(pdu_bytes)


def _get_request_command_id(request):
    if isinstance(request, common.BindReq):
        if request.bind_type == common.BindType.TRANSMITTER:
            return encoder.CommandId.BIND_TRANSMITTER_REQ

        elif request.bind_type == common.BindType.RECEIVER:
            return encoder.CommandId.BIND_RECEIVER_REQ

        elif request.bind_type == common.BindType.TRANSCEIVER:
            return encoder.CommandId.BIND_TRANSCEIVER_REQ

        else:
            raise ValueError('unsupported bind type')

    if isinstance(request, common.UnbindReq):
        return encoder.CommandId.UNBIND_REQ

    if isinstance(request, common.SubmitSmReq):
        return encoder.CommandId.SUBMIT_SM_REQ

    if isinstance(request, common.SubmitMultiReq):
        return encoder.CommandId.SUBMIT_MULTI_REQ

    if isinstance(request, common.DeliverSmReq):
        return encoder.CommandId.DELIVER_SM_REQ

    if isinstance(request, common.DataSmReq):
        return encoder.CommandId.DATA_SM_REQ

    if isinstance(request, common.QuerySmReq):
        return encoder.CommandId.QUERY_SM_REQ

    if isinstance(request, common.CancelSmReq):
        return encoder.CommandId.CANCEL_SM_REQ

    if isinstance(request, common.ReplaceSmReq):
        return encoder.CommandId.REPLACE_SM_REQ

    if isinstance(request, common.EnquireLinkReq):
        return encoder.CommandId.ENQUIRE_LINK_REQ

    raise TypeError('unsupported request type')


def _get_response_command_id(response):
    if isinstance(response, common.BindRes):
        if response.bind_type == common.BindType.TRANSMITTER:
            return encoder.CommandId.BIND_TRANSMITTER_RESP

        elif response.bind_type == common.BindType.RECEIVER:
            return encoder.CommandId.BIND_RECEIVER_RESP

        elif response.bind_type == common.BindType.TRANSCEIVER:
            return encoder.CommandId.BIND_TRANSCEIVER_RESP

        else:
            raise ValueError('unsupported bind type')

    if isinstance(response, common.UnbindRes):
        return encoder.CommandId.UNBIND_RESP

    if isinstance(response, common.SubmitSmRes):
        return encoder.CommandId.SUBMIT_SM_RESP

    if isinstance(response, common.SubmitMultiRes):
        return encoder.CommandId.SUBMIT_MULTI_RESP

    if isinstance(response, common.DeliverSmRes):
        return encoder.CommandId.DELIVER_SM_RESP

    if isinstance(response, common.DataSmRes):
        return encoder.CommandId.DATA_SM_RESP

    if isinstance(response, common.QuerySmRes):
        return encoder.CommandId.QUERY_SM_RESP

    if isinstance(response, common.CancelSmRes):
        return encoder.CommandId.CANCEL_SM_RESP

    if isinstance(response, common.ReplaceSmRes):
        return encoder.CommandId.REPLACE_SM_RESP

    if isinstance(response, common.EnquireLinkRes):
        return encoder.CommandId.ENQUIRE_LINK_RESP

    raise TypeError('unsupported response type')


def _get_notification_command_id(notification):
    if isinstance(notification, common.OutbindNotification):
        return encoder.CommandId.OUTBIND

    if isinstance(notification, common.AlertNotification):
        return encoder.CommandId.ALERT_NOTIFICATION

    raise TypeError('unsupported notification type')


_request_command_ids = {
    encoder.CommandId.BIND_RECEIVER_REQ,
    encoder.CommandId.BIND_TRANSMITTER_REQ,
    encoder.CommandId.QUERY_SM_REQ,
    encoder.CommandId.SUBMIT_SM_REQ,
    encoder.CommandId.DELIVER_SM_REQ,
    encoder.CommandId.UNBIND_REQ,
    encoder.CommandId.REPLACE_SM_REQ,
    encoder.CommandId.CANCEL_SM_REQ,
    encoder.CommandId.BIND_TRANSCEIVER_REQ,
    encoder.CommandId.ENQUIRE_LINK_REQ,
    encoder.CommandId.SUBMIT_MULTI_REQ,
    encoder.CommandId.DATA_SM_REQ}

_response_command_ids = {
    encoder.CommandId.GENERIC_NACK,
    encoder.CommandId.BIND_RECEIVER_RESP,
    encoder.CommandId.BIND_TRANSMITTER_RESP,
    encoder.CommandId.QUERY_SM_RESP,
    encoder.CommandId.SUBMIT_SM_RESP,
    encoder.CommandId.DELIVER_SM_RESP,
    encoder.CommandId.UNBIND_RESP,
    encoder.CommandId.REPLACE_SM_RESP,
    encoder.CommandId.CANCEL_SM_RESP,
    encoder.CommandId.BIND_TRANSCEIVER_RESP,
    encoder.CommandId.ENQUIRE_LINK_RESP,
    encoder.CommandId.SUBMIT_MULTI_RESP,
    encoder.CommandId.DATA_SM_RESP}

_notification_command_ids = {
    encoder.CommandId.OUTBIND,
    encoder.CommandId.ALERT_NOTIFICATION}
