from collections.abc import Collection, Iterable
import asyncio
import collections
import contextlib
import logging
import typing

from hat import aio

from hat.drivers import acse
from hat.drivers import mms
from hat.drivers import tcp
from hat.drivers.iec61850 import common


mlog = logging.getLogger(__name__)

ReportCb: typing.TypeAlias = aio.AsyncCallable[[common.Report], None]

TerminationCb: typing.TypeAlias = aio.AsyncCallable[[common.Termination], None]


async def connect(addr: tcp.Address,
                  reports: Collection[common.ReportDef] = [],
                  report_cb: ReportCb | None = None,
                  termination_cb: TerminationCb | None = None,
                  status_delay: float | None = None,
                  status_timeout: float = 30,
                  **kwargs
                  ) -> 'Client':
    """Connect to IEC61850 server

    Additional arguments are passed directly to `hat.drivers.mms.connect`
    (`request_cb` and `unconfirmed_cb` are set by this coroutine).

    """
    client = Client()
    client._report_cb = report_cb
    client._termination_cb = termination_cb
    client._status_event = asyncio.Event()
    client._report_data_defs = {report_def.report_id: report_def.data
                                for report_def in reports}

    client._conn = await mms.connect(addr=addr,
                                     request_cb=None,
                                     unconfirmed_cb=client._on_unconfirmed,
                                     **kwargs)

    if status_delay is not None and client.is_open:
        client.async_group.spawn(client._status_loop, status_delay,
                                 status_timeout)

    return client


