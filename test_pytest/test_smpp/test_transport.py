import asyncio
import datetime
import pytest

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.smpp import transport


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def create_server(addr,
                        request_cb=None,
                        notification_cb=None):

    async def on_connection(conn):
        conn = transport.Connection(conn=conn,
                                    request_cb=request_cb,
                                    notification_cb=notification_cb)

    return await tcp.listen(connection_cb=on_connection,
                            addr=addr,
                            bind_connections=True)


async def test_connection(addr):
    server = await create_server(addr)

    tcp_conn = await tcp.connect(addr)
    conn = transport.Connection(conn=tcp_conn,
                                request_cb=None,
                                notification_cb=None)

    assert conn.is_open

    tcp_conn.close()
    assert not conn.is_open
    await conn.wait_closed()

    await server.async_close()


async def test_connection_tcp_closed(addr):
    server = await create_server(addr)

    tcp_conn = await tcp.connect(addr)
    await tcp_conn.async_close()

    with pytest.raises(Exception):
        transport.Connection(conn=tcp_conn,
                             request_cb=None,
                             notification_cb=None)

    await server.async_close()


async def test_tcp_closes_on_conn_close(addr):
    server = await create_server(addr)

    tcp_conn = await tcp.connect(addr)

    conn = transport.Connection(conn=tcp_conn,
                                request_cb=None,
                                notification_cb=None)

    conn.close()

    await tcp_conn.wait_closed()
    await conn.wait_closed()

    await server.async_close()


async def test_conn_close_on_server_close(addr):
    server = await create_server(addr)

    tcp_conn = await tcp.connect(addr)
    conn = transport.Connection(conn=tcp_conn,
                                request_cb=None,
                                notification_cb=None)

    assert conn.is_open

    await server.async_close()

    assert not conn.is_open
    await conn.wait_closed()


