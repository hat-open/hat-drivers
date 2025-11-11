from collections.abc import Collection
import collections
import logging
import typing

from hat import util

from hat.drivers import acse
from hat.drivers.iec61850 import common
from hat.drivers.iec61850 import encoder


class CreateDatasetReq(typing.NamedTuple):
    ref: common.DatasetRef
    data: Collection[common.DataRef]


class CreateDatasetRes(typing.NamedTuple):
    result: common.ServiceError | None


class DeleteDatasetReq(typing.NamedTuple):
    ref: common.DatasetRef


class DeleteDatasetRes(typing.NamedTuple):
    result: common.ServiceError | None


class GetPersistedDatasetRefsReq(typing.NamedTuple):
    logical_device: str


class GetPersistedDatasetRefsRes(typing.NamedTuple):
    result: Collection[common.PersistedDatasetRef] | common.ServiceError


class GetDatasetDataRefsReq(typing.NamedTuple):
    ref: common.DatasetRef


class GetDatasetDataRefsRes(typing.NamedTuple):
    result: Collection[common.DataRef] | common.ServiceError


class GetRcbAttrsReq(typing.NamedTuple):
    ref: common.RcbRef
    attr_types: Collection[common.RcbAttrType]


class GetRcbAttrsRes(typing.NamedTuple):
    results: dict[common.RcbAttrType,
                  common.RcbAttrValue | common.ServiceError]


class SetRcbAttrsReq(typing.NamedTuple):
    ref: common.RcbRef
    attrs: Collection[tuple[common.RcbAttrType, common.RcbAttrValue]]


class SetRcbAttrsRes(typing.NamedTuple):
    results: dict[common.RcbAttrType, common.ServiceError | None]


class WriteDataReq(typing.NamedTuple):
    ref: common.DataRef
    value: common.Value


class WriteDataRes(typing.NamedTuple):
    result: common.ServiceError | None


class CommandReq(typing.NamedTuple):
    ref: common.CommandRef
    attr: str
    cmd: common.Command | None


class CommandRes(typing.NamedTuple):
    result: common.CommandError | None


ReportMsg: typing.TypeAlias = common.Report

TerminationMsg: typing.TypeAlias = common.Termination

Msg: typing.TypeAlias = (CreateDatasetReq |
                         CreateDatasetRes |
                         DeleteDatasetReq |
                         DeleteDatasetRes |
                         GetPersistedDatasetRefsReq |
                         GetPersistedDatasetRefsRes |
                         GetDatasetDataRefsReq |
                         GetDatasetDataRefsRes |
                         GetRcbAttrsReq |
                         GetRcbAttrsRes |
                         SetRcbAttrsReq |
                         SetRcbAttrsRes |
                         WriteDataReq |
                         WriteDataRes |
                         CommandReq |
                         CommandRes |
                         ReportMsg |
                         TerminationMsg)


def create_logger(logger: logging.Logger,
                  name: str | None,
                  info: acse.ConnectionInfo | None
                  ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec61850Client',
                      'name': name}}

    if info is not None:
        extra['meta']['local_addr'] = {'host': info.local_addr.host,
                                       'port': info.local_addr.port}
        extra['meta']['remote_addr'] = {'host': info.remote_addr.host,
                                        'port': info.remote_addr.port}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 name: str | None,
                 info: acse.ConnectionInfo | None):
        extra = {'meta': {'type': 'Iec61850Client',
                          'communication': True,
                          'name': name}}

        if info is not None:
            extra['meta']['local_addr'] = {'host': info.local_addr.host,
                                           'port': info.local_addr.port}
            extra['meta']['remote_addr'] = {'host': info.remote_addr.host,
                                            'port': info.remote_addr.port}

        self._log = logging.LoggerAdapter(logger, extra)

    @property
    def is_enabled(self) -> bool:
        return self._log.isEnabledFor(logging.DEBUG)

    def log(self,
            action: common.CommLogAction,
            msg: Msg | None = None):
        if not self.is_enabled:
            return

        if msg is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_msg(msg),
                            stacklevel=2)


