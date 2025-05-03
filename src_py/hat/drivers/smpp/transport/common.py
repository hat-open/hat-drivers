from hat.drivers.smpp.common import *  # NOQA

import datetime
import enum
import typing

from hat import util

from hat.drivers.smpp.common import (MessageId,
                                     Priority,
                                     TypeOfNumber,
                                     DataCoding)


class CommandStatus(enum.Enum):
    ESME_ROK = 0x00
    ESME_RINVMSGLEN = 0x01
    ESME_RINVCMDLEN = 0x02
    ESME_RINVCMDID = 0x03
    ESME_RINVBNDSTS = 0x04
    ESME_RALYBND = 0x05
    ESME_RINVPRTFLG = 0x06
    ESME_RINVREGDLVFLG = 0x07
    ESME_RSYSERR = 0x08
    ESME_RINVSRCADR = 0x0a
    ESME_RINVDSTADR = 0x0b
    ESME_RINVMSGID = 0x0c
    ESME_RBINDFAIL = 0x0d
    ESME_RINVPASWD = 0x0e
    ESME_RINVSYSID = 0x0f
    ESME_RCANCELFAIL = 0x11
    ESME_RREPLACEFAIL = 0x13
    ESME_RMSGQFUL = 0x14
    ESME_RINVSERTYP = 0x15
    ESME_RINVNUMDESTS = 0x33
    ESME_RINVDLNAME = 0x34
    ESME_RINVDESTFLAG = 0x40
    ESME_RINVSUBREP = 0x42
    ESME_RINVESMCLASS = 0x43
    ESME_RCNTSUBDL = 0x44
    ESME_RSUBMITFAIL = 0x45
    ESME_RINVSRCTON = 0x48
    ESME_RINVSRCNPI = 0x49
    ESME_RINVDSTTON = 0x50
    ESME_RINVDSTNPI = 0x51
    ESME_RINVSYSTYP = 0x53
    ESME_RINVREPFLAG = 0x54
    ESME_RINVNUMMSGS = 0x55
    ESME_RTHROTTLED = 0x58
    ESME_RINVSCHED = 0x61
    ESME_RINVEXPIRY = 0x62
    ESME_RINVDFTMSGID = 0x63
    ESME_RX_T_APPN = 0x64
    ESME_RX_P_APPN = 0x65
    ESME_RX_R_APPN = 0x66
    ESME_RQUERYFAIL = 0x67
    ESME_RINVOPTPARSTREAM = 0xc0
    ESME_ROPTPARNOTALLWD = 0xc1
    ESME_RINVPARLEN = 0xc2
    ESME_RMISSINGOPTPARAM = 0xc3
    ESME_RINVOPTPARAMVAL = 0xc4
    ESME_RDELIVERYFAILURE = 0xfe
    ESME_RUNKNOWNERR = 0xff


