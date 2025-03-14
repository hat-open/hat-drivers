from collections.abc import Collection
import enum
import typing
import datetime

from hat import asn1
from hat import util


class DataAccessError(enum.Enum):
    OBJECT_INVALIDATED = 0
    HARDWARE_FAULT = 1
    TEMPORARILY_UNAVAILABLE = 2
    OBJECT_ACCESS_DENIED = 3
    OBJECT_UNDEFINED = 4
    INVALID_ADDRESS = 5
    TYPE_UNSUPPORTED = 6
    TYPE_INCONSISTENT = 7
    OBJECT_ATTRIBUTE_INCONSISTENT = 8
    OBJECT_ACCESS_UNSUPPORTED = 9
    OBJECT_NON_EXISTENT = 10
    OBJECT_VALUE_INVALID = 11


class ObjectClass(enum.Enum):
    NAMED_VARIABLE = 0
    NAMED_VARIABLE_LIST = 2
    JOURNAL = 8
    DOMAIN = 9
    UNDEFINED = 0xFF


# object name #################################################################

class AaSpecificObjectName(typing.NamedTuple):
    identifier: str


class DomainSpecificObjectName(typing.NamedTuple):
    domain_id: str
    item_id: str


class VmdSpecificObjectName(typing.NamedTuple):
    identifier: str


ObjectName: typing.TypeAlias = (AaSpecificObjectName |
                                DomainSpecificObjectName |
                                VmdSpecificObjectName)


# object scope ################################################################

class AaSpecificObjectScope(typing.NamedTuple):
    pass


class DomainSpecificObjectScope(typing.NamedTuple):
    identifier: str


class VmdSpecificObjectScope(typing.NamedTuple):
    pass


ObjectScope: typing.TypeAlias = (AaSpecificObjectScope |
                                 DomainSpecificObjectScope |
                                 VmdSpecificObjectScope)


# data ########################################################################

class ArrayData(typing.NamedTuple):
    elements: Collection['Data']


class BcdData(typing.NamedTuple):
    value: int


class BinaryTimeData(typing.NamedTuple):
    value: datetime.datetime


class BitStringData(typing.NamedTuple):
    value: Collection[bool]


class BooleanData(typing.NamedTuple):
    value: bool


class BooleanArrayData(typing.NamedTuple):
    value: Collection[bool]


class FloatingPointData(typing.NamedTuple):
    value: float


class GeneralizedTimeData(typing.NamedTuple):
    value: str


class IntegerData(typing.NamedTuple):
    value: int


class MmsStringData(typing.NamedTuple):
    value: str


class ObjIdData(typing.NamedTuple):
    value: asn1.ObjectIdentifier


class OctetStringData(typing.NamedTuple):
    value: util.Bytes


class StructureData(typing.NamedTuple):
    elements: Collection['Data']


class UnsignedData(typing.NamedTuple):
    value: int


class UtcTimeData(typing.NamedTuple):
    value: datetime.datetime
    leap_second: bool
    clock_failure: bool
    not_synchronized: bool
    accuracy: int | None
    """accurate fraction bits [0,24]"""


class VisibleStringData(typing.NamedTuple):
    value: str


Data: typing.TypeAlias = (ArrayData |
                          BcdData |
                          BinaryTimeData |
                          BitStringData |
                          BooleanData |
                          BooleanArrayData |
                          FloatingPointData |
                          GeneralizedTimeData |
                          IntegerData |
                          MmsStringData |
                          ObjIdData |
                          OctetStringData |
                          StructureData |
                          UnsignedData |
                          UtcTimeData |
                          VisibleStringData)


# type description ############################################################

class ArrayTypeDescription(typing.NamedTuple):
    number_of_elements: int
    element_type: typing.Union['TypeDescription', ObjectName]


class BcdTypeDescription(typing.NamedTuple):
    xyz: int


class BinaryTimeTypeDescription(typing.NamedTuple):
    xyz: bool


class BitStringTypeDescription(typing.NamedTuple):
    xyz: int


class BooleanTypeDescription(typing.NamedTuple):
    pass


class FloatingPointTypeDescription(typing.NamedTuple):
    format_width: int
    exponent_width: int


class GeneralizedTimeTypeDescription(typing.NamedTuple):
    pass


class IntegerTypeDescription(typing.NamedTuple):
    xyz: int


class MmsStringTypeDescription(typing.NamedTuple):
    xyz: int


class ObjIdTypeDescription(typing.NamedTuple):
    pass


class OctetStringTypeDescription(typing.NamedTuple):
    xyz: int


