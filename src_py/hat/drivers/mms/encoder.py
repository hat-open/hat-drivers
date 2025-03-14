import datetime
import struct

from hat import asn1

from hat.drivers.mms import common


def encode_request(req: common.Request) -> asn1.Value:
    """Encode request"""
    if isinstance(req, common.StatusRequest):
        return 'status', False

    if isinstance(req, common.GetNameListRequest):
        service = {
            'objectClass': ('basicObjectClass', req.object_class.value),
            'objectScope': _encode_object_scope(req.object_scope)}

        if req.continue_after is not None:
            service['continueAfter'] = req.continue_after

        return 'getNameList', service

    if isinstance(req, common.IdentifyRequest):
        return 'identify', None

    if isinstance(req, common.GetVariableAccessAttributesRequest):
        if isinstance(req.value, common.ObjectName):
            service = 'name', _encode_object_name(req.value)

        else:
            service = 'address', _encode_address(req.value)

        return 'getVariableAccessAttributes', service

    if isinstance(req, common.GetNamedVariableListAttributesRequest):
        return 'getNamedVariableListAttributes', _encode_object_name(req.value)

    if isinstance(req, common.ReadRequest):
        if isinstance(req.value, common.ObjectName):
            specification = 'variableListName', _encode_object_name(req.value)

        else:
            specification = 'listOfVariable', [
                {'variableSpecification': _encode_variable_specification(i)}
                for i in req.value]

        return 'read', {'variableAccessSpecification': specification}

    if isinstance(req, common.WriteRequest):
        if isinstance(req.specification, common.ObjectName):
            specification = ('variableListName',
                             _encode_object_name(req.specification))

        else:
            specification = 'listOfVariable', [
                {'variableSpecification': _encode_variable_specification(i)}
                for i in req.specification]

        return 'write', {
            'variableAccessSpecification': specification,
            'listOfData': [_encode_data(i) for i in req.data]}

    if isinstance(req, common.DefineNamedVariableListRequest):
        return 'defineNamedVariableList', {
            'variableListName': _encode_object_name(req.name),
            'listOfVariable': [
                {'variableSpecification': _encode_variable_specification(i)}
                for i in req.specification]}

    if isinstance(req, common.DeleteNamedVariableListRequest):
        return 'deleteNamedVariableList', {
            'listOfVariableListName': [_encode_object_name(i)
                                       for i in req.names]}

    raise TypeError('unsupported req type')


def decode_request(req: asn1.Value) -> common.Request:
    """Decode request"""
    name, data = req

    if name == 'status':
        return common.StatusRequest()

    if name == 'getNameList':
        subname, subdata = data['objectClass']

        if subname == 'basicObjectClass':
            object_class = common.ObjectClass(subdata)

        else:
            object_class = common.ObjectClass.UNDEFINED

        object_scope = _decode_object_scope(data['objectScope'])
        continue_after = data.get('continueAfter')

        return common.GetNameListRequest(object_class=object_class,
                                         object_scope=object_scope,
                                         continue_after=continue_after)

    if name == 'identify':
        return common.IdentifyRequest()

    if name == 'getVariableAccessAttributes':
        subname, subdata = data

        if subname == 'address':
            value = _decode_address(subdata)

        elif subname == 'name':
            value = _decode_object_name(subdata)

        else:
            raise ValueError('unsupported subname')

        return common.GetVariableAccessAttributesRequest(value)

    if name == 'getNamedVariableListAttributes':
        return common.GetNamedVariableListAttributesRequest(
            _decode_object_name(data))

    if name == 'read':
        subname, subdata = data['variableAccessSpecification']

        if subname == 'variableListName':
            value = _decode_object_name(subdata)

        elif subname == 'listOfVariable':
            value = [_decode_variable_specification(i['variableSpecification'])
                     for i in subdata]

        else:
            raise ValueError('unsupported subname')

        return common.ReadRequest(value)

    if name == 'write':
        subname, subdata = data['variableAccessSpecification']

        if subname == 'variableListName':
            specification = _decode_object_name(subdata)

        elif subname == 'listOfVariable':
            specification = [
                _decode_variable_specification(i['variableSpecification'])
                for i in subdata]

        else:
            raise ValueError('unsupported subname')

        return common.WriteRequest(
            specification=specification,
            data=[_decode_data(i) for i in data['listOfData']])

    if name == 'defineNamedVariableList':
        return common.DefineNamedVariableListRequest(
            name=_decode_object_name(data['variableListName']),
            specification=[
                _decode_variable_specification(i['variableSpecification'])
                for i in data['listOfVariable']])

    if name == 'deleteNamedVariableList':
        return common.DeleteNamedVariableListRequest(
            [_decode_object_name(i)
             for i in data.get('listOfVariableListName', [])])

    raise ValueError('unsupported name')


