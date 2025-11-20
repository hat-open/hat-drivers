import collections
import enum
import logging

from hat.drivers.iec103 import common
from hat.drivers.iec60870.encodings import iec103
from hat.drivers.iec60870 import link


def create_logger(logger: logging.Logger,
                  info: link.ConnectionInfo
                  ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': 'Iec103Master',
                      'name': info.name,
                      'port': info.port,
                      'address': info.address}}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: link.ConnectionInfo):
        extra = {'meta': {'type': 'Iec103Master',
                          'communication': True,
                          'name': info.name,
                          'port': info.port,
                          'address': info.address}}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            asdu: iec103.ASDU | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if asdu is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            for io in asdu.ios:
                for element in io.elements:
                    self._log.debug(
                        '%s %s',
                        action.value,
                        _format_asdu_io_element(asdu, io, element),
                        stacklevel=2)


def _format_asdu_io_element(asdu, io, element):
    segments = collections.deque()
    segments.append(asdu.type.name)
    segments.append(f"cause={_format_cause(asdu.cause)}")
    segments.append(f"asdu_addr={asdu.address}")
    segments.append(f"function_type={io.address.function_type}")
    segments.append(f"information_number={io.address.information_number}")

    if isinstance(element, (
            iec103.IoElement_TIME_TAGGED_MESSAGE,
            iec103.IoElement_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME,
            iec103.IoElement_MEASURANDS_1,
            iec103.IoElement_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME,
            iec103.IoElement_MEASURANDS_2)):
        segments.append(f"value={_format_value(element.value)}")

    elif isinstance(element, iec103.IoElement_IDENTIFICATION):
        segments.append(f"compatibility={element.compatibility}")
        segments.append(f"value=({element.value.hex(' ')})")
        segments.append(f"software=({element.software.hex(' ')})")

    elif isinstance(element, iec103.IoElement_TIME_SYNCHRONIZATION):
        segments.append(f"time={_format_time(element.time)}")

    elif isinstance(element, (
            iec103.IoElement_GENERAL_INTERROGATION,
            iec103.IoElement_GENERAL_INTERROGATION_TERMINATION)):
        segments.append(f"scan_number={element.scan_number}")

    elif isinstance(element, iec103.IoElement_GENERIC_DATA):
        segments.append(f"return_identifier={element.return_identifier}")

        if element.counter:
            segments.append('counter')

        if element.more_follows:
            segments.append('more_follows')

        data = collections.deque()
        for identification, i in element.data:
            subsegments = collections.deque()
            subsegments.append(f"group_id={identification.group_id}")
            subsegments.append(f"entry_id={identification.entry_id}")
            subsegments.append(f"description={i.description.name}")
            subsegments.append(f"value={_format_value(i.value)}")

            data.append(_format_segments(subsegments))

        segments.append(f"data={_format_segments(data)}")

    elif isinstance(element, iec103.IoElement_GENERIC_IDENTIFICATION):
        segments.append(f"return_identifier={element.return_identifier}")
        segments.append(f"group_id={element.identification.group_id}")
        segments.append(f"entry_id={element.identification.entry_id}")

        if element.counter:
            segments.append('counter')

        if element.more_follows:
            segments.append('more_follows')

        data = collections.deque()
        for i in element.data:
            subsegments = collections.deque()
            subsegments.append(f"description={i.description.name}")
            subsegments.append(f"value={_format_value(i.value)}")

            data.append(_format_segments(subsegments))

        segments.append(f"data={_format_segments(data)}")

    elif isinstance(element, iec103.IoElement_GENERAL_COMMAND):
        segments.append(f"return_identifier={element.return_identifier}")
        segments.append(f"value={_format_value(element.value)}")

    elif isinstance(element, iec103.IoElement_GENERIC_COMMAND):
        segments.append(f"return_identifier={element.return_identifier}")

        data = collections.deque()
        for identification, i in element.data:
            subsegments = collections.deque()
            subsegments.append(f"group_id={identification.group_id}")
            subsegments.append(f"entry_id={identification.entry_id}")
            subsegments.append(f"description={i.description.name}")
            subsegments.append(f"value={_format_value(i.value)}")

            data.append(_format_segments(subsegments))

        segments.append(f"data={_format_segments(data)}")

    elif isinstance(element, iec103.IoElement_LIST_OF_RECORDED_DISTURBANCES):
        segments.append(f"fault_number={element.fault_number}")

        if element.trip:
            segments.append('trip')

        if element.transmitted:
            segments.append('transmitted')

        if element.test:
            segments.append('test')

        if element.other:
            segments.append('other')

        segments.append(f"time={_format_time(element.time)}")

    elif isinstance(element, (
            iec103.IoElement_ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION,
            iec103.IoElement_ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION)):  # NOQA
        segments.append(f"order_type={element.order_type.name}")
        segments.append(f"fault_number={element.fault_number}")
        segments.append(f"channel={element.channel.name}")

    elif isinstance(element, iec103.IoElement_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA):  # NOQA
        segments.append(f"fault_number={element.fault_number}")
        segments.append(f"number_of_faults={element.number_of_faults}")
        segments.append(f"number_of_channels={element.number_of_channels}")
        segments.append(f"number_of_elements={element.number_of_elements}")
        segments.append(f"interval={element.interval}")
        segments.append(f"time={_format_time(element.time)}")

    elif isinstance(element, iec103.IoElement_READY_FOR_TRANSMISSION_OF_A_CHANNEL):  # NOQA
        segments.append(f"fault_number={element.fault_number}")
        segments.append(f"channel={element.channel.name}")
        segments.append(f"primary={_format_value(element.primary)}")
        segments.append(f"secondary={_format_value(element.secondary)}")
        segments.append(f"reference={_format_value(element.reference)}")

    elif isinstance(element, iec103.IoElement_READY_FOR_TRANSMISSION_OF_TAGS):
        segments.append(f"fault_number={element.fault_number}")

    elif isinstance(element, iec103.IoElement_TRANSMISSION_OF_TAGS):
        segments.append(f"fault_number={element.fault_number}")
        segments.append(f"tag_position={element.tag_position}")

        values = collections.deque()
        for addr, value in element.values:
            subsegments = collections.deque()
            subsegments.append(f"function_type={addr.function_type}")
            subsegments.append(f"information_number={addr.information_number}")
            subsegments.append(f"value={_format_value(value)}")

            values.append(_format_segments(subsegments))

        segments.append(f"values={_format_segments(values)}")

    elif isinstance(element, iec103.IoElement_TRANSMISSION_OF_DISTURBANCE_VALUES):  # NOQA
        segments.append(f"fault_number={element.fault_number}")
        segments.append(f"channel={element.channel.name}")
        segments.append(f"element_number={element.element_number}")

        values = [str(i) for i in element.values]
        segments.append(f"values={_format_segments(values)}")

    elif isinstance(element, iec103.IoElement_END_OF_TRANSMISSION):
        segments.append(f"order_type={element.order_type.name}")
        segments.append(f"fault_number={element.fault_number}")
        segments.append(f"channel={element.channel.name}")

    else:
        raise TypeError('unsupported element type')

    return _format_segments(segments)


