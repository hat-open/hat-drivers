from collections.abc import Collection
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
from hat.drivers.iec61850.client import logger


mlog = logging.getLogger(__name__)
"""Module logger"""

ReportCb: typing.TypeAlias = aio.AsyncCallable[[common.Report], None]
"""Report callback"""

TerminationCb: typing.TypeAlias = aio.AsyncCallable[[common.Termination], None]
"""Termination callback"""


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

    `data_value_types` include value types used in report processing and
    writing data.

    `cmd_value_types` include value types used in command actions and
    termination processing.

    Only reports that are specified by `report_data_refs` are notified with
    `report_cb`.

    If `status_delay` is ``None``, periodical sending of status requests is
    disabled.

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

    client._log = logger.create_logger(mlog, kwargs.get('name'), None)
    client._comm_log = logger.CommunicationLogger(mlog, kwargs.get('name'),
                                                  None)

    client._conn = await mms.connect(addr=addr,
                                     request_cb=None,
                                     unconfirmed_cb=client._on_unconfirmed,
                                     **kwargs)

    try:
        client._log = logger.create_logger(mlog, client._conn.info.name,
                                           client._conn.info)
        client._comm_log = logger.CommunicationLogger(
            mlog, client._conn.info.name, client._conn.info)

        if status_delay is not None:
            client.async_group.spawn(client._status_loop, status_delay,
                                     status_timeout)

        client.async_group.spawn(aio.call_on_cancel, client._comm_log.log,
                                 common.CommLogAction.CLOSE)
        client._comm_log.log(common.CommLogAction.OPEN)

    except BaseException:
        await aio.uncancellable(client.async_close())
        raise

    return client


