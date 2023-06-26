import abc
import enum
import typing
import datetime

from hat import asn1
from hat import util


Request = type('Request', (abc.ABC, ), {})
Response = type('Response', (abc.ABC, ), {})
Unconfirmed = type('Unconfirmed', (abc.ABC, ), {})
Data = type('Data', (abc.ABC, ), {})
TypeDescription = type('TypeDescription', (abc.ABC, ), {})
ObjectName = type('ObjectName', (abc.ABC, ), {})
ObjectScope = type('ObjectScope', (abc.ABC, ), {})
VariableSpecification = type('VariableSpecification', (abc.ABC, ), {})


def request(cls):
    Request.register(cls)
    return cls


def response(cls):
    Response.register(cls)
    return cls


def unconfirmed(cls):
    Unconfirmed.register(cls)
    return cls


def data(cls):
    Data.register(cls)
    return cls


def type_description(cls):
    TypeDescription.register(cls)
    return cls


def object_name(cls):
    ObjectName.register(cls)
    return cls


def object_scope(cls):
    ObjectScope.register(cls)
    return cls


def variable_specification(cls):
    VariableSpecification.register(cls)
    return cls


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


class ErrorClass(enum.Enum):
    ACCESS = 'access'
    APPLICATION_REFERENCE = 'application-reference'
    CANCEL = 'cancel'
    CONCLUDE = 'conclude'
    DEFINITION = 'definition'
    FILE = 'file'
    INITIATE = 'initiate'
    OTHERS = 'others'
    RESOURCE = 'resource'
    SERVICE = 'service'
    SERVICE_PREEMPT = 'service-preempt'
    TIME_RESOLUTION = 'time-resolution'
    VMD_STATE = 'vmd-state'


@request
class StatusRequest(typing.NamedTuple):
    pass


@request
class GetNameListRequest(typing.NamedTuple):
    object_class: ObjectClass
    object_scope: ObjectScope
    continue_after: str | None


@request
class IdentifyRequest(typing.NamedTuple):
    pass


@request
class GetVariableAccessAttributesRequest(typing.NamedTuple):
    value: ObjectName | int | str | util.Bytes


@request
class GetNamedVariableListAttributesRequest(typing.NamedTuple):
    value: ObjectName


@request
class ReadRequest(typing.NamedTuple):
    value: list[VariableSpecification] | ObjectName


@request
class WriteRequest(typing.NamedTuple):
    specification: list[VariableSpecification] | ObjectName
    data: list[Data]


@request
class DefineNamedVariableListRequest(typing.NamedTuple):
    name: ObjectName
    specification: list[VariableSpecification]


@request
class DeleteNamedVariableListRequest(typing.NamedTuple):
    names: list[ObjectName]


@response
class ErrorResponse(typing.NamedTuple):
    error_class: ErrorClass
    value: int


@response
class StatusResponse(typing.NamedTuple):
    logical: int
    physical: int


@response
class GetNameListResponse(typing.NamedTuple):
    identifiers: list[str]
    more_follows: bool


@response
class IdentifyResponse(typing.NamedTuple):
    vendor: str
    model: str
    revision: str
    syntaxes: list[asn1.ObjectIdentifier] | None


@response
class GetVariableAccessAttributesResponse(typing.NamedTuple):
    mms_deletable: bool
    type_description: TypeDescription


@response
class GetNamedVariableListAttributesResponse(typing.NamedTuple):
    mms_deletable: bool
    specification: list[VariableSpecification]


@response
class ReadResponse(typing.NamedTuple):
    results: list[DataAccessError | Data]


@response
class WriteResponse(typing.NamedTuple):
    results: list[DataAccessError | None]


@response
class DefineNamedVariableListResponse(typing.NamedTuple):
    pass


@response
class DeleteNamedVariableListResponse(typing.NamedTuple):
    matched: int
    deleted: int


@unconfirmed
class EventNotificationUnconfirmed(typing.NamedTuple):
    enrollment: ObjectName
    condition: ObjectName
    severity: int
    time: Data | int | None


@unconfirmed
class InformationReportUnconfirmed(typing.NamedTuple):
    specification: list[VariableSpecification] | ObjectName
    data: list[DataAccessError | Data]


