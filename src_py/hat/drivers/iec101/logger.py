from collections.abc import Iterable
import collections
import enum
import logging

from hat.drivers.iec101 import common
from hat.drivers.iec101 import encoder
from hat.drivers.iec60870 import link


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: link.ConnectionInfo):
        extra = {'meta': {'type': 'Iec101Connection',
                          'communication': True,
                          'name': info.name,
                          'port': info.port,
                          'address': info.address}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            msgs: Iterable[common.Msg] | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if msgs is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            for msg in msgs:
                self._log.debug('%s %s', action.value, _format_msg(msg),
                                stacklevel=2)


def _format_msg(msg):
    segments = collections.deque()

    name = type(msg).__name__[:-3]
    segments.append(name)

    if msg.is_test:
        segments.append('test')

    asdu_type = encoder.get_msg_asdu_type(msg)
    segments.append(f"type={asdu_type.name}")

    segments.append(f"originator={msg.originator_address}")
    segments.append(f"asdu={msg.asdu_address}")

    if hasattr(msg, 'io_address'):
        segments.append(f"io={msg.io_address}")

    if hasattr(msg, 'data'):
        segments.append(f"data={_format_data(msg.data)}")

    if hasattr(msg, 'command'):
        segments.append(f"command={_format_command(msg.command)}")

    if hasattr(msg, 'request'):
        segments.append(f"request={msg.request}")

    if hasattr(msg, 'freeze'):
        segments.append(f"freeze={msg.freeze.name}")

    if hasattr(msg, 'qualifier'):
        segments.append(f"qualifier={msg.qualifier}")

    if hasattr(msg, 'parameter'):
        segments.append(f"parameter={_format_parameter(msg.parameter)}")

    if hasattr(msg, 'is_negative_confirm') and msg.is_negative_confirm:
        segments.append('negative')

    if hasattr(msg, 'param_change') and msg.param_change:
        segments.append('change')

    if hasattr(msg, 'time') and msg.time is not None:
        segments.append(f"time={_format_time(msg.time)}")

    if hasattr(msg, 'cause'):
        segments.append(f"cause={_format_cause(msg.cause)}")

    return _format_segments(segments)


def _format_data(data):
    segments = collections.deque()

    name = type(data).__name__[:-4]
    segments.append(name)

    segments.append(f"value={_format_value(data.value)}")

    if data.quality is not None:
        segments.append(f"quality={_format_quality(data.quality)}")

    if hasattr(data, 'elapsed_time'):
        segments.append(f"time={data.elapsed_time}")

    if hasattr(data, 'duration_time'):
        segments.append(f"time={data.duration_time}")

    if hasattr(data, 'operating_time'):
        segments.append(f"time={data.operating_time}")

    return _format_segments(segments)


def _format_command(command):
    segments = collections.deque()

    name = type(command).__name__[:-7]
    segments.append(name)

    if hasattr(command, 'select') and command.select:
        segments.append('select')

    segments.append(f"value={_format_value(command.value)}")

    if hasattr(command, 'qualifier'):
        segments.append(f"qualifier={command.qualifier}")

    return _format_segments(segments)


def _format_time(time):
    time_str = f"{time.milliseconds // 1000:02}.{time.milliseconds % 1000:03}"

    if time.size == common.TimeSize.TWO:
        return time_str

    time_str = f"{time.minutes:02}:{time_str}"

    if time.invalid:
        time_str = f"{time_str} invalid"

    if time.size == common.TimeSize.THREE:
        return f"({time_str})" if ' ' in time_str else time_str

    time_str = f"{time.hours:02}:{time_str}"

    if time.summer_time:
        time_str = f"{time_str} summer"

    if time.size == common.TimeSize.FOUR:
        return f"({time_str})" if ' ' in time_str else time_str

    time_str = (f"{time.years:02}-{time.months:02}-{time.day_of_month:02} "
                f"{time_str}")

    if time.size == common.TimeSize.SEVEN:
        return f"({time_str})"

    raise ValueError('unsupported time size')


def _format_cause(cause):
    if isinstance(cause, enum.Enum):
        return cause.name

    return str(cause)


def _format_parameter(parameter):
    segments = collections.deque()

    name = type(parameter).__name__[:-9]
    segments.append(name)

    segments.append(f"value={_format_value(parameter.value)}")
    segments.append(f"qualifier={parameter.qualifier}")

    return _format_segments(segments)


def _format_value(value):
    segments = collections.deque()

    if isinstance(value, (common.SingleValue,
                          common.DoubleValue,
                          common.RegulatingValue,
                          common.ProtectionValue)):
        segments.append(value.name)

    elif isinstance(value, common.StepPositionValue):
        segments.append(str(value.value))

        if value.transient:
            segments.append('transient')

    elif isinstance(value, common.BitstringValue):
        segments.append(f"({value.value.hex(' ')})")

    elif isinstance(value, (common.NormalizedValue,
                            common.ScaledValue,
                            common.FloatingValue,
                            common.BinaryCounterValue)):
        segments.append(str(value.value))

    elif isinstance(value, common.ProtectionStartValue):
        if value.general:
            segments.append('general')

        if value.l1:
            segments.append('l1')

        if value.l2:
            segments.append('l2')

        if value.l3:
            segments.append('l3')

        if value.ie:
            segments.append('ie')

        if value.reverse:
            segments.append('reverse')

    elif isinstance(value, common.ProtectionCommandValue):
        if value.general:
            segments.append('general')

        if value.l1:
            segments.append('l1')

        if value.l2:
            segments.append('l2')

        if value.l3:
            segments.append('l3')

    elif isinstance(value, common.StatusValue):
        for i, change in zip(value.value, value.change):
            subsegments = collections.deque()
            subsegments.append(str(i))

            if change:
                subsegments.append('change')

            segments.append(_format_segments(subsegments))

    else:
        raise TypeError('unsupported value type')

    return _format_segments(segments)


def _format_quality(quality):
    if quality is None:
        return ''

    if isinstance(quality, common.IndicationQuality):
        attrs = ['invalid', 'not_topical', 'substituted', 'blocked']

    elif isinstance(quality, common.MeasurementQuality):
        attrs = ['invalid', 'not_topical', 'substituted', 'blocked',
                 'overflow']

    elif isinstance(quality, common.CounterQuality):
        attrs = ['invalid', 'adjusted', 'overflow']

    elif isinstance(quality, common.ProtectionQuality):
        attrs = ['invalid', 'not_topical', 'substituted', 'blocked',
                 'time_invalid']

    else:
        raise TypeError('unsupported quality type')

    segments = collections.deque(attr for attr in attrs
                                 if getattr(quality, attr))

    if isinstance(quality, common.CounterQuality):
        segments.append(f"sequence={quality.sequence})")

    return _format_segments(segments)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
