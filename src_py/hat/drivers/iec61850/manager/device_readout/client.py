from collections.abc import Collection
import collections

from hat import aio

from hat.drivers import mms
from hat.drivers.iec61850 import encoder
from hat.drivers.iec61850.manager.device_readout import common


class Client(aio.Resource):

    def __init__(self, conn: mms.Connection):
        self._conn = conn

    @property
    def async_group(self) -> aio.Group:
        return self._conn.async_group

    async def get_logical_devices(self) -> Collection[str]:
        return await self._get_name_list(
            object_class=mms.ObjectClass.DOMAIN,
            object_scope=mms.VmdSpecificObjectScope())

    async def get_root_data_refs(self,
                                 logical_device: str,
                                 ) -> Collection[common.RootDataRef]:
        identifiers = await self._get_name_list(
            object_class=mms.ObjectClass.NAMED_VARIABLE,
            object_scope=mms.DomainSpecificObjectScope(logical_device))

        refs = collections.deque()
        for identifier in identifiers:
            segments = identifier.split('$')
            if len(segments) != 3:
                continue

            logical_node, fc, name = segments
            ref = common.RootDataRef(logical_device=logical_device,
                                     logical_node=logical_node,
                                     fc=fc,
                                     name=name)
            refs.append(ref)

        return refs

    async def get_value_type(self,
                             ref: common.DataRef
                             ) -> common.ValueType | None:
        req = mms.GetVariableAccessAttributesRequest(
            encoder.data_ref_to_object_name(ref))

        res = await self._conn.send_confirmed(req)

        if isinstance(res, mms.Error):
            raise Exception(f'received mms error {res}')

        if not isinstance(res, mms.GetVariableAccessAttributesResponse):
            raise Exception('unsupported response type')

        return _value_type_from_type_description(res.type_description)

    async def get_dataset_refs(self,
                               logical_device: str
                               ) -> Collection[common.PersistedDatasetRef]:
        identifiers = await self._get_name_list(
            object_class=mms.ObjectClass.NAMED_VARIABLE_LIST,
            object_scope=mms.DomainSpecificObjectScope(logical_device))

        refs = collections.deque()
        for identifier in identifiers:
            logical_node, name = identifier.split('$')
            ref = common.PersistedDatasetRef(logical_device=logical_device,
                                             logical_node=logical_node,
                                             name=name)
            refs.append(ref)

        return refs

    async def get_dataset_data_refs(self,
                                    ref: common.DatasetRef
                                    ) -> Collection[common.DataRef]:
        req = mms.GetNamedVariableListAttributesRequest(
            encoder.dataset_ref_to_object_name(ref))

        res = await self._conn.send_confirmed(req)

        if isinstance(res, mms.Error):
            raise Exception(f'received mms error {res}')

        if not isinstance(res, mms.GetNamedVariableListAttributesResponse):
            raise Exception('unsupported response type')

        refs = collections.deque()

        for i in res.specification:
            if not isinstance(i, mms.NameVariableSpecification):
                raise Exception('unsupported specification type')

            refs.append(encoder.data_ref_from_object_name(i.name))

        return refs

    async def get_control_model(self,
                                ref: common.CommandRef
                                ) -> common.ControlModel:
        req = mms.ReadRequest([
            mms.NameVariableSpecification(
                encoder.data_ref_to_object_name(
                    common.DataRef(logical_device=ref.logical_device,
                                   logical_node=ref.logical_node,
                                   fc='CF',
                                   names=(ref.name, 'ctlModel'))))])

        res = await self._conn.send_confirmed(req)

        if isinstance(res, mms.Error):
            raise Exception(f'received mms error {res}')

        if not isinstance(res, mms.ReadResponse):
            raise Exception('unsupported response type')

        if len(res.results) != 1:
            raise Exception('invalid results length')

        mms_data = next(iter(res.results))
        if isinstance(mms_data, mms.DataAccessError):
            raise Exception(f'received mms data access error {mms_data}')

        value = encoder.value_from_mms_data(mms_data,
                                            common.BasicValueType.INTEGER)

        return common.ControlModel(value)

    async def get_rcb_attr_values(self,
                                  ref: common.RcbRef
                                  ) -> dict[common.RcbAttrType,
                                            common.RcbAttrValue]:
        attr_types = [common.RcbAttrType.REPORT_ID,
                      common.RcbAttrType.DATASET,
                      common.RcbAttrType.CONF_REVISION,
                      common.RcbAttrType.OPTIONAL_FIELDS,
                      common.RcbAttrType.BUFFER_TIME,
                      common.RcbAttrType.TRIGGER_OPTIONS,
                      common.RcbAttrType.INTEGRITY_PERIOD]

        req = mms.ReadRequest([
            mms.NameVariableSpecification(
                encoder.data_ref_to_object_name(
                    common.DataRef(logical_device=ref.logical_device,
                                   logical_node=ref.logical_node,
                                   fc=ref.type.value,
                                   names=(ref.name, attr_type.value))))
            for attr_type in attr_types])

        res = await self._conn.send_confirmed(req)

        if isinstance(res, mms.Error):
            raise Exception(f'received mms error {res}')

        if not isinstance(res, mms.ReadResponse):
            raise Exception('unsupported response type')

        if len(res.results) != len(attr_types):
            raise Exception('invalid results length')

        results = {}

        for attr_type, mms_data in zip(attr_types, res.results):
            if isinstance(mms_data, mms.DataAccessError):
                raise Exception(f'received mms data access error {mms_data}')

            results[attr_type] = encoder.rcb_attr_value_from_mms_data(
                mms_data, attr_type)

        return results

    async def _get_name_list(self,
                             object_class: mms.ObjectClass,
                             object_scope: mms.ObjectScope
                             ) -> Collection[str]:
        identifiers = collections.deque()
        continue_after = None

        while True:
            req = mms.GetNameListRequest(
                object_class=object_class,
                object_scope=object_scope,
                continue_after=continue_after)

            res = await self._conn.send_confirmed(req)

            if isinstance(res, mms.Error):
                raise Exception(f'received mms error {res}')

            if not isinstance(res, mms.GetNameListResponse):
                raise Exception('unsupported response type')

            identifiers.extend(res.identifiers)

            if not res.more_follows:
                break

            if not res.identifiers:
                raise Exception('invalid more follows value')

            continue_after = identifiers[-1]

        return identifiers


