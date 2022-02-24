import asyncio
import contextlib
import datetime
import itertools
import logging
import typing

from hat import aio

from hat.drivers.iec60870 import link
from hat.drivers.iec60870 import app
from hat.drivers.iec60870.iec103 import common


mlog: logging.Logger = logging.getLogger(__name__)


DataCb = aio.AsyncCallable[[common.Data], None]
GenericDataCb = aio.AsyncCallable[[common.GenericData], None]


class MasterConnection(aio.Resource):

    def __init__(self,
                 conn: link.Connection,
                 data_cb: typing.Optional[DataCb] = None,
                 generic_data_cb: typing.Optional[GenericDataCb] = None):
        self._conn = conn
        self._data_cb = data_cb
        self._generic_data_cb = generic_data_cb

        self._encoder = app.iec103.encoder.Encoder()

        self._interrogate_lock = asyncio.Lock()
        self._interrogate_req_id = None
        self._interrogate_future = None

        self._send_command_lock = asyncio.Lock()
        self._send_command_req_id = None
        self._send_command_future = None

        self._interrogate_generic_lock = asyncio.Lock()
        self._interrogate_generic_req_id = None
        self._interrogate_generic_future = None

        self._next_req_ids = (i % 0x100 for i in itertools.count(0))

        self._process_single_element_fns = {
            app.iec103.common.AsduType.TIME_TAGGED_MESSAGE: self._process_TIME_TAGGED_MESSAGE,  # NOQA
            app.iec103.common.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME: self._process_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME,  # NOQA
            app.iec103.common.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME: self._process_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME,  # NOQA
            app.iec103.common.AsduType.IDENTIFICATION: self._process_IDENTIFICATION,  # NOQA
            app.iec103.common.AsduType.TIME_SYNCHRONIZATION: self._process_TIME_SYNCHRONIZATION,  # NOQA
            app.iec103.common.AsduType.GENERAL_INTERROGATION_TERMINATION: self._process_GENERAL_INTERROGATION_TERMINATION,  # NOQA
            app.iec103.common.AsduType.GENERIC_DATA: self._process_GENERIC_DATA,  # NOQA
            app.iec103.common.AsduType.GENERIC_IDENTIFICATION: self._process_GENERIC_IDENTIFICATION,  # NOQA
            app.iec103.common.AsduType.READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA: self._process_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA,  # NOQA
            app.iec103.common.AsduType.READY_FOR_TRANSMISSION_OF_A_CHANNEL: self._process_READY_FOR_TRANSMISSION_OF_A_CHANNEL,  # NOQA
            app.iec103.common.AsduType.READY_FOR_TRANSMISSION_OF_TAGS: self._process_READY_FOR_TRANSMISSION_OF_TAGS,  # NOQA
            app.iec103.common.AsduType.TRANSMISSION_OF_TAGS: self._process_TRANSMISSION_OF_TAGS,  # NOQA
            app.iec103.common.AsduType.TRANSMISSION_OF_DISTURBANCE_VALUES: self._process_TRANSMISSION_OF_DISTURBANCE_VALUES,  # NOQA
            app.iec103.common.AsduType.END_OF_TRANSMISSION: self._process_END_OF_TRANSMISSION}  # NOQA
        self._process_multiple_elements_fns = {
            app.iec103.common.AsduType.MEASURANDS_1: self._process_MEASURANDS_1,  # NOQA
            app.iec103.common.AsduType.MEASURANDS_2: self._process_MEASURANDS_2,  # NOQA
            app.iec103.common.AsduType.LIST_OF_RECORDED_DISTURBANCES: self._process_LIST_OF_RECORDED_DISTURBANCES}  # NOQA

        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self):
        return self._conn.async_group

    async def time_sync(self,
                        time: typing.Optional[common.Time] = None,
                        asdu_address: common.AsduAddress = 0xFF):
        if not self.is_open:
            raise ConnectionError()

        time = time or common.time_from_datetime(datetime.datetime.now())
        io_address = common.IoAddress(
            common.FunctionType.GLOBAL_FUNCTION_TYPE,
            common.InformationNumber.GENERAL_INTERROGATION_OR_TIME_SYNCHRONIZATION)  # NOQA
        asdu = app.iec103.common.ASDU(
            type=app.iec103.common.AsduType.TIME_SYNCHRONIZATION,
            cause=app.iec103.common.Cause.TIME_SYNCHRONIZATION,
            address=asdu_address,
            ios=[app.iec103.common.IO(
                address=io_address,
                elements=[app.iec103.common.IoElement_TIME_SYNCHRONIZATION(
                    time=time)])])
        data = self._encoder.encode_asdu(asdu)

        await self._conn.send(data)

    async def interrogate(self, asdu_address: common.AsduAddress):
        async with self._interrogate_lock:
            if not self.is_open:
                raise ConnectionError()

            scan_number = next(self._next_req_ids)
            asdu = app.iec103.common.ASDU(
                type=app.iec103.common.AsduType.GENERAL_INTERROGATION,
                cause=app.iec103.common.Cause.GENERAL_INTERROGATION,
                address=asdu_address,
                ios=[app.iec103.common.IO(
                    address=app.iec103.common.IoAddress(
                        function_type=app.iec103.common.FunctionType.GLOBAL_FUNCTION_TYPE,  # NOQA
                        information_number=app.iec103.common.InformationNumber.GENERAL_INTERROGATION_OR_TIME_SYNCHRONIZATION),  # NOQA
                    elements=[app.iec103.common.IoElement_GENERAL_INTERROGATION(  # NOQA
                        scan_number=scan_number)])])
            data = self._encoder.encode_asdu(asdu)

            try:
                self._interrogate_req_id = scan_number
                self._interrogate_future = asyncio.Future()
                await self._conn.send(data)
                await self._interrogate_future

            finally:
                self._interrogate_req_id = None
                self._interrogate_future = None

    async def send_command(self,
                           asdu_address: common.AsduAddress,
                           io_address: common.IoAddress,
                           value: common.DoubleValue
                           ) -> bool:
        async with self._send_command_lock:
            if not self.is_open:
                raise ConnectionError()

            return_identifier = next(self._next_req_ids)
            asdu = app.iec103.common.ASDU(
                type=app.iec103.common.AsduType.GENERAL_COMMAND,
                cause=app.iec103.common.Cause.GENERAL_COMMAND,
                address=asdu_address,
                ios=[app.iec103.common.IO(
                    address=io_address,
                    elements=[app.iec103.common.IoElement_GENERAL_COMMAND(
                        value=value,
                        return_identifier=return_identifier)])])
            data = self._encoder.encode_asdu(asdu)

            try:
                self._send_command_req_id = return_identifier
                self._send_command_future = asyncio.Future()
                await self._conn.send(data)
                return await self._send_command_future

            finally:
                self._send_command_req_id = None
                self._send_command_future = None

    async def interrogate_generic(self, asdu_address: common.AsduAddress):
        async with self._interrogate_generic_lock:
            if not self.is_open:
                raise ConnectionError()

            return_identifier = next(self._next_req_ids)
            asdu = app.iec103.common.ASDU(
                type=app.iec103.common.AsduType.GENERIC_COMMAND,
                cause=app.iec103.common.Cause.GENERAL_INTERROGATION,
                address=asdu_address,
                ios=[app.iec103.common.IO(
                    address=app.iec103.common.IoAddress(
                        function_type=app.iec103.common.FunctionType.GENERIC_FUNCTION_TYPE,  # NOQA
                        information_number=app.iec103.common.InformationNumber.GENERAL_INTERROGATION_OF_GENERIC_DATA),  # NOQA
                    elements=[app.iec103.common.IoElement_GENERIC_COMMAND(
                        return_identifier=return_identifier,
                        data=[])])])
            data = self._encoder.encode_asdu(asdu)

            try:
                self._interrogate_generic_req_id = return_identifier
                self._interrogate_generic_future = asyncio.Future()
                await self._conn.send(data)
                await self._interrogate_generic_future

            finally:
                self._interrogate_generic_req_id = None
                self._interrogate_generic_future = None

    async def _receive_loop(self):
        try:
            while True:
                data = await self._conn.receive()
                asdu = self._encoder.decode_asdu(data)

                for io in asdu.ios:
                    if asdu.type in self._process_single_element_fns:
                        fn = self._process_single_element_fns[asdu.type]
                        for element in io.elements:
                            await fn(asdu.cause, asdu.address, io.address,
                                     element)

                    elif asdu.type in self._process_multiple_elements_fns:
                        fn = self._process_multiple_elements_fns[asdu.type]
                        await fn(asdu.cause, asdu.address, io.address,
                                 io.elements)

                    else:
                        raise ValueError('unsupported asdu type')

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()
            _try_set_exception(self._interrogate_future, ConnectionError())
            _try_set_exception(self._send_command_future, ConnectionError())
            _try_set_exception(self._interrogate_generic_future,
                               ConnectionError())

    async def _process_TIME_TAGGED_MESSAGE(self, cause, asdu_address, io_address, element):  # NOQA
        if cause == app.iec103.common.Cause.GENERAL_COMMAND:
            if element.value.supplementary == self._send_command_req_id:
                _try_set_result(self._send_command_future, True)

        elif cause == app.iec103.common.Cause.GENERAL_COMMAND_NACK:
            if element.value.supplementary == self._send_command_req_id:
                _try_set_result(self._send_command_future, False)

        else:
            await _try_aio_call(self._data_cb, common.Data(
                asdu_address=asdu_address,
                io_address=io_address,
                cause=_try_decode_enum(cause.value, common.DataCause),
                value=element.value))

    async def _process_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME(self, cause, asdu_address, io_address, element):  # NOQA
        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_enum(cause.value, common.DataCause),
            value=element.value))

    async def _process_MEASURANDS_1(self, cause, asdu_address, io_address, elements):  # NOQA
        value = common.MeasurandValues()
        for i, element in enumerate(elements):
            measurand_type = common.MeasurandType((
                app.iec103.common.AsduType.MEASURANDS_1.value, i))
            value.values[measurand_type] = element.value

        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_enum(cause.value, common.DataCause),
            value=value))

    async def _process_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME(self, cause, asdu_address, io_address, element):  # NOQA
        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_enum(cause.value, common.DataCause),
            value=element.value))

    async def _process_IDENTIFICATION(self, cause, asdu_address, io_address, element):  # NOQA
        mlog.debug("received device identification "
                   "(compatibility: %s; value: %s; software: %s)",
                   element.compatibility,
                   bytes(element.value),
                   bytes(element.software))

    async def _process_TIME_SYNCHRONIZATION(self, cause, asdu_address, io_address, element):  # NOQA
        mlog.info("received time sync response")

    async def _process_GENERAL_INTERROGATION_TERMINATION(self, cause, asdu_address, io_address, element):  # NOQA
        if element.scan_number != self._interrogate_req_id:
            return
        _try_set_result(self._interrogate_future, None)

    async def _process_MEASURANDS_2(self, cause, asdu_address, io_address, elements):  # NOQA
        value = common.MeasurandValues()
        for i, element in enumerate(elements):
            measurand_type = common.MeasurandType((
                app.iec103.common.AsduType.MEASURANDS_2.value, i))
            value.values[measurand_type] = element.value

        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_enum(cause.value, common.DataCause),
            value=value))

    async def _process_GENERIC_DATA(self, cause, asdu_address, io_address, element):  # NOQA
        if cause == app.iec103.common.Cause.TERMINATION_OF_GENERAL_INTERROGATION:  # NOQA
            if element.return_identifier == self._interrogate_generic_req_id:
                _try_set_result(self._interrogate_generic_future, None)

        else:
            data_cause = _try_decode_enum(cause.value, common.GenericDataCause)
            for identification, data in element.data:
                await _try_aio_call(self._generic_data_cb, common.GenericData(
                    asdu_address=asdu_address,
                    io_address=io_address,
                    cause=data_cause,
                    identification=identification,
                    description=data.description,
                    value=data.value))

    async def _process_GENERIC_IDENTIFICATION(self, cause, asdu_address, io_address, element):  # NOQA
        pass

    async def _process_LIST_OF_RECORDED_DISTURBANCES(self, cause, asdu_address, io_address, elements):  # NOQA
        pass

    async def _process_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA(self, cause, asdu_address, io_address, element):  # NOQA
        pass

    async def _process_READY_FOR_TRANSMISSION_OF_A_CHANNEL(self, cause, asdu_address, io_address, element):  # NOQA
        pass

    async def _process_READY_FOR_TRANSMISSION_OF_TAGS(self, cause, asdu_address, io_address, element):  # NOQA
        pass

    async def _process_TRANSMISSION_OF_TAGS(self, cause, asdu_address, io_address, element):  # NOQA
        pass

    async def _process_TRANSMISSION_OF_DISTURBANCE_VALUES(self, cause, asdu_address, io_address, element):  # NOQA
        pass

    async def _process_END_OF_TRANSMISSION(self, cause, asdu_address, io_address, element):  # NOQA
        pass


def _try_decode_enum(value, enum_cls, default=None):
    with contextlib.suppress(ValueError):
        return enum_cls(value)
    return default


def _try_set_exception(future, exc):
    if not future or future.done():
        return
    future.set_exception(exc)


def _try_set_result(future, result):
    if not future or future.done():
        return
    future.set_result(result)


async def _try_aio_call(cb, *args):
    if not cb:
        return
    return await aio.call(cb, *args)