command_status_descriptions: dict[CommandStatus, str] = {
    CommandStatus.ESME_ROK: 'No Error',
    CommandStatus.ESME_RINVMSGLEN: 'Message Length is invalid',
    CommandStatus.ESME_RINVCMDLEN: 'Command Length is invalid',
    CommandStatus.ESME_RINVCMDID: 'Invalid Command ID',
    CommandStatus.ESME_RINVBNDSTS: 'Incorrect BIND Status for given command',
    CommandStatus.ESME_RALYBND: 'ESME Already in Bound State',
    CommandStatus.ESME_RINVPRTFLG: 'Invalid Priority Flag',
    CommandStatus.ESME_RINVREGDLVFLG: 'Invalid Registered Delivery Flag',
    CommandStatus.ESME_RSYSERR: 'System Error',
    CommandStatus.ESME_RINVSRCADR: 'Invalid Source Address',
    CommandStatus.ESME_RINVDSTADR: 'Invalid Dest Addr',
    CommandStatus.ESME_RINVMSGID: 'Message ID is invalid',
    CommandStatus.ESME_RBINDFAIL: 'Bind Failed',
    CommandStatus.ESME_RINVPASWD: 'Invalid Password',
    CommandStatus.ESME_RINVSYSID: 'Invalid System ID',
    CommandStatus.ESME_RCANCELFAIL: 'Cancel SM Failed',
    CommandStatus.ESME_RREPLACEFAIL: 'Replace SM Failed',
    CommandStatus.ESME_RMSGQFUL: 'Message Queue Full',
    CommandStatus.ESME_RINVSERTYP: 'Invalid Service Type',
    CommandStatus.ESME_RINVNUMDESTS: 'Invalid number of destinations',
    CommandStatus.ESME_RINVDLNAME: 'Invalid Distribution List name',
    CommandStatus.ESME_RINVDESTFLAG: 'Destination flag is invalid',
    CommandStatus.ESME_RINVSUBREP: 'Invalid submit with replace request',
    CommandStatus.ESME_RINVESMCLASS: 'Invalid esm_class field data',
    CommandStatus.ESME_RCNTSUBDL: 'Cannot Submit to Distribution List',
    CommandStatus.ESME_RSUBMITFAIL: 'submit_sm or submit_multi failed',
    CommandStatus.ESME_RINVSRCTON: 'Invalid Source address TON',
    CommandStatus.ESME_RINVSRCNPI: 'Invalid Source address NPI',
    CommandStatus.ESME_RINVDSTTON: 'Invalid Destination address TON',
    CommandStatus.ESME_RINVDSTNPI: 'Invalid Destination address NPI',
    CommandStatus.ESME_RINVSYSTYP: 'Invalid system_type field',
    CommandStatus.ESME_RINVREPFLAG: 'Invalid replace_if_present flag',
    CommandStatus.ESME_RINVNUMMSGS: 'Invalid number of messages',
    CommandStatus.ESME_RTHROTTLED: 'Throttling error',
    CommandStatus.ESME_RINVSCHED: 'Invalid Scheduled Delivery Time',
    CommandStatus.ESME_RINVEXPIRY: 'Invalid message validity period',
    CommandStatus.ESME_RINVDFTMSGID: 'Predefined Message Invalid or Not Found',
    CommandStatus.ESME_RX_T_APPN: 'ESME Receiver Temporary App Error Code',
    CommandStatus.ESME_RX_P_APPN: 'ESME Receiver Permanent App Error Code',
    CommandStatus.ESME_RX_R_APPN: 'ESME Receiver Reject Message Error Code',
    CommandStatus.ESME_RQUERYFAIL: 'query_sm request failed',
    CommandStatus.ESME_RINVOPTPARSTREAM: 'Error in the optional part of the PDU Body',  # NOQA
    CommandStatus.ESME_ROPTPARNOTALLWD: 'Optional Parameter not allowed',
    CommandStatus.ESME_RINVPARLEN: 'Invalid Parameter Length',
    CommandStatus.ESME_RMISSINGOPTPARAM: 'Expected Optional Parameter missing',
    CommandStatus.ESME_RINVOPTPARAMVAL: 'Invalid Optional Parameter Value',
    CommandStatus.ESME_RDELIVERYFAILURE: 'Delivery Failure',
    CommandStatus.ESME_RUNKNOWNERR: 'Unknown Error'}


class BindType(enum.Enum):
    TRANSMITTER = 'TRANSMITTER'
    RECEIVER = 'RECEIVER'
    TRANSCEIVER = 'TRANSCEIVER'


class NumericPlanIndicator(enum.Enum):
    UNKNOWN = 0
    ISDN = 1
    DATA = 3
    TELEX = 4
    LAND_MOBILE = 6
    NATIONAL = 8
    PRIVATE = 9
    ERMES = 10
    INTERNET = 14
    WAP_CLIENT_ID = 18


class MessagingMode(enum.Enum):
    DEFAULT = 0
    DATAGRAM = 1
    FORWARD = 2
    STORE_AND_FORWARD = 3


