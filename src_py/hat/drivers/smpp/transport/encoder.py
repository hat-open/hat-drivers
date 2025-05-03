from collections.abc import Iterable
import datetime
import enum
import struct
import typing

from hat import util

from hat.drivers.smpp.transport import common


header_length: int = 16


class CommandStatusError(Exception):

    def __init__(self, command_status: common.CommandStatus):
        super().__init__(common.command_status_descriptions[command_status])
        self.__command_status = command_status

    @property
    def command_status(self):
        return self.__command_status


class CommandId(enum.Enum):
    GENERIC_NACK = 0x80000000
    BIND_RECEIVER_REQ = 0x00000001
    BIND_RECEIVER_RESP = 0x80000001
    BIND_TRANSMITTER_REQ = 0x00000002
    BIND_TRANSMITTER_RESP = 0x80000002
    QUERY_SM_REQ = 0x00000003
    QUERY_SM_RESP = 0x80000003
    SUBMIT_SM_REQ = 0x00000004
    SUBMIT_SM_RESP = 0x80000004
    DELIVER_SM_REQ = 0x00000005
    DELIVER_SM_RESP = 0x80000005
    UNBIND_REQ = 0x00000006
    UNBIND_RESP = 0x80000006
    REPLACE_SM_REQ = 0x00000007
    REPLACE_SM_RESP = 0x80000007
    CANCEL_SM_REQ = 0x00000008
    CANCEL_SM_RESP = 0x80000008
    BIND_TRANSCEIVER_REQ = 0x00000009
    BIND_TRANSCEIVER_RESP = 0x80000009
    OUTBIND = 0x0000000b
    ENQUIRE_LINK_REQ = 0x00000015
    ENQUIRE_LINK_RESP = 0x80000015
    SUBMIT_MULTI_REQ = 0x00000021
    SUBMIT_MULTI_RESP = 0x80000021
    ALERT_NOTIFICATION = 0x00000102
    DATA_SM_REQ = 0x00000103
    DATA_SM_RESP = 0x80000103


class Header(typing.NamedTuple):
    command_length: int
    command_id: CommandId
    command_status: common.CommandStatus
    sequence_number: int


Body: typing.TypeAlias = (common.Request |
                          common.Response |
                          common.Notification)


def decode_sequence_number(header_bytes: util.Bytes) -> int:
    return struct.unpack('>I', header_bytes[12:])[0]


def decode_header(header_bytes: util.Bytes) -> Header:
    cmd_len, cmd_id, cmd_status, seq_num = struct.unpack('>IIII', header_bytes)

    if cmd_len < header_length:
        raise CommandStatusError(common.CommandStatus.ESME_RINVCMDLEN)

    try:
        command_id = CommandId(cmd_id)

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVCMDID)

    try:
        command_status = common.CommandStatus(cmd_status)

    except ValueError:
        command_status = common.CommandStatus.ESME_RUNKNOWNERR

    return Header(command_length=cmd_len,
                  command_id=command_id,
                  command_status=command_status,
                  sequence_number=seq_num)


def encode_header(header: Header) -> util.Bytes:
    return struct.pack('>IIII',
                       header.command_length,
                       header.command_id.value,
                       header.command_status.value,
                       header.sequence_number)


def decode_body(command_id: CommandId,
                body_bytes: util.Bytes
                ) -> Body:
    if command_id == CommandId.GENERIC_NACK:
        raise CommandStatusError(common.CommandStatus.ESME_RUNKNOWNERR)

    if command_id == CommandId.BIND_RECEIVER_REQ:
        return _decode_bind_req(common.BindType.RECEIVER, body_bytes)

    if command_id == CommandId.BIND_RECEIVER_RESP:
        return _decode_bind_res(common.BindType.RECEIVER, body_bytes)

    if command_id == CommandId.BIND_TRANSMITTER_REQ:
        return _decode_bind_req(common.BindType.TRANSMITTER, body_bytes)

    if command_id == CommandId.BIND_TRANSMITTER_RESP:
        return _decode_bind_res(common.BindType.TRANSMITTER, body_bytes)

    if command_id == CommandId.QUERY_SM_REQ:
        return _decode_query_sm_req(body_bytes)

    if command_id == CommandId.QUERY_SM_RESP:
        return _decode_query_sm_res(body_bytes)

    if command_id == CommandId.SUBMIT_SM_REQ:
        return _decode_submit_sm_req(body_bytes)

    if command_id == CommandId.SUBMIT_SM_RESP:
        return _decode_submit_sm_res(body_bytes)

    if command_id == CommandId.DELIVER_SM_REQ:
        return _decode_deliver_sm_req(body_bytes)

    if command_id == CommandId.DELIVER_SM_RESP:
        return _decode_deliver_sm_res(body_bytes)

    if command_id == CommandId.UNBIND_REQ:
        return _decode_unbind_req(body_bytes)

    if command_id == CommandId.UNBIND_RESP:
        return _decode_unbind_res(body_bytes)

    if command_id == CommandId.REPLACE_SM_REQ:
        return _decode_replace_sm_req(body_bytes)

    if command_id == CommandId.REPLACE_SM_RESP:
        return _decode_replace_sm_res(body_bytes)

    if command_id == CommandId.CANCEL_SM_REQ:
        return _decode_cancel_sm_req(body_bytes)

    if command_id == CommandId.CANCEL_SM_RESP:
        return _decode_cancel_sm_res(body_bytes)

    if command_id == CommandId.BIND_TRANSCEIVER_REQ:
        return _decode_bind_req(common.BindType.TRANSCEIVER, body_bytes)

    if command_id == CommandId.BIND_TRANSCEIVER_RESP:
        return _decode_bind_res(common.BindType.TRANSCEIVER, body_bytes)

    if command_id == CommandId.OUTBIND:
        return _decode_outbind_notification(body_bytes)

    if command_id == CommandId.ENQUIRE_LINK_REQ:
        return _decode_enquire_link_req(body_bytes)

    if command_id == CommandId.ENQUIRE_LINK_RESP:
        return _decode_enquire_link_res(body_bytes)

    if command_id == CommandId.SUBMIT_MULTI_REQ:
        return _decode_submit_multi_req(body_bytes)

    if command_id == CommandId.SUBMIT_MULTI_RESP:
        return _decode_submit_multi_res(body_bytes)

    if command_id == CommandId.ALERT_NOTIFICATION:
        return _decode_alert_notification(body_bytes)

    if command_id == CommandId.DATA_SM_REQ:
        return _decode_data_sm_req(body_bytes)

    if command_id == CommandId.DATA_SM_RESP:
        return _decode_data_sm_res(body_bytes)

    raise ValueError('unsupported command id')


