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
from hat.drivers.iec61850 import encoder


mlog = logging.getLogger(__name__)

ReportCb: typing.TypeAlias = aio.AsyncCallable[[common.Report], None]

TerminationCb: typing.TypeAlias = aio.AsyncCallable[[common.Termination], None]


async def connect(addr: tcp.Address,
                  data_value_types: dict[common.DataRef,
                                         common.ValueType] = {},
                  cmd_value_types: dict[common.CommandRef,
                                        common.ValueType] = {},
                  report_data_refs: dict[common.ReportId,
                                         Collection[common.DataRef]] = {},
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
    client._data_value_types = data_value_types
    client._cmd_value_types = cmd_value_types
    client._report_cb = report_cb
    client._termination_cb = termination_cb
    client._loop = asyncio.get_running_loop()
    client._status_event = asyncio.Event()
    client._last_appl_errors = {}
    client._report_data_defs = {
        report_id: [encoder.DataDef(ref=data_ref,
                                    value_type=data_value_types[data_ref])
                    for data_ref in data_refs]
        for report_id, data_refs in report_data_refs.items()}

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
            name=encoder.dataset_ref_to_object_name(ref),
            specification=[
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(i))
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
        req = mms.DeleteNamedVariableListRequest([
            encoder.dataset_ref_to_object_name(ref)])

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
            encoder.dataset_ref_to_object_name(ref))

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

            refs.append(encoder.data_ref_from_object_name(i.name))

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
            mms.NameVariableSpecification(
                encoder.data_ref_to_object_name(
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
                    report_id=encoder.value_from_mms_data(
                        data, common.BasicValueType.VISIBLE_STRING))

            elif attr == 'RptEna':
                rcb = rcb._replace(
                    report_enable=encoder.value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            elif attr == 'DatSet':
                value = encoder.value_from_mms_data(
                    data, common.BasicValueType.VISIBLE_STRING)
                rcb = rcb._replace(
                    dataset=encoder.dataset_ref_from_str(value, '$'))

            elif attr == 'ConfRev':
                rcb = rcb._replace(
                    conf_revision=encoder.value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'OptFlds':
                value = encoder.value_from_mms_data(
                    data, common.BasicValueType.BIT_STRING)
                rcb = rcb._replace(
                    optional_fields={common.OptionalField(index)
                                     for index, i in enumerate(value)
                                     if i})

            elif attr == 'BufTm':
                rcb = rcb._replace(
                    buffer_time=encoder.value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'SqNum':
                rcb = rcb._replace(
                    sequence_number=encoder.value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'TrgOps':
                value = encoder.value_from_mms_data(
                    data, common.BasicValueType.BIT_STRING)
                rcb = rcb._replace(
                    trigger_options={common.TriggerCondition(index)
                                     for index, i in enumerate(value)
                                     if i})

            elif attr == 'IntgPd':
                rcb = rcb._replace(
                    integrity_period=encoder.value_from_mms_data(
                        data, common.BasicValueType.UNSIGNED))

            elif attr == 'GI':
                rcb = rcb._replace(
                    gi=encoder.value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            elif attr == 'PurgeBuf':
                rcb = rcb._replace(
                    purge_buffer=encoder.value_from_mms_data(
                        data, common.BasicValueType.BOOLEAN))

            elif attr == 'EntryID':
                rcb = rcb._replace(
                    entry_id=encoder.value_from_mms_data(
                        data, common.BasicValueType.OCTET_STRING))

            elif attr == 'TimeOfEntry':
                if not isinstance(data, mms.BinaryTimeData):
                    raise Exception('unexpected data type')

                rcb = rcb._replace(time_of_entry=data.value)

            elif attr == 'ResvTms':
                rcb = rcb._replace(
                    reservation_time=encoder.value_from_mms_data(
                        data, common.BasicValueType.INTEGER))

            elif attr == 'Resv':
                rcb = rcb._replace(
                    reserve=encoder.value_from_mms_data(
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
                encoder.value_to_mms_data(
                    rcb.report_id, common.BasicValueType.VISIBLE_STRING))

        if rcb.report_enable is not None:
            attrs.append('RptEna')
            data.append(
                encoder.value_to_mms_data(
                    rcb.report_enable, common.BasicValueType.BOOLEAN))

        if rcb.dataset is not None:
            attrs.append('DatSet')
            data.append(
                encoder.value_to_mms_data(
                    encoder.dataset_ref_to_str(rcb.dataset, '$'),
                    common.BasicValueType.VISIBLE_STRING))

        if rcb.conf_revision is not None:
            attrs.append('ConfRev')
            data.append(
                encoder.value_to_mms_data(
                    rcb.conf_revision, common.BasicValueType.UNSIGNED))

        if rcb.optional_fields is not None:
            attrs.append('OptFlds')
            data.append(
                encoder.value_to_mms_data(
                    [False,
                     ...(common.OptionalField(i) in rcb.optional_fields
                         for i in range(1, 9)),
                     False],
                    common.BasicValueType.BIT_STRING))

        if rcb.buffer_time is not None:
            attrs.append('BufTm')
            data.append(
                encoder.value_to_mms_data(
                    rcb.buffer_time, common.BasicValueType.UNSIGNED))

        if rcb.sequence_number is not None:
            attrs.append('SqNum')
            data.append(
                encoder.value_to_mms_data(
                    rcb.sequence_number, common.BasicValueType.UNSIGNED))

        if rcb.trigger_options is not None:
            attrs.append('TrgOps')
            data.append(
                encoder.value_to_mms_data(
                    [False,
                     ...(common.TriggerCondition(i) in rcb.trigger_options
                         for i in range(1, 5))],
                    common.BasicValueType.BIT_STRING))

        if rcb.integrity_period is not None:
            attrs.append('IntgPd')
            data.append(
                encoder.value_to_mms_data(
                    rcb.integrity_period, common.BasicValueType.UNSIGNED))

        if rcb.gi is not None:
            attrs.append('GI')
            data.append(
                encoder.value_to_mms_data(
                    rcb.gi, common.BasicValueType.BOOLEAN))

        if isinstance(rcb, common.Brcb):
            if rcb.purge_buffer is not None:
                attrs.append('PurgeBuf')
                data.append(
                    encoder.value_to_mms_data(
                        rcb.purge_buffer, common.BasicValueType.BOOLEAN))

            if rcb.entry_id is not None:
                attrs.append('EntryID')
                data.append(
                    encoder.value_to_mms_data(
                        rcb.entry_id, common.BasicValueType.OCTET_STRING))

            if rcb.time_of_entry is not None:
                attrs.append('TimeOfEntry')
                data.append(mms.BinaryTimeData(rcb.time_of_entry))

            if rcb.reservation_time is not None:
                attrs.append('ResvTms')
                data.append(
                    encoder.value_to_mms_data(
                        rcb.reservation_time, common.BasicValueType.INTEGER))

        elif isinstance(rcb, common.Urcb):
            if rcb.reserve is not None:
                attrs.append('Resv')
                data.append(
                    encoder.value_to_mms_data(
                        rcb.reserve, common.BasicValueType.BOOLEAN))

        else:
            raise TypeError('unsupported rcb type')

        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(
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
                         value: common.Value
                         ) -> common.ServiceError | None:
        value_type = self._data_value_types[ref]

        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(ref))],
            data=[encoder.value_to_mms_data(value,  value_type)])

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
                     ) -> common.CommandError | None:
        if cmd is not None:
            return await self._command_with_last_appl_error(ref=ref,
                                                            cmd=cmd,
                                                            attr='SBOw',
                                                            with_checks=True)

        req = mms.ReadRequest([
            mms.NameVariableSpecification(
                encoder.data_ref_to_object_name(
                    common.DataRef(logical_device=ref.logical_device,
                                   logical_node=ref.logical_node,
                                   fc='CO',
                                   names=[ref.name, 'SBO'])))])

        res = await self._send(req)

        if isinstance(res, mms.Error):
            return _create_command_error(
                service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                last_appl_error=None)

        if not isinstance(res, mms.ReadResponse):
            raise Exception('unsupported response type')

        if not isinstance(res.results[0], mms.VisibleStringData):
            return _create_command_error(
                service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                last_appl_error=None)

        if res.results[0].value == '':
            return _create_command_error(
                service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                last_appl_error=None)

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
                await self._process_report(unconfirmed.data)

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
                data_ref = encoder.data_ref_from_object_name(names[-1])
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
        if not self._report_cb:
            return

        report_id = encoder.value_from_mms_data(
            mms_data[0], common.BasicValueType.VISIBLE_STRING)

        data_defs = self._report_data_defs.get(report_id)
        if data_defs is None:
            return

        report = encoder.report_from_mms_data(mms_data, data_defs)

        await aio.call(self._report_cb, report)

    def _process_last_appl_error(self, mms_data):
        last_appl_error = encoder.last_appl_error_from_mms_data(mms_data)

        key = last_appl_error.name, last_appl_error.control_number
        if key in self._last_appl_errors:
            self._last_appl_errors[key] = last_appl_error

    async def _process_termination(self, ref, cmd_mms_data,
                                   last_appl_error_mms_data):
        if not self._termination_cb:
            return

        value_type = self._cmd_value_types.get(ref)
        if value_type is None:
            return

        cmd = encoder.command_from_mms_data(mms_data=cmd_mms_data,
                                            value_type=value_type,
                                            with_checks=True)

        if last_appl_error_mms_data:
            last_appl_error = encoder.last_appl_error_from_mms_data(
                last_appl_error_mms_data)

        else:
            last_appl_error = None

        termination = common.Termination(
            ref=ref,
            cmd=cmd,
            error=_create_command_error(service_error=None,
                                        last_appl_error=last_appl_error))

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
        value_type = self._cmd_value_types[ref]

        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(
                        common.DataRef(logical_device=ref.logical_device,
                                       logical_node=ref.logical_node,
                                       fc='CO',
                                       names=[ref.name, attr])))],
            data=[encoder.command_to_mms_data(cmd=cmd,
                                              value_type=value_type,
                                              with_checks=with_checks)])

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
            return _create_command_error(
                service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                last_appl_error=last_appl_error)

        if not isinstance(res, mms.WriteResponse):
            raise Exception('unsupported response type')

        if res.results[0] is not None:
            return _create_command_error(service_error=None,
                                         last_appl_error=last_appl_error)


def _create_command_error(service_error, last_appl_error):
    additional_cause = (last_appl_error.additional_cause
                        if last_appl_error else None)
    test_error = last_appl_error.error if last_appl_error else None

    return common.CommandError(service_error=service_error,
                               additional_cause=additional_cause,
                               test_error=test_error)