class MessageType(enum.Enum):
    DEFAULT = 0
    DELIVERY_RECEIPT = 1
    DELIVERY_ACKNOWLEDGEMENT = 2
    MANUAL_ACKNOWLEDGEMENT = 4
    CONVERSATION_ABORT = 6
    INTERMEDIATE_DELIVERY_NOTIFICATION = 8


class GsmFeature(enum.Enum):
    UDHI = 1
    REPLY_PATH = 2


class EsmClass(typing.NamedTuple):
    messaging_mode: MessagingMode
    message_type: MessageType
    gsm_features: set[GsmFeature]


AbsoluteTime: typing.TypeAlias = datetime.datetime


class RelativeTime(typing.NamedTuple):
    years: int = 0  # [0, 99]
    months: int = 0  # [0, 12]
    days: int = 0  # [0, 31]
    hours: int = 0  # [0, 23]
    minutes: int = 0  # [0, 59]
    seconds: float = 0  # [0, 59.9]


Time: typing.TypeAlias = AbsoluteTime | RelativeTime


class DeliveryReceipt(enum.Enum):
    NO_RECEIPT = 0
    RECEIPT = 1
    RECEIPT_ON_FAILURE = 2


class Acknowledgement(enum.Enum):
    DELIVERY = 1
    MANUAL = 2


class RegisteredDelivery(typing.NamedTuple):
    delivery_receipt: DeliveryReceipt
    acknowledgements: set[Acknowledgement]
    intermediate_notification: bool


class Subunit(enum.Enum):
    UNKNOWN = 0
    MS_DISPLAY = 1
    MOBILE_EQUIPMENT = 2
    SMART_CARD = 3
    EXTERNAL_UNIT = 4


class NetworkType(enum.Enum):
    UNKNOWN = 0
    GSM = 1
    TDMA = 2
    CDMA = 3
    PDC = 4
    PHS = 5
    IDEN = 6
    AMPS = 7
    PAGING_NETWORK = 8


class BearerType(enum.Enum):
    UNKNOWN = 0
    SMS = 1
    CSD = 2
    PACKET_DATA = 3
    USSD = 4
    CDPD = 5
    DATATAC = 6
    FLEX = 7
    CELL_BROADCAST = 8


class MessageWaitingIndicator(enum.Enum):
    VOICEMAIL = 0
    FAX = 1
    ELECTRONICE_MAIL = 2
    OTHER = 3


class SubaddressType(enum.Enum):
    NSAP_EVEN = 0x80
    NSAP_ODD = 0x88
    USER = 0xa0


class Subaddress(typing.NamedTuple):
    type: SubaddressType
    value: util.Bytes


# optional parameter ##########################################################

class OptionalParamTag(enum.Enum):
    DEST_ADDR_SUBUNIT = 0x0005
    DEST_NETWORK_TYPE = 0x0006
    DEST_BEARER_TYPE = 0x0007
    DEST_TELEMATICS_ID = 0x0008
    SOURCE_ADDR_SUBUNIT = 0x000d
    SOURCE_NETWORK_TYPE = 0x000e
    SOURCE_BEARER_TYPE = 0x000f
    SOURCE_TELEMATICS_ID = 0x0010
    QOS_TIME_TO_LIVE = 0x0017
    PAYLOAD_TYPE = 0x0019
    ADDITIONAL_STATUS_INFO_TEXT = 0x001d
    RECEIPTED_MESSAGE_ID = 0x001e
    MS_MSG_WAIT_FACILITIES = 0x0030
    PRIVACY_INDICATOR = 0x0201
    SOURCE_SUBADDRESS = 0x0202
    DEST_SUBADDRESS = 0x0203
    USER_MESSAGE_REFERENCE = 0x0204
    USER_RESPONSE_CODE = 0x0205
    SOURCE_PORT = 0x020a
    DESTINATION_PORT = 0x020b
    SAR_MSG_REF_NUM = 0x020c
    LANGUAGE_INDICATOR = 0x020d
    SAR_TOTAL_SEGMENTS = 0x020e
    SAR_SEGMENT_SEQNUM = 0x020f
    SC_INTERFACE_VERSION = 0x0210
    CALLBACK_NUM_PRES_IND = 0x0302
    CALLBACK_NUM_ATAG = 0x0303
    NUMBER_OF_MESSAGES = 0x0304
    CALLBACK_NUM = 0x0381
    DPF_RESULT = 0x0420
    SET_DPF = 0x0421
    MS_AVAILABILITY_STATUS = 0x0422
    NETWORK_ERROR_CODE = 0x0423
    MESSAGE_PAYLOAD = 0x0424
    DELIVERY_FAILURE_REASON = 0x0425
    MORE_MESSAGES_TO_SEND = 0x0426
    MESSAGE_STATE = 0x0427
    USSD_SERVICE_OP = 0x0501
    DISPLAY_TIME = 0x1201
    SMS_SIGNAL = 0x1203
    MS_VALIDITY = 0x1204
    ALERT_ON_MESSAGE_DELIVERY = 0x130c
    ITS_REPLY_TYPE = 0x1380
    ITS_SESSION_INFO = 0x1383