def encode_body(body: Body) -> util.Bytes:
    if isinstance(body, common.BindReq):
        return bytes(_encode_bind_req(body))

    if isinstance(body, common.BindRes):
        return bytes(_encode_bind_res(body))

    if isinstance(body, common.UnbindReq):
        return bytes(_encode_unbind_req(body))

    if isinstance(body, common.UnbindRes):
        return bytes(_encode_unbind_res(body))

    if isinstance(body, common.SubmitSmReq):
        return bytes(_encode_submit_sm_req(body))

    if isinstance(body, common.SubmitSmRes):
        return bytes(_encode_submit_sm_res(body))

    if isinstance(body, common.SubmitMultiReq):
        return bytes(_encode_submit_multi_req(body))

    if isinstance(body, common.SubmitMultiRes):
        return bytes(_encode_submit_multi_res(body))

    if isinstance(body, common.DeliverSmReq):
        return bytes(_encode_deliver_sm_req(body))

    if isinstance(body, common.DeliverSmRes):
        return bytes(_encode_deliver_sm_res(body))

    if isinstance(body, common.DataSmReq):
        return bytes(_encode_data_sm_req(body))

    if isinstance(body, common.DataSmRes):
        return bytes(_encode_data_sm_res(body))

    if isinstance(body, common.QuerySmReq):
        return bytes(_encode_query_sm_req(body))

    if isinstance(body, common.QuerySmRes):
        return bytes(_encode_query_sm_res(body))

    if isinstance(body, common.CancelSmReq):
        return bytes(_encode_cancel_sm_req(body))

    if isinstance(body, common.CancelSmRes):
        return bytes(_encode_cancel_sm_res(body))

    if isinstance(body, common.ReplaceSmReq):
        return bytes(_encode_replace_sm_req(body))

    if isinstance(body, common.ReplaceSmRes):
        return bytes(_encode_replace_sm_res(body))

    if isinstance(body, common.EnquireLinkReq):
        return bytes(_encode_enquire_link_req(body))

    if isinstance(body, common.EnquireLinkRes):
        return bytes(_encode_enquire_link_res(body))

    if isinstance(body, common.OutbindNotification):
        return bytes(_encode_outbind_notification(body))

    if isinstance(body, common.AlertNotification):
        return bytes(_encode_alert_notification(body))

    raise TypeError('unsupported body type')


def _decode_bind_req(bind_type: common.BindType,
                     req_bytes: util.Bytes
                     ) -> common.BindReq:
    system_id, rest = _decode_cstring(req_bytes)
    password, rest = _decode_cstring(rest)
    system_type, rest = _decode_cstring(rest)
    interface_version, rest = rest[0], rest[1:]
    addr_ton, rest = _decode_source_addr_ton(rest)
    addr_npi, rest = _decode_source_addr_npi(rest)
    address_range, rest = _decode_cstring(rest)

    return common.BindReq(bind_type=bind_type,
                          system_id=system_id,
                          password=password,
                          system_type=system_type,
                          interface_version=interface_version,
                          addr_ton=addr_ton,
                          addr_npi=addr_npi,
                          address_range=address_range)


def _encode_bind_req(req: common.BindReq) -> Iterable[int]:
    yield from _encode_cstring(req.system_id)
    yield from _encode_cstring(req.password)
    yield from _encode_cstring(req.system_type)
    yield req.interface_version
    yield req.addr_ton.value
    yield req.addr_npi.value
    yield from _encode_cstring(req.address_range)


def _decode_bind_res(bind_type: common.BindType,
                     res_bytes: util.Bytes
                     ) -> common.BindRes:
    system_id, rest = _decode_cstring(res_bytes)
    optional_params = _decode_optional_params(CommandId.BIND_RECEIVER_RESP,
                                              rest)

    return common.BindRes(bind_type=bind_type,
                          system_id=system_id,
                          optional_params=optional_params)


def _encode_bind_res(res: common.BindRes) -> Iterable[int]:
    yield from _encode_cstring(res.system_id)
    yield from _encode_optional_params(CommandId.BIND_RECEIVER_RESP,
                                       res.optional_params)


def _decode_unbind_req(req_bytes: util.Bytes) -> common.UnbindReq:
    return common.UnbindReq()


def _encode_unbind_req(req: common.UnbindReq) -> Iterable[int]:
    yield from b''


def _decode_unbind_res(res_bytes: util.Bytes) -> common.UnbindRes:
    return common.UnbindRes()


def _encode_unbind_res(res: common.UnbindRes) -> Iterable[int]:
    yield from b''


def _decode_submit_sm_req(req_bytes: util.Bytes) -> common.SubmitSmReq:
    service_type, rest = _decode_cstring(req_bytes)
    source_addr_ton, rest = _decode_source_addr_ton(rest)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)
    dest_addr_ton, rest = _decode_dest_addr_ton(rest)
    dest_addr_npi, rest = _decode_dest_addr_npi(rest)
    destination_addr, rest = _decode_cstring(rest)
    esm_class, rest = _decode_esm_class(rest)
    protocol_id, rest = rest[0], rest[1:]
    priority_flag, rest = _decode_priority_flag(rest)
    schedule_delivery_time, rest = _decode_schedule_delivery_time(rest)
    validity_period, rest = _decode_validity_period(rest)
    registered_delivery, rest = _decode_registered_delivery(rest)
    replace_if_present_flag, rest = bool(rest[0]), rest[1:]
    data_coding, rest = common.DataCoding(rest[0] & 0x0f), rest[1:]
    sm_default_msg_id, rest = rest[0], rest[1:]

    short_message_len, rest = rest[0], rest[1:]
    short_message, rest = rest[:short_message_len], rest[short_message_len:]

    optional_params = _decode_optional_params(CommandId.SUBMIT_SM_REQ, rest)

    return common.SubmitSmReq(service_type=service_type,
                              source_addr_ton=source_addr_ton,
                              source_addr_npi=source_addr_npi,
                              source_addr=source_addr,
                              dest_addr_ton=dest_addr_ton,
                              dest_addr_npi=dest_addr_npi,
                              destination_addr=destination_addr,
                              esm_class=esm_class,
                              protocol_id=protocol_id,
                              priority_flag=priority_flag,
                              schedule_delivery_time=schedule_delivery_time,
                              validity_period=validity_period,
                              registered_delivery=registered_delivery,
                              replace_if_present_flag=replace_if_present_flag,
                              data_coding=data_coding,
                              sm_default_msg_id=sm_default_msg_id,
                              short_message=short_message,
                              optional_params=optional_params)


def _encode_submit_sm_req(req: common.SubmitSmReq) -> Iterable[int]:
    yield from _encode_cstring(req.service_type)
    yield req.source_addr_ton.value
    yield req.source_addr_npi.value
    yield from _encode_cstring(req.source_addr)
    yield req.dest_addr_ton.value
    yield req.dest_addr_npi.value
    yield from _encode_cstring(req.destination_addr)
    yield from _encode_esm_class(req.esm_class)
    yield req.protocol_id
    yield req.priority_flag.value
    yield from _encode_time(req.schedule_delivery_time)
    yield from _encode_time(req.validity_period)
    yield from _encode_registered_delivery(req.registered_delivery)
    yield int(req.replace_if_present_flag)
    yield req.data_coding.value
    yield req.sm_default_msg_id

    if len(req.short_message) > 254:
        raise CommandStatusError(common.CommandStatus.ESME_RINVMSGLEN)

    yield len(req.short_message)
    yield from req.short_message

    yield from _encode_optional_params(CommandId.SUBMIT_SM_REQ,
                                       req.optional_params)