class Client(aio.Resource):
    """Client"""

    @property
    def async_group(self):
        """Async group"""
        return self._conn.async_group

    @property
    def info(self) -> acse.ConnectionInfo:
        """Connection info"""
        return self._conn.info

    async def create_dataset(self,
                             ref: common.DatasetRef,
                             data: Collection[common.DataRef]
                             ) -> common.ServiceError | None:
        """Create dataset"""
        req = mms.DefineNamedVariableListRequest(
            name=encoder.dataset_ref_to_object_name(ref),
            specification=[
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(i))
                for i in data])

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.CreateDatasetReq(ref=ref,
                                                       data=data))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                result = common.ServiceError.INSTANCE_NOT_AVAILABLE

            elif res == mms.AccessError.OBJECT_ACCESS_DENIED:
                result = common.ServiceError.ACCESS_VIOLATION

            elif res == mms.DefinitionError.OBJECT_EXISTS:
                result = common.ServiceError.INSTANCE_IN_USE

            elif res == mms.DefinitionError.OBJECT_UNDEFINED:
                result = common.ServiceError.PARAMETER_VALUE_INCONSISTENT

            elif res == mms.ResourceError.CAPABILITY_UNAVAILABLE:
                result = common.ServiceError.FAILED_DUE_TO_SERVER_CONSTRAINT

            else:
                result = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

        elif isinstance(res, mms.DefineNamedVariableListResponse):
            result = None

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.CreateDatasetRes(result))

        return result

    async def delete_dataset(self,
                             ref: common.DatasetRef
                             ) -> common.ServiceError | None:
        """Delete dataset"""
        req = mms.DeleteNamedVariableListRequest([
            encoder.dataset_ref_to_object_name(ref)])

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.DeleteDatasetReq(ref))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                result = common.ServiceError.INSTANCE_NOT_AVAILABLE

            elif res == mms.AccessError.OBJECT_ACCESS_DENIED:
                result = common.ServiceError.ACCESS_VIOLATION

            else:
                result = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

        elif isinstance(res, mms.DeleteNamedVariableListResponse):
            if res.matched == 0 and res.deleted == 0:
                result = common.ServiceError.INSTANCE_NOT_AVAILABLE

            elif res.matched != res.deleted:
                result = common.ServiceError.FAILED_DUE_TO_SERVER_CONSTRAINT

            else:
                result = None

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.DeleteDatasetRes(result))

        return result

    async def get_persisted_dataset_refs(self,
                                         logical_device: str
                                         ) -> Collection[common.PersistedDatasetRef] | common.ServiceError:  # NOQA
        """Get persisted dataset references associated with logical device"""

        if self._comm_log.is_enabled:
            self._comm_log.log(
                common.CommLogAction.SEND,
                logger.GetPersistedDatasetRefsReq(logical_device))

        identifiers = await self._get_name_list(
            object_class=mms.ObjectClass.NAMED_VARIABLE_LIST,
            object_scope=mms.DomainSpecificObjectScope(logical_device))

        if isinstance(identifiers, common.ServiceError):
            result = identifiers

        else:
            result = collections.deque()
            for identifier in identifiers:
                logical_node, name = identifier.split('$')
                result.append(
                    common.PersistedDatasetRef(logical_device=logical_device,
                                               logical_node=logical_node,
                                               name=name))

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.GetPersistedDatasetRefsRes(result))

        return result

    async def get_dataset_data_refs(self,
                                    ref: common.DatasetRef
                                    ) -> Collection[common.DataRef] | common.ServiceError:  # NOQA
        """Get data references associated with single dataset"""
        req = mms.GetNamedVariableListAttributesRequest(
            encoder.dataset_ref_to_object_name(ref))

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.GetDatasetDataRefsReq(ref))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                result = common.ServiceError.INSTANCE_NOT_AVAILABLE

            elif res == mms.AccessError.OBJECT_ACCESS_DENIED:
                result = common.ServiceError.ACCESS_VIOLATION

            elif res == mms.ServiceError.PDU_SIZE:
                result = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

            else:
                result = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

        elif isinstance(res, mms.GetNamedVariableListAttributesResponse):
            result = collections.deque()

            for i in res.specification:
                if not isinstance(i, mms.NameVariableSpecification):
                    raise Exception('unsupported specification type')

                result.append(encoder.data_ref_from_object_name(i.name))

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.GetDatasetDataRefsRes(result))

        return result

    async def get_rcb_attrs(self,
                            ref: common.RcbRef,
                            attr_types: Collection[common.RcbAttrType]
                            ) -> dict[common.RcbAttrType,
                                      common.RcbAttrValue | common.ServiceError]:  # NOQA
        """Get RCB attribute value"""
        specification = collections.deque()

        for attr_type in attr_types:
            if ref.type == common.RcbType.BUFFERED:
                if attr_type == common.RcbAttrType.RESERVE:
                    raise ValueError('unsupported attribute type')

            elif ref.type == common.RcbType.UNBUFFERED:
                if attr_type in (common.RcbAttrType.PURGE_BUFFER,
                                 common.RcbAttrType.ENTRY_ID,
                                 common.RcbAttrType.TIME_OF_ENTRY,
                                 common.RcbAttrType.RESERVATION_TIME):
                    raise ValueError('unsupported attribute type')

            else:
                raise TypeError('unsupported rcb type')

            specification.append(
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(
                        common.DataRef(logical_device=ref.logical_device,
                                       logical_node=ref.logical_node,
                                       fc=ref.type.value,
                                       names=(ref.name, attr_type.value)))))

        req = mms.ReadRequest(specification)

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.GetRcbAttrsReq(ref=ref,
                                                     attr_types=attr_types))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            results = {
                attr_type: common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA
                for attr_type in attr_types}

        elif isinstance(res, mms.ReadResponse):
            if len(res.results) != len(attr_types):
                raise Exception('invalid results length')

            results = {}

            for attr_type, mms_data in zip(attr_types, res.results):
                if isinstance(mms_data, mms.DataAccessError):
                    if mms_data == mms.DataAccessError.OBJECT_ACCESS_DENIED:
                        results[attr_type] = common.ServiceError.ACCESS_VIOLATION  # NOQA

                    elif mms_data == mms.DataAccessError.OBJECT_NON_EXISTENT:
                        results[attr_type] = common.ServiceError.INSTANCE_NOT_AVAILABLE  # NOQA

                    else:
                        results[attr_type] = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

                else:
                    results[attr_type] = encoder.rcb_attr_value_from_mms_data(
                        mms_data, attr_type)

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.GetRcbAttrsRes(results))

        return results

    async def set_rcb_attrs(self,
                            ref: common.RcbRef,
                            attrs: Collection[tuple[common.RcbAttrType,
                                                    common.RcbAttrValue]]
                            ) -> dict[common.RcbAttrType,
                                      common.ServiceError | None]:
        """Set RCB attribute values"""
        specification = collections.deque()
        data = collections.deque()

        for attr_type, attr_value in attrs:
            if ref.type == common.RcbType.BUFFERED:
                if attr_type == common.RcbAttrType.RESERVE:
                    raise ValueError('unsupported attribute type')

            elif ref.type == common.RcbType.UNBUFFERED:
                if attr_type in (common.RcbAttrType.PURGE_BUFFER,
                                 common.RcbAttrType.ENTRY_ID,
                                 common.RcbAttrType.TIME_OF_ENTRY,
                                 common.RcbAttrType.RESERVATION_TIME):
                    raise ValueError('unsupported attribute type')

            else:
                raise TypeError('unsupported rcb type')

            specification.append(
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(
                        common.DataRef(logical_device=ref.logical_device,
                                       logical_node=ref.logical_node,
                                       fc=ref.type.value,
                                       names=(ref.name, attr_type.value)))))
            data.append(
                encoder.rcb_attr_value_to_mms_data(attr_value, attr_type))

        req = mms.WriteRequest(specification=specification,
                               data=data)

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.SetRcbAttrsReq(ref=ref,
                                                     attrs=attrs))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            results = {
                attr_type: common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA
                for attr_type, _ in attrs}

        elif isinstance(res, mms.WriteResponse):
            if len(res.results) != len(attrs):
                raise Exception('invalid results length')

            results = {}

            for (attr_type, _), mms_data in zip(attrs, res.results):
                if mms_data is None:
                    results[attr_type] = None

                elif mms_data == mms.DataAccessError.OBJECT_ACCESS_DENIED:
                    results[attr_type] = common.ServiceError.ACCESS_VIOLATION

                elif mms_data == mms.DataAccessError.OBJECT_NON_EXISTENT:
                    results[attr_type] = common.ServiceError.INSTANCE_NOT_AVAILABLE  # NOQA

                elif mms_data == mms.DataAccessError.TEMPORARILY_UNAVAILABLE:
                    results[attr_type] = common.ServiceError.INSTANCE_LOCKED_BY_OTHER_CLIENT  # NOQA

                elif mms_data == mms.DataAccessError.TYPE_INCONSISTENT:
                    results[attr_type] = common.ServiceError.TYPE_CONFLICT

                elif mms_data == mms.DataAccessError.OBJECT_VALUE_INVALID:
                    results[attr_type] = common.ServiceError.PARAMETER_VALUE_INCONSISTENT  # NOQA

                else:
                    results[attr_type] = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.SetRcbAttrsRes(results))

        return results

    async def write_data(self,
                         ref: common.DataRef,
                         value: common.Value
                         ) -> common.ServiceError | None:
        """Write data"""
        value_type = self._data_value_types[ref]

        req = mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    encoder.data_ref_to_object_name(ref))],
            data=[encoder.value_to_mms_data(value,  value_type)])

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.WriteDataReq(ref=ref,
                                                   value=value))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            result = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

        elif isinstance(res, mms.WriteResponse):
            if len(res.results) != 1:
                raise Exception('invalid results size')

            if res.results[0] is not None:
                if res.results[0] == mms.DataAccessError.OBJECT_ACCESS_DENIED:
                    result = common.ServiceError.ACCESS_VIOLATION

                elif res.results[0] == mms.DataAccessError.OBJECT_NON_EXISTENT:
                    result = common.ServiceError.INSTANCE_NOT_AVAILABLE

                elif res.results[0] == mms.DataAccessError.TEMPORARILY_UNAVAILABLE:  # NOQA
                    result = common.ServiceError.INSTANCE_LOCKED_BY_OTHER_CLIENT  # NOQA

                elif res.results[0] == mms.DataAccessError.TYPE_INCONSISTENT:
                    result = common.ServiceError.TYPE_CONFLICT

                elif res.results[0] == mms.DataAccessError.OBJECT_VALUE_INVALID:  # NOQA
                    result = common.ServiceError.PARAMETER_VALUE_INCONSISTENT

                else:
                    result = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

            else:
                result = None

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.WriteDataRes(result))

        return result

    async def select(self,
                     ref: common.CommandRef,
                     cmd: common.Command | None
                     ) -> common.CommandError | None:
        """Select command"""
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
                                   names=(ref.name, 'SBO'))))])

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.CommandReq(ref=ref,
                                                 attr='SBO',
                                                 cmd=cmd))

        res = await self._send(req)

        if isinstance(res, mms.Error):
            result = _create_command_error(
                service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                last_appl_error=None)

        elif isinstance(res, mms.ReadResponse):
            if len(res.results) != 1:
                raise Exception('invalid results size')

            if not isinstance(res.results[0], mms.VisibleStringData):
                if res.results[0] == mms.DataAccessError.OBJECT_ACCESS_DENIED:
                    service_error = common.ServiceError.ACCESS_VIOLATION

                elif res.results[0] == mms.DataAccessError.OBJECT_NON_EXISTENT:
                    service_error = common.ServiceError.INSTANCE_NOT_AVAILABLE

                else:
                    service_error = common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

                result = _create_command_error(service_error=service_error,
                                               last_appl_error=None)

            elif res.results[0].value == '':
                result = _create_command_error(
                    service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                    last_appl_error=None)

            else:
                result = None

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.CommandRes(result))

        return result

    async def cancel(self,
                     ref: common.CommandRef,
                     cmd: common.Command
                     ) -> common.CommandError | None:
        """Cancel command"""
        return await self._command_with_last_appl_error(ref=ref,
                                                        cmd=cmd,
                                                        attr='Cancel',
                                                        with_checks=False)

    async def operate(self,
                      ref: common.CommandRef,
                      cmd: common.Command
                      ) -> common.CommandError | None:
        """Operate command"""
        return await self._command_with_last_appl_error(ref=ref,
                                                        cmd=cmd,
                                                        attr='Oper',
                                                        with_checks=True)

    async def _on_unconfirmed(self, conn, unconfirmed):
        self._status_event.set()

        if _is_unconfirmed_report(unconfirmed):
            try:
                await self._process_report(unconfirmed.data)

            except Exception as e:
                self._log.error("error processing report: %s", e, exc_info=e)

        elif _is_unconfirmed_last_appl_error(unconfirmed):
            try:
                self._process_last_appl_error(unconfirmed.data[0])

            except Exception as e:
                self._log.error("error processing last application error: %s",
                                e, exc_info=e)

        elif _is_unconfirmed_termination(unconfirmed):
            names = [i.name for i in unconfirmed.specification]
            data = list(unconfirmed.data)

            if len(names) != len(data):
                self._log.warning("names/data size mismatch")
                return

            data_ref = encoder.data_ref_from_object_name(names[-1])

            try:
                await self._process_termination(
                    ref=common.CommandRef(
                        logical_device=data_ref.logical_device,
                        logical_node=data_ref.logical_node,
                        name=data_ref.names[0]),
                    cmd_mms_data=data[-1],
                    last_appl_error_mms_data=(data[0] if len(data) > 1
                                              else None))

            except Exception as e:
                self._log.error("error processing termination: %s",
                                e, exc_info=e)

        else:
            self._log.info("received unprocessed unconfirmed message")

    async def _process_report(self, mms_data):
        if not self._report_cb:
            self._log.info("report callback not defined - skipping report")
            return

        report_id = encoder.value_from_mms_data(
            mms_data[0], common.BasicValueType.VISIBLE_STRING)

        data_defs = self._report_data_defs.get(report_id)
        if data_defs is None:
            self._log.info("report id not defined - skipping report")
            return

        report = encoder.report_from_mms_data(mms_data, data_defs)

        self._comm_log.log(common.CommLogAction.RECEIVE, report)

        await aio.call(self._report_cb, report)

    def _process_last_appl_error(self, mms_data):
        last_appl_error = encoder.last_appl_error_from_mms_data(mms_data)

        key = last_appl_error.name, last_appl_error.control_number
        if key in self._last_appl_errors:
            self._last_appl_errors[key] = last_appl_error

    async def _process_termination(self, ref, cmd_mms_data,
                                   last_appl_error_mms_data):
        if not self._termination_cb:
            self._log.info("termination callback not defined - "
                           "skipping termination")
            return

        value_type = self._cmd_value_types.get(ref)
        if value_type is None:
            self._log.info("command value type not defined - "
                           "skipping termination")
            return

        cmd = encoder.command_from_mms_data(mms_data=cmd_mms_data,
                                            value_type=value_type,
                                            with_checks=True)

        if last_appl_error_mms_data:
            error = _create_command_error(
                service_error=None,
                last_appl_error=encoder.last_appl_error_from_mms_data(
                    last_appl_error_mms_data))

        else:
            error = None

        termination = common.Termination(ref=ref,
                                         cmd=cmd,
                                         error=error)

        self._comm_log.log(common.CommLogAction.RECEIVE, termination)

        await aio.call(self._termination_cb, termination)

    async def _send(self, req):
        res = await self._conn.send_confirmed(req)
        self._status_event.set()
        return res

    async def _status_loop(self, delay, timeout):
        try:
            self._log.debug("starting status loop")
            while True:
                self._status_event.clear()

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._status_event.wait(), delay)
                    continue

                self._log.debug("sending status request")
                await aio.wait_for(self._send(mms.StatusRequest()), timeout)

        except asyncio.TimeoutError:
            self._log.warning("status timeout")

        except ConnectionError:
            pass

        except Exception as e:
            self._log.error("status loop error: %s", e, exc_info=e)

        finally:
            self._log.debug("stopping status loop")
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
                                       names=(ref.name, attr))))],
            data=[encoder.command_to_mms_data(cmd=cmd,
                                              value_type=value_type,
                                              with_checks=with_checks)])

        name = (f'{req.specification[0].name.domain_id}/'
                f'{req.specification[0].name.item_id}')
        key = name, cmd.control_number

        if key in self._last_appl_errors:
            raise Exception('active control number duplicate')

        self._last_appl_errors[key] = None

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.SEND,
                               logger.CommandReq(ref=ref,
                                                 attr=attr,
                                                 cmd=cmd))

        try:
            res = await self._send(req)

        finally:
            last_appl_error = self._last_appl_errors.pop(key, None)

        if isinstance(res, mms.Error):
            result = _create_command_error(
                service_error=common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,  # NOQA
                last_appl_error=last_appl_error)

        elif isinstance(res, mms.WriteResponse):
            if len(res.results) != 1:
                raise Exception('invalid results size')

            if res.results[0] is not None:
                result = _create_command_error(service_error=None,
                                               last_appl_error=last_appl_error)

            else:
                result = None

        else:
            raise Exception('unsupported response type')

        if self._comm_log.is_enabled:
            self._comm_log.log(common.CommLogAction.RECEIVE,
                               logger.CommandRes(result))

        return result


