import collections
import logging
import typing

from hat import util

from hat.drivers import acse
from hat.drivers import tcp
from hat.drivers.mms import common


Msg: typing.TypeAlias = (common.Request |
                         common.Response |
                         common.Error |
                         common.Unconfirmed)


def create_server_logger(logger: logging.Logger,
                         name: str | None,
                         info: tcp.ServerInfo | None
                         ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'MmsServer',
                      'name': name}}

    if info is not None:
        extra['meta']['addresses'] = [{'host': addr.host,
                                       'port': addr.port}
                                      for addr in info.addresses]

    return logging.LoggerAdapter(logger, extra)


def create_connection_logger(logger: logging.Logger,
                             info: acse.ConnectionInfo):
    extra = {'meta': {'type': 'MmsConnection',
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: acse.ConnectionInfo):
        extra = {'meta': {'type': 'MmsConnection',
                          'name': info.name,
                          'local_addr': {'host': info.local_addr.host,
                                         'port': info.local_addr.port},
                          'remote_addr': {'host': info.remote_addr.host,
                                          'port': info.remote_addr.port}}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            msg: Msg | None = None):  # NOQA
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if msg is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_msg(msg),
                            stacklevel=2)


def _format_msg(msg):
    segments = collections.deque()

    if isinstance(msg, common.StatusRequest):
        segments.append('StatusReq')

    elif isinstance(msg, common.GetNameListRequest):
        segments.append('GetNameListReq')
        segments.append(f"class={msg.object_class.name}")
        segments.append(f"scope={_format_object_scope(msg.object_scope)}")

        if msg.continue_after is not None:
            segments.append(f"after={msg.continue_after}")

    elif isinstance(msg, common.IdentifyRequest):
        segments.append('IdentifyReq')

    elif isinstance(msg, common.GetVariableAccessAttributesRequest):
        segments.append('GetVariableAccessAttributesReq')

        if isinstance(msg.value, common.ObjectName):
            segments.append(_format_object_name(msg.value))

        elif isinstance(msg.value, (int, str)):
            segments.append(str(msg.value))

        elif isinstance(msg.value, util.Bytes):
            segments.append(f"({msg.value.hex(' ')})")

        else:
            raise TypeError('unsupported value type')

    elif isinstance(msg, common.GetNamedVariableListAttributesRequest):
        segments.append('GetNamedVariableListAttributesReq')
        segments.append(_format_object_name(msg.value))

    elif isinstance(msg, common.ReadRequest):
        segments.append('ReadReq')

        if isinstance(msg.value, common.ObjectName):
            segments.append(_format_object_name(msg.value))

        else:
            segments.extend(_format_variable_specification(i)
                            for i in msg.value)

    elif isinstance(msg, common.WriteRequest):
        segments.append('WriteReq')

        if isinstance(msg.specification, common.ObjectName):
            segments.append(f"spec={_format_object_name(msg.specification)}")

        else:
            specifications = [_format_variable_specification(i)
                              for i in msg.specification]
            segments.append(f"spec={_format_segments(specifications)}")

        segments.append(
            f"data={_format_segments([_format_data(i) for i in msg.data])}")

    elif isinstance(msg, common.DefineNamedVariableListRequest):
        segments.append('DefineNamedVariableListReq')
        segments.append(f"name={_format_object_name(msg.name)}")

        specifications = [_format_variable_specification(i)
                          for i in msg.specification]
        segments.append(f"spec={_format_segments(specifications)}")

    elif isinstance(msg, common.DeleteNamedVariableListRequest):
        segments.append('DeleteNamedVariableListReq')
        segments.append(
            f"{_format_segments([_format_object_name(i) for i in msg.names])}")

    elif isinstance(msg, common.StatusResponse):
        segments.append('StatusRes')
        segments.append(f"logical={msg.logical}")
        segments.append(f"physical={msg.physical}")

    elif isinstance(msg, common.GetNameListResponse):
        segments.append('GetNameListRes')
        segments.append(_format_segments(msg.identifiers))

        if msg.more_follows:
            segments.append('more_follows')

    elif isinstance(msg, common.IdentifyResponse):
        segments.append('IdentifyRes')
        segments.append(f"vendor={msg.vendor}")
        segments.append(f"model={msg.model}")
        segments.append(f"revision={msg.revision}")

        if msg.syntaxes is not None:
            segments.append(_format_segments([_format_object_identifier(i)
                                              for i in msg.syntaxes]))

    elif isinstance(msg, common.GetVariableAccessAttributesResponse):
        segments.append('GetVariableAccessAttributesRes')

        if msg.mms_deletable:
            segments.append('deletable')

        segments.append(_format_type_description(msg.type_description))

    elif isinstance(msg, common.GetNamedVariableListAttributesResponse):
        segments.append('GetNamedVariableListAttributesRes')

        if msg.mms_deletable:
            segments.append('deletable')

        specification = [_format_variable_specification(i)
                         for i in msg.specification]
        segments.append(_format_segments(specification))

    elif isinstance(msg, common.ReadResponse):
        segments.append('ReadRes')

        for result in msg.results:
            if isinstance(result, common.DataAccessError):
                segments.append(result.name)

            elif isinstance(result, common.Data):
                segments.append(_format_data(result))

            else:
                raise TypeError('unsupported result type')

    elif isinstance(msg, common.WriteResponse):
        segments.append('WriteRes')

        for result in msg.results:
            if isinstance(result, common.DataAccessError):
                segments.append(result.name)

            elif result is None:
                segments.append('None')

            else:
                raise TypeError('unsupported result type')

    elif isinstance(msg, common.DefineNamedVariableListResponse):
        segments.append('DefineNamedVariableListRes')

    elif isinstance(msg, common.DeleteNamedVariableListResponse):
        segments.append('DeleteNamedVariableListRes')
        segments.append(f"matched={msg.matched}")
        segments.append(f"deleted={msg.deleted}")

    elif isinstance(msg, common.Error):
        segments.append(type(msg).__name__)

        if isinstance(msg, common.OtherError):
            segments.append(str(msg.value))

        else:
            segments.append(msg.name)

    elif isinstance(msg, common.EventNotificationUnconfirmed):
        segments.append('EventNotification')
        segments.append(f"enrollment={_format_object_name(msg.enrollment)}")
        segments.append(f"condition={_format_object_name(msg.condition)}")
        segments.append(f"severity={msg.severity}")

        if isinstance(msg.time, common.Data):
            segments.append(f"time={_format_data(msg.time)}")

        elif isinstance(msg.time, int):
            segments.append(f"time={msg.time}")

        elif msg.time is None:
            pass

        else:
            raise TypeError('unsupported time type')

    elif isinstance(msg, common.InformationReportUnconfirmed):
        segments.append('InformationReport')

        if isinstance(msg.specification, common.ObjectName):
            segments.append(f"spec={_format_object_name(msg.specification)}")

        else:
            specifications = [_format_variable_specification(i)
                              for i in msg.specification]
            segments.append(f"spec={_format_segments(specifications)}")

        data = collections.deque()
        for i in msg.data:
            if isinstance(i, common.DataAccessError):
                data.append(i.name)

            elif isinstance(i, common.Data):
                data.append(_format_data(i))

            else:
                raise TypeError('unsupported data type')

        segments.append(f"data={_format_segments(data)}")

    elif isinstance(msg, common.UnsolicitedStatusUnconfirmed):
        segments.append('UnsolicitedStatus')
        segments.append(f"logical={msg.logical}")
        segments.append(f"physical={msg.physical}")

    else:
        raise TypeError('unsupported message type')

    return _format_segments(segments)