def encode_response(res: common.Response) -> asn1.Value:
    """Encode response"""
    if isinstance(res, common.StatusResponse):
        return 'status', {
            'vmdLogicalStatus': res.logical,
            'vmdPhysicalStatus': res.physical}

    if isinstance(res, common.GetNameListResponse):
        return 'getNameList', {
            'listOfIdentifier': list(res.identifiers),
            'moreFollows': res.more_follows}

    if isinstance(res, common.IdentifyResponse):
        service = {'vendorName': res.vendor,
                   'modelName': res.model,
                   'revision': res.revision}

        if res.syntaxes is not None:
            service['listOfAbstractSyntaxes'] = list(res.syntaxes)

        return 'identify', service

    if isinstance(res, common.GetVariableAccessAttributesResponse):
        return 'getVariableAccessAttributes', {
            'mmsDeletable': res.mms_deletable,
            'typeDescription': _encode_type_description(res.type_description)}

    if isinstance(res, common.GetNamedVariableListAttributesResponse):
        return 'getNamedVariableListAttributes', {
            'mmsDeletable': res.mms_deletable,
            'listOfVariable': [
                {'variableSpecification': _encode_variable_specification(i)}
                for i in res.specification]}

    if isinstance(res, common.ReadResponse):
        results = [
            (('failure', i.value) if isinstance(i, common.DataAccessError)
             else ('success', _encode_data(i)))
            for i in res.results]

        return 'read', {'listOfAccessResult': results}

    if isinstance(res, common.WriteResponse):
        results = [
            (('success', None) if i is None else ('failure', i.value))
            for i in res.results]

        return 'write', results

    if isinstance(res, common.DefineNamedVariableListResponse):
        return 'defineNamedVariableList', None

    if isinstance(res, common.DeleteNamedVariableListResponse):
        return 'deleteNamedVariableList', {
            'numberMatched': res.matched,
            'numberDeleted': res.deleted}

    raise TypeError('unsupported res type')


def decode_response(res: asn1.Value) -> common.Response:
    """Decode response"""
    name, data = res

    if name == 'status':
        return common.StatusResponse(logical=data['vmdLogicalStatus'],
                                     physical=data['vmdPhysicalStatus'])

    if name == 'getNameList':
        return common.GetNameListResponse(
            identifiers=data['listOfIdentifier'],
            more_follows=data.get('moreFollows', True))

    if name == 'identify':
        return common.IdentifyResponse(
            vendor=data['vendorName'],
            model=data['modelName'],
            revision=data['revision'],
            syntaxes=data.get('listOfAbstractSyntaxes'))

    if name == 'getVariableAccessAttributes':
        return common.GetVariableAccessAttributesResponse(
            mms_deletable=data['mmsDeletable'],
            type_description=_decode_type_description(data['typeDescription']))

    if name == 'getNamedVariableListAttributes':
        specification = [
            _decode_variable_specification(i['variableSpecification'])
            for i in data['listOfVariable']]

        return common.GetNamedVariableListAttributesResponse(
            mms_deletable=data['mmsDeletable'],
            specification=specification)

    if name == 'read':
        results = [
            (common.DataAccessError(i[1]) if i[0] == 'failure' else
             _decode_data(i[1]))
            for i in data['listOfAccessResult']]

        return common.ReadResponse(results)

    if name == 'write':
        results = [
            (None if i[0] == 'success' else common.DataAccessError(i[1]))
            for i in data]

        return common.WriteResponse(results)

    if name == 'defineNamedVariableList':
        return common.DefineNamedVariableListResponse()

    if name == 'deleteNamedVariableList':
        return common.DeleteNamedVariableListResponse(
            matched=data['numberMatched'],
            deleted=data['numberDeleted'])

    raise ValueError('unsupported name')


