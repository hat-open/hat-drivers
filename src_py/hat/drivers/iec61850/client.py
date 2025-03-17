from collections.abc import Collection, Iterable
import asyncio
import collections
import contextlib
import logging
import typing

from hat import aio
from hat import util

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
    client._loop = asyncio.get_running_loop()
    client._status_event = asyncio.Event()
    client._last_appl_errors = {}
    client._report_data_defs = {report_def.report_id: report_def.data
                                for report_def in reports}

    client._conn = await mms.connect(addr=addr,
                                     request_cb=None,
                                     unconfirmed_cb=client._on_unconfirmed,
                                     **kwargs)

    if client.is_open and status_delay is not None:
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
        attrs = collections.deque()
        data = collections.deque()

        if rcb.report_id is not None:
            attrs.append('RptID')
            data.append(
                _value_to_mms_data(rcb.report_id,
                                   common.BasicValueType.VISIBLE_STRING))

        if rcb.report_enable is not None:
            attrs.append('RptEna')
            data.append(
                _value_to_mms_data(rcb.report_enable,
                                   common.BasicValueType.BOOLEAN))

        if rcb.dataset is not None:
            attrs.append('DatSet')
            data.append(
                _value_to_mms_data(_dataset_ref_to_str(rcb.dataset, '$'),
                                   common.BasicValueType.VISIBLE_STRING))

        if rcb.conf_revision is not None:
            attrs.append('ConfRev')
            data.append(
                _value_to_mms_data(rcb.conf_revision,
                                   common.BasicValueType.UNSIGNED))

        if rcb.optional_fields is not None:
            attrs.append('OptFlds')
            data.append(
                _value_to_mms_data(
                    [False,
                     ...(common.OptionalField(i) in rcb.optional_fields
                         for i in range(1, 9))],
                    common.BasicValueType.BIT_STRING))

        if rcb.buffer_time is not None:
            attrs.append('BufTm')
            data.append(
                _value_to_mms_data(rcb.buffer_time,
                                   common.BasicValueType.UNSIGNED))

        if rcb.sequence_number is not None:
            attrs.append('SqNum')
            data.append(
                _value_to_mms_data(rcb.sequence_number,
                                   common.BasicValueType.UNSIGNED))

        if rcb.trigger_options is not None:
            attrs.append('TrgOps')
            data.append(
                _value_to_mms_data(
                    [False,
                     ...(common.TriggerCondition(i) in rcb.trigger_options
                         for i in range(1, 5))],
                    common.BasicValueType.BIT_STRING))

        if rcb.integrity_period is not None:
            attrs.append('IntgPd')
            data.append(
                _value_to_mms_data(rcb.integrity_period,
                                   common.BasicValueType.UNSIGNED))

        if rcb.gi is not None:
            attrs.append('GI')
            data.append(
                _value_to_mms_data(rcb.gi,
                                   common.BasicValueType.BOOLEAN))

        if isinstance(rcb, common.Brcb):
            if rcb.purge_buffer is not None:
                attrs.append('PurgeBuf')
                data.append(
                    _value_to_mms_data(rcb.purge_buffer,
                                       common.BasicValueType.BOOLEAN))

            if rcb.entry_id is not None:
                attrs.append('EntryID')
                data.append(
                    _value_to_mms_data(rcb.entry_id,
                                       common.BasicValueType.OCTET_STRING))

            if rcb.time_of_entry is not None:
                attrs.append('TimeOfEntry')
                data.append(mms.BinaryTimeData(rcb.time_of_entry))

            if rcb.reservation_time is not None:
                attrs.append('ResvTms')
                data.append(
                    _value_to_mms_data(rcb.reservation_time,
                                       common.BasicValueType.INTEGER))

        elif isinstance(rcb, common.Urcb):
            if rcb.reserve is not None:
                attrs.append('Resv')
                data.append(
                    _value_to_mms_data(rcb.reserve,
                                       common.BasicValueType.BOOLEAN))

        else:
            raise TypeError('unsupported rcb type')

        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    _data_ref_to_object_name(
                        common.DataRef(logical_device=ref.logical_device,
                                       logical_node=ref.logical_node,
                                       fc=ref.type.value,
                                       names=[ref.name, attr])))
                for attr in attrs],
            data=data)

        res = await self._send(req)

        if isinstance(res, mms.Error):
            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        if not isinstance(res, mms.WriteResponse):
            raise Exception('unsupported response type')

        if any(i is not None for i in res.results):
            if all(i == mms.DataAccessError.OBJECT_ACCESS_DENIED
                   for i in res.results
                   if i):
                return common.ServiceError.ACCESS_VIOLATION

            if all(i == mms.DataAccessError.OBJECT_NON_EXISTENT
                   for i in res.results
                   if i):
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if all(i == mms.DataAccessError.TEMPORARILY_UNAVAILABLE
                   for i in res.results
                   if i):
                return common.ServiceError.INSTANCE_LOCKED_BY_OTHER_CLIENT

            if all(i == mms.DataAccessError.TYPE_INCONSISTENT
                   for i in res.results
                   if i):
                return common.ServiceError.TYPE_CONFLICT

            if all(i == mms.DataAccessError.OBJECT_VALUE_INVALID
                   for i in res.results
                   if i):
                return common.ServiceError.PARAMETER_VALUE_INCONSISTENT

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

    async def write_data(self,
                         ref: common.DataRef,
                         value_type: common.ValueType,
                         value: common.Value
                         ) -> common.ServiceError | None:
        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(_data_ref_to_object_name(ref))],
            data=[_value_to_mms_data(value, value_type)])

        res = await self._send(req)

        if isinstance(res, mms.Error):
            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        if not isinstance(res, mms.WriteResponse):
            raise Exception('unsupported response type')

        if res.results[0] is not None:
            if res.results[0] == mms.DataAccessError.OBJECT_ACCESS_DENIED:
                return common.ServiceError.ACCESS_VIOLATION

            if res.results[0] == mms.DataAccessError.OBJECT_NON_EXISTENT:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res.results[0] == mms.DataAccessError.TEMPORARILY_UNAVAILABLE:
                return common.ServiceError.INSTANCE_LOCKED_BY_OTHER_CLIENT

            if res.results[0] == mms.DataAccessError.TYPE_INCONSISTENT:
                return common.ServiceError.TYPE_CONFLICT

            if res.results[0] == mms.DataAccessError.OBJECT_VALUE_INVALID:
                return common.ServiceError.PARAMETER_VALUE_INCONSISTENT

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

    async def select(self,
                     ref: common.CommandRef,
                     cmd: common.Command | None
                     ) -> common.AdditionalCause | None:
        if cmd is not None:
            return await self._command_with_last_appl_error(ref=ref,
                                                            cmd=cmd,
                                                            attr='SBOw',
                                                            with_checks=True)

        req = mms.ReadRequest([
            mms.NameVariableSpecification(
                _data_ref_to_object_name(
                    common.DataRef(logical_device=ref.logical_device,
                                   logical_node=ref.logical_node,
                                   fc='CO',
                                   names=[ref.name, 'SBO'])))])

        res = await self._send(req)

        if isinstance(res, mms.Error):
            return common.AdditionalCause.UNKNOWN

        if not isinstance(res, mms.ReadResponse):
            raise Exception('unsupported response type')

        if not isinstance(res.results[0], mms.VisibleStringData):
            return common.AdditionalCause.UNKNOWN

        if res.results[0].value == '':
            return common.AdditionalCause.UNKNOWN

    async def cancel(self,
                     ref: common.CommandRef,
                     cmd: common.Command
                     ) -> common.AdditionalCause | None:
        return await self._command_with_last_appl_error(ref=ref,
                                                        cmd=cmd,
                                                        attr='Cancel',
                                                        with_checks=False)

    async def operate(self,
                      ref: common.CommandRef,
                      cmd: common.Command
                      ) -> common.AdditionalCause | None:
        return await self._command_with_last_appl_error(ref=ref,
                                                        cmd=cmd,
                                                        attr='Oper',
                                                        with_checks=True)

    async def _on_unconfirmed(self, conn, unconfirmed):
        self._status_event.set()

        if not isinstance(unconfirmed, mms.InformationReportUnconfirmed):
            return

        if isinstance(unconfirmed.specification, mms.ObjectName):
            if unconfirmed.specification == mms.VmdSpecificObjectName('RPT'):
                await self._process_report(unconfirmed.data[0])

        elif (len(unconfirmed.specification) == 1 and
                list(unconfirmed.specification) == [
                    mms.NameVariableSpecification(
                        mms.VmdSpecificObjectName('LastApplError'))]):
            self._process_last_appl_error(unconfirmed.data[0])

        elif ((1 <= len(unconfirmed.specification) <= 2) and
                all(isinstance(i, mms.NameVariableSpecification)
                    for i in unconfirmed.specification)):
            names = [i.name for i in unconfirmed.specification]
            data = list(unconfirmed.data)

            if ((len(names) == 1 and
                 isinstance(names[0], mms.DomainSpecificObjectName)) or
                (len(names) == 2 and
                 names[0] == mms.VmdSpecificObjectName('LastApplError') and
                 isinstance(names[1], mms.DomainSpecificObjectName))):
                data_ref = _data_ref_from_object_name(names[-1])
                data_ref_names = list(data_ref.names)

                if (data_ref.fc == 'CO' and
                        len(data_ref_names) == 2 and
                        data_ref_names[1] == 'Oper'):
                    await self._process_termination(
                        ref=common.CommandRef(
                            logical_device=data_ref.logical_device,
                            logical_node=data_ref.logical_node,
                            name=data_ref_names[0]),
                        cmd_mms_data=data[-1],
                        last_appl_error_mms_data=(data[0] if len(data) > 1
                                                  else None))

    async def _process_report(self, mms_data):
        pass

    def _process_last_appl_error(self, mms_data):
        last_appl_error = _last_appl_error_from_mms_data(mms_data)

        key = last_appl_error.name, last_appl_error.control_number
        if key in self._last_appl_errors:
            self._last_appl_errors[key] = last_appl_error

    async def _process_termination(self, ref, cmd_mms_data,
                                   last_appl_error_mms_data):
        if not self._termination_cb:
            return

        cmd = _command_from_mms_data(cmd_mms_data)

        if last_appl_error_mms_data:
            last_appl_error = _last_appl_error_from_mms_data(
                last_appl_error_mms_data)
            additional_cause = last_appl_error.additional_cause

        else:
            additional_cause = None

        termination = common.Termination(ref=ref,
                                         cmd=cmd,
                                         error=additional_cause)

        await aio.call(self._termination_cb, termination)

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

    async def _command_with_last_appl_error(self, ref, cmd, attr, with_checks):
        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    _data_ref_to_object_name(
                        common.DataRef(logical_device=ref.logical_device,
                                       logical_node=ref.logical_node,
                                       fc='CO',
                                       names=[ref.name, attr])))],
            data=[_command_to_mms_data(cmd, with_checks)])

        name = (f'{req.specification[0].name.domain_id}/'
                f'{req.specification[0].name.item_id}')
        key = name, cmd.control_number

        if key in self._last_appl_errors:
            raise Exception('active control number duplicate')

        self._last_appl_errors[key] = None

        try:
            res = await self._send(req)

        finally:
            last_appl_error = self._last_appl_errors.pop(key, None)

        if isinstance(res, mms.Error):
            return common.AdditionalCause.UNKNOWN

        if not isinstance(res, mms.WriteResponse):
            raise Exception('unsupported response type')

        if res.results[0] is not None:
            if last_appl_error is None:
                return common.AdditionalCause.UNKNOWN

            return last_appl_error.additional_cause