def _format_object_scope(object_scope):
    if isinstance(object_scope, common.AaSpecificObjectScope):
        return 'Aa'

    if isinstance(object_scope, common.DomainSpecificObjectScope):
        return f"(Domain {object_scope.identifier})"

    if isinstance(object_scope, common.VmdSpecificObjectScope):
        return 'Vmd'

    raise TypeError('unsupported object scope type')


def _format_object_name(object_name):
    if isinstance(object_name, common.AaSpecificObjectName):
        return f"(Aa {object_name.identifier})"

    if isinstance(object_name, common.DomainSpecificObjectName):
        return (f"(Domain "
                f"domain={object_name.domain_id} "
                f"item={object_name.item_id})")

    if isinstance(object_name, common.VmdSpecificObjectName):
        return f"(Vmd {object_name.identifier})"

    raise TypeError('unsupported object name type')


def _format_variable_specification(variable_specification):
    segments = collections.deque()

    if isinstance(variable_specification, common.AddressVariableSpecification):
        if isinstance(variable_specification.address, (int, str)):
            segments.append(str(variable_specification.address))

        elif isinstance(variable_specification.address, util.Bytes):
            segments.append(f"({variable_specification.address.hex(' ')})")

        else:
            raise TypeError('unsupported address type')

    elif isinstance(variable_specification,
                    common.InvalidatedVariableSpecification):
        segments.append('Invalidated')

    elif isinstance(variable_specification, common.NameVariableSpecification):
        segments.append(_format_object_name(variable_specification.name))

    elif isinstance(variable_specification,
                    common.ScatteredAccessDescriptionVariableSpecification):
        specifications = [_format_variable_specification(i)
                          for i in variable_specification.specifications]
        segments.append(f"{_format_segments(specifications)}")

    elif isinstance(variable_specification,
                    common.VariableDescriptionVariableSpecification):
        segments.append('VariableDescription')

        if isinstance(variable_specification.address, (int, str)):
            segments.append(f"addr={variable_specification.address}")

        elif isinstance(variable_specification.address, util.Bytes):
            segments.append(
                f"addr=({variable_specification.address.hex(' ')})")

        else:
            raise TypeError('unsupported address type')

        if isinstance(variable_specification.type_specification,
                      common.TypeDescription):
            segments.append(
                f"type={_format_type_specification(variable_specification.type_specification)}")  # NOQA

        elif isinstance(variable_specification.type_specification,
                        common.ObjectName):
            segments.append(
                f"type={_format_object_name(variable_specification.type_specification)}")  # NOQA

        else:
            raise TypeError('unsupported address type')

    else:
        raise TypeError('unsupported variable specification type')

    return _format_segments(segments)