def encode_error(error: common.Error) -> asn1.Value:
    """Encode error"""
    if isinstance(error, common.VmdStateError):
        error_class = ('vmd-state', error.value)

    elif isinstance(error, common.ApplicationReferenceError):
        error_class = ('application-reference', error.value)

    elif isinstance(error, common.DefinitionError):
        error_class = ('definition', error.value)

    elif isinstance(error, common.ResourceError):
        error_class = ('resource', error.value)

    elif isinstance(error, common.ServiceError):
        error_class = ('service', error.value)

    elif isinstance(error, common.ServicePreemptError):
        error_class = ('service-preempt', error.value)

    elif isinstance(error, common.TimeResolutionError):
        error_class = ('time-resolution', error.value)

    elif isinstance(error, common.AccessError):
        error_class = ('access', error.value)

    elif isinstance(error, common.InitiateError):
        error_class = ('initiate', error.value)

    elif isinstance(error, common.ConcludeError):
        error_class = ('conclude', error.value)

    elif isinstance(error, common.CancelError):
        error_class = ('cancel', error.value)

    elif isinstance(error, common.FileError):
        error_class = ('file', error.value)

    elif isinstance(error, common.OtherError):
        error_class = ('others', error.value)

    else:
        raise TypeError('unsupported error type')

    return {'errorClass': error_class}


def decode_error(error: asn1.Value) -> common.Error:
    """Decode error"""
    name, value = error['errorClass']

    if name == 'vmd-state':
        return common.VmdStateError(value)

    if name == 'application-reference':
        return common.ApplicationReferenceError(value)

    if name == 'definition':
        return common.DefinitionError(value)

    if name == 'resource':
        return common.ResourceError(value)

    if name == 'service':
        return common.ServiceError(value)

    if name == 'service-preempt':
        return common.ServicePreemptError(value)

    if name == 'time-resolution':
        return common.TimeResolutionError(value)

    if name == 'access':
        return common.AccessError(value)

    if name == 'initiate':
        return common.InitiateError(value)

    if name == 'conclude':
        return common.ConcludeError(value)

    if name == 'cancel':
        return common.CancelError(value)

    if name == 'file':
        return common.FileError(value)

    if name == 'others':
        return common.OtherError(value)

    raise ValueError('unsupported name')


def encode_unconfirmed(unconfirmed: common.Unconfirmed) -> asn1.Value:
    """Encode unconfirmed"""
    if isinstance(unconfirmed, common.EventNotificationUnconfirmed):
        if unconfirmed.time is None:
            transition_time = 'undefined', None

        elif isinstance(unconfirmed.time, int):
            transition_time = 'timeSequenceIdentifier', unconfirmed.time

        else:
            transition_time = 'timeOfDay', unconfirmed.time

        return 'eventNotification', {
            'eventEnrollmentName': _encode_object_name(unconfirmed.enrollment),
            'eventConditionName': _encode_object_name(unconfirmed.condition),
            'severity': unconfirmed.severity,
            'transitionTime': transition_time}

    if isinstance(unconfirmed, common.InformationReportUnconfirmed):
        if isinstance(unconfirmed.specification, common.ObjectName):
            specification = ('variableListName',
                             _encode_object_name(unconfirmed.specification))

        else:
            specification = 'listOfVariable', [
                {'variableSpecification': _encode_variable_specification(i)}
                for i in unconfirmed.specification]

        data = [(('failure', i.value)
                 if isinstance(i, common.DataAccessError)
                 else ('success', _encode_data(i)))
                for i in unconfirmed.data]

        return 'informationReport', {
            'variableAccessSpecification': specification,
            'listOfAccessResult': data}

    if isinstance(unconfirmed, common.UnsolicitedStatusUnconfirmed):
        return 'unsolicitedStatus', {
            'vmdLogicalStatus': unconfirmed.logical,
            'vmdPhysicalStatus': unconfirmed.physical}

    raise TypeError('unsupported unconfirmed type')


def decode_unconfirmed(unconfirmed: asn1.Value) -> common.Unconfirmed:
    """Decode unconfirmed"""
    name, data = unconfirmed

    if name == 'eventNotification':
        return common.EventNotificationUnconfirmed(
            enrollment=_decode_object_name(data['eventEnrollmentName']),
            condition=_decode_object_name(data['eventConditionName']),
            severity=data['severity'],
            time=data['transitionTime'][1])

    if name == 'informationReport':
        subname, subdata = data['variableAccessSpecification']

        if subname == 'variableListName':
            specification = _decode_object_name(subdata)

        elif subname == 'listOfVariable':
            specification = [
                _decode_variable_specification(i['variableSpecification'])
                for i in subdata]

        else:
            raise ValueError('unsupported subname')

        data = [(common.DataAccessError(v) if k == 'failure'
                 else _decode_data(v))
                for k, v in data['listOfAccessResult']]

        return common.InformationReportUnconfirmed(specification=specification,
                                                   data=data)

    if name == 'unsolicitedStatus':
        return common.UnsolicitedStatusUnconfirmed(
            logical=data['vmdLogicalStatus'],
            physical=data['vmdPhysicalStatus'])

    raise ValueError('unsupported name')