def _format_msg(msg):
    segments = collections.deque()

    if isinstance(msg, CreateDatasetReq):
        segments.append('CreateDatasetReq')
        segments.append(f"ref={encoder.dataset_ref_to_str(msg.ref)}")

        data = [encoder.data_ref_to_str(i) for i in msg.data]
        segments.append(f"data={_format_segments(data)}")

    elif isinstance(msg, CreateDatasetRes):
        segments.append('CreateDatasetRes')

        if msg.result is not None:
            segments.append(msg.result.name)

    elif isinstance(msg, DeleteDatasetReq):
        segments.append('DeleteDatasetReq')
        segments.append(encoder.dataset_ref_to_str(msg.ref))

    elif isinstance(msg, DeleteDatasetRes):
        segments.append('DeleteDatasetRes')

        if msg.result is not None:
            segments.append(msg.result.name)

    elif isinstance(msg, GetPersistedDatasetRefsReq):
        segments.append('GetPersistedDatasetRefsReq')
        segments.append(msg.logical_device)

    elif isinstance(msg, GetPersistedDatasetRefsRes):
        segments.append('GetPersistedDatasetRefsRes')

        if isinstance(msg.result, common.ServiceError):
            segments.append(msg.result.name)

        else:
            for ref in msg.result:
                segments.append(encoder.dataset_ref_to_str(ref))

    elif isinstance(msg, GetDatasetDataRefsReq):
        segments.append('GetDatasetDataRefsReq')
        segments.append(encoder.dataset_ref_to_str(msg.ref))

    elif isinstance(msg, GetDatasetDataRefsRes):
        segments.append('GetDatasetDataRefsRes')

        if isinstance(msg.result, common.ServiceError):
            segments.append(msg.result.name)

        else:
            for ref in msg.result:
                segments.append(encoder.data_ref_to_str(ref))

    elif isinstance(msg, GetRcbAttrsReq):
        segments.append('GetRcbAttrsReq')
        segments.append(f"ref={_format_rcb_ref(msg.ref)}")

        attrs = [i.name for i in msg.attr_types]
        segments.append(f"attrs={_format_segments(attrs)}")

    elif isinstance(msg, GetRcbAttrsRes):
        segments.append('GetRcbAttrsRes')

        for k, v in msg.results.items():
            subsegments = collections.deque()
            subsegments.append(k.name)

            if isinstance(v, common.ServiceError):
                subsegments.append(v.name)

            else:
                subsegments.append(_format_rcb_attr_value(v))

            segments.append(_format_segments(subsegments))

    elif isinstance(msg, SetRcbAttrsReq):
        segments.append('SetRcbAttrsReq')
        segments.append(f"ref={_format_rcb_ref(msg.ref)}")

        attrs = [f"({k.name}, {_format_rcb_attr_value(v)})"
                 for k, v in msg.attrs]
        segments.append(f"attrs={_format_segments(attrs)}")

    elif isinstance(msg, SetRcbAttrsRes):
        segments.append('SetRcbAttrsRes')

        for k, v in msg.results.items():
            subsegments = collections.deque()
            subsegments.append(k.name)

            if isinstance(v, common.ServiceError):
                subsegments.append(v.name)

            segments.append(_format_segments(subsegments))

    elif isinstance(msg, WriteDataReq):
        segments.append('WriteDataReq')
        segments.append(f"ref={encoder.data_ref_to_str(msg.ref)}")
        segments.append(f"value={_format_value(msg.value)}")

    elif isinstance(msg, WriteDataRes):
        segments.append('WriteDataRes')

        if msg.result is not None:
            segments.append(msg.result.name)

    elif isinstance(msg, CommandReq):
        segments.append('CommandReq')

        data_ref = common.DataRef(logical_device=msg.ref.logical_device,
                                  logical_node=msg.ref.logical_node,
                                  fc='CO',
                                  names=(msg.ref.name, msg.attr))
        segments.append(f"ref={encoder.data_ref_to_str(data_ref)}")

        if msg.cmd is not None:
            segments.append(f"cmd={_format_command(msg.cmd)}")

    elif isinstance(msg, CommandRes):
        segments.append('CommandRes')

        if msg.result is not None:
            segments.append(_format_command_error(msg.result))

    elif isinstance(msg, ReportMsg):
        segments.append('ReportMsg')
        segments.append(f"report_id={msg.report_id}")

        if msg.sequence_number is not None:
            segments.append(f"sequence_number={msg.sequence_number}")

        if msg.subsequence_number is not None:
            segments.append(f"subsequence_number={msg.subsequence_number}")

        if msg.more_segments_follow:
            segments.append('more_segments_follow')

        if msg.dataset is not None:
            segments.append(
                f"dataset={encoder.dataset_ref_to_str(msg.dataset)}")

        if msg.buffer_overflow:
            segments.append('buffer_overflow')

        if msg.conf_revision is not None:
            segments.append(f"conf_revision={msg.conf_revision}")

        if msg.entry_time is not None:
            segments.append(f"entry_time={msg.entry_time.isoformat()}")

        if msg.entry_id is not None:
            segments.append(f"entry_id=({msg.entry_id.hex(' ')})")

        data = [_format_report_data(i) for i in msg.data]
        segments.append(f"data={_format_segments(data)}")

    elif isinstance(msg, TerminationMsg):
        segments.append('TerminationMsg')

        data_ref = common.DataRef(logical_device=msg.ref.logical_device,
                                  logical_node=msg.ref.logical_node,
                                  fc='CO',
                                  names=(msg.ref.name, ))
        segments.append(f"ref={encoder.data_ref_to_str(data_ref)}")

        segments.append(f"cmd={_format_command(msg.cmd)}")

        if msg.error is not None:
            segments.append(f"error={_format_command_error(msg.error)}")

    else:
        raise TypeError('unsupported message type')

    return _format_segments(segments)