def _format_data(data):
    segments = collections.deque()

    if isinstance(data, common.BinaryTimeData):
        segments.append(data.value.isoformat())

    elif isinstance(data, common.ObjIdData):
        segments.append(_format_object_identifier(data.value))

    elif isinstance(data, common.OctetStringData):
        segments.append(f"({data.value.hex(' ')})")

    elif isinstance(data, common.UtcTimeData):
        segments.append(data.value.isoformat())

        if data.leap_second:
            segments.append('leap_second')

        if data.clock_failure:
            segments.append('clock_failure')

        if data.not_synchronized:
            segments.append('not_synchronized')

        if data.accuracy is not None:
            segments.append(f"accuracy={data.accuracy}")

    elif isinstance(data, (common.ArrayData,
                           common.StructureData)):
        segments.append(
            f"{_format_segments([_format_data(i) for i in data.elements])}")

    elif isinstance(data, (common.BcdData,
                           common.BitStringData,
                           common.BooleanData,
                           common.BooleanArrayData,
                           common.FloatingPointData,
                           common.GeneralizedTimeData,
                           common.IntegerData,
                           common.MmsStringData,
                           common.UnsignedData,
                           common.VisibleStringData)):
        segments.append(str(data.value))

    else:
        raise TypeError('unsupported data type')

    return _format_segments(segments)


def _format_type_description(type_description):
    segments = collections.deque()

    if isinstance(type_description, common.ArrayTypeDescription):
        segments.append('Array')
        segments.append(f"size={type_description.number_of_elements}")

        if isinstance(type_description.element_type, common.TypeDescription):
            segments.append(
                f"type={_format_type_description(type_description.element_type)}")  # NOQA

        elif isinstance(type_description.element_type, common.ObjectName):
            segments.append(
                f"type={_format_object_name(type_description.element_type)}")

        else:
            raise TypeError('unsupported element type')

    elif isinstance(type_description, common.BcdTypeDescription):
        segments.append('Bcd')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.BinaryTimeTypeDescription):
        segments.append('BinaryTime')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.BitStringTypeDescription):
        segments.append('BitString')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.BooleanTypeDescription):
        segments.append('Boolean')

    elif isinstance(type_description, common.FloatingPointTypeDescription):
        segments.append('Floating')
        segments.append(f"format={type_description.format_width}")
        segments.append(f"exponent={type_description.exponent_width}")

    elif isinstance(type_description, common.GeneralizedTimeTypeDescription):
        segments.append('GeneralizedTime')

    elif isinstance(type_description, common.IntegerTypeDescription):
        segments.append('Integer')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.MmsStringTypeDescription):
        segments.append('MmsString')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.ObjIdTypeDescription):
        segments.append('ObjId')

    elif isinstance(type_description, common.OctetStringTypeDescription):
        segments.append('OctetString')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.StructureTypeDescription):
        segments.append('Structure')

        for component_name, component_type in type_description.components:
            subsegments = collections.deque()

            if component_name is not None:
                subsegments.append(component_name)

            if isinstance(component_type, common.TypeDescription):
                subsegments.append(_format_type_description(component_type))

            elif isinstance(component_type, common.ObjectName):
                subsegments.append(_format_object_name(component_type))

            else:
                raise TypeError('unsupported component type')

            segments.append(_format_segments(subsegments))

    elif isinstance(type_description, common.UnsignedTypeDescription):
        segments.append('Unsigned')
        segments.append(str(type_description.xyz))

    elif isinstance(type_description, common.UtcTimeTypeDescription):
        segments.append('UtcTime')

    elif isinstance(type_description, common.VisibleStringTypeDescription):
        segments.append('VisibleString')
        segments.append(str(type_description.xyz))

    else:
        raise TypeError('unsupported type description')

    return _format_segments(segments)


def _format_object_identifier(oid):
    return '.'.join(str(i) for i in oid)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