class _LastApplError(typing.NamedTuple):
    name: str
    error: int
    origin: common.Originator
    control_number: int
    additional_cause: common.AdditionalCause


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


def _dataset_ref_to_str(ref, delimiter):
    if isinstance(ref, common.PersistedDatasetRef):
        return f'{ref.logical_device}/{ref.logical_node}{delimiter}{ref.name}'

    if isinstance(ref, common.NonPersistedDatasetRef):
        return f'@{ref.name}'

    raise TypeError('unsupported ref type')


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
                          names=names)


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

        return common.Timestamp(**mms_data._asdict())

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


def _value_to_mms_data(value, value_type):
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

        mms.BitStringData([bool(value.validity.value & 2),
                           bool(value.validity.value & 1),
                           ...(common.QualityDetail(i) in value.details
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

        return mms.IntegerData(value)

    if value_type == common.AcsiValueType.ANALOGUE:
        if not isinstance(value, common.Analogue):
            raise Exception('unexpected value type')

        if value.i is None and value.f is None:
            raise Exception('invalid analogue value')

        mms_data = mms.StructureData([])

        if value.i is not None:
            mms_data.elements.append(
                _value_to_mms_data(value.i, common.BasicValueType.INTEGER))

        if value.f is not None:
            mms_data.elements.append(
                _value_to_mms_data(value.f, common.BasicValueType.FLOAT))

        return mms_data

    if value_type == common.AcsiValueType.VECTOR:
        if not isinstance(value, common.Vector):
            raise Exception('unexpected value type')

        mms_data = mms.StructureData([
            _value_to_mms_data(value.magnitude,
                               common.AcsiValueType.ANALOGUE)])

        if value.angle is not None:
            mms_data.elements.append(
                _value_to_mms_data(value.angle, common.AcsiValueType.ANALOGUE))

        return mms_data

    if value_type == common.AcsiValueType.STEP_POSITION:
        if not isinstance(value, common.StepPosition):
            raise Exception('unexpected value type')

        mms_data = mms.StructureData([
            _value_to_mms_data(value.value, common.BasicValueType.INTEGER)])

        if value.transient is not None:
            mms_data.elements.append(
                _value_to_mms_data(value.transient,
                                   common.BasicValueType.BOOLEAN))

    if value_type == common.AcsiValueType.BINARY_CONTROL:
        if not isinstance(value, common.BinaryControl):
            raise Exception('unexpected value type')

        return mms.BitStringData([bool(value.value & 2),
                                  bool(value.value & 1)])

    if isinstance(value_type, common.ArrayValueType):
        if any(not isinstance(i, value_type.type) for i in value):
            raise Exception('unexpected value type')

        return mms.ArrayData([_value_to_mms_data(i, value_type.type)
                              for i in value])

    if isinstance(value_type, common.StructValueType):
        if len(value) != len(value_type.elements):
            raise Exception('invalid structure size')

        return mms.StructureData([_value_to_mms_data(i, t)
                                  for i, t in zip(value, value_type.elements)])

    raise TypeError('unsupported value type')


def _command_to_mms_data(cmd, with_checks):
    pass


def _command_from_mms_data(mms_data):
    pass


def _last_appl_error_from_mms_data(mms_data):
    pass
