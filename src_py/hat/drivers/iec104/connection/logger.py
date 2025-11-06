import enum
import logging

from hat.drivers import tcp

from hat.drivers.iec104 import common
from hat.drivers.iec104 import encoder


def create_logger(logger: logging.Logger,
                  info: tcp.ConnectionInfo
                  ) -> logging.LoggerAdapter:
    return _create_logger_adapter(logger, False, info)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: tcp.ConnectionInfo):
        self._log = _create_logger_adapter(logger, True, info)

    @property
    def is_enabled(self):
        return self._log.isEnabledFor(logging.DEBUG)

    def log(self,
            action: common.CommLogAction,
            msg: common.Msg | None = None):
        if not self.is_enabled:
            return

        if msg is None:
            self._log.debug(action.value)

        else:
            self._log.debug('%s %s', action.value, _format_msg(msg))


def _create_logger_adapter(logger, communication, info):
    extra = {'meta': {'type': 'Iec104Connection',
                      'communication': communication,
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port},
                      'remote_addr': {'host': info.remote_addr.host,
                                      'port': info.remote_addr.port}}}

    return logging.LoggerAdapter(logger, extra)


def _format_msg(msg):
    asdu_type = encoder.get_msg_asdu_type(msg)

    if isinstance(msg, common.DataMsg):
        return (f"(Data "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"io={msg.io_address} "
                f"data={_format_data(msg.data)} "
                f"time={_format_time(msg.time)} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.CommandMsg):
        return (f"(Command "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"io={msg.io_address} "
                f"command={_format_command(msg.command)} "
                f"negative={msg.is_negative_confirm} "
                f"time={_format_time(msg.time)} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.InitializationMsg):
        return (f"(Initialization "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"change={msg.param_change} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.InterrogationMsg):
        return (f"(Interrogation "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"request={msg.request} "
                f"negative={msg.is_negative_confirm} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.CounterInterrogationMsg):
        return (f"(CounterInterrogation "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"request={msg.request} "
                f"freeze={msg.freeze.name} "
                f"negative={msg.is_negative_confirm} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.ReadMsg):
        return (f"(Read "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"io={msg.io_address} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.ClockSyncMsg):
        return (f"(ClockSync "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"time={_format_time(msg.time)} "
                f"negative={msg.is_negative_confirm} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.TestMsg):
        return (f"(Test "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"counter={msg.counter} "
                f"time={_format_time(msg.time)} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.ResetMsg):
        return (f"(Reset "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"qualifier={msg.qualifier} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.ParameterMsg):
        return (f"(Parameter "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"io={msg.io_address} "
                f"parameter={_format_parameter(msg.parameter)} "
                f"cause={_format_cause(msg.cause)})")

    if isinstance(msg, common.ParameterActivationMsg):
        return (f"(ParameterActivation "
                f"type={asdu_type.name} "
                f"test={msg.is_test} "
                f"originator={msg.originator_address} "
                f"asdu={msg.asdu_address} "
                f"io={msg.io_address} "
                f"qualifier={msg.qualifier} "
                f"cause={_format_cause(msg.cause)})")

    raise TypeError('unsupported message type')


def _format_data(data):
    if isinstance(data, common.SingleData):
        return (f"(Single "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.DoubleData):
        return (f"(Double "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.StepPositionData):
        return (f"(StepPosition "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.BitstringData):
        return (f"(Bitstring "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.NormalizedData):
        return (f"(Normalized "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.ScaledData):
        return (f"(Scaled "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.FloatingData):
        return (f"(Floating "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.BinaryCounterData):
        return (f"(BinaryCounter "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    if isinstance(data, common.ProtectionData):
        return (f"(Protection "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)} "
                f"time={data.elapsed_time})")

    if isinstance(data, common.ProtectionStartData):
        return (f"(Protection "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)} "
                f"time={data.duration_time})")

    if isinstance(data, common.ProtectionCommandData):
        return (f"(ProtectionCommand "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)} "
                f"time={data.operating_time})")

    if isinstance(data, common.StatusData):
        return (f"(Status "
                f"value={_format_value(data.value)} "
                f"quality={_format_quality(data.quality)})")

    raise TypeError('unsupported data type')


def _format_command(command):
    if isinstance(command, common.SingleCommand):
        return (f"(Single "
                f"value={_format_value(command.value)} "
                f"select={command.select} "
                f"qualifier={command.qualifier})")

    if isinstance(command, common.DoubleCommand):
        return (f"(Double "
                f"value={_format_value(command.value)} "
                f"select={command.select} "
                f"qualifier={command.qualifier})")

    if isinstance(command, common.RegulatingCommand):
        return (f"(Regulating "
                f"value={_format_value(command.value)} "
                f"select={command.select} "
                f"qualifier={command.qualifier})")

    if isinstance(command, common.NormalizedCommand):
        return (f"(Normalized "
                f"value={_format_value(command.value)} "
                f"select={command.select})")

    if isinstance(command, common.ScaledCommand):
        return (f"(Scaled "
                f"value={_format_value(command.value)} "
                f"select={command.select})")

    if isinstance(command, common.FloatingCommand):
        return (f"(Floating "
                f"value={_format_value(command.value)} "
                f"select={command.select})")

    if isinstance(command, common.BitstringCommand):
        return (f"(Bitstring "
                f"value={_format_value(command.value)})")


def _format_time(time):
    if time is None:
        return ''

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

    return cause


def _format_parameter(parameter):
    if isinstance(parameter, common.NormalizedParameter):
        return (f"(Normalized "
                f"value={_format_value(parameter.value)} "
                f"qualifier={parameter.qualifier})")

    if isinstance(parameter, common.ScaledParameter):
        return (f"(Scaled "
                f"value={_format_value(parameter.value)} "
                f"qualifier={parameter.qualifier})")

    if isinstance(parameter, common.FloatingParameter):
        return (f"(Floating "
                f"value={_format_value(parameter.value)} "
                f"qualifier={parameter.qualifier})")

    raise TypeError('unsupported parameter type')


def _format_value(value):
    if isinstance(value, common.SingleValue):
        return value.name

    if isinstance(value, common.DoubleValue):
        return value.name

    if isinstance(value, common.RegulatingValue):
        return value.name

    if isinstance(value, common.StepPositionValue):
        return (f"({value.value} "
                f"transient={value.transient})")

    if isinstance(value, common.BitstringValue):
        return f"({value.value.hex(' ')})"

    if isinstance(value, common.NormalizedValue):
        return value.value

    if isinstance(value, common.ScaledValue):
        return value.value

    if isinstance(value, common.FloatingValue):
        return value.value

    if isinstance(value, common.BinaryCounterValue):
        return value.value

    if isinstance(value, common.ProtectionValue):
        return value.name

    if isinstance(value, common.ProtectionStartValue):
        return (f"(general={value.general} "
                f"l1={value.l1} "
                f"l2={value.l2} "
                f"l3={value.l3} "
                f"ie={value.ie} "
                f"reverse={value.reverse})")

    if isinstance(value, common.ProtectionCommandValue):
        return (f"(general={value.general} "
                f"l1={value.l1} "
                f"l2={value.l2} "
                f"l3={value.l3})")

    if isinstance(value, common.StatusValue):
        return (f"({value.value} "
                f"change={value.change})")

    raise TypeError('unsupported value type')


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

    segments = [attr for attr in attrs if getattr(quality, attr)]

    if isinstance(quality, common.CounterQuality):
        segments.append(f"sequence={quality.sequence})")

    return f"({' '.join(segments)})"