@pytest.mark.parametrize('req, resp', [
    (transport.BindReq(
        bind_type=transport.BindType.TRANSCEIVER,
        system_id='xyz',
        password='pass1',
        system_type='abc',
        interface_version=12,
        addr_ton=transport.TypeOfNumber.UNKNOWN,
        addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        address_range=''),
     transport.BindRes(
        bind_type=transport.BindType.TRANSCEIVER,
        system_id='xyz',
        optional_params={
            transport.OptionalParamTag.SC_INTERFACE_VERSION: 21})),
    (transport.UnbindReq(), transport.UnbindRes()),
    (transport.SubmitSmReq(
        service_type='',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        protocol_id=0,
        priority_flag=transport.Priority.BULK,
        schedule_delivery_time=None,
        validity_period=None,
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        replace_if_present_flag=False,
        data_coding=transport.DataCoding.DEFAULT,
        sm_default_msg_id=0,
        short_message=b'blablaaaa',
        optional_params={
            transport.OptionalParamTag.USER_MESSAGE_REFERENCE: 13,
            transport.OptionalParamTag.SOURCE_PORT: 23,
            transport.OptionalParamTag.SOURCE_ADDR_SUBUNIT:
                transport.Subunit.UNKNOWN,
            transport.OptionalParamTag.DESTINATION_PORT: 345,
            transport.OptionalParamTag.DEST_ADDR_SUBUNIT:
                transport.Subunit.MS_DISPLAY,
            transport.OptionalParamTag.SAR_MSG_REF_NUM: 0,
            transport.OptionalParamTag.SAR_TOTAL_SEGMENTS: 1,
            transport.OptionalParamTag.SAR_SEGMENT_SEQNUM: 2,
            transport.OptionalParamTag.MORE_MESSAGES_TO_SEND: False,
            transport.OptionalParamTag.PAYLOAD_TYPE:
                transport.PayloadType.DEFAULT,
            transport.OptionalParamTag.MESSAGE_PAYLOAD: b'blaabc123',
            transport.OptionalParamTag.PRIVACY_INDICATOR:
                transport.PrivacyIndicator.NOT_RESTRICTED,
            transport.OptionalParamTag.CALLBACK_NUM: b'num',
            transport.OptionalParamTag.CALLBACK_NUM_PRES_IND: 4,
            transport.OptionalParamTag.CALLBACK_NUM_ATAG: b'1',
            transport.OptionalParamTag.SOURCE_SUBADDRESS:
                transport.Subaddress(type=transport.SubaddressType.NSAP_EVEN,
                                     value=b'src'),
            transport.OptionalParamTag.DEST_SUBADDRESS:
                transport.Subaddress(type=transport.SubaddressType.NSAP_ODD,
                                     value=b'dst'),
            transport.OptionalParamTag.USER_RESPONSE_CODE: 0,
            transport.OptionalParamTag.DISPLAY_TIME:
                transport.DisplayTime.TEMPORARY,
            transport.OptionalParamTag.SMS_SIGNAL: 123,
            transport.OptionalParamTag.MS_VALIDITY:
                transport.MsValidity.STORE_INDEFINITELY,
            transport.OptionalParamTag.MS_MSG_WAIT_FACILITIES:
                transport.MsMsgWaitFacilities(
                    active=False,
                    indicator=transport.MessageWaitingIndicator.FAX),
            transport.OptionalParamTag.NUMBER_OF_MESSAGES: 2,
            transport.OptionalParamTag.ALERT_ON_MESSAGE_DELIVERY: (),
            transport.OptionalParamTag.LANGUAGE_INDICATOR: 21,
            transport.OptionalParamTag.ITS_REPLY_TYPE:
                transport.ItsReplyType.DIGIT,
            transport.OptionalParamTag.ITS_SESSION_INFO:
                transport.ItsSessionInfo(
                    session_number=1,
                    sequence_number=2,
                    end_of_session=True),
            transport.OptionalParamTag.USSD_SERVICE_OP: 3}),
     transport.SubmitSmRes(message_id=b'msgid123')),
    (transport.DeliverSmReq(
        service_type='',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        protocol_id=0,
        priority_flag=transport.Priority.URGENT,
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        data_coding=transport.DataCoding.ASCII,
        short_message=b'some short msg',
        optional_params={
            transport.OptionalParamTag.USER_MESSAGE_REFERENCE: 0,
            transport.OptionalParamTag.SOURCE_PORT: 32,
            transport.OptionalParamTag.DESTINATION_PORT: 23,
            transport.OptionalParamTag.SAR_MSG_REF_NUM: 3,
            transport.OptionalParamTag.SAR_TOTAL_SEGMENTS: 4,
            transport.OptionalParamTag.SAR_SEGMENT_SEQNUM: 5,
            transport.OptionalParamTag.USER_RESPONSE_CODE: 1,
            transport.OptionalParamTag.PRIVACY_INDICATOR:
                transport.PrivacyIndicator.RESTRICTED,
            transport.OptionalParamTag.PAYLOAD_TYPE:
                transport.PayloadType.WCMP,
            transport.OptionalParamTag.MESSAGE_PAYLOAD: b'abc',
            transport.OptionalParamTag.CALLBACK_NUM: b'num',
            transport.OptionalParamTag.SOURCE_SUBADDRESS:
                transport.Subaddress(type=transport.SubaddressType.NSAP_EVEN,
                                     value=b'src'),
            transport.OptionalParamTag.DEST_SUBADDRESS:
                transport.Subaddress(type=transport.SubaddressType.USER,
                                     value=b'dst'),
            transport.OptionalParamTag.LANGUAGE_INDICATOR: 5,
            transport.OptionalParamTag.ITS_SESSION_INFO:
                transport.ItsSessionInfo(
                    session_number=1,
                    sequence_number=2,
                    end_of_session=True),
            transport.OptionalParamTag.NETWORK_ERROR_CODE:
                transport.NetworkErrorCode(network_type=1,
                                           error_code=11),
            transport.OptionalParamTag.MESSAGE_STATE:
                transport.MessageState.ENROUTE,
            transport.OptionalParamTag.RECEIPTED_MESSAGE_ID: b'msgid'
        }),
     transport.DeliverSmRes()),
    (transport.DataSmReq(
        service_type='xyz',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.RECEIPT_ON_FAILURE,
            acknowledgements={transport.Acknowledgement.DELIVERY},
            intermediate_notification=False),
        data_coding=transport.DataCoding.ASCII,
        optional_params={
            transport.OptionalParamTag.SOURCE_BEARER_TYPE:
                transport.BearerType.UNKNOWN,
            transport.OptionalParamTag.SOURCE_TELEMATICS_ID: 123,
            transport.OptionalParamTag.DEST_BEARER_TYPE:
                transport.BearerType.SMS,
            transport.OptionalParamTag.DEST_TELEMATICS_ID: 321,
            transport.OptionalParamTag.QOS_TIME_TO_LIVE: 54321,
            transport.OptionalParamTag.SET_DPF: True
        }),
     transport.DataSmRes(
        message_id=b'id1',
        optional_params={
            transport.OptionalParamTag.DELIVERY_FAILURE_REASON:
                transport.DeliveryFailureReason.DESTINATION_UNAVAILABLE,
            transport.OptionalParamTag.NETWORK_ERROR_CODE:
                transport.NetworkErrorCode(
                    network_type=2,
                    error_code=13),
            transport.OptionalParamTag.ADDITIONAL_STATUS_INFO_TEXT: 'abc 123',
            transport.OptionalParamTag.DPF_RESULT: False})),
    (transport.QuerySmReq(
        message_id=b'1',
        source_addr_ton=transport.TypeOfNumber.INTERNATIONAL,
        source_addr_npi=transport.NumericPlanIndicator.TELEX,
        source_addr=''),
     transport.QuerySmRes(
        message_id=b'1',
        final_date=transport.RelativeTime(
            years=1,
            months=2,
            days=3,
            hours=4,
            minutes=5,
            seconds=6),
        message_state=transport.MessageState.ENROUTE,
        error_code=12)),
    (transport.CancelSmReq(
        service_type='xyz',
        message_id=b'ab12',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='xyz',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='def'),
     transport.CancelSmRes()),
    (transport.ReplaceSmReq(
        message_id=b'ab12',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='1234',
        schedule_delivery_time=transport.RelativeTime(
            years=1,
            months=2,
            days=3,
            hours=4,
            minutes=5,
            seconds=6),
        validity_period=datetime.datetime(
            2025, 1, 1, tzinfo=datetime.timezone.utc),
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        sm_default_msg_id=9,
        short_message=b'a short msg'),
     transport.ReplaceSmRes()),
    (transport.EnquireLinkReq(), transport.EnquireLinkRes()),
    ])