class StructureTypeDescription(typing.NamedTuple):
    components: Collection[tuple[str | None,
                                 typing.Union['TypeDescription', ObjectName]]]


class UnsignedTypeDescription(typing.NamedTuple):
    xyz: int


class UtcTimeTypeDescription(typing.NamedTuple):
    pass


class VisibleStringTypeDescription(typing.NamedTuple):
    xyz: int


TypeDescription: typing.TypeAlias = (ArrayTypeDescription |
                                     BcdTypeDescription |
                                     BinaryTimeTypeDescription |
                                     BitStringTypeDescription |
                                     BooleanTypeDescription |
                                     FloatingPointTypeDescription |
                                     GeneralizedTimeTypeDescription |
                                     IntegerTypeDescription |
                                     MmsStringTypeDescription |
                                     ObjIdTypeDescription |
                                     OctetStringTypeDescription |
                                     StructureTypeDescription |
                                     UnsignedTypeDescription |
                                     UtcTimeTypeDescription |
                                     VisibleStringTypeDescription)


# variable specification ######################################################

class AddressVariableSpecification(typing.NamedTuple):
    address: int | str | util.Bytes


class InvalidatedVariableSpecification(typing.NamedTuple):
    pass


class NameVariableSpecification(typing.NamedTuple):
    name: ObjectName


class ScatteredAccessDescriptionVariableSpecification(typing.NamedTuple):
    specifications: Collection['VariableSpecification']


class VariableDescriptionVariableSpecification(typing.NamedTuple):
    address: int | str | util.Bytes
    type_specification: TypeDescription | ObjectName


VariableSpecification: typing.TypeAlias = (
    AddressVariableSpecification |
    InvalidatedVariableSpecification |
    NameVariableSpecification |
    ScatteredAccessDescriptionVariableSpecification |
    VariableDescriptionVariableSpecification)


# request #####################################################################

class StatusRequest(typing.NamedTuple):
    pass


class GetNameListRequest(typing.NamedTuple):
    object_class: ObjectClass
    object_scope: ObjectScope
    continue_after: str | None


class IdentifyRequest(typing.NamedTuple):
    pass


class GetVariableAccessAttributesRequest(typing.NamedTuple):
    value: ObjectName | int | str | util.Bytes


class GetNamedVariableListAttributesRequest(typing.NamedTuple):
    value: ObjectName


class ReadRequest(typing.NamedTuple):
    value: Collection[VariableSpecification] | ObjectName


class WriteRequest(typing.NamedTuple):
    specification: Collection[VariableSpecification] | ObjectName
    data: Collection[Data]


class DefineNamedVariableListRequest(typing.NamedTuple):
    name: ObjectName
    specification: Collection[VariableSpecification]


class DeleteNamedVariableListRequest(typing.NamedTuple):
    names: Collection[ObjectName]


Request: typing.TypeAlias = (StatusRequest |
                             GetNameListRequest |
                             IdentifyRequest |
                             GetVariableAccessAttributesRequest |
                             GetNamedVariableListAttributesRequest |
                             ReadRequest |
                             WriteRequest |
                             DefineNamedVariableListRequest |
                             DeleteNamedVariableListRequest)


# response ####################################################################

class StatusResponse(typing.NamedTuple):
    logical: int
    physical: int


class GetNameListResponse(typing.NamedTuple):
    identifiers: Collection[str]
    more_follows: bool


class IdentifyResponse(typing.NamedTuple):
    vendor: str
    model: str
    revision: str
    syntaxes: Collection[asn1.ObjectIdentifier] | None


class GetVariableAccessAttributesResponse(typing.NamedTuple):
    mms_deletable: bool
    type_description: TypeDescription


class GetNamedVariableListAttributesResponse(typing.NamedTuple):
    mms_deletable: bool
    specification: Collection[VariableSpecification]


class ReadResponse(typing.NamedTuple):
    results: Collection[DataAccessError | Data]


class WriteResponse(typing.NamedTuple):
    results: Collection[DataAccessError | None]


class DefineNamedVariableListResponse(typing.NamedTuple):
    pass


class DeleteNamedVariableListResponse(typing.NamedTuple):
    matched: int
    deleted: int


Response: typing.TypeAlias = (StatusResponse |
                              GetNameListResponse |
                              IdentifyResponse |
                              GetVariableAccessAttributesResponse |
                              GetNamedVariableListAttributesResponse |
                              ReadResponse |
                              WriteResponse |
                              DefineNamedVariableListResponse |
                              DeleteNamedVariableListResponse)


