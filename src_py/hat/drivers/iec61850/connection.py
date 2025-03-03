from collections.abc import Collection
import typing

from hat import aio

from hat.drivers import tcp
from hat.drivers.iec61850 import common


ReportCb: typing.TypeAlias = aio.AsyncCallable[[common.Report], None]

TerminationCb: typing.TypeAlias = aio.AsyncCallable[[common.Termination], None]


async def connect(addr: tcp.Address,
                  reports: Collection[common.ReportDef] = [],
                  report_cb: ReportCb | None = None,
                  termination_cb: TerminationCb | None = None,
                  status_delay: float | None = None,
                  status_timeout: float = 30,
                  **kwargs
                  ) -> 'Connection':
    """Connect to IEC61850 server

    Additional arguments are passed directly to `hat.drivers.mms.connect`
    (`request_cb` and `unconfirmed_cb` are set by this coroutine).

    """


class Connection(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def create_dataset(self,
                             ref: common.DatasetRef,
                             data: Collection[common.DataRef]):
        pass

    async def delete_dataset(self, ref: common.DatasetRef):
        pass

    async def get_dataset_data_refs(self,
                                    ref: common.DatasetRef
                                    ) -> Collection[common.DataRef]:
        pass

    async def get_rcb(self, ref: common.RcbRef) -> common.Rcb:
        pass

    async def set_rcb(self, ref: common.RcbRef, rcb: common.Rcb):
        pass

    async def select(self,
                     ref: common.CommandRef,
                     cmd: common.Command | None
                     ) -> common.AdditionalCause | None:
        pass

    async def cancel(self,
                     ref: common.CommandRef,
                     cmd: common.Command
                     ) -> common.AdditionalCause | None:
        pass

    async def operate(self,
                      ref: common.CommandRef,
                      cmd: common.Command
                      ) -> common.AdditionalCause | None:
        pass