def _decode_submit_sm_res(res_bytes: util.Bytes) -> common.SubmitSmRes:
    message_id, rest = _decode_cbytes(res_bytes)

    return common.SubmitSmRes(message_id=message_id)


def _encode_submit_sm_res(res: common.SubmitSmRes) -> Iterable[int]:
    yield from _encode_cbytes(res.message_id)


def _decode_submit_multi_req(req_bytes: util.Bytes) -> common.SubmitMultiReq:
    # TODO
    return common.SubmitMultiReq()


def _encode_submit_multi_req(req: common.SubmitMultiReq) -> Iterable[int]:
    # TODO
    raise NotImplementedError()


def _decode_submit_multi_res(res_bytes: util.Bytes) -> common.SubmitMultiRes:
    # TODO
    return common.SubmitMultiRes()


def _encode_submit_multi_res(res: common.SubmitMultiRes) -> Iterable[int]:
    # TODO
    raise NotImplementedError()


def _decode_deliver_sm_req(req_bytes: util.Bytes) -> common.DeliverSmReq:
    service_type, rest = _decode_cstring(req_bytes)
    source_addr_ton, rest = _decode_source_addr_ton(rest)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)
    dest_addr_ton, rest = _decode_dest_addr_ton(rest)
    dest_addr_npi, rest = _decode_dest_addr_npi(rest)
    destination_addr, rest = _decode_cstring(rest)
    esm_class, rest = _decode_esm_class(rest)
    protocol_id, rest = rest[0], rest[1:]
    priority_flag, rest = _decode_priority_flag(rest)
    _, rest = _decode_cstring(rest)
    _, rest = _decode_cstring(rest)
    registered_delivery, rest = _decode_registered_delivery(rest)
    rest = rest[1:]
    data_coding, rest = common.DataCoding(rest[0] & 0x0f), rest[1:]
    rest = rest[1:]

    short_message_len, rest = rest[0], rest[1:]
    short_message, rest = rest[:short_message_len], rest[short_message_len:]

    optional_params = _decode_optional_params(CommandId.DELIVER_SM_REQ, rest)

    return common.DeliverSmReq(service_type=service_type,
                               source_addr_ton=source_addr_ton,
                               source_addr_npi=source_addr_npi,
                               source_addr=source_addr,
                               dest_addr_ton=dest_addr_ton,
                               dest_addr_npi=dest_addr_npi,
                               destination_addr=destination_addr,
                               esm_class=esm_class,
                               protocol_id=protocol_id,
                               priority_flag=priority_flag,
                               registered_delivery=registered_delivery,
                               data_coding=data_coding,
                               short_message=short_message,
                               optional_params=optional_params)


def _encode_deliver_sm_req(req: common.DeliverSmReq) -> Iterable[int]:
    yield from _encode_cstring(req.service_type)
    yield req.source_addr_ton.value
    yield req.source_addr_npi.value
    yield from _encode_cstring(req.source_addr)
    yield req.dest_addr_ton.value
    yield req.dest_addr_npi.value
    yield from _encode_cstring(req.destination_addr)
    yield from _encode_esm_class(req.esm_class)
    yield req.protocol_id
    yield req.priority_flag.value
    yield 0
    yield 0
    yield from _encode_registered_delivery(req.registered_delivery)
    yield 0
    yield req.data_coding.value
    yield 0

    if len(req.short_message) > 254:
        raise CommandStatusError(common.CommandStatus.ESME_RINVMSGLEN)

    yield len(req.short_message)
    yield from req.short_message

    yield from _encode_optional_params(CommandId.DELIVER_SM_REQ,
                                       req.optional_params)


def _decode_deliver_sm_res(res_bytes: util.Bytes) -> common.DeliverSmRes:
    return common.DeliverSmRes()


def _encode_deliver_sm_res(res: common.DeliverSmRes) -> Iterable[int]:
    yield from b''


def _decode_data_sm_req(req_bytes: util.Bytes) -> common.DataSmReq:
    service_type, rest = _decode_cstring(req_bytes)
    source_addr_ton, rest = _decode_source_addr_ton(rest)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)
    dest_addr_ton, rest = _decode_dest_addr_ton(rest)
    dest_addr_npi, rest = _decode_dest_addr_npi(rest)
    destination_addr, rest = _decode_cstring(rest)
    esm_class, rest = _decode_esm_class(rest)
    registered_delivery, rest = _decode_registered_delivery(rest)
    data_coding, rest = common.DataCoding(rest[0] & 0x0f), rest[1:]

    optional_params = _decode_optional_params(CommandId.DATA_SM_REQ, rest)

    return common.DataSmReq(service_type=service_type,
                            source_addr_ton=source_addr_ton,
                            source_addr_npi=source_addr_npi,
                            source_addr=source_addr,
                            dest_addr_ton=dest_addr_ton,
                            dest_addr_npi=dest_addr_npi,
                            destination_addr=destination_addr,
                            esm_class=esm_class,
                            registered_delivery=registered_delivery,
                            data_coding=data_coding,
                            optional_params=optional_params)


def _encode_data_sm_req(req: common.DataSmReq) -> Iterable[int]:
    yield from _encode_cstring(req.service_type)
    yield req.source_addr_ton.value
    yield req.source_addr_npi.value
    yield from _encode_cstring(req.source_addr)
    yield req.dest_addr_ton.value
    yield req.dest_addr_npi.value
    yield from _encode_cstring(req.destination_addr)
    yield from _encode_esm_class(req.esm_class)
    yield from _encode_registered_delivery(req.registered_delivery)
    yield req.data_coding.value

    yield from _encode_optional_params(CommandId.DATA_SM_REQ,
                                       req.optional_params)


def _decode_data_sm_res(res_bytes: util.Bytes) -> common.DataSmRes:
    message_id, rest = _decode_cbytes(res_bytes)

    optional_params = _decode_optional_params(CommandId.DATA_SM_RESP, rest)

    return common.DataSmRes(message_id=message_id,
                            optional_params=optional_params)


def _encode_data_sm_res(res: common.DataSmRes) -> Iterable[int]:
    yield from _encode_cbytes(res.message_id)

    yield from _encode_optional_params(CommandId.DATA_SM_RESP,
                                       res.optional_params)


def _decode_query_sm_req(req_bytes: util.Bytes) -> common.QuerySmReq:
    message_id, rest = _decode_cbytes(req_bytes)
    source_addr_ton, rest = _decode_source_addr_ton(rest)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)

    return common.QuerySmReq(message_id=message_id,
                             source_addr_ton=source_addr_ton,
                             source_addr_npi=source_addr_npi,
                             source_addr=source_addr)