DestAddrSubunit: typing.TypeAlias = Subunit

DestNetworkType: typing.TypeAlias = NetworkType

DestBearerType: typing.TypeAlias = BearerType

DestTelematicsId: typing.TypeAlias = int  # [0, 0xffff]

SourceAddrSubunit: typing.TypeAlias = Subunit

SourceNetworkType: typing.TypeAlias = NetworkType

SourceBearerType: typing.TypeAlias = BearerType

SourceTelematicsId: typing.TypeAlias = int  # [0, 0xffff]

QosTimeToLive: typing.TypeAlias = int  # [0, 0xffffffff]


class PayloadType(enum.Enum):
    DEFAULT = 0
    WCMP = 1


AdditionalStatusInfoText: typing.TypeAlias = str  # max byte len 255

ReceiptedMessageId: typing.TypeAlias = MessageId


class MsMsgWaitFacilities(typing.NamedTuple):
    active: bool
    indicator: MessageWaitingIndicator


class PrivacyIndicator(enum.Enum):
    NOT_RESTRICTED = 0
    RESTRICTED = 1
    CONFIDENTAL = 2
    SECRET = 3


SourceSubaddress: typing.TypeAlias = Subaddress

DestSubaddress: typing.TypeAlias = Subaddress

UserMessageReference: typing.TypeAlias = int  # [0, 0xffff]

UserResponseCode: typing.TypeAlias = int  # [0, 0xff]

SourcePort: typing.TypeAlias = int  # [0, 0xffff]

DestinationPort: typing.TypeAlias = int  # [0, 0xffff]

SarMsgRefNum: typing.TypeAlias = int  # [0, 0xffff]

LanguageIndicator: typing.TypeAlias = int  # [0, 0xff]

SarTotalSegments: typing.TypeAlias = int  # [1, 0xff]

SarSegmentSeqnum: typing.TypeAlias = int  # [1, 0xff]

ScInterfaceVersion: typing.TypeAlias = int  # [0, 0x34]

CallbackNumPresInd: typing.TypeAlias = int  # [0, 0x0f]

CallbackNumAtag: typing.TypeAlias = util.Bytes

NumberOfMessages: typing.TypeAlias = int  # [0, 99]

CallbackNum: typing.TypeAlias = util.Bytes  # min len 4; max len 19

DpfResult: typing.TypeAlias = bool

SetDpf: typing.TypeAlias = bool


class MsAvailabilityStatus(enum.Enum):
    AVAILABLE = 0
    DENIED = 1
    UNAVAILABLE = 2


class NetworkErrorCode(typing.NamedTuple):
    network_type: int  # [1, 3]
    error_code: int  # [0, 0xffff]


MessagePayload: typing.TypeAlias = util.Bytes


class DeliveryFailureReason(enum.Enum):
    DESTINATION_UNAVAILABLE = 0
    DESTINATION_ADDRESS_INVALID = 1
    PERMANENT_NETWORK_ERROR = 2
    TEMPORARY_NETWORK_ERROR = 3


