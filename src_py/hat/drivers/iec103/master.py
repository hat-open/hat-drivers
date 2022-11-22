import asyncio
import contextlib
import datetime
import enum
import itertools
import logging
import typing

from hat import aio

from hat.drivers.iec103 import common
from hat.drivers.iec60870 import link
from hat.drivers.iec60870.msgs import iec103


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

        self._encoder = iec103.encoder.Encoder()

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
            iec103.common.AsduType.TIME_TAGGED_MESSAGE: self._process_TIME_TAGGED_MESSAGE,  # NOQA
            iec103.common.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME: self._process_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME,  # NOQA
            iec103.common.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME: self._process_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME,  # NOQA
            iec103.common.AsduType.IDENTIFICATION: self._process_IDENTIFICATION,  # NOQA
            iec103.common.AsduType.TIME_SYNCHRONIZATION: self._process_TIME_SYNCHRONIZATION,  # NOQA
            iec103.common.AsduType.GENERAL_INTERROGATION_TERMINATION: self._process_GENERAL_INTERROGATION_TERMINATION,  # NOQA
            iec103.common.AsduType.GENERIC_DATA: self._process_GENERIC_DATA,  # NOQA
            iec103.common.AsduType.GENERIC_IDENTIFICATION: self._process_GENERIC_IDENTIFICATION,  # NOQA
            iec103.common.AsduType.READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA: self._process_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA,  # NOQA
            iec103.common.AsduType.READY_FOR_TRANSMISSION_OF_A_CHANNEL: self._process_READY_FOR_TRANSMISSION_OF_A_CHANNEL,  # NOQA
            iec103.common.AsduType.READY_FOR_TRANSMISSION_OF_TAGS: self._process_READY_FOR_TRANSMISSION_OF_TAGS,  # NOQA
            iec103.common.AsduType.TRANSMISSION_OF_TAGS: self._process_TRANSMISSION_OF_TAGS,  # NOQA
            iec103.common.AsduType.TRANSMISSION_OF_DISTURBANCE_VALUES: self._process_TRANSMISSION_OF_DISTURBANCE_VALUES,  # NOQA
            iec103.common.AsduType.END_OF_TRANSMISSION: self._process_END_OF_TRANSMISSION}  # NOQA
        self._process_multiple_elements_fns = {
            iec103.common.AsduType.MEASURANDS_1: self._process_MEASURANDS_1,  # NOQA
            iec103.common.AsduType.MEASURANDS_2: self._process_MEASURANDS_2,  # NOQA
            iec103.common.AsduType.LIST_OF_RECORDED_DISTURBANCES: self._process_LIST_OF_RECORDED_DISTURBANCES}  # NOQA

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
            _FunctionType.GLOBAL_FUNCTION_TYPE.value,
            _InformationNumber.GENERAL_INTERROGATION_OR_TIME_SYNCHRONIZATION.value)  # NOQA
        asdu = iec103.common.ASDU(
            type=iec103.common.AsduType.TIME_SYNCHRONIZATION,
            cause=iec103.common.Cause.TIME_SYNCHRONIZATION,
            address=asdu_address,
            ios=[iec103.common.IO(
                address=io_address,
                elements=[iec103.common.IoElement_TIME_SYNCHRONIZATION(
                    time=time)])])
        data = self._encoder.encode_asdu(asdu)

        await self._conn.send(data)

    async def interrogate(self, asdu_address: common.AsduAddress):
        async with self._interrogate_lock:
            if not self.is_open:
                raise ConnectionError()

            scan_number = next(self._next_req_ids)
            asdu = iec103.common.ASDU(
                type=iec103.common.AsduType.GENERAL_INTERROGATION,
                cause=iec103.common.Cause.GENERAL_INTERROGATION,
                address=asdu_address,
                ios=[iec103.common.IO(
                    address=iec103.common.IoAddress(
                        function_type=_FunctionType.GLOBAL_FUNCTION_TYPE.value,  # NOQA
                        information_number=_InformationNumber.GENERAL_INTERROGATION_OR_TIME_SYNCHRONIZATION.value),  # NOQA
                    elements=[iec103.common.IoElement_GENERAL_INTERROGATION(  # NOQA
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
            asdu = iec103.common.ASDU(
                type=iec103.common.AsduType.GENERAL_COMMAND,
                cause=iec103.common.Cause.GENERAL_COMMAND,
                address=asdu_address,
                ios=[iec103.common.IO(
                    address=io_address,
                    elements=[iec103.common.IoElement_GENERAL_COMMAND(
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
            asdu = iec103.common.ASDU(
                type=iec103.common.AsduType.GENERIC_COMMAND,
                cause=iec103.common.Cause.GENERAL_INTERROGATION,
                address=asdu_address,
                ios=[iec103.common.IO(
                    address=iec103.common.IoAddress(
                        function_type=_FunctionType.GENERIC_FUNCTION_TYPE.value,  # NOQA
                        information_number=_InformationNumber.GENERAL_INTERROGATION_OF_GENERIC_DATA.value),  # NOQA
                    elements=[iec103.common.IoElement_GENERIC_COMMAND(
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
        if cause == iec103.common.Cause.GENERAL_COMMAND:
            if element.value.supplementary == self._send_command_req_id:
                _try_set_result(self._send_command_future, True)

        elif cause == iec103.common.Cause.GENERAL_COMMAND_NACK:
            if element.value.supplementary == self._send_command_req_id:
                _try_set_result(self._send_command_future, False)

        else:
            await _try_aio_call(self._data_cb, common.Data(
                asdu_address=asdu_address,
                io_address=io_address,
                cause=_try_decode_cause(cause, common.DataCause),
                value=element.value))

    async def _process_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME(self, cause, asdu_address, io_address, element):  # NOQA
        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_cause(cause, common.DataCause),
            value=element.value))

    async def _process_MEASURANDS_1(self, cause, asdu_address, io_address, elements):  # NOQA
        value = common.MeasurandValues(values={})
        for i, element in enumerate(elements):
            measurand_type = common.MeasurandType((
                iec103.common.AsduType.MEASURANDS_1.value, i))
            value.values[measurand_type] = element.value

        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_cause(cause, common.DataCause),
            value=value))

    async def _process_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME(self, cause, asdu_address, io_address, element):  # NOQA
        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_cause(cause, common.DataCause),
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
        value = common.MeasurandValues(values={})
        for i, element in enumerate(elements):
            measurand_type = common.MeasurandType((
                iec103.common.AsduType.MEASURANDS_2.value, i))
            value.values[measurand_type] = element.value

        await _try_aio_call(self._data_cb, common.Data(
            asdu_address=asdu_address,
            io_address=io_address,
            cause=_try_decode_cause(cause, common.DataCause),
            value=value))

    async def _process_GENERIC_DATA(self, cause, asdu_address, io_address, element):  # NOQA
        if cause == iec103.common.Cause.TERMINATION_OF_GENERAL_INTERROGATION:  # NOQA
            if element.return_identifier == self._interrogate_generic_req_id:
                _try_set_result(self._interrogate_generic_future, None)

        else:
            data_cause = _try_decode_cause(cause, common.GenericDataCause)
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


class _FunctionType(enum.Enum):
    DISTANCE_PROTECTION = 128
    OVERCURRENT_PROTECTION = 160
    TRANSFORMER_DIFFERENTIAL_PROTECTION = 176
    LINE_DIFFERENTIAL_PROTECTION = 192
    GENERIC_FUNCTION_TYPE = 254
    GLOBAL_FUNCTION_TYPE = 255


class _InformationNumber(enum.Enum):
    GENERAL_INTERROGATION_OR_TIME_SYNCHRONIZATION = 0
    RESET_FRAME_COUNT_BIT = 2
    RESET_COMMUNICATION_UNIT = 3
    START_RESTART = 4
    POWER_ON = 5
    AUTO_RECLOSER = 16
    TELEPROTECTION = 17
    PROTECTION = 18
    LED_RESET = 19
    MONITOR_DIRECTION_BLOCKED = 20
    TEST_MODE = 21
    LOCAL_PARAMETER_SETTING = 22
    CHARACTERISTIC_1 = 23
    CHARACTERISTIC_2 = 24
    CHARACTERISTIC_3 = 25
    CHARACTERISTIC_4 = 26
    AUXILIARY_INPUT_1 = 27
    AUXILIARY_INPUT_2 = 28
    AUXILIARY_INPUT_3 = 29
    AUXILIARY_INPUT_4 = 30
    MEASURAND_SUPERVISION_I = 32
    MEASURAND_SUPERVISION_V = 33
    PHASE_SEQUENCE_SUPERVISION = 35
    TRIP_CIRCUIT_SUPERVISION = 36
    I_BACKUP_OPERATION = 37
    VT_FUSE_FAILURE = 38
    TELEPROTECTION_DISTURBED = 39
    GROUP_WARNING = 46
    GROUP_ALARM = 47
    EARTH_FAULT_L1 = 48
    EARTH_FAULT_L2 = 49
    EARTH_FAULT_L3 = 50
    EARTH_FAULT_FORWARD = 51
    EARTH_FAULT_REVERSE = 52
    START_PICKUP_L1 = 64
    START_PICKUP_L2 = 65
    START_PICKUP_L3 = 66
    START_PICKUP_N = 67
    GENERAL_TRIP = 68
    TRIP_L1 = 69
    TRIP_L2 = 70
    TRIP_L3 = 71
    TRIP_I = 72
    FAULT_LOCATION = 73
    FAULT_FORWARD = 74
    FAULT_REVERSE = 75
    TELEPROTECTION_SIGNAL_TRANSMITTED = 76
    TELEPROTECTION_SIGNAL_RECEIVED = 77
    ZONE_1 = 78
    ZONE_2 = 79
    ZONE_3 = 80
    ZONE_4 = 81
    ZONE_5 = 82
    ZONE_6 = 83
    GENERAL_START_PICKUP = 84
    BREAKER_FAILURE = 85
    TRIP_MEASURING_SYSTEM_L1 = 86
    TRIP_MEASURING_SYSTEM_L2 = 87
    TRIP_MEASURING_SYSTEM_L3 = 88
    TRIP_MEASURING_SYSTEM_E = 89
    TRIP_I_1 = 90
    TRIP_I_2 = 91
    TRIP_IN_1 = 92
    TRIP_IN_2 = 93
    CB_ON_BY_AR = 128
    CB_ON_BY_LONG_TIME_AR = 129
    AR_BLOCKED = 130
    MEASURAND_I = 144
    MEASURAND_I_V = 145
    MEASURAND_I_V_P_Q = 146
    MEASURAND_IN_VEN = 147
    MEASURAND_IL123_VL123_P_Q_F = 148
    READ_HEADINGS_OF_ALL_DEFINED_GROUPS = 240
    READ_VALUES_OR_ATTRIBUTES_OF_ALL_ENTRIES_OF_ONE_GROUP = 241
    READ_DIRECTORY_OF_SINGLE_ENTRY = 243
    READ_VALUE_OR_ATTRIBUTE_OF_A_SINGLE_ENTRY = 244
    GENERAL_INTERROGATION_OF_GENERIC_DATA = 245
    WRITE_ENTRY = 248
    WRITE_ENTRY_WITH_CONFIRMATION = 249
    WRITE_ENTRY_WITH_EXECUTION = 250
    WRITE_ENTRY_ABORT = 251


def _try_decode_cause(cause, enum_cls):
    value = cause.value if isinstance(cause, enum.Enum) else cause
    with contextlib.suppress(ValueError):
        return enum_cls(value)
    return value


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