def _encode_query_sm_req(req: common.QuerySmReq) -> Iterable[int]:
    yield from _encode_cbytes(req.message_id)
    yield req.source_addr_ton.value
    yield req.source_addr_npi.value
    yield from _encode_cstring(req.source_addr)


def _decode_query_sm_res(res_bytes: util.Bytes) -> common.QuerySmRes:
    message_id, rest = _decode_cbytes(res_bytes)
    final_date, rest = _decode_time(rest)
    message_state, rest = common.MessageState(rest[0]), rest[1:]
    error_code, rest = rest[0], rest[1:]

    return common.QuerySmRes(message_id=message_id,
                             final_date=final_date,
                             message_state=message_state,
                             error_code=error_code)


def _encode_query_sm_res(res: common.QuerySmRes) -> Iterable[int]:
    yield from _encode_cbytes(res.message_id)
    yield from _encode_time(res.final_date)
    yield res.message_state.value
    yield res.error_code


def _decode_cancel_sm_req(req_bytes: util.Bytes) -> common.CancelSmReq:
    service_type, rest = _decode_cstring(req_bytes)
    message_id, rest = _decode_cbytes(rest)
    source_addr_ton, rest = _decode_source_addr_ton(rest)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)
    dest_addr_ton, rest = _decode_dest_addr_ton(rest)
    dest_addr_npi, rest = _decode_dest_addr_npi(rest)
    destination_addr, rest = _decode_cstring(rest)

    return common.CancelSmReq(service_type=service_type,
                              message_id=message_id,
                              source_addr_ton=source_addr_ton,
                              source_addr_npi=source_addr_npi,
                              source_addr=source_addr,
                              dest_addr_ton=dest_addr_ton,
                              dest_addr_npi=dest_addr_npi,
                              destination_addr=destination_addr)


def _encode_cancel_sm_req(req: common.CancelSmReq) -> Iterable[int]:
    yield from _encode_cstring(req.service_type)
    yield from _encode_cbytes(req.message_id)
    yield req.source_addr_ton.value
    yield req.source_addr_npi.value
    yield from _encode_cstring(req.source_addr)
    yield req.dest_addr_ton.value
    yield req.dest_addr_npi.value
    yield from _encode_cstring(req.destination_addr)


def _decode_cancel_sm_res(res_bytes: util.Bytes) -> common.CancelSmRes:
    return common.CancelSmRes()


def _encode_cancel_sm_res(res: common.CancelSmRes) -> Iterable[int]:
    yield from b''


def _decode_replace_sm_req(req_bytes: util.Bytes) -> common.ReplaceSmReq:
    message_id, rest = _decode_cbytes(req_bytes)
    source_addr_ton, rest = _decode_source_addr_ton(rest)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)
    schedule_delivery_time, rest = _decode_schedule_delivery_time(rest)
    validity_period, rest = _decode_validity_period(rest)
    registered_delivery, rest = _decode_registered_delivery(rest)
    sm_default_msg_id, rest = rest[0], rest[1:]

    short_message_len, rest = rest[0], rest[1:]
    short_message, rest = rest[:short_message_len], rest[short_message_len:]

    return common.ReplaceSmReq(message_id=message_id,
                               source_addr_ton=source_addr_ton,
                               source_addr_npi=source_addr_npi,
                               source_addr=source_addr,
                               schedule_delivery_time=schedule_delivery_time,
                               validity_period=validity_period,
                               registered_delivery=registered_delivery,
                               sm_default_msg_id=sm_default_msg_id,
                               short_message=short_message)


def _encode_replace_sm_req(req: common.ReplaceSmReq) -> Iterable[int]:
    yield from _encode_cbytes(req.message_id)
    yield req.source_addr_ton.value
    yield req.source_addr_npi.value
    yield from _encode_cstring(req.source_addr)
    yield from _encode_time(req.schedule_delivery_time)
    yield from _encode_time(req.validity_period)
    yield from _encode_registered_delivery(req.registered_delivery)
    yield req.sm_default_msg_id

    if len(req.short_message) > 254:
        raise CommandStatusError(common.CommandStatus.ESME_RINVMSGLEN)

    yield len(req.short_message)
    yield from req.short_message


def _decode_replace_sm_res(res_bytes: util.Bytes) -> common.ReplaceSmRes:
    return common.ReplaceSmRes()


def _encode_replace_sm_res(res: common.ReplaceSmRes) -> Iterable[int]:
    yield from b''


def _decode_enquire_link_req(req_bytes: util.Bytes) -> common.EnquireLinkReq:
    return common.EnquireLinkReq()


def _encode_enquire_link_req(req: common.EnquireLinkReq) -> Iterable[int]:
    yield from b''


def _decode_enquire_link_res(res_bytes: util.Bytes) -> common.EnquireLinkRes:
    return common.EnquireLinkRes()


def _encode_enquire_link_res(res: common.EnquireLinkRes) -> Iterable[int]:
    yield from b''


def _decode_outbind_notification(notification_bytes: util.Bytes
                                 ) -> common.OutbindNotification:
    system_id, rest = _decode_cstring(notification_bytes)
    password, rest = _decode_cstring(rest)

    return common.OutbindNotification(system_id=system_id,
                                      password=password)


def _encode_outbind_notification(notification: common.OutbindNotification
                                 ) -> Iterable[int]:
    yield from _encode_cstring(notification.system_id)
    yield from _encode_cstring(notification.password)


def _decode_alert_notification(notification_bytes: util.Bytes
                               ) -> common.AlertNotification:
    source_addr_ton, rest = _decode_source_addr_ton(notification_bytes)
    source_addr_npi, rest = _decode_source_addr_npi(rest)
    source_addr, rest = _decode_cstring(rest)
    esme_addr_ton, rest = _decode_dest_addr_ton(rest)
    esme_addr_npi, rest = _decode_dest_addr_npi(rest)
    esme_addr, rest = _decode_cstring(rest)

    optional_params = _decode_optional_params(CommandId.ALERT_NOTIFICATION,
                                              rest)

    return common.AlertNotification(source_addr_ton=source_addr_ton,
                                    source_addr_npi=source_addr_npi,
                                    source_addr=source_addr,
                                    esme_addr_ton=esme_addr_ton,
                                    esme_addr_npi=esme_addr_npi,
                                    esme_addr=esme_addr,
                                    optional_params=optional_params)


def _encode_alert_notification(notification: common.AlertNotification
                               ) -> Iterable[int]:
    yield notification.source_addr_ton.value
    yield notification.source_addr_npi.value
    yield from _encode_cstring(notification.source_addr)
    yield notification.esme_addr_ton.value
    yield notification.esme_addr_npi.value
    yield from _encode_cstring(notification.esme_addr)

    yield from _encode_optional_params(CommandId.ALERT_NOTIFICATION,
                                       notification.optional_params)


def _decode_source_addr_ton(data: util.Bytes
                            ) -> tuple[common.TypeOfNumber, util.Bytes]:
    try:
        return common.TypeOfNumber(data[0]), data[1:]

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVSRCTON)


