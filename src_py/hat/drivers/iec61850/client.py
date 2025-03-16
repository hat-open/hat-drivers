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

        if isinstance(res, mms.DefineNamedVariableListResponse):
            return

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

        raise Exception('unsupported response type')

    async def delete_dataset(self,
                             ref: common.DatasetRef
                             ) -> common.ServiceError | None:
        req = mms.DeleteNamedVariableListRequest(
            [_dataset_ref_to_object_name(ref)])

        res = await self._send(req)

        if isinstance(res, mms.DeleteNamedVariableListResponse):
            if res.matched == 0 and res.deleted == 0:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res.matched == res.deleted:
                return

            return common.ServiceError.FAILED_DUE_TO_SERVER_CONTRAINT

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res == mms.AccessError.OBJECT_ACCESS_DENIED:
                return common.ServiceError.ACCESS_VIOLATION

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        raise Exception('unsupported response type')

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

        if isinstance(res, mms.GetNamedVariableListAttributesResponse):
            refs = collections.deque()

            for i in res.specification:
                if not isinstance(i, mms.NameVariableSpecification):
                    raise Exception('unsupported specification type')

                refs.append(_data_ref_from_object_name(i.name))

            return ref

        if isinstance(res, mms.Error):
            if res == mms.AccessError.OBJECT_NON_EXISTENT:
                return common.ServiceError.INSTANCE_NOT_AVAILABLE

            if res == mms.AccessError.OBJECT_ACCESS_DENIED:
                return common.ServiceError.ACCESS_VIOLATION

            if res == mms.ServiceError.PDU_SIZE:
                return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

            return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT

        raise Exception('unsupported response type')

    async def get_rcb(self,
                      ref: common.RcbRef
                      ) -> common.Rcb | common.ServiceError:
        pass

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

            if not isinstance(res, mms.GetNameListResponse):
                # TODO not defined by standard
                return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

            identifiers.extend(res.identifiers)

            if not res.more_follows:
                break

            if not res.identifiers:
                # TODO not defined by standard
                return common.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT  # NOQA

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
