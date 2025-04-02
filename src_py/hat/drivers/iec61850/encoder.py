from collections.abc import Collection
import collections
import typing

from hat import util

from hat.drivers import mms
from hat.drivers.iec61850 import common


class LastApplError(typing.NamedTuple):
    name: str
    error: common.TestError
    origin: common.Origin
    control_number: int
    additional_cause: common.AdditionalCause


class DataDef(typing.NamedTuple):
    ref: common.DataRef
    value_type: common.ValueType


def dataset_ref_to_object_name(ref: common.DatasetRef) -> mms.ObjectName:
    if isinstance(ref, common.PersistedDatasetRef):
        return mms.DomainSpecificObjectName(
            domain_id=ref.logical_device,
            item_id=f'{ref.logical_node}${ref.name}')

    if isinstance(ref, common.NonPersistedDatasetRef):
        return mms.AaSpecificObjectName(ref.name)

    raise TypeError('unsupported ref type')


def dataset_ref_from_object_name(object_name: mms.ObjectName
                                 ) -> common.DatasetRef:
    if isinstance(object_name, mms.DomainSpecificObjectName):
        logical_node, name = object_name.item_id.split('$')
        return common.PersistedDatasetRef(
            logical_device=object_name.domain_id,
            logical_node=logical_node,
            name=name)

    if isinstance(object_name, mms.AaSpecificObjectName):
        return common.NonPersistedDatasetRef(object_name.identifier)

    raise TypeError('unsupported object name type')


def dataset_ref_from_str(ref_str: str) -> common.DatasetRef:
    if ref_str.startswith('@'):
        return common.NonPersistedDatasetRef(ref_str[1:])

    logical_device, rest = ref_str.split('/', 1)
    logical_node, name = rest.split('$')

    return common.PersistedDatasetRef(logical_device=logical_device,
                                      logical_node=logical_node,
                                      name=name)


def dataset_ref_to_str(ref: common.DatasetRef) -> str:
    if isinstance(ref, common.PersistedDatasetRef):
        return f'{ref.logical_device}/{ref.logical_node}${ref.name}'

    if isinstance(ref, common.NonPersistedDatasetRef):
        return f'@{ref.name}'

    raise TypeError('unsupported ref type')


def data_ref_to_object_name(ref: common.DataRef) -> mms.ObjectName:
    item_id = f'{ref.logical_node}${ref.fc}' + ''.join(
        (f'({i})' if isinstance(i, int) else f'${i}')
        for i in ref.names)

    return mms.DomainSpecificObjectName(
        domain_id=ref.logical_device,
        item_id=item_id)


def data_ref_from_object_name(object_name: mms.ObjectName) -> common.DataRef:
    if not isinstance(object_name, mms.DomainSpecificObjectName):
        raise TypeError('unsupported object name type')

    logical_node, fc, *rest = object_name.item_id.split('$')

    names = collections.deque()
    for name in rest:
        indexes = collections.deque()

        while name.endswith(')'):
            pos = name.rfind('(')
            if pos < 0:
                raise Exception('invalid array index syntax')

            name, index = name[:pos], int(name[pos+1:-1])
            indexes.appendleft(index)

        names.append(name)
        names.extend(indexes)

    return common.DataRef(logical_device=object_name.domain_id,
                          logical_node=logical_node,
                          fc=fc,
                          names=tuple(names))


def data_ref_to_str(ref: common.DataRef) -> str:
    object_name = data_ref_to_object_name(ref)
    return f'{object_name.domain_id}/{object_name.item_id}'


def data_ref_from_str(ref_str: str) -> common.DataRef:
    object_name = mms.DomainSpecificObjectName(*ref_str.split('/', 1))
    return data_ref_from_object_name(object_name)