def _create_command_error(service_error, last_appl_error):
    additional_cause = (last_appl_error.additional_cause
                        if last_appl_error else None)
    test_error = last_appl_error.error if last_appl_error else None

    return common.CommandError(service_error=service_error,
                               additional_cause=additional_cause,
                               test_error=test_error)


def _is_unconfirmed_report(unconfirmed):
    if not isinstance(unconfirmed, mms.InformationReportUnconfirmed):
        return False

    if not isinstance(unconfirmed.specification, mms.ObjectName):
        return False

    return unconfirmed.specification == mms.VmdSpecificObjectName('RPT')


def _is_unconfirmed_last_appl_error(unconfirmed):
    if not isinstance(unconfirmed, mms.InformationReportUnconfirmed):
        return False

    if isinstance(unconfirmed.specification, mms.ObjectName):
        return False

    if len(unconfirmed.specification) != 1:
        return False

    return unconfirmed.specification[0] == mms.NameVariableSpecification(
        mms.VmdSpecificObjectName('LastApplError'))


def _is_unconfirmed_termination(unconfirmed):
    if not isinstance(unconfirmed, mms.InformationReportUnconfirmed):
        return False

    if isinstance(unconfirmed.specification, mms.ObjectName):
        return False

    if not (1 <= len(unconfirmed.specification) <= 2):
        return False

    if any(not isinstance(i, mms.NameVariableSpecification)
           for i in unconfirmed.specification):
        return False

    names = [i.name for i in unconfirmed.specification]

    if len(names) == 1:
        if not isinstance(names[0], mms.DomainSpecificObjectName):
            return False

    elif len(names) == 2:
        if names[0] != mms.VmdSpecificObjectName('LastApplError'):
            return False

        if not isinstance(names[1], mms.DomainSpecificObjectName):
            return False

    else:
        return False

    try:
        data_ref = encoder.data_ref_from_object_name(names[-1])

    except Exception:
        return False

    data_ref_names = list(data_ref.names)

    return (data_ref.fc == 'CO' and
            len(data_ref_names) == 2 and
            data_ref_names[1] == 'Oper')