MoreMessagesToSend: typing.TypeAlias = bool


class MessageState(enum.Enum):
    ENROUTE = 1
    DELIVERED = 2
    EXPIRED = 3
    DELETED = 4
    UNDELIVERABLE = 5
    ACCEPTED = 6
    UNKNOWN = 7
    REJECTED = 8


UssdServiceOp: typing.TypeAlias = int  # [0, 0xff]


class DisplayTime(enum.Enum):
    TEMPORARY = 0
    DEFAULT = 1
    INVOKE = 2


SmsSignal: typing.TypeAlias = int  # [0, 0xffff]


class MsValidity(enum.Enum):
    STORE_INDEFINITELY = 0
    POWER_DOWN = 1
    REGISTRATION_AREA = 2
    DISPLAY_ONLY = 3


AlertOnMessageDelivery: typing.TypeAlias = tuple[()]


class ItsReplyType(enum.Enum):
    DIGIT = 0
    NUMBER = 1
    TELEPHONE_NUMBER = 2
    PASSWORD = 3
    CHARACTER_LINE = 4
    MENU = 5
    DATE = 6
    TIME = 7
    CONTINUE = 8


class ItsSessionInfo(typing.NamedTuple):
    session_number: int  # [0, 0xff]
    sequence_number: int  # [0, 0x7f]
    end_of_session: bool


OptionalParamValue: typing.TypeAlias = (DestAddrSubunit |
                                        DestNetworkType |
                                        DestBearerType |
                                        DestTelematicsId |
                                        SourceAddrSubunit |
                                        SourceNetworkType |
                                        SourceBearerType |
                                        SourceTelematicsId |
                                        QosTimeToLive |
                                        PayloadType |
                                        AdditionalStatusInfoText |
                                        ReceiptedMessageId |
                                        MsMsgWaitFacilities |
                                        PrivacyIndicator |
                                        SourceSubaddress |
                                        DestSubaddress |
                                        UserMessageReference |
                                        UserResponseCode |
                                        SourcePort |
                                        DestinationPort |
                                        SarMsgRefNum |
                                        LanguageIndicator |
                                        SarTotalSegments |
                                        SarSegmentSeqnum |
                                        ScInterfaceVersion |
                                        CallbackNumPresInd |
                                        CallbackNumAtag |
                                        NumberOfMessages |
                                        CallbackNum |
                                        DpfResult |
                                        SetDpf |
                                        MsAvailabilityStatus |
                                        NetworkErrorCode |
                                        MessagePayload |
                                        DeliveryFailureReason |
                                        MoreMessagesToSend |
                                        MessageState |
                                        UssdServiceOp |
                                        DisplayTime |
                                        SmsSignal |
                                        MsValidity |
                                        AlertOnMessageDelivery |
                                        ItsReplyType |
                                        ItsSessionInfo)

OptionalParams: typing.TypeAlias = dict[OptionalParamTag, OptionalParamValue]


# request #####################################################################

class BindReq(typing.NamedTuple):
    bind_type: BindType
    system_id: str  # max byte len 15
    password: str  # max byte len 8
    system_type: str  # max byte len 12
    interface_version: int  # [0, 0x34]
    addr_ton: TypeOfNumber
    addr_npi: NumericPlanIndicator
    address_range: str  # max byte len 40


class UnbindReq(typing.NamedTuple):
    pass


class SubmitSmReq(typing.NamedTuple):
    service_type: str  # max byte len 5
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 20
    dest_addr_ton: TypeOfNumber
    dest_addr_npi: NumericPlanIndicator
    destination_addr: str  # max byte len 20
    esm_class: EsmClass
    protocol_id: int  # [0, 0xff]
    priority_flag: Priority
    schedule_delivery_time: Time | None
    validity_period: Time | None
    registered_delivery: RegisteredDelivery
    replace_if_present_flag: bool
    data_coding: DataCoding
    sm_default_msg_id: int  # [0, 0xfe]
    short_message: util.Bytes  # max len 254
    optional_params: OptionalParams