def _format_rcb_ref(ref):
    return encoder.data_ref_to_str(
        common.DataRef(logical_device=ref.logical_device,
                       logical_node=ref.logical_node,
                       fc=ref.type.value,
                       names=(ref.name, )))


def _format_rcb_attr_value(value):
    if isinstance(value, common.DatasetRef):
        return encoder.dataset_ref_to_str(value)

    if isinstance(value, set):
        return _format_segments([i.name for i in value])

    if isinstance(value, util.Bytes):
        return f"({value.hex(' ')})"

    if isinstance(value, common.EntryTime):
        return value.isoformat()

    return str(value)


def _format_value(value):
    segments = collections.deque()

    if isinstance(value, (bool, int, float, str)):
        segments.append(str(value))

    elif isinstance(value, util.Bytes):
        segments.append(f"({value.hex(' ')})")

    elif isinstance(value, common.Quality):
        segments.append(f"validity={value.validity.name}")

        details = [i.name for i in value.details]
        segments.append(f"details={_format_segments(details)}")

        segments.append(f"source={value.source.name}")

        if value.test:
            segments.append('test')

        if value.operator_blocked:
            segments.append('blocked')

    elif isinstance(value, common.Timestamp):
        segments.append(_format_timestamp(value))

    elif isinstance(value, (common.DoublePoint,
                            common.Direction,
                            common.Severity,
                            common.BinaryControl)):
        segments.append(value.name)

    elif isinstance(value, common.Analogue):
        segments.append(_format_analogue(value))

    elif isinstance(value, common.Vector):
        segments.append(f"mag={_format_analogue(value.magnitude)}")

        if value.angle is not None:
            segments.append(f"ang={_format_analogue(value.angle)}")

    elif isinstance(value, common.StepPosition):
        segments.append(str(value.value))

        if value.transient:
            segments.append('transient')

    elif isinstance(value, dict):
        segments.extend(f"({k}, {_format_value(v)})" for k, v in value.items())

    else:
        segments.extend(_format_value(i) for i in value)

    return _format_segments(segments)


def _format_analogue(analogue):
    segments = collections.deque()

    if analogue.i is not None:
        segments.append(f"i={analogue.i}")

    if analogue.f is not None:
        segments.append(f"f={analogue.f}")

    return _format_segments(segments)


def _format_timestamp(timestamp):
    segments = collections.deque()
    segments.append(timestamp.value.isoformat())

    if timestamp.leap_second:
        segments.append('leap_second')

    if timestamp.clock_failure:
        segments.append('clock_failure')

    if timestamp.not_synchronized:
        segments.append('not_synchronized')

    if timestamp.accuracy is not None:
        segments.append(f"accuracy={timestamp.accuracy}")

    return _format_segments(segments)


def _format_origin(origin):
    segments = collections.deque()
    segments.append(f"category={origin.category.name}")
    segments.append(f"identification=({origin.identification.hex(' ')})")
    return _format_segments(segments)


def _format_report_data(data):
    segments = collections.deque()
    segments.append(f"ref={encoder.data_ref_to_str(data.ref)}")
    segments.append(f"value={_format_value(data.value)}")

    if data.reasons is not None:
        reasons = [i.name for i in data.reasons]
        segments.append(f"reasons={_format_segments(reasons)}")

    return _format_segments(segments)


def _format_command(cmd):
    segments = collections.deque()
    segments.append(f"value={_format_value(cmd.value)}")

    if cmd.operate_time is not None:
        segments.append(f"operate_time={_format_timestamp(cmd.operate_time)}")

    segments.append(f"origin={_format_origin(cmd.origin)}")
    segments.append(f"control_number={cmd.control_number}")
    segments.append(f"t={_format_timestamp(cmd.t)}")

    if cmd.test:
        segments.append('test')

    checks = [i.name for i in cmd.checks]
    segments.append(f"checks={_format_segments(checks)}")

    return _format_segments(segments)


def _format_command_error(cmd_error):
    segments = collections.deque()

    if cmd_error.service_error is not None:
        segments.append(
            f"service_error={cmd_error.service_error.name}")

    if cmd_error.additional_cause is not None:
        segments.append(
            f"additional_cause={cmd_error.additional_cause.name}")

    if cmd_error.test_error is not None:
        segments.append(
            f"test_error={cmd_error.test_error.name}")

    return _format_segments(segments)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
