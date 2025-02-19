import enum
import typing

from hat.drivers import mms


class SupportedFeature(enum.Enum):
    BLOCK1 = 0
    BLOCK2 = 1
    BLOCK4 = 3
    BLOCK5 = 4
    BLOCK11 = 10
    BLOCK12 = 11


class ValueType(enum.Enum):
    REAL = 'REAL'
    STATE = 'STATE'
    DISCRETE = 'DISCRETE'


class QualityType(enum.Enum):
    NO_QUALITY = 'NO_QUALITY'
    QUALITY = 'QUALITY'


class TimestampType(enum.Enum):
    NO_TIMESTAMP = 'NO_TIMESTAMP'
    TIMESTAMP = 'TIMESTAMP'
    TIMESTAMP_EXTENDED = 'TIMESTAMP_EXTENDED'


class CovType(enum.Enum):
    NO_COV = 'NO_COV'
    COV = 'COV'


class DataType(typing.NamedTuple):
    value: ValueType
    quality: QualityType
    timestamp: TimestampType
    cov: CovType


class Validity(enum.Enum):
    VALID = 0
    HELD = 1
    SUSPECT = 2
    NOT_VALID = 3


class Source(enum.Enum):
    TELEMETERED = 0
    CALCULATED = 1
    ENTERED = 2
    ESTIMATED = 3


class ValueQuality(enum.Enum):
    NORMAL = 0
    ABNORMAL = 1


class TimestampQuality(enum.Enum):
    VALID = 0
    INVALID = 1


class Quality(enum.Enum):
    validity: Validity
    source: Source
    value: ValueQuality
    timestamp: TimestampQuality


class Data(typing.NamedTuple):
    name: str
    value: float | int
    quality: Quality | None = None
    timestamp: float | None = None
    """number of seconds since 1970-01-01"""
    cov: int | None = None
    """change of value counter"""


class VmdIdentifier(typing.NamedTuple):
    name: str


class DomainIdentifier(typing.NamedTuple):
    name: str
    domain: str


Identifier: typing.TypeAlias = VmdIdentifier | DomainIdentifier


class Dataset(typing.NamedTuple):
    identifier: Identifier
    data: dict[Identifier, DataType]  # order is significant


class TransfersetCondition(enum.Enum):
    INTERVAL_TIMEOUT = 0
    INTEGRITY_TIMEOUT = 1
    OBJECT_CHANGE = 2
    OPERATOR_REQUEST = 3
    OTHER_EXTERNAL_EVENT = 4


class Transferset(typing.NamedTuple):
    identifier: Identifier
    dataset_identifier: Identifier
    start_time: int
    interval: int
    tle: int
    buffer_time: int
    integrity_check: int
    conditions: set[TransfersetCondition]
    block_data: bool
    critical: bool
    rbe: bool
    all_changes_reported: bool
    status: bool
    event_code_requested: int


def validate_data_type(data_type: DataType):
    if (data_type.value == ValueType.STATE and
            data_type.quality == QualityType.NO_QUALITY):
        raise ValueError('state value without quality not supported')

    if (data_type.timestamp != TimestampType.NO_TIMESTAMP and
            data_type.quality == QualityType.NO_QUALITY):
        raise ValueError('timestamp without quality not supported')

    if (data_type.cov == CovType.COV and
            data_type.timestamp != TimestampType.TIMESTAMP):
        raise ValueError('cov without non extended timestamp not supported')


def get_system_identifiers(domain: str) -> set[Identifier]:
    return {VmdIdentifier('TASE2_Version'),
            VmdIdentifier('Supported_Features'),
            DomainIdentifier('Bilateral_Table_ID', domain),
            DomainIdentifier('DSConditions', domain),
            DomainIdentifier('DSConditions_Detected', domain),
            DomainIdentifier('Event_Code_Detected', domain),
            DomainIdentifier('Next_DSTransfer_Set', domain),
            DomainIdentifier('Transfer_Report_ACK', domain),
            DomainIdentifier('Transfer_Report_NACK', domain),
            DomainIdentifier('Transfer_Set_Name', domain),
            DomainIdentifier('Transfer_Set_Time_Stamp', domain)}


def identifier_to_object_name(identifier: Identifier
                              ) -> mms.ObjectName:
    if isinstance(identifier, VmdIdentifier):
        return mms.VmdSpecificObjectName(identifier.name)

    if isinstance(identifier, DomainIdentifier):
        return mms.DomainSpecificObjectName(domain_id=identifier.domain,
                                            item_id=identifier.name)

    raise TypeError('unsupported identifier type')


def identifier_from_object_name(object_name: mms.ObjectName
                                ) -> Identifier:
    if isinstance(object_name, mms.VmdSpecificObjectName):
        return VmdIdentifier(object_name.identifier)

    if isinstance(object_name, mms.DomainSpecificObjectName):
        return DomainIdentifier(name=object_name.item_id,
                                domain=object_name.domain_id)

    raise TypeError('unsupported object name type')