@pytest.mark.parametrize('cmd_status', transport.CommandStatus)
async def test_send(addr, req, resp, cmd_status):
    req_queue = aio.Queue()

    def on_request(request):
        req_queue.put_nowait(request)
        if cmd_status == transport.CommandStatus.ESME_ROK:
            return resp

        return cmd_status

    server = await create_server(addr,
                                 request_cb=on_request)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    rec_resp = await conn.send(req)
    if cmd_status == transport.CommandStatus.ESME_ROK:
        assert rec_resp == resp
    else:
        assert rec_resp == cmd_status

    rec_req = req_queue.get_nowait()
    assert rec_req == req
    assert req_queue.empty

    await conn.async_close()
    await server.async_close()


@pytest.mark.parametrize('notification', [
    transport.OutbindNotification(system_id='system_xyz',
                                  password='test_pass'),
    transport.AlertNotification(
        source_addr_ton=transport.TypeOfNumber.NATIONAL,
        source_addr_npi=transport.NumericPlanIndicator.NATIONAL,
        source_addr='54321',
        esme_addr_ton=transport.TypeOfNumber.ALPHANUMERIC,
        esme_addr_npi=transport.NumericPlanIndicator.DATA,
        esme_addr='12345',
        optional_params={
            transport.OptionalParamTag.MS_AVAILABILITY_STATUS:
                transport.MsAvailabilityStatus.AVAILABLE})
    ])
async def test_notify(addr, notification):
    notification_queue = aio.Queue()

    server = await create_server(
        addr,
        notification_cb=notification_queue.put_nowait)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    resp = await conn.notify(notification)
    assert resp is None

    rec_notification = await notification_queue.get()
    assert rec_notification == notification

    await conn.async_close()
    await server.async_close()


async def test_send_on_conn_closed(addr):
    server = await create_server(addr)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    conn.close()

    with pytest.raises(ConnectionError):
        await conn.send(transport.EnquireLinkReq())

    await server.async_close()


async def test_notify_on_conn_closed(addr):
    server = await create_server(addr)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    conn.close()

    with pytest.raises(ConnectionError):
        await conn.notify(
            transport.OutbindNotification(system_id='system_xyz',
                                          password='test_pass'))

    await server.async_close()


async def test_send_no_resp(addr):

    async def on_request(req):
        await asyncio.Future()

    server = await create_server(addr,
                                 request_cb=on_request)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(conn.send(transport.EnquireLinkReq()), 0.01)

    await conn.async_close()
    await server.async_close()


async def test_send_multi(addr):
    no_reqs = 5
    req = transport.SubmitSmReq(
        service_type='',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        protocol_id=0,
        priority_flag=transport.Priority.BULK,
        schedule_delivery_time=None,
        validity_period=None,
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        replace_if_present_flag=False,
        data_coding=transport.DataCoding.DEFAULT,
        sm_default_msg_id=0,
        short_message=b'',
        optional_params={})
    reqs = [req._replace(short_message=str(i).encode())
            for i in range(no_reqs)]
    resps = [transport.SubmitSmRes(message_id=str(i).encode())
             for i in range(no_reqs)]

    async def on_request(request):
        for req, res in zip(reqs, resps):
            if request == req:
                return res

        raise Exception('unexpected req')

    server = await create_server(addr,
                                 request_cb=on_request)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    resp_futures = []
    for req in reqs:
        resp_fut = conn.async_group.spawn(conn.send, req)
        resp_futures.append(resp_fut)

    for req, resp, resp_fut in zip(reqs, resps, resp_futures):
        rec_resp = await resp_fut
        assert rec_resp == resp

    await conn.async_close()
    await server.async_close()