def _decode_source_addr_npi(data: util.Bytes
                            ) -> tuple[common.NumericPlanIndicator,
                                       util.Bytes]:
    try:
        return common.NumericPlanIndicator(data[0]), data[1:]

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVSRCNPI)


def _decode_dest_addr_ton(data: util.Bytes
                          ) -> tuple[common.TypeOfNumber, util.Bytes]:
    try:
        return common.TypeOfNumber(data[0]), data[1:]

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVDSTTON)


def _decode_dest_addr_npi(data: util.Bytes
                          ) -> tuple[common.NumericPlanIndicator, util.Bytes]:
    try:
        return common.NumericPlanIndicator(data[0]), data[1:]

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVDSTNPI)


def _decode_priority_flag(data: util.Bytes
                          ) -> tuple[common.Priority, util.Bytes]:
    try:
        return common.Priority(data[0]), data[1:]

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVPRTFLG)


def _decode_schedule_delivery_time(data: util.Bytes
                                   ) -> tuple[common.Time | None, util.Bytes]:
    try:
        return _decode_time(data)

    except Exception:
        raise CommandStatusError(common.CommandStatus.ESME_RINVSCHED)


def _decode_validity_period(data: util.Bytes
                            ) -> tuple[common.Time | None, util.Bytes]:
    try:
        return _decode_time(data)

    except Exception:
        raise CommandStatusError(common.CommandStatus.ESME_RINVEXPIRY)


def _decode_registered_delivery(data: util.Bytes
                                ) -> tuple[common.RegisteredDelivery,
                                           util.Bytes]:
    try:
        registered_delivery = common.RegisteredDelivery(
            delivery_receipt=common.DeliveryReceipt(data[0] & 0x03),
            acknowledgements={i for i in common.Acknowledgement
                              if (data[0] >> 2) & i.value},
            intermediate_notification=bool(data[0] & 0x10))
        return registered_delivery, data[1:]

    except ValueError:
        raise CommandStatusError(common.CommandStatus.ESME_RINVREGDLVFLG)


def _encode_registered_delivery(registered_delivery: common.RegisteredDelivery
                                ) -> Iterable[int]:
    registered_delivery_int = registered_delivery.delivery_receipt.value

    for i in registered_delivery.acknowledgements:
        registered_delivery_int |= (i.value << 2)

    if registered_delivery.intermediate_notification:
        registered_delivery_int |= 0x10

    yield registered_delivery_int


def _decode_esm_class(esm_class_bytes: util.Bytes
                      ) -> tuple[common.EsmClass, util.Bytes]:
    esm_class_int, rest = esm_class_bytes[0], esm_class_bytes[1:]
    messaging_mode = common.MessagingMode(esm_class_int & 0x03)
    message_type = common.MessageType((esm_class_int >> 2) & 0x0f)
    gsm_features = {i
                    for i in common.GsmFeature
                    if (esm_class_int >> 6) & i.value}

    esm_class = common.EsmClass(messaging_mode=messaging_mode,
                                message_type=message_type,
                                gsm_features=gsm_features)
    return esm_class, rest


def _encode_esm_class(esm_class: common.EsmClass) -> Iterable[int]:
    esm_class_int = (esm_class.messaging_mode.value |
                     (esm_class.message_type.value << 2))

    for i in esm_class.gsm_features:
        esm_class_int |= (i.value << 6)

    yield esm_class_int


def _decode_time(time_bytes: util.Bytes
                 ) -> tuple[common.Time | None, util.Bytes]:
    time_str, rest = _decode_cstring(time_bytes)
    if time_str == '':
        return None, rest

    if len(time_str) != 16:
        raise Exception('invalid time string length')

    years = int(time_str[:2])
    months = int(time_str[2:4])
    days = int(time_str[4:6])
    hours = int(time_str[6:8])
    minutes = int(time_str[8:10])
    seconds = int(time_str[10:12])
    tenths = int(time_str[12])
    offset = int(time_str[13:15])
    direction = time_str[15]

    if direction == 'R':
        time = common.RelativeTime(years=years,
                                   months=months,
                                   days=days,
                                   hours=hours,
                                   minutes=minutes,
                                   seconds=seconds + tenths * 0.1)
        return time, rest

    if direction == '+':
        delta = datetime.timedelta(minutes=15 * offset)

    elif direction == '-':
        delta = datetime.timedelta(minutes=-15 * offset)

    else:
        raise Exception('invalid direction sign')

    time = datetime.datetime(year=2000 + years,
                             month=months,
                             day=days,
                             hour=hours,
                             minute=minutes,
                             second=seconds,
                             microsecond=tenths * 100_000,
                             tzinfo=datetime.timezone(delta))
    return time, rest


def _encode_time(time: common.Time | None) -> Iterable[int]:
    if time is None:
        time_str = ''

    elif isinstance(time, common.RelativeTime):
        time_str = (f'{time.years:02}'
                    f'{time.months:02}'
                    f'{time.days:02}'
                    f'{time.hours:02}'
                    f'{time.minutes:02}'
                    f'{int(time.seconds):02}'
                    f'{round(time.seconds * 10) % 10}'
                    f'00R')

    elif isinstance(time, datetime.datetime):
        time_str = time.strftime('%y%m%d%H%M%S')
        time_str += str(round(time.microsecond / 100_000))

        time_with_tz = time if time.tzinfo is not None else time.astimezone()
        delta = time_with_tz.tzinfo.utcoffset(time_with_tz)

        offset = round(delta.total_seconds() / 60 / 15)

        time_str += f'{abs(offset):02}'
        time_str += ('-' if offset < 0 else '+')

    else:
        raise TypeError('unsupported time type')

    if len(time_str) not in [0, 16]:
        raise Exception('invalid time string length')

    yield from _encode_cstring(time_str)


def _decode_optional_params(command_id: CommandId,
                            data: util.Bytes
                            ) -> common.OptionalParams:
    optional_params = {}

    rest = data
    while rest:
        tag_int, value_len = struct.unpack('>HH', rest[:4])

        try:
            tag = common.OptionalParamTag(tag_int)

        except ValueError:
            raise CommandStatusError(common.CommandStatus.ESME_ROPTPARNOTALLWD)

        if tag not in _valid_optional_params[command_id]:
            raise CommandStatusError(common.CommandStatus.ESME_ROPTPARNOTALLWD)

        value_bytes, rest = rest[4:4+value_len], rest[4+value_len:]

        try:
            value = _decode_optional_param_value(tag, value_bytes)

        except Exception:
            raise CommandStatusError(common.CommandStatus.ESME_RINVOPTPARAMVAL)

        optional_params[tag] = value

    return optional_params


def _encode_optional_params(command_id: CommandId,
                            optional_params: common.OptionalParams
                            ) -> Iterable[int]:
    for tag, value in optional_params.items():
        if tag not in _valid_optional_params[command_id]:
            raise CommandStatusError(common.CommandStatus.ESME_ROPTPARNOTALLWD)

        value_bytes = bytes(_encode_optional_param_value(tag, value))

        yield from struct.pack('>HH', tag.value, len(value_bytes))
        yield from value_bytes