def _value_type_from_type_description(type_description: mms.TypeDescription
                                      ) -> common.ValueType | None:
    if isinstance(type_description, mms.ArrayTypeDescription):
        if isinstance(type_description.element_type, mms.ObjectName):
            return

        element_type = _value_type_from_type_description(
            type_description.element_type)
        if element_type is None:
            return

        return common.ArrayValueType(
            type=element_type,
            length=type_description.number_of_elements)

    if isinstance(type_description, mms.BcdTypeDescription):
        return

    if isinstance(type_description, mms.BinaryTimeTypeDescription):
        return

    if isinstance(type_description, mms.BitStringTypeDescription):
        return common.BasicValueType.BIT_STRING

    if isinstance(type_description, mms.BooleanTypeDescription):
        return common.BasicValueType.BOOLEAN

    if isinstance(type_description, mms.FloatingPointTypeDescription):
        return common.BasicValueType.FLOAT

    if isinstance(type_description, mms.GeneralizedTimeTypeDescription):
        return

    if isinstance(type_description, mms.IntegerTypeDescription):
        return common.BasicValueType.INTEGER

    if isinstance(type_description, mms.MmsStringTypeDescription):
        return common.BasicValueType.MMS_STRING

    if isinstance(type_description, mms.ObjIdTypeDescription):
        return

    if isinstance(type_description, mms.OctetStringTypeDescription):
        return common.BasicValueType.OCTET_STRING

    if isinstance(type_description, mms.StructureTypeDescription):
        elements = collections.deque()

        for i_name, i_type in type_description.components:
            if i_name is None or isinstance(i_type, mms.ObjectName):
                return

            element_type = _value_type_from_type_description(i_type)
            if element_type is None:
                return

            elements.append((i_name, element_type))

        return common.StructValueType(elements)

    if isinstance(type_description, mms.UnsignedTypeDescription):
        return common.BasicValueType.UNSIGNED

    if isinstance(type_description, mms.UtcTimeTypeDescription):
        return common.AcsiValueType.TIMESTAMP

    if isinstance(type_description, mms.VisibleStringTypeDescription):
        return common.BasicValueType.VISIBLE_STRING

    raise TypeError('unsupported type description')