def value_from_mms_data(mms_data: mms.Data,
                        value_type: common.ValueType
                        ) -> common.Value:
    if value_type == common.BasicValueType.BOOLEAN:
        if not isinstance(mms_data, mms.BooleanData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.INTEGER:
        if not isinstance(mms_data, mms.IntegerData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.UNSIGNED:
        if not isinstance(mms_data, mms.UnsignedData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.FLOAT:
        if not isinstance(mms_data, mms.FloatingPointData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.BIT_STRING:
        if not isinstance(mms_data, mms.BitStringData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.OCTET_STRING:
        if not isinstance(mms_data, mms.OctetStringData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.VISIBLE_STRING:
        if not isinstance(mms_data, mms.VisibleStringData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.BasicValueType.MMS_STRING:
        if not isinstance(mms_data, mms.MmsStringData):
            raise Exception('unexpected data type')

        return mms_data.value

    if value_type == common.AcsiValueType.QUALITY:
        if not isinstance(mms_data, mms.BitStringData):
            raise Exception('unexpected data type')

        if len(mms_data.value) != 13:
            raise Exception('invalid bit string length')

        return common.Quality(
            validity=common.QualityValidity((mms_data.value[0] << 1) |
                                            mms_data.value[1]),
            details={common.QualityDetail(index)
                     for index, i in enumerate(mms_data.value)
                     if index >= 2 and index <= 9 and i},
            source=common.QualitySource(int(mms_data.value[10])),
            test=mms_data.value[11],
            operator_blocked=mms_data.value[12])

    if value_type == common.AcsiValueType.TIMESTAMP:
        if not isinstance(mms_data, mms.UtcTimeData):
            raise Exception('unexpected data type')

        return common.Timestamp(**mms_data._asdict())

    if value_type == common.AcsiValueType.DOUBLE_POINT:
        if not isinstance(mms_data, mms.BitStringData):
            raise Exception('unexpected data type')

        if len(mms_data.value) != 2:
            raise Exception('invalid bit string length')

        return common.DoublePoint((mms_data.value[0] << 1) |
                                  mms_data.value[1])

    if value_type == common.AcsiValueType.DIRECTION:
        if not isinstance(mms_data, mms.IntegerData):
            raise Exception('unexpected data type')

        return common.Direction(mms_data.value)

    if value_type == common.AcsiValueType.SEVERITY:
        if not isinstance(mms_data, mms.IntegerData):
            raise Exception('unexpected data type')

        return common.Severity(mms_data.value)

    if value_type == common.AcsiValueType.ANALOGUE:
        if not isinstance(mms_data, mms.StructureData):
            raise Exception('unexpected data type')

        if len(mms_data.elements) < 1 or len(mms_data.elements) > 2:
            raise Exception('invalid structure size')

        value = common.Analogue()

        for i in mms_data.elements:
            if isinstance(i, mms.IntegerData):
                value = value._replace(i=i.value)

            elif isinstance(i, mms.FloatingPointData):
                value = value._replace(f=i.value)

            else:
                raise Exception('unexpected data type')

        return value

    if value_type == common.AcsiValueType.VECTOR:
        if not isinstance(mms_data, mms.StructureData):
            raise Exception('unexpected data type')

        if len(mms_data.elements) < 1 or len(mms_data.elements) > 2:
            raise Exception('invalid structure size')

        elements = list(mms_data.elements)

        return common.Vector(
            magnitude=value_from_mms_data(
                elements[0], common.AcsiValueType.ANALOGUE),
            angle=(
                value_from_mms_data(
                    elements[1], common.AcsiValueType.ANALOGUE)
                if len(elements) > 1 else None))

    if value_type == common.AcsiValueType.STEP_POSITION:
        if not isinstance(mms_data, mms.StructureData):
            raise Exception('unexpected data type')

        if len(mms_data.elements) < 1 or len(mms_data.elements) > 2:
            raise Exception('invalid structure size')

        elements = list(mms_data.elements)

        return common.StepPosition(
            value=value_from_mms_data(
                elements[0], common.BasicValueType.INTEGER),
            transient=(
                value_from_mms_data(
                    elements[1], common.BasicValueType.BOOLEAN)
                if len(elements) > 1 else None))

    if value_type == common.AcsiValueType.BINARY_CONTROL:
        if not isinstance(mms_data, mms.BitStringData):
            raise Exception('unexpected data type')

        if len(mms_data.value) != 2:
            raise Exception('invalid bit string length')

        return common.BinaryControl((mms_data.value[0] << 1) |
                                    mms_data.value[1])

    if isinstance(value_type, common.ArrayValueType):
        if not isinstance(mms_data, mms.ArrayData):
            raise Exception('unexpected data type')

        return [value_from_mms_data(i, value_type.type)
                for i in mms_data.elements]

    if isinstance(value_type, common.StructValueType):
        if not isinstance(mms_data, mms.StructureData):
            raise Exception('unexpected data type')

        if len(mms_data.elements) != len(value_type.elements):
            raise Exception('invalid structure size')

        return {k: value_from_mms_data(i, t)
                for i, (k, t) in zip(mms_data.elements, value_type.elements)}

    raise TypeError('unsupported value type')


def value_to_mms_data(value: common.Value,
                      value_type: common.ValueType
                      ) -> mms.Data:
    if value_type == common.BasicValueType.BOOLEAN:
        if not isinstance(value, bool):
            raise Exception('unexpected value type')

        return mms.BooleanData(value)

    if value_type == common.BasicValueType.INTEGER:
        if not isinstance(value, int):
            raise Exception('unexpected value type')

        return mms.IntegerData(value)

    if value_type == common.BasicValueType.UNSIGNED:
        if not isinstance(value, int):
            raise Exception('unexpected value type')

        return mms.UnsignedData(value)

    if value_type == common.BasicValueType.FLOAT:
        if not isinstance(value, (float, int)):
            raise Exception('unexpected value type')

        return mms.FloatingPointData(value)

    if value_type == common.BasicValueType.BIT_STRING:
        if any(not isinstance(i, bool) for i in value):
            raise Exception('unexpected value type')

        return mms.BitStringData(value)

    if value_type == common.BasicValueType.OCTET_STRING:
        if not isinstance(value, util.Bytes):
            raise Exception('unexpected value type')

        return mms.OctetStringData(value)

    if value_type == common.BasicValueType.VISIBLE_STRING:
        if not isinstance(value, str):
            raise Exception('unexpected value type')

        return mms.VisibleStringData(value)

    if value_type == common.BasicValueType.MMS_STRING:
        if not isinstance(value, str):
            raise Exception('unexpected value type')

        return mms.MmsStringData(value)

    if value_type == common.AcsiValueType.QUALITY:
        if not isinstance(value, common.Quality):
            raise Exception('unexpected value type')

        return mms.BitStringData([bool(value.validity.value & 2),
                                  bool(value.validity.value & 1),
                                  *(common.QualityDetail(i) in value.details
                                    for i in range(2, 10)),
                                  bool(value.source.value),
                                  value.test,
                                  value.operator_blocked])

    if value_type == common.AcsiValueType.TIMESTAMP:
        if not isinstance(value, common.Timestamp):
            raise Exception('unexpected value type')

        return mms.UtcTimeData(**value._asdict())

    if value_type == common.AcsiValueType.DOUBLE_POINT:
        if not isinstance(value, common.DoublePoint):
            raise Exception('unexpected value type')

        return mms.BitStringData([bool(value.value & 2),
                                  bool(value.value & 1)])

    if value_type == common.AcsiValueType.DIRECTION:
        if not isinstance(value, common.Direction):
            raise Exception('unexpected value type')

        return mms.IntegerData(value.value)

    if value_type == common.AcsiValueType.SEVERITY:
        if not isinstance(value, common.Severity):
            raise Exception('unexpected value type')

        return mms.IntegerData(value.value)

    if value_type == common.AcsiValueType.ANALOGUE:
        if not isinstance(value, common.Analogue):
            raise Exception('unexpected value type')

        if value.i is None and value.f is None:
            raise Exception('invalid analogue value')

        mms_data = mms.StructureData([])

        if value.i is not None:
            mms_data.elements.append(
                value_to_mms_data(value.i, common.BasicValueType.INTEGER))

        if value.f is not None:
            mms_data.elements.append(
                value_to_mms_data(value.f, common.BasicValueType.FLOAT))

        return mms_data

    if value_type == common.AcsiValueType.VECTOR:
        if not isinstance(value, common.Vector):
            raise Exception('unexpected value type')

        mms_data = mms.StructureData([
            value_to_mms_data(value.magnitude, common.AcsiValueType.ANALOGUE)])

        if value.angle is not None:
            mms_data.elements.append(
                value_to_mms_data(value.angle, common.AcsiValueType.ANALOGUE))

        return mms_data

    if value_type == common.AcsiValueType.STEP_POSITION:
        if not isinstance(value, common.StepPosition):
            raise Exception('unexpected value type')

        mms_data = mms.StructureData([
            value_to_mms_data(value.value, common.BasicValueType.INTEGER)])

        if value.transient is not None:
            mms_data.elements.append(
                value_to_mms_data(value.transient,
                                  common.BasicValueType.BOOLEAN))

        return mms_data

    if value_type == common.AcsiValueType.BINARY_CONTROL:
        if not isinstance(value, common.BinaryControl):
            raise Exception('unexpected value type')

        return mms.BitStringData([bool(value.value & 2),
                                  bool(value.value & 1)])

    if isinstance(value_type, common.ArrayValueType):
        return mms.ArrayData([value_to_mms_data(i, value_type.type)
                              for i in value])

    if isinstance(value_type, common.StructValueType):
        return mms.StructureData([value_to_mms_data(value[k], t)
                                  for k, t in value_type.elements])

    raise TypeError('unsupported value type')


def rcb_attr_value_from_mms_data(mms_data: mms.Data,
                                 attr_type: common.RcbAttrType
                                 ) -> common.RcbAttrValue:
    if attr_type == common.RcbAttrType.REPORT_ID:
        return value_from_mms_data(
            mms_data, common.BasicValueType.VISIBLE_STRING)

    if attr_type == common.RcbAttrType.REPORT_ENABLE:
        return value_from_mms_data(
            mms_data, common.BasicValueType.BOOLEAN)

    if attr_type == common.RcbAttrType.DATASET:
        return dataset_ref_from_str(
            value_from_mms_data(
                mms_data, common.BasicValueType.VISIBLE_STRING))

    if attr_type == common.RcbAttrType.CONF_REVISION:
        return value_from_mms_data(
            mms_data, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.OPTIONAL_FIELDS:
        value = value_from_mms_data(
            mms_data, common.BasicValueType.BIT_STRING)
        if len(value) != 10:
            raise Exception('invalid optional fields size')

        return {common.OptionalField(index)
                for index, i in enumerate(value)
                if (1 <= index <= 8) and i}

    if attr_type == common.RcbAttrType.BUFFER_TIME:
        return value_from_mms_data(
            mms_data, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.SEQUENCE_NUMBER:
        return value_from_mms_data(
            mms_data, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.TRIGGER_OPTIONS:
        value = value_from_mms_data(
            mms_data, common.BasicValueType.BIT_STRING)
        if len(value) != 6:
            raise Exception('invalid trigger options size')

        return {common.TriggerCondition(index)
                for index, i in enumerate(value)
                if index >= 1 and i}

    if attr_type == common.RcbAttrType.INTEGRITY_PERIOD:
        return value_from_mms_data(
            mms_data, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.GI:
        return value_from_mms_data(
            mms_data, common.BasicValueType.BOOLEAN)

    if attr_type == common.RcbAttrType.PURGE_BUFFER:
        return value_from_mms_data(
            mms_data, common.BasicValueType.BOOLEAN)

    if attr_type == common.RcbAttrType.ENTRY_ID:
        return value_from_mms_data(
            mms_data, common.BasicValueType.OCTET_STRING)

    if attr_type == common.RcbAttrType.TIME_OF_ENTRY:
        if not isinstance(mms_data, mms.BinaryTimeData):
            raise Exception('unexpected data type')

        return mms_data.value

    if attr_type == common.RcbAttrType.RESERVATION_TIME:
        return value_from_mms_data(
            mms_data, common.BasicValueType.INTEGER)

    if attr_type == common.RcbAttrType.RESERVE:
        return value_from_mms_data(
            mms_data, common.BasicValueType.BOOLEAN)

    raise ValueError('unsupported attribute type')


def rcb_attr_value_to_mms_data(attr_value: common.RcbAttrValue,
                               attr_type: common.RcbAttrType
                               ) -> mms.Data:
    if attr_type == common.RcbAttrType.REPORT_ID:
        return value_to_mms_data(
            attr_value, common.BasicValueType.VISIBLE_STRING)

    if attr_type == common.RcbAttrType.REPORT_ENABLE:
        return value_to_mms_data(
            attr_value, common.BasicValueType.BOOLEAN)

    if attr_type == common.RcbAttrType.DATASET:
        return value_to_mms_data(
            dataset_ref_to_str(attr_value),
            common.BasicValueType.VISIBLE_STRING)

    if attr_type == common.RcbAttrType.CONF_REVISION:
        return value_to_mms_data(
            attr_value, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.OPTIONAL_FIELDS:
        return value_to_mms_data(
            [False,
             *(common.OptionalField(i) in attr_value for i in range(1, 9)),
             False],
            common.BasicValueType.BIT_STRING)

    if attr_type == common.RcbAttrType.BUFFER_TIME:
        return value_to_mms_data(
            attr_value, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.SEQUENCE_NUMBER:
        return value_to_mms_data(
            attr_value, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.TRIGGER_OPTIONS:
        return value_to_mms_data(
            [False,
             *(common.TriggerCondition(i) in attr_value for i in range(1, 6))],
            common.BasicValueType.BIT_STRING)

    if attr_type == common.RcbAttrType.INTEGRITY_PERIOD:
        return value_to_mms_data(
            attr_value, common.BasicValueType.UNSIGNED)

    if attr_type == common.RcbAttrType.GI:
        return value_to_mms_data(
            attr_value, common.BasicValueType.BOOLEAN)

    if attr_type == common.RcbAttrType.PURGE_BUFFER:
        return value_to_mms_data(
            attr_value, common.BasicValueType.BOOLEAN)

    if attr_type == common.RcbAttrType.ENTRY_ID:
        return value_to_mms_data(
            attr_value, common.BasicValueType.OCTET_STRING)

    if attr_type == common.RcbAttrType.TIME_OF_ENTRY:
        return mms.BinaryTimeData(attr_value)

    if attr_type == common.RcbAttrType.RESERVATION_TIME:
        return value_to_mms_data(
            attr_value, common.BasicValueType.INTEGER)

    if attr_type == common.RcbAttrType.RESERVE:
        return value_to_mms_data(
            attr_value, common.BasicValueType.BOOLEAN)

    raise ValueError('unsupported attribute type')


def command_to_mms_data(cmd: common.Command,
                        value_type: common.ValueType,
                        with_checks: bool
                        ) -> mms.Data:
    elements = collections.deque([value_to_mms_data(cmd.value, value_type)])

    if cmd.operate_time is not None:
        elements.append(value_to_mms_data(cmd.operate_time,
                                          common.AcsiValueType.TIMESTAMP))

    elements.extend([
        _origin_to_mms_data(cmd.origin),
        value_to_mms_data(cmd.control_number, common.BasicValueType.UNSIGNED),
        value_to_mms_data(cmd.t, common.AcsiValueType.TIMESTAMP),
        value_to_mms_data(cmd.test, common.BasicValueType.BOOLEAN)])

    if with_checks:
        elements.append(value_to_mms_data([common.Check(i) in cmd.checks
                                           for i in range(2)],
                                          common.BasicValueType.BIT_STRING))

    return mms.StructureData(elements)


def command_from_mms_data(mms_data: mms.Data,
                          value_type: common.ValueType,
                          with_checks: bool
                          ) -> common.Command:
    if not isinstance(mms_data, mms.StructureData):
        raise Exception('invalid data type')

    if with_checks:
        if len(mms_data.elements) == 7:
            with_operate_time = True

        elif len(mms_data.elements) == 6:
            with_operate_time = False

        else:
            raise Exception('invalid elements size')

    else:
        if len(mms_data.elements) == 6:
            with_operate_time = True

        elif len(mms_data.element) == 5:
            with_operate_time = False

        else:
            raise Exception('invalid elements size')

    elements = iter(mms_data.elements)

    value = value_from_mms_data(next(elements), value_type)

    if with_operate_time:
        operate_time = value_from_mms_data(next(elements),
                                           common.AcsiValueType.TIMESTAMP)

    else:
        operate_time = None

    origin = _origin_from_mms_data(next(elements))
    control_number = value_from_mms_data(next(elements),
                                         common.BasicValueType.UNSIGNED)
    t = value_from_mms_data(next(elements), common.AcsiValueType.TIMESTAMP)
    test = value_from_mms_data(next(elements), common.BasicValueType.BOOLEAN)

    if with_checks:
        checks_bits = value_from_mms_data(next(elements),
                                          common.BasicValueType.BIT_STRING)
        # TODO check checks_bits length
        checks = {common.Check(index)
                  for index, i in enumerate(checks_bits)
                  if i}

    else:
        checks = set()

    return common.Command(value=value,
                          operate_time=operate_time,
                          origin=origin,
                          control_number=control_number,
                          t=t,
                          test=test,
                          checks=checks)


def last_appl_error_from_mms_data(mms_data: mms.Data) -> LastApplError:
    if not isinstance(mms_data, mms.StructureData):
        raise Exception('invalid data type')

    if len(mms_data.elements) != 5:
        raise Exception('invalid elements size')

    elements = iter(mms_data.elements)

    name = value_from_mms_data(next(elements),
                               common.BasicValueType.VISIBLE_STRING)
    error = common.TestError(
        value_from_mms_data(next(elements), common.BasicValueType.INTEGER))
    origin = _origin_from_mms_data(next(elements))
    control_number = value_from_mms_data(next(elements),
                                         common.BasicValueType.UNSIGNED)
    additional_cause = common.AdditionalCause(
        value_from_mms_data(next(elements), common.BasicValueType.INTEGER))

    return LastApplError(name=name,
                         error=error,
                         origin=origin,
                         control_number=control_number,
                         additional_cause=additional_cause)


def report_from_mms_data(mms_data: Collection[mms.Data],
                         data_defs: Collection[DataDef]
                         ) -> common.Report:
    elements = iter(mms_data)

    report_id = value_from_mms_data(next(elements),
                                    common.BasicValueType.VISIBLE_STRING)

    optional_fields_bits = value_from_mms_data(
        next(elements), common.BasicValueType.BIT_STRING)
    if len(optional_fields_bits) != 10:
        raise Exception('invalid optional fields size')

    optional_fields = {common.OptionalField(index)
                       for index, i in enumerate(optional_fields_bits[:-1])
                       if i}
    segmentation = optional_fields_bits[-1]

    if common.OptionalField.SEQUENCE_NUMBER in optional_fields:
        sequence_number = value_from_mms_data(next(elements),
                                              common.BasicValueType.UNSIGNED)

    else:
        sequence_number = None

    if common.OptionalField.REPORT_TIME_STAMP in optional_fields:
        time_of_entry_data = next(elements)
        if not isinstance(time_of_entry_data, mms.BinaryTimeData):
            raise Exception('unexpected data type')

        time_of_entry = time_of_entry_data.value

    else:
        time_of_entry = None

    if common.OptionalField.DATA_SET_NAME in optional_fields:
        dataset_str = value_from_mms_data(next(elements),
                                          common.BasicValueType.VISIBLE_STRING)
        dataset = dataset_ref_from_str(dataset_str)

    else:
        dataset = None

    if common.OptionalField.BUFFER_OVERFLOW in optional_fields:
        buffer_overflow = value_from_mms_data(next(elements),
                                              common.BasicValueType.BOOLEAN)

    else:
        buffer_overflow = None

    if common.OptionalField.ENTRY_ID in optional_fields:
        entry_id = value_from_mms_data(next(elements),
                                       common.BasicValueType.OCTET_STRING)

    else:
        entry_id = None

    if common.OptionalField.CONF_REVISION in optional_fields:
        conf_revision = value_from_mms_data(next(elements),
                                            common.BasicValueType.UNSIGNED)

    else:
        conf_revision = None

    if segmentation:
        subsequence_number = value_from_mms_data(
            next(elements), common.BasicValueType.UNSIGNED)
        more_segments_follow = value_from_mms_data(
            next(elements), common.BasicValueType.BOOLEAN)

    else:
        subsequence_number = None
        more_segments_follow = None

    inclusion = value_from_mms_data(next(elements),
                                    common.BasicValueType.BIT_STRING)
    if len(inclusion) != len(data_defs):
        raise Exception('unexpected number of inclusion bits')

    if common.OptionalField.DATA_REFERENCE in optional_fields:
        for exists, data_def in zip(inclusion, data_defs):
            if not exists:
                continue

            data_ref_str = value_from_mms_data(
                next(elements), common.BasicValueType.VISIBLE_STRING)
            data_ref = data_ref_from_str(data_ref_str)

            if data_ref != data_def.ref:
                raise Exception('data reference mismatch')

    values = collections.deque()
    for exists, data_def in zip(inclusion, data_defs):
        if not exists:
            continue

        values.append(value_from_mms_data(next(elements), data_def.value_type))

    if common.OptionalField.REASON_FOR_INCLUSION in optional_fields:
        reasons = collections.deque()
        for exists in inclusion:
            if not exists:
                continue

            reason_bits = value_from_mms_data(
                next(elements), common.BasicValueType.BIT_STRING)
            if len(reason_bits) != 7:
                raise Exception('invalid reason bits size')

            reasons.append({common.ReasonCode(index)
                            for index, i in enumerate(reason_bits)
                            if i})

    else:
        reasons = None

    data = collections.deque()
    for exists, data_def in zip(inclusion, data_defs):
        if not exists:
            continue

        data.append(
            common.ReportData(
                ref=data_def.ref,
                value=values.popleft(),
                reasons=(reasons.popleft() if reasons is not None else None)))

    return common.Report(report_id=report_id,
                         sequence_number=sequence_number,
                         subsequence_number=subsequence_number,
                         more_segments_follow=more_segments_follow,
                         dataset=dataset,
                         buffer_overflow=buffer_overflow,
                         conf_revision=conf_revision,
                         entry_time=time_of_entry,
                         entry_id=entry_id,
                         data=data)


def _origin_to_mms_data(origin):
    return mms.StructureData([
        value_to_mms_data(origin.category.value,
                          common.BasicValueType.INTEGER),
        value_to_mms_data(origin.identification,
                          common.BasicValueType.OCTET_STRING)])


def _origin_from_mms_data(mms_data):
    if not isinstance(mms_data, mms.StructureData):
        raise Exception('invalid data type')

    if len(mms_data.elements) != 2:
        raise Exception('invalid elements size')

    elements = iter(mms_data.elements)

    category = common.OriginCategory(
        value_from_mms_data(next(elements), common.BasicValueType.INTEGER))
    identification = value_from_mms_data(next(elements),
                                         common.BasicValueType.OCTET_STRING)

    return common.Origin(category=category,
                         identification=identification)