def _decode_optional_param_value(tag: common.OptionalParamTag,
                                 value_bytes: util.Bytes
                                 ) -> common.OptionalParamValue:
    if tag == common.OptionalParamTag.DEST_ADDR_SUBUNIT:
        return common.Subunit(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.DEST_NETWORK_TYPE:
        return common.NetworkType(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.DEST_BEARER_TYPE:
        return common.BearerType(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.DEST_TELEMATICS_ID:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.SOURCE_ADDR_SUBUNIT:
        return common.Subunit(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.SOURCE_NETWORK_TYPE:
        return common.NetworkType(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.SOURCE_BEARER_TYPE:
        return common.BearerType(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.SOURCE_TELEMATICS_ID:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.QOS_TIME_TO_LIVE:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.PAYLOAD_TYPE:
        return common.PayloadType(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.ADDITIONAL_STATUS_INFO_TEXT:
        value, _ = _decode_cstring(value_bytes)
        return value

    if tag == common.OptionalParamTag.RECEIPTED_MESSAGE_ID:
        value, _ = _decode_cbytes(value_bytes)
        return value

    if tag == common.OptionalParamTag.MS_MSG_WAIT_FACILITIES:
        return common.MsMsgWaitFacilities(
            active=bool(value_bytes[0] & 0x80),
            indicator=common.MessageWaitingIndicator(value_bytes[0] & 0x03))

    if tag == common.OptionalParamTag.PRIVACY_INDICATOR:
        return common.PrivacyIndicator(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.SOURCE_SUBADDRESS:
        return common.Subaddress(type=common.SubaddressType(value_bytes[0]),
                                 value=value_bytes[1:])

    if tag == common.OptionalParamTag.DEST_SUBADDRESS:
        return common.Subaddress(type=common.SubaddressType(value_bytes[0]),
                                 value=value_bytes[1:])

    if tag == common.OptionalParamTag.USER_MESSAGE_REFERENCE:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.USER_RESPONSE_CODE:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.SOURCE_PORT:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.DESTINATION_PORT:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.SAR_MSG_REF_NUM:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.LANGUAGE_INDICATOR:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.SAR_TOTAL_SEGMENTS:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.SAR_SEGMENT_SEQNUM:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.SC_INTERFACE_VERSION:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.CALLBACK_NUM_PRES_IND:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.CALLBACK_NUM_ATAG:
        return value_bytes

    if tag == common.OptionalParamTag.NUMBER_OF_MESSAGES:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.CALLBACK_NUM:
        return value_bytes

    if tag == common.OptionalParamTag.DPF_RESULT:
        return bool(value_bytes[0])

    if tag == common.OptionalParamTag.SET_DPF:
        return bool(value_bytes[0])

    if tag == common.OptionalParamTag.MS_AVAILABILITY_STATUS:
        return common.MsAvailabilityStatus(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.NETWORK_ERROR_CODE:
        return common.NetworkErrorCode(
            network_type=value_bytes[0],
            error_code=_decode_uint(value_bytes[1:]))

    if tag == common.OptionalParamTag.MESSAGE_PAYLOAD:
        return value_bytes

    if tag == common.OptionalParamTag.DELIVERY_FAILURE_REASON:
        return common.DeliveryFailureReason(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.MORE_MESSAGES_TO_SEND:
        return bool(value_bytes[0])

    if tag == common.OptionalParamTag.MESSAGE_STATE:
        return common.MessageState(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.USSD_SERVICE_OP:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.DISPLAY_TIME:
        return common.DisplayTime(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.SMS_SIGNAL:
        return _decode_uint(value_bytes)

    if tag == common.OptionalParamTag.MS_VALIDITY:
        return common.MsValidity(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.ALERT_ON_MESSAGE_DELIVERY:
        return tuple()

    if tag == common.OptionalParamTag.ITS_REPLY_TYPE:
        return common.ItsReplyType(_decode_uint(value_bytes))

    if tag == common.OptionalParamTag.ITS_SESSION_INFO:
        return common.ItsSessionInfo(
            session_number=value_bytes[0],
            sequence_number=value_bytes[1] >> 1,
            end_of_session=bool(value_bytes[1] & 0x01))

    raise ValueError('unsupported tag value')


def _encode_optional_param_value(tag: common.OptionalParamTag,
                                 value: common.OptionalParamValue
                                 ) -> Iterable[int]:
    if tag == common.OptionalParamTag.DEST_ADDR_SUBUNIT:
        if not isinstance(value, common.DestAddrSubunit):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.DEST_NETWORK_TYPE:
        if not isinstance(value, common.DestNetworkType):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.DEST_BEARER_TYPE:
        if not isinstance(value, common.DestBearerType):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.DEST_TELEMATICS_ID:
        if not isinstance(value, common.DestTelematicsId):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.SOURCE_ADDR_SUBUNIT:
        if not isinstance(value, common.SourceAddrSubunit):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.SOURCE_NETWORK_TYPE:
        if not isinstance(value, common.SourceNetworkType):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.SOURCE_BEARER_TYPE:
        if not isinstance(value, common.SourceBearerType):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.SOURCE_TELEMATICS_ID:
        if not isinstance(value, common.SourceTelematicsId):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.QOS_TIME_TO_LIVE:
        if not isinstance(value, common.QosTimeToLive):
            raise TypeError('invalid value type')

        yield from _encode_uint32(value)

    elif tag == common.OptionalParamTag.PAYLOAD_TYPE:
        if not isinstance(value, common.PayloadType):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.ADDITIONAL_STATUS_INFO_TEXT:
        if not isinstance(value, common.AdditionalStatusInfoText):
            raise TypeError('invalid value type')

        yield from _encode_cstring(value)

    elif tag == common.OptionalParamTag.RECEIPTED_MESSAGE_ID:
        if not isinstance(value, common.ReceiptedMessageId):
            raise TypeError('invalid value type')

        yield from _encode_cbytes(value)

    elif tag == common.OptionalParamTag.MS_MSG_WAIT_FACILITIES:
        if not isinstance(value, common.MsMsgWaitFacilities):
            raise TypeError('invalid value type')

        yield ((0x80 if value.active else 0x00) |
               (value.indicator.value & 0x03))

    elif tag == common.OptionalParamTag.PRIVACY_INDICATOR:
        if not isinstance(value, common.PrivacyIndicator):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.SOURCE_SUBADDRESS:
        if not isinstance(value, common.SourceSubaddress):
            raise TypeError('invalid value type')

        yield value.type.value
        yield from value.value

    elif tag == common.OptionalParamTag.DEST_SUBADDRESS:
        if not isinstance(value, common.DestSubaddress):
            raise TypeError('invalid value type')

        yield value.type.value
        yield from value.value

    elif tag == common.OptionalParamTag.USER_MESSAGE_REFERENCE:
        if not isinstance(value, common.UserMessageReference):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.USER_RESPONSE_CODE:
        if not isinstance(value, common.UserResponseCode):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.SOURCE_PORT:
        if not isinstance(value, common.SourcePort):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.DESTINATION_PORT:
        if not isinstance(value, common.DestinationPort):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.SAR_MSG_REF_NUM:
        if not isinstance(value, common.SarMsgRefNum):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.LANGUAGE_INDICATOR:
        if not isinstance(value, common.LanguageIndicator):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.SAR_TOTAL_SEGMENTS:
        if not isinstance(value, common.SarTotalSegments):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.SAR_SEGMENT_SEQNUM:
        if not isinstance(value, common.SarSegmentSeqnum):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.SC_INTERFACE_VERSION:
        if not isinstance(value, common.ScInterfaceVersion):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.CALLBACK_NUM_PRES_IND:
        if not isinstance(value, common.CallbackNumPresInd):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.CALLBACK_NUM_ATAG:
        if not isinstance(value, common.CallbackNumAtag):
            raise TypeError('invalid value type')

        yield from value

    elif tag == common.OptionalParamTag.NUMBER_OF_MESSAGES:
        if not isinstance(value, common.NumberOfMessages):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.CALLBACK_NUM:
        if not isinstance(value, common.CallbackNum):
            raise TypeError('invalid value type')

        yield from value

    elif tag == common.OptionalParamTag.DPF_RESULT:
        if not isinstance(value, common.DpfResult):
            raise TypeError('invalid value type')

        yield int(value)

    elif tag == common.OptionalParamTag.SET_DPF:
        if not isinstance(value, common.SetDpf):
            raise TypeError('invalid value type')

        yield int(value)

    elif tag == common.OptionalParamTag.MS_AVAILABILITY_STATUS:
        if not isinstance(value, common.MsAvailabilityStatus):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.NETWORK_ERROR_CODE:
        if not isinstance(value, common.NetworkErrorCode):
            raise TypeError('invalid value type')

        yield value.network_type
        yield from _encode_uint16(value.error_code)

    elif tag == common.OptionalParamTag.MESSAGE_PAYLOAD:
        if not isinstance(value, common.MessagePayload):
            raise TypeError('invalid value type')

        yield from value

    elif tag == common.OptionalParamTag.DELIVERY_FAILURE_REASON:
        if not isinstance(value, common.DeliveryFailureReason):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.MORE_MESSAGES_TO_SEND:
        if not isinstance(value, common.MoreMessagesToSend):
            raise TypeError('invalid value type')

        yield int(value)

    elif tag == common.OptionalParamTag.MESSAGE_STATE:
        if not isinstance(value, common.MessageState):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.USSD_SERVICE_OP:
        if not isinstance(value, common.UssdServiceOp):
            raise TypeError('invalid value type')

        yield value

    elif tag == common.OptionalParamTag.DISPLAY_TIME:
        if not isinstance(value, common.DisplayTime):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.SMS_SIGNAL:
        if not isinstance(value, common.SmsSignal):
            raise TypeError('invalid value type')

        yield from _encode_uint16(value)

    elif tag == common.OptionalParamTag.MS_VALIDITY:
        if not isinstance(value, common.MsValidity):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.ALERT_ON_MESSAGE_DELIVERY:
        yield from b''

    elif tag == common.OptionalParamTag.ITS_REPLY_TYPE:
        if not isinstance(value, common.ItsReplyType):
            raise TypeError('invalid value type')

        yield value.value

    elif tag == common.OptionalParamTag.ITS_SESSION_INFO:
        if not isinstance(value, common.ItsSessionInfo):
            raise TypeError('invalid value type')

        yield value.session_number
        yield ((value.sequence_number << 1) | int(value.end_of_session))

    else:
        raise ValueError('unsupported tag value')


def _decode_cstring(data: util.Bytes) -> tuple[str, util.Bytes]:
    i = 0
    while data[i] != 0:
        i += 1

    return str(data[:i], encoding='ascii'), data[i+1:]


def _encode_cstring(value: str) -> Iterable[int]:
    yield from bytes(value, encoding='ascii')
    yield 0


def _decode_cbytes(data: util.Bytes) -> tuple[util.Bytes, util.Bytes]:
    i = 0
    while data[i] != 0:
        i += 1

    return data[:i], data[i+1:]


def _encode_cbytes(value: util.Bytes) -> Iterable[int]:
    yield from value
    yield 0


def _decode_uint(data: util.Bytes) -> int:
    return int.from_bytes(data, 'big')


def _encode_uint16(value: int) -> Iterable[int]:
    yield from struct.pack('>H', value)


def _encode_uint32(value: int) -> Iterable[int]:
    yield from struct.pack('>I', value)


_valid_optional_params = {
    CommandId.GENERIC_NACK: set(),
    CommandId.BIND_RECEIVER_REQ: set(),
    CommandId.BIND_RECEIVER_RESP: {
        common.OptionalParamTag.SC_INTERFACE_VERSION},
    CommandId.BIND_TRANSMITTER_REQ: set(),
    CommandId.BIND_TRANSMITTER_RESP: {
        common.OptionalParamTag.SC_INTERFACE_VERSION},
    CommandId.QUERY_SM_REQ: set(),
    CommandId.QUERY_SM_RESP: set(),
    CommandId.SUBMIT_SM_REQ: {
        common.OptionalParamTag.USER_MESSAGE_REFERENCE,
        common.OptionalParamTag.SOURCE_PORT,
        common.OptionalParamTag.SOURCE_ADDR_SUBUNIT,
        common.OptionalParamTag.DESTINATION_PORT,
        common.OptionalParamTag.DEST_ADDR_SUBUNIT,
        common.OptionalParamTag.SAR_MSG_REF_NUM,
        common.OptionalParamTag.SAR_TOTAL_SEGMENTS,
        common.OptionalParamTag.SAR_SEGMENT_SEQNUM,
        common.OptionalParamTag.MORE_MESSAGES_TO_SEND,
        common.OptionalParamTag.PAYLOAD_TYPE,
        common.OptionalParamTag.MESSAGE_PAYLOAD,
        common.OptionalParamTag.PRIVACY_INDICATOR,
        common.OptionalParamTag.CALLBACK_NUM,
        common.OptionalParamTag.CALLBACK_NUM_PRES_IND,
        common.OptionalParamTag.CALLBACK_NUM_ATAG,
        common.OptionalParamTag.SOURCE_SUBADDRESS,
        common.OptionalParamTag.DEST_SUBADDRESS,
        common.OptionalParamTag.USER_RESPONSE_CODE,
        common.OptionalParamTag.DISPLAY_TIME,
        common.OptionalParamTag.SMS_SIGNAL,
        common.OptionalParamTag.MS_VALIDITY,
        common.OptionalParamTag.MS_MSG_WAIT_FACILITIES,
        common.OptionalParamTag.NUMBER_OF_MESSAGES,
        common.OptionalParamTag.ALERT_ON_MESSAGE_DELIVERY,
        common.OptionalParamTag.LANGUAGE_INDICATOR,
        common.OptionalParamTag.ITS_REPLY_TYPE,
        common.OptionalParamTag.ITS_SESSION_INFO,
        common.OptionalParamTag.USSD_SERVICE_OP},
    CommandId.SUBMIT_SM_RESP: set(),
    CommandId.DELIVER_SM_REQ: {
        common.OptionalParamTag.USER_MESSAGE_REFERENCE,
        common.OptionalParamTag.SOURCE_PORT,
        common.OptionalParamTag.DESTINATION_PORT,
        common.OptionalParamTag.SAR_MSG_REF_NUM,
        common.OptionalParamTag.SAR_TOTAL_SEGMENTS,
        common.OptionalParamTag.SAR_SEGMENT_SEQNUM,
        common.OptionalParamTag.USER_RESPONSE_CODE,
        common.OptionalParamTag.PRIVACY_INDICATOR,
        common.OptionalParamTag.PAYLOAD_TYPE,
        common.OptionalParamTag.MESSAGE_PAYLOAD,
        common.OptionalParamTag.CALLBACK_NUM,
        common.OptionalParamTag.SOURCE_SUBADDRESS,
        common.OptionalParamTag.DEST_SUBADDRESS,
        common.OptionalParamTag.LANGUAGE_INDICATOR,
        common.OptionalParamTag.ITS_SESSION_INFO,
        common.OptionalParamTag.NETWORK_ERROR_CODE,
        common.OptionalParamTag.MESSAGE_STATE,
        common.OptionalParamTag.RECEIPTED_MESSAGE_ID},
    CommandId.DELIVER_SM_RESP: set(),
    CommandId.UNBIND_REQ: set(),
    CommandId.UNBIND_RESP: set(),
    CommandId.REPLACE_SM_REQ: set(),
    CommandId.REPLACE_SM_RESP: set(),
    CommandId.CANCEL_SM_REQ: set(),
    CommandId.CANCEL_SM_RESP: set(),
    CommandId.BIND_TRANSCEIVER_REQ: set(),
    CommandId.BIND_TRANSCEIVER_RESP: {
        common.OptionalParamTag.SC_INTERFACE_VERSION},
    CommandId.OUTBIND: set(),
    CommandId.ENQUIRE_LINK_REQ: set(),
    CommandId.ENQUIRE_LINK_RESP: set(),
    CommandId.SUBMIT_MULTI_REQ: {
        common.OptionalParamTag.USER_MESSAGE_REFERENCE,
        common.OptionalParamTag.SOURCE_PORT,
        common.OptionalParamTag.SOURCE_ADDR_SUBUNIT,
        common.OptionalParamTag.DESTINATION_PORT,
        common.OptionalParamTag.DEST_ADDR_SUBUNIT,
        common.OptionalParamTag.SAR_MSG_REF_NUM,
        common.OptionalParamTag.SAR_TOTAL_SEGMENTS,
        common.OptionalParamTag.SAR_SEGMENT_SEQNUM,
        common.OptionalParamTag.PAYLOAD_TYPE,
        common.OptionalParamTag.MESSAGE_PAYLOAD,
        common.OptionalParamTag.PRIVACY_INDICATOR,
        common.OptionalParamTag.CALLBACK_NUM,
        common.OptionalParamTag.CALLBACK_NUM_PRES_IND,
        common.OptionalParamTag.CALLBACK_NUM_ATAG,
        common.OptionalParamTag.SOURCE_SUBADDRESS,
        common.OptionalParamTag.DEST_SUBADDRESS,
        common.OptionalParamTag.DISPLAY_TIME,
        common.OptionalParamTag.SMS_SIGNAL,
        common.OptionalParamTag.MS_VALIDITY,
        common.OptionalParamTag.MS_MSG_WAIT_FACILITIES,
        common.OptionalParamTag.ALERT_ON_MESSAGE_DELIVERY,
        common.OptionalParamTag.LANGUAGE_INDICATOR},
    CommandId.SUBMIT_MULTI_RESP: set(),
    CommandId.ALERT_NOTIFICATION: {
        common.OptionalParamTag.MS_AVAILABILITY_STATUS},
    CommandId.DATA_SM_REQ: {
        common.OptionalParamTag.SOURCE_PORT,
        common.OptionalParamTag.SOURCE_ADDR_SUBUNIT,
        common.OptionalParamTag.SOURCE_NETWORK_TYPE,
        common.OptionalParamTag.SOURCE_BEARER_TYPE,
        common.OptionalParamTag.SOURCE_TELEMATICS_ID,
        common.OptionalParamTag.DESTINATION_PORT,
        common.OptionalParamTag.DEST_ADDR_SUBUNIT,
        common.OptionalParamTag.DEST_NETWORK_TYPE,
        common.OptionalParamTag.DEST_BEARER_TYPE,
        common.OptionalParamTag.DEST_TELEMATICS_ID,
        common.OptionalParamTag.SAR_MSG_REF_NUM,
        common.OptionalParamTag.SAR_TOTAL_SEGMENTS,
        common.OptionalParamTag.SAR_SEGMENT_SEQNUM,
        common.OptionalParamTag.MORE_MESSAGES_TO_SEND,
        common.OptionalParamTag.QOS_TIME_TO_LIVE,
        common.OptionalParamTag.PAYLOAD_TYPE,
        common.OptionalParamTag.MESSAGE_PAYLOAD,
        common.OptionalParamTag.SET_DPF,
        common.OptionalParamTag.RECEIPTED_MESSAGE_ID,
        common.OptionalParamTag.MESSAGE_STATE,
        common.OptionalParamTag.NETWORK_ERROR_CODE,
        common.OptionalParamTag.USER_MESSAGE_REFERENCE,
        common.OptionalParamTag.PRIVACY_INDICATOR,
        common.OptionalParamTag.CALLBACK_NUM,
        common.OptionalParamTag.CALLBACK_NUM_PRES_IND,
        common.OptionalParamTag.CALLBACK_NUM_ATAG,
        common.OptionalParamTag.SOURCE_SUBADDRESS,
        common.OptionalParamTag.DEST_SUBADDRESS,
        common.OptionalParamTag.USER_RESPONSE_CODE,
        common.OptionalParamTag.DISPLAY_TIME,
        common.OptionalParamTag.SMS_SIGNAL,
        common.OptionalParamTag.MS_VALIDITY,
        common.OptionalParamTag.MS_MSG_WAIT_FACILITIES,
        common.OptionalParamTag.NUMBER_OF_MESSAGES,
        common.OptionalParamTag.ALERT_ON_MESSAGE_DELIVERY,
        common.OptionalParamTag.LANGUAGE_INDICATOR,
        common.OptionalParamTag.ITS_REPLY_TYPE,
        common.OptionalParamTag.ITS_SESSION_INFO},
    CommandId.DATA_SM_RESP: {
        common.OptionalParamTag.DELIVERY_FAILURE_REASON,
        common.OptionalParamTag.NETWORK_ERROR_CODE,
        common.OptionalParamTag.ADDITIONAL_STATUS_INFO_TEXT,
        common.OptionalParamTag.DPF_RESULT}}
