from collections.abc import Collection
import asyncio
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
                             data: Collection[common.DataRef]
                             ) -> common.ServiceError | None:
        pass

    async def delete_dataset(self,
                             ref: common.DatasetRef
                             ) -> common.ServiceError | None:
        pass

    async def get_dataset_refs(self) -> Collection[common.DatasetRef] | common.ServiceError:  # NOQA
        pass

    async def get_dataset_data_refs(self,
                                    ref: common.DatasetRef
                                    ) -> Collection[common.DataRef] | common.ServiceError:  # NOQA
        pass

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