# error #######################################################################

class VmdStateError(enum.Enum):
    OTHER = 0
    VMD_STATE_CONFLICT = 1
    VMD_OPERATIONAL_PROBLEM = 2
    DOMAIN_TRANSFER_PROBLEM = 3
    STATE_MACHINE_ID_INVALID = 4


class ApplicationReferenceError(enum.Enum):
    OTHER = 0
    APPLICATION_UNREACHABLE = 1
    CONNECTION_LOST = 2
    APPLICATION_REFERENCE_INVALID = 3
    CONTEXT_UNSUPPORTED = 4


class DefinitionError(enum.Enum):
    OTHER = 0
    OBJECT_UNDEFINED = 1
    INVALID_ADDRESS = 2
    TYPE_UNSUPPORTED = 3
    TYPE_INCONSISTENT = 4
    OBJECT_EXISTS = 5
    OBJECT_ATTRIBUTE_INCONSISTENT = 6


class ResourceError(enum.Enum):
    OTHER = 0
    MEMORY_UNAVAILABLE = 1
    PROCESSOR_RESOURCE_UNAVAILABLE = 2
    MASS_STORAGE_UNAVAILABLE = 3
    CAPABILITY_UNAVAILABLE = 4
    CAPABILITY_UNKNOWN = 5


class ServiceError(enum.Enum):
    OTHER = 0
    PRIMITIVES_OUT_OF_SEQUENCE = 1
    OBJECT_STATE_CONFLICT = 2
    PDU_SIZE = 3
    CONTINUATION_INVALID = 4
    OBJECT_CONSTRAINT_CONFLICT = 5


class ServicePreemptError(enum.Enum):
    OTHER = 0
    TIMEOUT = 1
    DEADLOCK = 2
    CANCEL = 3


class TimeResolutionError(enum.Enum):
    OTHER = 0
    UNSUPPORTABLE_TIME_RESOLUTION = 1


class AccessError(enum.Enum):
    OTHER = 0
    OBJECT_ACCESS_UNSUPPORTED = 1
    OBJECT_NON_EXISTENT = 2
    OBJECT_ACCESS_DENIED = 3
    OBJECT_INVALIDATED = 4


class InitiateError(enum.Enum):
    OTHER = 0
    MAX_SERVICES_OUTSTANDING_CALLING_INSUFFICIENT = 3
    MAX_SERVICES_OUTSTANDING_CALLED_INSUFFICIENT = 4
    SERVICE_CBB_INSUFFICIENT = 5
    PARAMETER_CBB_INSUFFICIENT = 6
    NESTING_LEVEL_INSUFFICIENT = 7


class ConcludeError(enum.Enum):
    OTHER = 0
    FURTHER_COMMUNICATION_REQUIRED = 1


class CancelError(enum.Enum):
    OTHER = 0
    INVOKE_ID_UNKNOWN = 1
    CANCEL_NOT_POSSIBLE = 2


class FileError(enum.Enum):
    OTHER = 0
    FILENAME_AMBIGUOUS = 1
    FILE_BUSY = 2
    FILENAME_SYNTAX_ERROR = 3
    CONTENT_TYPE_INVALID = 4
    POSITION_INVALID = 5
    FILE_ACCESS_DENIED = 6
    FILE_NON_EXISTENT = 7
    DUPLICATE_FILENAME = 8
    INSUFFICIENT_SPACE_IN_FILESTORE = 9


class OtherError(typing.NamedTuple):
    value: int


Error: typing.TypeAlias = (VmdStateError |
                           ApplicationReferenceError |
                           DefinitionError |
                           ResourceError |
                           ServiceError |
                           ServicePreemptError |
                           TimeResolutionError |
                           AccessError |
                           InitiateError |
                           ConcludeError |
                           CancelError |
                           FileError |
                           OtherError)


# unconfirmed #################################################################

class EventNotificationUnconfirmed(typing.NamedTuple):
    enrollment: ObjectName
    condition: ObjectName
    severity: int
    time: Data | int | None


class InformationReportUnconfirmed(typing.NamedTuple):
    specification: Collection[VariableSpecification] | ObjectName
    data: Collection[DataAccessError | Data]


class UnsolicitedStatusUnconfirmed(typing.NamedTuple):
    logical: int
    physical: int


Unconfirmed: typing.TypeAlias = (EventNotificationUnconfirmed |
                                 InformationReportUnconfirmed |
                                 UnsolicitedStatusUnconfirmed)