# TODO
class SubmitMultiReq(typing.NamedTuple):
    pass


class DeliverSmReq(typing.NamedTuple):
    service_type: str  # max byte len 5
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 20
    dest_addr_ton: TypeOfNumber
    dest_addr_npi: NumericPlanIndicator
    destination_addr: str  # max byte len 20
    esm_class: EsmClass
    protocol_id: int  # [0, 0xff]
    priority_flag: Priority
    registered_delivery: RegisteredDelivery
    data_coding: DataCoding
    short_message: util.Bytes  # max len 254
    optional_params: OptionalParams


class DataSmReq(typing.NamedTuple):
    service_type: str  # max byte len 5
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 20
    dest_addr_ton: TypeOfNumber
    dest_addr_npi: NumericPlanIndicator
    destination_addr: str  # max byte len 20
    esm_class: EsmClass
    registered_delivery: RegisteredDelivery
    data_coding: DataCoding
    optional_params: OptionalParams


class QuerySmReq(typing.NamedTuple):
    message_id: MessageId
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 20


class CancelSmReq(typing.NamedTuple):
    service_type: str  # max byte len 5
    message_id: MessageId
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 20
    dest_addr_ton: TypeOfNumber
    dest_addr_npi: NumericPlanIndicator
    destination_addr: str  # max byte len 20


class ReplaceSmReq(typing.NamedTuple):
    message_id: MessageId
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 20
    schedule_delivery_time: Time | None
    validity_period: Time | None
    registered_delivery: RegisteredDelivery
    sm_default_msg_id: int  # [0, 0xfe]
    short_message: util.Bytes  # max len 254


class EnquireLinkReq(typing.NamedTuple):
    pass


Request: typing.TypeAlias = (BindReq |
                             UnbindReq |
                             SubmitSmReq |
                             SubmitMultiReq |
                             DeliverSmReq |
                             DataSmReq |
                             QuerySmReq |
                             CancelSmReq |
                             ReplaceSmReq |
                             EnquireLinkReq)


# response ####################################################################

class BindRes(typing.NamedTuple):
    bind_type: BindType
    system_id: str  # max byte len 15
    optional_params: OptionalParams


class UnbindRes(typing.NamedTuple):
    pass


class SubmitSmRes(typing.NamedTuple):
    message_id: MessageId


# TODO
class SubmitMultiRes(typing.NamedTuple):
    pass


class DeliverSmRes(typing.NamedTuple):
    pass


class DataSmRes(typing.NamedTuple):
    message_id: MessageId
    optional_params: OptionalParams


class QuerySmRes(typing.NamedTuple):
    message_id: MessageId
    final_date: Time | None
    message_state: MessageState
    error_code: int  # [0, 0xff]


class CancelSmRes(typing.NamedTuple):
    pass


class ReplaceSmRes(typing.NamedTuple):
    pass


class EnquireLinkRes(typing.NamedTuple):
    pass


Response: typing.TypeAlias = (BindRes |
                              UnbindRes |
                              SubmitSmRes |
                              SubmitMultiRes |
                              DeliverSmRes |
                              DataSmRes |
                              QuerySmRes |
                              CancelSmRes |
                              ReplaceSmRes |
                              EnquireLinkRes)


# notification ################################################################

class OutbindNotification(typing.NamedTuple):
    system_id: str  # max byte len 15
    password: str  # max byte len 8


class AlertNotification(typing.NamedTuple):
    source_addr_ton: TypeOfNumber
    source_addr_npi: NumericPlanIndicator
    source_addr: str  # max byte len 64
    esme_addr_ton: TypeOfNumber
    esme_addr_npi: NumericPlanIndicator
    esme_addr: str  # max byte len 64
    optional_params: OptionalParams


Notification: typing.TypeAlias = (OutbindNotification |
                                  AlertNotification)