@pytest.mark.parametrize('resp', [
    transport.BindRes(
        bind_type=transport.BindType.TRANSCEIVER,
        system_id='xyz',
        optional_params={}),
    transport.UnbindRes(),
    transport.DeliverSmRes(),
    transport.DataSmRes(
            message_id=b'id1',
            optional_params={}),
    transport.QuerySmRes(
            message_id=b'1',
            final_date=transport.RelativeTime(
                years=1,
                months=2,
                days=3,
                hours=4,
                minutes=5,
                seconds=6),
            message_state=transport.MessageState.ENROUTE,
            error_code=12),
    transport.CancelSmRes(),
    transport.ReplaceSmRes(),
    transport.EnquireLinkRes()])
async def test_send_invalid_resp(addr, resp):
    req = transport.SubmitSmReq(
        service_type='',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        protocol_id=0,
        priority_flag=transport.Priority.BULK,
        schedule_delivery_time=None,
        validity_period=None,
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        replace_if_present_flag=False,
        data_coding=transport.DataCoding.DEFAULT,
        sm_default_msg_id=0,
        short_message=b'',
        optional_params={})

    async def on_request(request):
        return resp

    server = await create_server(addr,
                                 request_cb=on_request)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    resp = await conn.send(req)
    assert resp == transport.CommandStatus.ESME_RSYSERR

    await conn.async_close()
    await server.async_close()


async def test_send_no_req_cb(addr):
    server = await create_server(addr)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    resp = await conn.send(transport.EnquireLinkReq())
    assert resp == transport.CommandStatus.ESME_RINVCMDID

    await conn.async_close()
    await server.async_close()


async def test_send_req_cb_exc(addr):

    def on_request(request):
        raise Exception()

    server = await create_server(addr,
                                 request_cb=on_request)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    resp = await conn.send(transport.EnquireLinkReq())
    assert resp == transport.CommandStatus.ESME_RSYSERR

    await conn.async_close()
    await server.async_close()


async def test_receive_invalid_header(addr):
    tcp_conn_queue = aio.Queue()

    server = await tcp.listen(connection_cb=tcp_conn_queue.put_nowait,
                              addr=addr,
                              bind_connections=True)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    tcp_conn = await tcp_conn_queue.get()

    await tcp_conn.write(b'\x11' * 16)

    # connection is expected to close on wrong header
    await conn.wait_closed()

    await server.async_close()


@pytest.mark.parametrize('req', [
    transport.SubmitSmReq(
        service_type='',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        protocol_id=0,
        priority_flag=transport.Priority.BULK,
        schedule_delivery_time=None,
        validity_period=None,
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        replace_if_present_flag=False,
        data_coding=transport.DataCoding.DEFAULT,
        sm_default_msg_id=0,
        short_message=b'blablaaaa',
        optional_params={
            transport.OptionalParamTag.DEST_BEARER_TYPE:
                transport.BearerType.SMS}),
    transport.DeliverSmReq(
        service_type='',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        protocol_id=0,
        priority_flag=transport.Priority.URGENT,
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.NO_RECEIPT,
            acknowledgements=set(),
            intermediate_notification=False),
        data_coding=transport.DataCoding.ASCII,
        short_message=b'some short msg',
        optional_params={
            transport.OptionalParamTag.DEST_ADDR_SUBUNIT:
                transport.Subunit.MS_DISPLAY}),
    transport.DataSmReq(
        service_type='xyz',
        source_addr_ton=transport.TypeOfNumber.UNKNOWN,
        source_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        source_addr='',
        dest_addr_ton=transport.TypeOfNumber.UNKNOWN,
        dest_addr_npi=transport.NumericPlanIndicator.UNKNOWN,
        destination_addr='abc123',
        esm_class=transport.EsmClass(
            messaging_mode=transport.MessagingMode.DEFAULT,
            message_type=transport.MessageType.DEFAULT,
            gsm_features={transport.GsmFeature.UDHI,
                          transport.GsmFeature.REPLY_PATH}),
        registered_delivery=transport.RegisteredDelivery(
            delivery_receipt=transport.DeliveryReceipt.RECEIPT_ON_FAILURE,
            acknowledgements={transport.Acknowledgement.DELIVERY},
            intermediate_notification=False),
        data_coding=transport.DataCoding.ASCII,
        optional_params={
            transport.OptionalParamTag.ADDITIONAL_STATUS_INFO_TEXT: 'aa'})])
async def test_invalid_req_optional_param(addr, req):
    server = await create_server(addr)

    conn = await tcp.connect(addr)
    conn = transport.Connection(conn=conn,
                                request_cb=None,
                                notification_cb=None)

    with pytest.raises(transport.encoder.CommandStatusError,
                       match='Optional Parameter not allowed'):
        await conn.send(req)

    await conn.async_close()
    await server.async_close()