def _encode_data(data):
    if isinstance(data, common.ArrayData):
        return 'array', [_encode_data(i) for i in data.elements]

    if isinstance(data, common.BcdData):
        return 'bcd', data.value

    if isinstance(data, common.BinaryTimeData):
        epoch = datetime.datetime(1984, 1, 1, tzinfo=datetime.timezone.utc)
        delta = data.value - epoch
        binary_time = [0xFF & (delta.seconds >> 24),
                       0xFF & (delta.seconds >> 16),
                       0xFF & (delta.seconds >> 8),
                       0xFF & delta.seconds,
                       0xFF & (delta.days >> 8),
                       0xFF & delta.days]
        return 'binary-time', bytes(binary_time)

    if isinstance(data, common.BitStringData):
        return 'bit-string', list(data.value)

    if isinstance(data, common.BooleanData):
        return 'boolean', data.value

    if isinstance(data, common.BooleanArrayData):
        return 'booleanArray', list(data.value)

    if isinstance(data, common.FloatingPointData):
        floating_point = b'\x08' + struct.pack(">f", data.value)
        return 'floating-point', floating_point

    if isinstance(data, common.GeneralizedTimeData):
        return 'generalized-time', data.value

    if isinstance(data, common.IntegerData):
        return 'integer', data.value

    if isinstance(data, common.MmsStringData):
        return 'mMSString', data.value

    if isinstance(data, common.ObjIdData):
        return 'objId', data.value

    if isinstance(data, common.OctetStringData):
        return 'octet-string', data.value

    if isinstance(data, common.StructureData):
        return 'structure', [_encode_data(i) for i in data.elements]

    if isinstance(data, common.UnsignedData):
        return 'unsigned', data.value

    if isinstance(data, common.UtcTimeData):
        if data.accuracy is not None and not (0 <= data.accuracy <= 24):
            raise ValueError('invalid UtcTime accuracy')

        ts = data.value.timestamp()
        decimal = ts - int(ts)
        fraction = bytearray([0, 0, 0])
        for i in range(24):
            if decimal >= 2 ** -(i + 1):
                decimal -= 2 ** -(i + 1)
                fraction[i // 8] |= 1 << (7 - (i % 8))
        quality = ((0x80 if data.leap_second else 0) |
                   (0x40 if data.clock_failure else 0) |
                   (0x20 if data.not_synchronized else 0) |
                   (0x1F if data.accuracy is None else data.accuracy))
        utc_time = bytes([*struct.pack(">I", int(ts)),
                          *fraction,
                          quality])

        return 'utc-time', utc_time

    if isinstance(data, common.VisibleStringData):
        return 'visible-string', data.value

    raise TypeError('unsupported data type')


def _decode_data(data):
    name, data = data

    if name == 'array':
        return common.ArrayData([_decode_data(i) for i in data])

    if name == 'bcd':
        return common.BcdData(data)

    if name == 'binary-time':
        delta = datetime.timedelta(
            days=(data[4] << 8) | data[5],
            seconds=((data[0] << 24) |
                     (data[1] << 16) |
                     (data[2] << 8) |
                     data[3]))
        epoch = datetime.datetime(1984, 1, 1, tzinfo=datetime.timezone.utc)
        return common.BinaryTimeData(epoch + delta)

    if name == 'bit-string':
        return common.BitStringData(data)

    if name == 'boolean':
        return common.BooleanData(data)

    if name == 'booleanArray':
        return common.BooleanArrayData(data)

    if name == 'floating-point':
        floating_point = struct.unpack(">f", data[1:])[0]
        return common.FloatingPointData(floating_point)

    if name == 'generalized-time':
        return common.GeneralizedTimeData(data)

    if name == 'integer':
        return common.IntegerData(data)

    if name == 'mMSString':
        return common.MmsStringData(data)

    if name == 'objId':
        return common.ObjIdData(data)

    if name == 'octet-string':
        return common.OctetStringData(data)

    if name == 'structure':
        return common.StructureData([_decode_data(i) for i in data])

    if name == 'unsigned':
        return common.UnsignedData(data)

    if name == 'utc-time':
        ts = struct.unpack(">I", data[:4])[0]
        for i in range(24):
            if data[4 + i // 8] & (1 << (7 - (i % 8))):
                ts += 2 ** -(i + 1)
        t = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
        leap_second = bool(0x80 & data[7])
        clock_failure = bool(0x40 & data[7])
        not_synchronized = bool(0x20 & data[7])
        accuracy = 0x1F & data[7]
        if accuracy > 24:
            accuracy = None
        return common.UtcTimeData(value=t,
                                  leap_second=leap_second,
                                  clock_failure=clock_failure,
                                  not_synchronized=not_synchronized,
                                  accuracy=accuracy)

    if name == 'visible-string':
        return common.VisibleStringData(data)

    raise ValueError('unsupported name')


def _encode_type_description(t):
    if isinstance(t, common.ArrayTypeDescription):
        if isinstance(t.element_type, common.TypeDescription):
            element_type = ('typeDescription',
                            _encode_type_description(t.element_type))

        elif isinstance(t.element_type, common.ObjectName):
            element_type = ('typeName',
                            _encode_object_name(t.element_type))

        else:
            raise TypeError('unsupported element type')

        return 'array', {
            'numberOfElements': t.number_of_elements,
            'elementType': element_type}

    if isinstance(t, common.BcdTypeDescription):
        return 'bcd', t.xyz

    if isinstance(t, common.BinaryTimeTypeDescription):
        return 'binary-time', t.xyz

    if isinstance(t, common.BitStringTypeDescription):
        return 'bit-string', t.xyz

    if isinstance(t, common.BooleanTypeDescription):
        return 'boolean', None

    if isinstance(t, common.FloatingPointTypeDescription):
        return 'floating-point', {
            'format-width': t.format_width,
            'exponent-width': t.exponent_width}

    if isinstance(t, common.GeneralizedTimeTypeDescription):
        return 'generalized-time', None

    if isinstance(t, common.IntegerTypeDescription):
        return 'integer', t.xyz

    if isinstance(t, common.MmsStringTypeDescription):
        return 'mMSString', t.xyz

    if isinstance(t, common.ObjIdTypeDescription):
        return 'objId', None

    if isinstance(t, common.OctetStringTypeDescription):
        return 'octet-string', t.xyz

    if isinstance(t, common.StructureTypeDescription):
        components = []
        for k, v in t.components:
            if isinstance(v, common.TypeDescription):
                component_type = 'typeDescription', _encode_type_description(v)

            elif isinstance(v, common.ObjectName):
                component_type = 'typeName', _encode_object_name(v)

            else:
                raise TypeError('unsupported value type')

            component = {'componentType': component_type}
            if k is not None:
                component['componentName'] = k

            components.append(component)

        return 'structure', {'components': components}

    if isinstance(t, common.UnsignedTypeDescription):
        return 'unsigned', t.xyz

    if isinstance(t, common.UtcTimeTypeDescription):
        return 'utc-time', None

    if isinstance(t, common.VisibleStringTypeDescription):
        return 'visible-string', t.xyz

    raise TypeError('unsupported type description')


def _decode_type_description(t):
    name, data = t

    if name == 'array':
        subname, subdata = data['elementType']

        if subname == 'typeDescription':
            element_type = _decode_type_description(subdata)

        elif subname == 'typeName':
            element_type = _decode_object_name(subdata)

        else:
            raise ValueError('unsupported subname')

        return common.ArrayTypeDescription(
            number_of_elements=data['numberOfElements'],
            element_type=element_type)

    if name == 'bcd':
        return common.BcdTypeDescription(data)

    if name == 'binary-time':
        return common.BinaryTimeTypeDescription(data)

    if name == 'bit-string':
        return common.BitStringTypeDescription(data)

    if name == 'boolean':
        return common.BooleanTypeDescription()

    if name == 'floating-point':
        return common.FloatingPointTypeDescription(
            format_width=data['format-width'],
            exponent_width=data['exponent-width'])

    if name == 'generalized-time':
        return common.GeneralizedTimeTypeDescription()

    if name == 'integer':
        return common.IntegerTypeDescription(data)

    if name == 'mMSString':
        return common.MmsStringTypeDescription(data)

    if name == 'objId':
        return common.ObjIdTypeDescription()

    if name == 'octet-string':
        return common.OctetStringTypeDescription(data)

    if name == 'structure':
        components = []
        for i in data['components']:
            subname, subdata = i['componentType']

            if subname == 'typeDescription':
                component_type = _decode_type_description(subdata)

            elif subname == 'typeName':
                component_type = _decode_object_name(subdata)

            else:
                raise ValueError('unsupported subname')

            component = i.get('componentName'), component_type
            components.append(component)

        return common.StructureTypeDescription(components)

    if name == 'unsigned':
        return common.UnsignedTypeDescription(data)

    if name == 'utc-time':
        return common.UtcTimeTypeDescription()

    if name == 'visible-string':
        return common.VisibleStringTypeDescription(data)

    raise ValueError('unsupported name')


def _encode_object_name(object_name):
    if isinstance(object_name, common.AaSpecificObjectName):
        return 'aa-specific', object_name.identifier

    if isinstance(object_name, common.DomainSpecificObjectName):
        return 'domain-specific', {
            'domainID': object_name.domain_id,
            'itemID': object_name.item_id}

    if isinstance(object_name, common.VmdSpecificObjectName):
        return 'vmd-specific', object_name.identifier

    raise TypeError('unsupported object name type')


def _decode_object_name(object_name):
    name, data = object_name

    if name == 'aa-specific':
        return common.AaSpecificObjectName(data)

    if name == 'domain-specific':
        return common.DomainSpecificObjectName(
            domain_id=data['domainID'],
            item_id=data['itemID'])

    if name == 'vmd-specific':
        return common.VmdSpecificObjectName(data)

    raise ValueError('unsupported name')


def _encode_object_scope(object_scope):
    if isinstance(object_scope, common.AaSpecificObjectScope):
        return 'aaSpecific', None

    if isinstance(object_scope, common.DomainSpecificObjectScope):
        return 'domainSpecific', object_scope.identifier

    if isinstance(object_scope, common.VmdSpecificObjectScope):
        return 'vmdSpecific', None

    raise TypeError('unsupported object scope type')


def _decode_object_scope(object_scope):
    name, data = object_scope

    if name == 'aaSpecific':
        return common.AaSpecificObjectScope()

    if name == 'domainSpecific':
        return common.DomainSpecificObjectScope(data)

    if name == 'vmdSpecific':
        return common.VmdSpecificObjectScope()

    raise ValueError('unsupported name')


def _encode_address(address):
    if isinstance(address, int):
        return 'numericAddress', address

    if isinstance(address, str):
        return 'symbolicAddress', address

    return 'unconstrainedAddress', address


def _decode_address(address):
    _, data = address
    return data


def _encode_variable_specification(var_spec):
    if isinstance(var_spec, common.AddressVariableSpecification):
        return 'address', _encode_address(var_spec.address)

    if isinstance(var_spec, common.InvalidatedVariableSpecification):
        return 'invalidated', None

    if isinstance(var_spec, common.NameVariableSpecification):
        return 'name', _encode_object_name(var_spec.name)

    if isinstance(var_spec,
                  common.ScatteredAccessDescriptionVariableSpecification):
        return 'scatteredAccessDescription', [
            {'variableSpecification': _encode_variable_specification(i)}
            for i in var_spec.specifications]

    if isinstance(var_spec, common.VariableDescriptionVariableSpecification):
        if isinstance(var_spec.type_specification, common.TypeDescription):
            type_specification = (
                'typeDescription',
                _encode_type_description(var_spec.type_specification))

        elif isinstance(var_spec.type_specification, common.ObjectName):
            type_specification = (
                'typeName',
                _encode_object_name(var_spec.type_specification))

        else:
            raise TypeError('unsupported type specification type')

        return 'variableDescription', {
            'address': _encode_address(var_spec.address),
            'typeSpecification': type_specification}

    raise TypeError('unsupported variable specification type')


def _decode_variable_specification(var_spec):
    name, data = var_spec

    if name == 'address':
        return common.AddressVariableSpecification(_decode_address(data))

    if name == 'invalidated':
        return common.InvalidatedVariableSpecification()

    if name == 'name':
        return common.NameVariableSpecification(_decode_object_name(data))

    if name == 'scatteredAccessDescription':
        return common.ScatteredAccessDescriptionVariableSpecification([
            _decode_variable_specification(i['variableSpecification'])
            for i in data])

    if name == 'variableDescription':
        subname, subdata = data['typeSpecification']

        if subname == 'typeDescription':
            type_specification = _decode_type_description(subdata)

        elif subname == 'typeName':
            type_specification = _decode_object_name(subdata)

        else:
            raise ValueError('unsupported subname')

        return common.VariableDescriptionVariableSpecification(
            address=_decode_address(data['address']),
            type_specification=type_specification)

    raise ValueError('unsupported name')