@unconfirmed
class UnsolicitedStatusUnconfirmed(typing.NamedTuple):
    logical: int
    physical: int


@data
class ArrayData(typing.NamedTuple):
    elements: list[Data]


@data
class BcdData(typing.NamedTuple):
    value: int


@data
class BinaryTimeData(typing.NamedTuple):
    value: datetime.datetime


@data
class BitStringData(typing.NamedTuple):
    value: list[bool]


@data
class BooleanData(typing.NamedTuple):
    value: bool


@data
class BooleanArrayData(typing.NamedTuple):
    value: list[bool]


@data
class FloatingPointData(typing.NamedTuple):
    value: float


@data
class GeneralizedTimeData(typing.NamedTuple):
    value: str


@data
class IntegerData(typing.NamedTuple):
    value: int


@data
class MmsStringData(typing.NamedTuple):
    value: str


@data
class ObjIdData(typing.NamedTuple):
    value: asn1.ObjectIdentifier


@data
class OctetStringData(typing.NamedTuple):
    value: asn1.Bytes


@data
class StructureData(typing.NamedTuple):
    elements: list[Data]


@data
class UnsignedData(typing.NamedTuple):
    value: int


@data
class UtcTimeData(typing.NamedTuple):
    value: datetime.datetime
    leap_second: bool
    clock_failure: bool
    not_synchronized: bool
    accuracy: int | None
    """accurate fraction bits [0,24]"""


@data
class VisibleStringData(typing.NamedTuple):
    value: str


@type_description
class ArrayTypeDescription(typing.NamedTuple):
    number_of_elements: int
    element_type: TypeDescription | ObjectName


@type_description
class BcdTypeDescription(typing.NamedTuple):
    xyz: int


@type_description
class BinaryTimeTypeDescription(typing.NamedTuple):
    xyz: bool


@type_description
class BitStringTypeDescription(typing.NamedTuple):
    xyz: int


@type_description
class BooleanTypeDescription(typing.NamedTuple):
    pass


@type_description
class FloatingPointTypeDescription(typing.NamedTuple):
    format_width: int
    exponent_width: int


@type_description
class GeneralizedTimeTypeDescription(typing.NamedTuple):
    pass


@type_description
class IntegerTypeDescription(typing.NamedTuple):
    xyz: int


@type_description
class MmsStringTypeDescription(typing.NamedTuple):
    xyz: int


@type_description
class ObjIdTypeDescription(typing.NamedTuple):
    pass


@type_description
class OctetStringTypeDescription(typing.NamedTuple):
    xyz: int


@type_description
class StructureTypeDescription(typing.NamedTuple):
    components: list[tuple[str | None, TypeDescription | ObjectName]]


@type_description
class UnsignedTypeDescription(typing.NamedTuple):
    xyz: int


@type_description
class UtcTimeTypeDescription(typing.NamedTuple):
    pass


@type_description
class VisibleStringTypeDescription(typing.NamedTuple):
    xyz: int


@object_name
class AaSpecificObjectName(typing.NamedTuple):
    identifier: str


@object_name
class DomainSpecificObjectName(typing.NamedTuple):
    domain_id: str
    item_id: str


@object_name
class VmdSpecificObjectName(typing.NamedTuple):
    identifier: str


@object_scope
class AaSpecificObjectScope(typing.NamedTuple):
    pass


@object_scope
class DomainSpecificObjectScope(typing.NamedTuple):
    identifier: str


@object_scope
class VmdSpecificObjectScope(typing.NamedTuple):
    pass


@variable_specification
class AddressVariableSpecification(typing.NamedTuple):
    address: int | str | asn1.Bytes


@variable_specification
class InvalidatedVariableSpecification(typing.NamedTuple):
    pass


@variable_specification
class NameVariableSpecification(typing.NamedTuple):
    name: ObjectName


@variable_specification
class ScatteredAccessDescriptionVariableSpecification(typing.NamedTuple):
    specifications: list[VariableSpecification]


@variable_specification
class VariableDescriptionVariableSpecification(typing.NamedTuple):
    address: int | str | asn1.Bytes
    type_specification: TypeDescription | ObjectName