class Client(aio.Resource):

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def info(self) -> acse.ConnectionInfo:
        return self._conn.info

    async def create_dataset(self,
                             ref: common.DatasetRef,
                             data: Iterable[common.DataRef]
                             ) -> common.ServiceError | None:
        req = mms.DefineNamedVariableListRequest(
            name=_dataset_ref_to_object_name(ref),
            specification=[
                mms.NameVariableSpecification(_data_ref_to_object_name(i))
                for i in data])

        res = await self._send(req)

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res == mms.AccessError.OBJECT_ACCESS_DENIED:
                return common.ServiceError.ACCESS_VIOLATION

            if res == mms.DefinitionError.OBJECT_EXISTS:
                return common.ServiceError.INSTANCE_IN_USE

            if res == mms.DefinitionError.OBJECT_UNDEFINED:
                return common.ServiceError.PARAMETER_VALUE_INCONSISTENT

            if res == mms.ResourceError.CAPABILITY_UNAVAILABLE:
                return common.ServiceError.FAILED_DUE_TO_SERVER_CONTRAINT

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        if not isinstance(res, mms.DefineNamedVariableListResponse):
            raise Exception('unsupported response type')

    async def delete_dataset(self,
                             ref: common.DatasetRef
                             ) -> common.ServiceError | None:
        req = mms.DeleteNamedVariableListRequest(
            [_dataset_ref_to_object_name(ref)])

        res = await self._send(req)

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res == mms.AccessError.OBJECT_ACCESS_DENIED:
                return common.ServiceError.ACCESS_VIOLATION

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        if not isinstance(res, mms.DeleteNamedVariableListResponse):
            raise Exception('unsupported response type')

        if res.matched == 0 and res.deleted == 0:
            return common.ServiceError.INSTANCE_NOT_AVAILABLE

        if res.matched != res.deleted:
            return common.ServiceError.FAILED_DUE_TO_SERVER_CONTRAINT

    async def get_dataset_refs(self) -> Collection[common.DatasetRef] | common.ServiceError:  # NOQA
        logical_devices = await self._get_name_list(
            object_class=mms.ObjectClass.DOMAIN,
            object_scope=mms.VmdSpecificObjectScope())

        if isinstance(logical_devices, common.ServiceError):
            return logical_devices

        refs = collections.deque()

        for logical_device in logical_devices:
            identifiers = await self._get_name_list(
                object_class=mms.ObjectClass.NAMED_VARIABLE_LIST,
                object_scope=mms.DomainSpecificObjectScope(logical_device))

            if isinstance(identifiers, common.ServiceError):
                return identifiers

            for identifier in identifiers:
                logical_node, name = identifier.split('$')
                refs.append(
                    common.PersistedDatasetRef(logical_device=logical_device,
                                               logical_node=logical_node,
                                               name=name))

        names = await self._get_name_list(
            object_class=mms.ObjectClass.NAMED_VARIABLE_LIST,
            object_scope=mms.AaSpecificObjectScope())

        if isinstance(names, common.ServiceError):
            return names

        for name in names:
            refs.append(common.NonPersistedDatasetRef(name))

        return refs

    async def get_dataset_data_refs(self,
                                    ref: common.DatasetRef
                                    ) -> Collection[common.DataRef] | common.ServiceError:  # NOQA
        req = mms.GetNamedVariableListAttributesRequest(
            _dataset_ref_to_object_name(ref))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res == mms.AccessError.OBJECT_ACCESS_DENIED:
                return common.ServiceError.ACCESS_VIOLATION

            if res == mms.ServiceError.PDU_SIZE:
                return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        if not isinstance(res, mms.GetNamedVariableListAttributesResponse):
            raise Exception('unsupported response type')

        refs = collections.deque()

        for i in res.specification:
            if not isinstance(i, mms.NameVariableSpecification):
                raise Exception('unsupported specification type')

            refs.append(_data_ref_from_object_name(i.name))

        return ref

    async def get_rcb(self,
                      ref: common.RcbRef
                      ) -> common.Rcb | common.ServiceError:
        attrs = ['RptID', 'RptEna', 'DatSet', 'ConfRev', 'OptFlds', 'BufTm',
                 'SqNum', 'TrgOps', 'IntgPd', 'GI']

        if ref.type == common.RcbType.BUFFERED:
            attrs.extend(['PurgeBuf', 'EntryID', 'TimeOfEntry', 'ResvTms'])
            rcb = common.Brcb()

        elif ref.type == common.RcbType.UNBUFFERED:
            attrs.extend(['Resv'])
            rcb = common.Urcb()

        else:
            raise TypeError('unsupported rcb type')

        req = mms.ReadRequest([
            mms.NameVariableSpecification(_data_ref_to_object_name(
                common.DataRef(logical_device=ref.logical_device,
                               logical_node=ref.logical_node,
                               fc=ref.type.value,
                               names=[ref.name, attr])))
            for attr in attrs])

        res = await self._send(req)

        if isinstance(res, mms.Error):
            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        if not isinstance(res, mms.ReadResponse):
            raise Exception('unsupported response type')

        if all(isinstance(i, mms.DataAccessError) for i in res.results):
            if all(i == mms.DataAccessError.OBJECT_ACCESS_DENIED
                   for i in res.results):
                return common.ServiceError.ACCESS_VIOLATION

            if all(i == mms.DataAccessError.OBJECT_NON_EXISTENT
                   for i in res.results):
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        for attr, data in zip(attrs, res.results):
            if isinstance(data, mms.DataAccessError):
                continue

            if attr == 'RptID':
                rcb = rcb._replace(
                    report_id=_value_from_mms_data(
                        data, common.BasicValueType.VISIBLE_STRING))

            elif attr == 'RptEna':
                rcb = rcb._replace(
                    report_enable=_value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            elif attr == 'DatSet':
                value = _value_from_mms_data(
                    data, common.BasicValueType.VISIBLE_STRING)
                rcb = rcb._replace(
                    dataset=_dataset_ref_from_str(value, '$'))

            elif attr == 'ConfRev':
                rcb = rcb._replace(
                    conf_revision=_value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'OptFlds':
                value = _value_from_mms_data(
                    data, common.BasicValueType.BIT_STRING)
                rcb = rcb._replace(
                    optional_fields={common.OptionalField(index)
                                     for index, i in enumerate(value)
                                     if i})

            elif attr == 'BufTm':
                rcb = rcb._replace(
                    buffer_time=_value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'SqNum':
                rcb = rcb._replace(
                    sequence_number=_value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'TrgOps':
                value = _value_from_mms_data(
                    data, common.BasicValueType.BIT_STRING)
                rcb = rcb._replace(
                    trigger_options={common.TriggerCondition(index)
                                     for index, i in enumerate(value)
                                     if i})

            elif attr == 'IntgPd':
                rcb = rcb._replace(
                    integrity_period=_value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'GI':
                rcb = rcb._replace(
                    gi=_value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            elif attr == 'PurgeBuf':
                rcb = rcb._replace(
                    purge_buffer=_value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            elif attr == 'EntryID':
                rcb = rcb._replace(
                    entry_id=_value_from_mms_data(
                        data, common.BasicValueType.OCTET_STRING))

            elif attr == 'TimeOfEntry':
                if not isinstance(data, mms.BinaryTimeData):
                    raise Exception('unexpected data type')

                rcb = rcb._replace(time_of_entry=data.value)

            elif attr == 'ResvTms':
                rcb = rcb._replace(
                    reservation_time=_value_from_mms_data(
                        data, common.BasicValueType.INTEGER))

            elif attr == 'Resv':
                rcb = rcb._replace(
                    reserve=_value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            else:
                raise ValueError('unsupported attribute')

        return rcb

    async def set_rcb(self,
                      ref: common.RcbRef,
                      rcb: common.Rcb
                      ) -> common.ServiceError | None:
        pass

    async def write_data(self,
                         ref: common.DataRef,
                         type: common.ValueType,
                         value: common.Value
                         ) -> common.ServiceError | None:
        pass

    async def select(self,
                     ref: common.CommandRef,
                     model: common.ControlModel,
                     cmd: common.Command | None
                     ) -> common.AdditionalCause | None:
        pass

    async def cancel(self,
                     ref: common.CommandRef,
                     model: common.ControlModel,
                     cmd: common.Command
                     ) -> common.AdditionalCause | None:
        pass

    async def operate(self,
                      ref: common.CommandRef,
                      model: common.ControlModel,
                      cmd: common.Command
                      ) -> common.AdditionalCause | None:
        pass

    async def _on_unconfirmed(self, conn, unconfirmed):
        self._status_event.set()

    async def _send(self, req):
        res = await self._conn.send_confirmed(req)
        self._status_event.set()
        return res

    async def _status_loop(self, delay, timeout):
        try:
            while True:
                self._status_event.clear()

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._status_event.wait(), delay)
                    continue

                await aio.wait_for(self._send(mms.StatusRequest()), timeout)

        except asyncio.TimeoutError:
            mlog.warning("status timeout")

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("status loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _get_name_list(self, object_class, object_scope):
        identifiers = collections.deque()
        continue_after = None

        while True:
            req = mms.GetNameListRequest(
                object_class=object_class,
                object_scope=object_scope,
                continue_after=continue_after)

            res = await self._send(req)

            if isinstance(res, mms.Error):
                if res == mms.AccessError.OBJECT_NON_EXISTENT:
                    return common.ServiceError.INSTANCE_NOT_AVAILABLE

                if res == mms.AccessError.OBJECT_ACCESS_DENIED:
                    return common.ServiceError.ACCESS_VIOLATION

                if res == mms.ServiceError.OBJECT_CONSTRAINT_CONFLICT:
                    return common.ServiceError.PARAMETER_VALUE_INCONSISTENT

                return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

            if not isinstance(res, mms.GetNameListResponse):
                raise Exception('unsupported response type')

            identifiers.extend(res.identifiers)

            if not res.more_follows:
                break

            if not res.identifiers:
                raise Exception('invalid more follows value')

            continue_after = identifiers[-1]

        return identifiers


def _dataset_ref_to_object_name(ref):
    if isinstance(ref, common.PersistedDatasetRef):
        return mms.DomainSpecificObjectName(
            domain_id=ref.logical_device,
            item_id=f'{ref.logical_node}${ref.name}')

    if isinstance(ref, common.NonPersistedDatasetRef):
        return mms.AaSpecificObjectName(ref.name)

    raise TypeError('unsupported ref type')


def _dataset_ref_from_str(ref_str, delimiter):
    if ref_str.startswith('@'):
        return common.NonPersistedDatasetRef(ref_str[1:])

    logical_device, rest = ref_str.split('/', 1)
    logical_node, name = rest.split(delimiter)

    return common.PersistedDatasetRef(logical_device=logical_device,
                                      logical_node=logical_node,
                                      name=name)


def _data_ref_to_object_name(ref):
    item_id = f'{ref.logical_node}${ref.fc}' + ''.join(
        (f'({i})' if isinstance(i, int) else f'${i}')
        for i in ref.names)

    return mms.DomainSpecificObjectName(
        domain_id=ref.logical_device,
        item_id=item_id)


def _data_ref_from_object_name(object_name):
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
                          names=list(names))


def _value_from_mms_data(mms_data, value_type):
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

        return common.Timestamp(t=mms_data.value,
                                leap_seconds_known=mms_data.leap_second,
                                clock_failure=mms_data.clock_failure,
                                clock_not_synchronized=mms.not_synchronized,
                                time_accuracy=mms.accuracy)

    if value_type == common.AcsiValueType.DOUBLE_POINT:
        if not isinstance(mms_data, mms.BitStringData):
            raise Exception('unexpected data type')

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
            magnitude=_value_from_mms_data(
                elements[0], common.AcsiValueType.ANALOGUE),
            angle=(
                _value_from_mms_data(
                    elements[1], common.AcsiValueType.ANALOGUE)
                if len(elements) > 1 else None))

    if value_type == common.AcsiValueType.STEP_POSITION:
        if not isinstance(mms_data, mms.StructureData):
            raise Exception('unexpected data type')

        if len(mms_data.elements) < 1 or len(mms_data.elements) > 2:
            raise Exception('invalid structure size')

        elements = list(mms_data.elements)

        return common.StepPosition(
            value=_value_from_mms_data(
                elements[0], common.BasicValueType.INTEGER),
            transient=(
                _value_from_mms_data(
                    elements[1], common.BasicValueType.BOOLEAN)
                if len(elements) > 1 else None))

    if value_type == common.AcsiValueType.BINARY_CONTROL:
        if not isinstance(mms_data, mms.BitStringData):
            raise Exception('unexpected data type')

        return common.BinaryControl((mms_data.value[0] << 1) |
                                    mms_data.value[1])

    if isinstance(value_type, common.ArrayValueType):
        if not isinstance(mms_data, mms.ArrayData):
            raise Exception('unexpected data type')

        return [_value_from_mms_data(i, value_type.type)
                for i in mms_data.elements]

    if isinstance(value_type, common.StructValueType):
        if not isinstance(mms_data, mms.StructureData):
            raise Exception('unexpected data type')

        if len(mms_data.elements) != len(value_type.elements):
            raise Exception('invalid structure size')

        return [_value_from_mms_data(i, t)
                for i, t in zip(mms_data.elements, value_type.elements)]

    raise TypeError('unsupported value type')