def _format_cause(cause):
    if isinstance(cause, enum.Enum):
        return cause.name

    return str(cause)


def _format_value(value):
    segments = collections.deque()

    if isinstance(value, iec103.NoneValue):
        segments.append('None')

    elif isinstance(value, iec103.TextValue):
        segments.append(f"({value.value.hex(' ')})")

    elif isinstance(value, iec103.BitstringValue):
        segments.append(_format_segments([str(i) for i in value.value]))

    elif isinstance(value, (iec103.UIntValue,
                            iec103.IntValue,
                            iec103.UFixedValue,
                            iec103.FixedValue,
                            iec103.Real32Value,
                            iec103.Real64Value,
                            iec103.RelativeTimeValue,
                            iec103.TextNumberValue,
                            iec103.IndexValue)):
        segments.append(str(value.value))

    elif isinstance(value, (iec103.DoubleValue,
                            iec103.SingleValue,
                            iec103.ExtendedDoubleValue,
                            iec103.ReplyValue)):
        segments.append(value.name)

    elif isinstance(value, iec103.MeasurandValue):
        segments.append(str(value.value))

        if value.overflow:
            segments.append('overflow')

        if value.invalid:
            segments.append('invalid')

    elif isinstance(value, iec103.TimeValue):
        segments.append(_format_time(value.value))

    elif isinstance(value, iec103.IdentificationValue):
        segments.append(f"group_id={value.value.group_id}")
        segments.append(f"entry_id={value.value.entry_id}")

    elif isinstance(value, iec103.IoAddressValue):
        segments.append(f"function_type={value.value.function_type}")
        segments.append(f"information_number={value.value.information_number}")

    elif isinstance(value, iec103.DoubleWithTimeValue):
        segments.append(_format_value(value.value))
        segments.append(f"time={_format_time(value.time)}")
        segments.append(f"supplementary={value.supplementary}")

    elif isinstance(value, iec103.DoubleWithRelativeTimeValue):
        segments.append(_format_value(value.value))
        segments.append(f"relative_time={value.relative_time}")
        segments.append(f"fault_number={value.fault_number}")
        segments.append(f"time={_format_time(value.time)}")
        segments.append(f"supplementary={value.supplementary}")

    elif isinstance(value, iec103.MeasurandWithRelativeTimeValue):
        segments.append(str(value.value))
        segments.append(f"relative_time={value.relative_time}")
        segments.append(f"fault_number={value.fault_number}")
        segments.append(f"time={_format_time(value.time)}")

    elif isinstance(value, iec103.ArrayValue):
        segments.append(f"value_type={value.value_type.name}")

        if value.more_follows:
            segments.append('more_follows')

        values = collections.deque()
        for i in value.values:
            values.append(_format_value(i))

        segments.append(f"values={_format_segments(values)}")

    else:
        raise TypeError('unsupported value type')

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


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
