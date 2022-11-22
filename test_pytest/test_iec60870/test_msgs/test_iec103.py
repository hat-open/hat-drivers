import math

import pytest

from hat.drivers.iec60870.msgs.iec103 import common
from hat.drivers.iec60870.msgs.iec103 import encoder


default_time_seven = common.Time(
    size=common.TimeSize.SEVEN,
    milliseconds=1,
    invalid=False,
    minutes=2,
    summer_time=False,
    hours=3,
    day_of_week=1,
    day_of_month=1,
    months=4,
    years=5)


default_time_four = common.Time(
    size=common.TimeSize.FOUR,
    milliseconds=1,
    invalid=False,
    minutes=2,
    summer_time=False,
    hours=3,
    day_of_week=None,
    day_of_month=None,
    months=None,
    years=None)


def assert_encode_decode(asdu_type, ioes, assert_asdu_fn=None):
    _encoder = encoder.Encoder()
    asdu = common.ASDU(
        type=asdu_type,
        cause=common.Cause.SPONTANEOUS,
        address=1,
        ios=[common.IO(
            address=common.IoAddress(
                function_type=255,
                information_number=17),
            elements=ioes)])
    asdu_encoded = _encoder.encode_asdu(asdu)
    asdu_decoded = _encoder.decode_asdu(asdu_encoded)

    if assert_asdu_fn:
        assert_asdu_fn(asdu, asdu_decoded)
    else:
        assert asdu == asdu_decoded


def assert_measurand_asdu(asdu, asdu_decoded):
    assert len(asdu_decoded.ios) == 1
    io = asdu.ios[0]
    io_decoded = asdu_decoded.ios[0]
    assert len(io.elements) == len(io_decoded.elements)
    for ioe, ioe_decoded in zip(io.elements, io_decoded.elements):
        assert len(ioe) == len(ioe_decoded)
        for attr in ioe._fields:
            if attr != 'value':
                assert getattr(ioe, attr) == getattr(ioe_decoded, attr)
                continue
            assert len(ioe.value) == len(ioe_decoded.value)
            for value_attr in ioe.value._fields:
                if value_attr != 'value':
                    assert (getattr(ioe.value, value_attr) ==
                            getattr(ioe_decoded.value, value_attr))
                    continue
                assert math.isclose(ioe.value.value,
                                    ioe_decoded.value.value,
                                    rel_tol=1e-3)


def assert_generic_data_asdu_types(asdu, asdu_decoded):

    fixed_types = [common.ValueType.FIXED,
                   common.ValueType.UFIXED,
                   common.ValueType.REAL32,
                   common.ValueType.REAL64,
                   common.ValueType.MEASURAND,
                   common.ValueType.MEASURAND_WITH_RELATIVE_TIME]

    def assert_array_values(a1, a2):
        assert a1.more_follows == a2.more_follows
        assert a1.value_type == a2.value_type
        assert len(a1.values) == len(a2.values)
        value_type = a1.value_type

        if value_type == common.ValueType.BITSTRING:
            for value, value_decoded in zip(a1.values, a2.values):
                for bit, bit_decoded in zip(value.value, value_decoded.value):
                    assert bit == bit_decoded

        elif value_type == common.ValueType.ARRAY:
            for value, value_decoded in zip(a1.values, a2.values):
                assert_array_values(value, value_decoded)

        elif value_type in fixed_types:
            for value, value_decoded in zip(a1.values, a2.values):
                assert math.isclose(value.value,
                                    value_decoded.value,
                                    rel_tol=1e-2)

        else:
            assert a1.values == a2.values

    if asdu == asdu_decoded:
        return

    assert len(asdu_decoded.ios) == 1
    assert len(asdu_decoded.ios[0].elements) == 1
    ioe = asdu.ios[0].elements[0]
    ioe_decoded = asdu_decoded.ios[0].elements[0]

    for attr in ioe._fields:
        if attr == 'data':
            assert len(ioe.data) == len(ioe_decoded.data)

            for data, data_decoded in zip(ioe.data, ioe_decoded.data):
                if asdu.type == common.AsduType.GENERIC_DATA:
                    assert data[0] == data_decoded[0]
                    assert data[1].description == data_decoded[1].description
                    assert_array_values(data[1].value, data_decoded[1].value)

                elif asdu.type == common.AsduType.GENERIC_IDENTIFICATION:
                    assert data.description == data_decoded.description
                    assert_array_values(data.value, data_decoded.value)

                elif asdu.type == common.AsduType.GENERIC_COMMAND:
                    assert data == data_decoded

                else:
                    raise ValueError('invalid asdu type')

        else:
            assert getattr(ioe, attr) == getattr(ioe_decoded, attr)


@pytest.mark.parametrize('value, supplementary, time', [
    (common.DoubleValue.TRANSIENT, 0, default_time_four),
    (common.DoubleValue.ERROR, 255, default_time_four),
    (common.DoubleValue.OFF, 1, default_time_four),
    (common.DoubleValue.ON, 5, default_time_four)])
def test_time_tagged_message(value, supplementary, time):
    asdu_type = common.AsduType.TIME_TAGGED_MESSAGE
    io_element_cls = common.IoElement_TIME_TAGGED_MESSAGE
    assert_encode_decode(asdu_type, [io_element_cls(common.DoubleWithTimeValue(
        value=value,
        time=time,
        supplementary=supplementary))])


@pytest.mark.parametrize(
    'value, relative_time, fault_number, supplementary, time', [
        (common.DoubleValue.TRANSIENT, 0, 0, 0, default_time_four),
        (common.DoubleValue.ERROR, 65535, 65535, 255, default_time_four),
        (common.DoubleValue.OFF, 2, 3, 4, default_time_four),
        (common.DoubleValue.ON, 5, 6, 7, default_time_four)])
def test_time_tagged_message_with_relative_time(value, relative_time,
                                                fault_number, supplementary,
                                                time):
    asdu_type = common.AsduType.TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME
    io_element_cls = common.IoElement_TIME_TAGGED_MESSAGE_WITH_RELATIVE_TIME
    assert_encode_decode(asdu_type,
                         [io_element_cls(common.DoubleWithRelativeTimeValue(
                              value=value,
                              relative_time=relative_time,
                              fault_number=fault_number,
                              time=time,
                              supplementary=supplementary))])


@pytest.mark.parametrize('overflow, invalid, value, io_element_count', [
    (True, True, -1.0, 1),
    (False, False, 0.99, 1),
    (True, False, 0.0, 1),
    (True, False, -0.5, 2),
    (False, True, 0.5, 4)])
def test_measurands_1(overflow, invalid, value, io_element_count):
    asdu_type = common.AsduType.MEASURANDS_1
    io_element_cls = common.IoElement_MEASURANDS_1
    assert_encode_decode(asdu_type, [io_element_cls(common.MeasurandValue(
         overflow=overflow,
         invalid=invalid,
         value=value))] * io_element_count, assert_measurand_asdu)


@pytest.mark.parametrize('value, relative_time, fault_number, time', [
    (0.0, 0, 0, default_time_four),
    (1.1, 65535, 65535, default_time_four),
    (-1.1, 10, 20, default_time_four)])
def test_time_tagged_measurands_with_relative_time(value, relative_time,
                                                   fault_number, time):
    asdu_type = common.AsduType.TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME
    io_element_cls = common.IoElement_TIME_TAGGED_MEASURANDS_WITH_RELATIVE_TIME
    assert_encode_decode(asdu_type,
                         [io_element_cls(common.MeasurandWithRelativeTimeValue(
                          value=value,
                          relative_time=relative_time,
                          fault_number=fault_number,
                          time=time))],
                         assert_measurand_asdu)


@pytest.mark.parametrize('compatibility, value, software', [
    (0, b'00000000', b'0000'),
    (255, b'11111111', b'1111'),
    (10, b'01010101', b'0101')])
def test_identification(compatibility, value, software):
    asdu_type = common.AsduType.IDENTIFICATION
    io_element_cls = common.IoElement_IDENTIFICATION
    assert_encode_decode(asdu_type, [io_element_cls(
        compatibility=compatibility,
        value=value,
        software=software)])


@pytest.mark.parametrize('time', [default_time_seven])
def test_time_synchronization(time):
    asdu_type = common.AsduType.TIME_SYNCHRONIZATION
    io_element_cls = common.IoElement_TIME_SYNCHRONIZATION
    assert_encode_decode(asdu_type, [io_element_cls(
        time=time)])


@pytest.mark.parametrize('scan_number', [0, 255, 5])
def test_general_interrogation(scan_number):
    asdu_type = common.AsduType.GENERAL_INTERROGATION
    io_element_cls = common.IoElement_GENERAL_INTERROGATION
    assert_encode_decode(asdu_type, [io_element_cls(scan_number=scan_number)])


@pytest.mark.parametrize('scan_number', [0, 255, 5])
def test_general_interrogation_termination(scan_number):
    asdu_type = common.AsduType.GENERAL_INTERROGATION_TERMINATION
    io_element_cls = common.IoElement_GENERAL_INTERROGATION_TERMINATION
    assert_encode_decode(asdu_type, [io_element_cls(scan_number=scan_number)])


@pytest.mark.parametrize('overflow, invalid, value, io_element_count', [
    (False, False, -1.0, 1),
    (True, True, 0.9999, 1),
    (False, True, 0.0, 2),
    (True, False, 0.5, 5),
    (False, False, -0.5, 9)])
def test_measurands_2(overflow, invalid, value, io_element_count):
    asdu_type = common.AsduType.MEASURANDS_2
    io_element_cls = common.IoElement_MEASURANDS_2
    assert_encode_decode(asdu_type, [io_element_cls(common.MeasurandValue(
        overflow=overflow,
        invalid=invalid,
        value=value
    ))] * io_element_count, assert_measurand_asdu)


generic_data = [
    (0, False, False, 1,
     common.ValueType.NONE, common.NoneValue(), 1, False),
    (255, True, True, 1,
     common.ValueType.TEXT, common.TextValue(b'Group1'), 1, True),
    (10, True, False, 1,
     common.ValueType.BITSTRING,
     common.BitstringValue([True, False, True]), 1, False),
    (10, False, True, 1,
     common.ValueType.UINT, common.UIntValue(15), 1, True),
    (10, False, False, 1,
     common.ValueType.INT, common.IntValue(-15), 1, False),
    (10, False, False, 1,
     common.ValueType.UFIXED, common.UFixedValue(0.5), 1, False),
    (10, False, False, 1,
     common.ValueType.FIXED, common.FixedValue(-0.5), 1, False),
    (10, False, False, 1,
     common.ValueType.REAL32, common.Real32Value(156.471), 1, False),
    (10, False, False, 1,
     common.ValueType.REAL64, common.Real64Value(1.7976e+100), 1, False),
    (10, False, False, 1,
     common.ValueType.DOUBLE, common.DoubleValue.ON, 1, False),
    (10, False, False, 1,
     common.ValueType.SINGLE, common.SingleValue.OFF, 1, False),
    (10, False, False, 1,
     common.ValueType.EXTENDED_DOUBLE,
     common.ExtendedDoubleValue.TRANSIENT, 1, False),
    (10, False, False, 1,
     common.ValueType.MEASURAND,
     common.MeasurandValue(overflow=False, invalid=False,
                           value=0.1), 1, False),
    (10, False, False, 1,
     common.ValueType.TIME, common.TimeValue(common.Time(
         size=common.TimeSize.SEVEN,
         milliseconds=100,
         invalid=False,
         minutes=55,
         summer_time=True,
         hours=11,
         day_of_week=1,
         day_of_month=15,
         months=8,
         years=25)), 1, False),
    (10, False, False, 1,
     common.ValueType.IDENTIFICATION,
     common.IdentificationValue(
         common.Identification(group_id=0, entry_id=255)), 1, False),
    (10, False, False, 1,
     common.ValueType.RELATIVE_TIME,
     common.RelativeTimeValue(20), 1, False),
    (10, False, False, 1,
     common.ValueType.IO_ADDRESS,
     common.IoAddressValue(common.IoAddress(
         function_type=12, information_number=3)), 1, False),
    (10, False, False, 1,
     common.ValueType.DOUBLE_WITH_TIME,
     common.DoubleWithTimeValue(
         value=common.DoubleValue.OFF,
         time=default_time_four,
         supplementary=5), 1, False),
    (10, False, False, 1,
     common.ValueType.DOUBLE_WITH_RELATIVE_TIME,
     common.DoubleWithRelativeTimeValue(
         value=common.DoubleValue.ON,
         relative_time=15,
         fault_number=33,
         time=common.Time(
             size=common.TimeSize.FOUR,
             milliseconds=100,
             invalid=False,
             minutes=55,
             summer_time=True,
             hours=11,
             day_of_week=None,
             day_of_month=None,
             months=None,
             years=None),
         supplementary=12), 1, False),
    (10, False, False, 1,
     common.ValueType.MEASURAND_WITH_RELATIVE_TIME,
     common.MeasurandWithRelativeTimeValue(
         value=123.456,
         relative_time=678,
         fault_number=71,
         time=default_time_four), 1, False),
    (10, False, False, 1,
     common.ValueType.TEXT_NUMBER,
     common.TextNumberValue(781), 1, False),
    (10, False, False, 1,
     common.ValueType.REPLY, common.ReplyValue.ACK, 1, False),
    (10, False, False, 1,
     common.ValueType.ARRAY, common.ArrayValue(
         value_type=common.ValueType.INT,
         more_follows=False,
         values=[common.IntValue(11), common.IntValue(12)]), 1, False),
    (10, False, False, 1,
     common.ValueType.INDEX, common.IndexValue(17), 1, False),
    (10, False, False, 5,
     common.ValueType.INT, common.IntValue(13), 1, False),
    (10, False, False, 1,
     common.ValueType.INT, common.IntValue(13), 10, False),
    (10, False, False, 2,
     common.ValueType.INT, common.IntValue(13), 5, False)]


@pytest.mark.parametrize('generic_data', generic_data)
def test_generic_data(generic_data):
    return_identifier, counter, io_more_follows, data_count, value_type, \
        value, values_count, av_more_follows = generic_data

    asdu_type = common.AsduType.GENERIC_DATA
    io_element_cls = common.IoElement_GENERIC_DATA
    assert_encode_decode(
        asdu_type, [io_element_cls(
            return_identifier=return_identifier,
            counter=counter,
            more_follows=io_more_follows,
            data=[(common.Identification(group_id=0, entry_id=1),
                   common.DescriptiveData(
                        description=common.Description.VALUE_ARRAY,
                        value=common.ArrayValue(
                            value_type=value_type,
                            more_follows=av_more_follows,
                            values=[value] * values_count)))] * data_count)],
        assert_generic_data_asdu_types)


@pytest.mark.parametrize('generic_data', generic_data)
def test_generic_identification(generic_data):
    return_identifier, counter, io_more_follows, data_count, value_type, \
        value, values_count, av_more_follows = generic_data

    asdu_type = common.AsduType.GENERIC_IDENTIFICATION
    io_element_cls = common.IoElement_GENERIC_IDENTIFICATION
    assert_encode_decode(
        asdu_type, [io_element_cls(
            return_identifier=return_identifier,
            identification=common.Identification(
                group_id=0,
                entry_id=0),
            counter=counter,
            more_follows=io_more_follows,
            data=[common.DescriptiveData(
                description=common.Description.VALUE_ARRAY,
                value=common.ArrayValue(
                    value_type=value_type,
                    more_follows=av_more_follows,
                    values=[value] * values_count))] * data_count)],
        assert_generic_data_asdu_types)


@pytest.mark.parametrize('value, return_identifier', [
    (common.DoubleValue.TRANSIENT, 0),
    (common.DoubleValue.ERROR, 255),
    (common.DoubleValue.OFF, 2),
    (common.DoubleValue.ON, 5)])
def test_general_command(value, return_identifier):
    asdu_type = common.AsduType.GENERAL_COMMAND
    io_element_cls = common.IoElement_GENERAL_COMMAND
    for value in list(common.DoubleValue):
        assert_encode_decode(asdu_type, [io_element_cls(
            value=common.DoubleValue(value=value),
            return_identifier=return_identifier)])


@pytest.mark.parametrize('return_identifier, data_count, description', [
    (0, 0, common.Description.DESCRIPTION),
    (255, 1, common.Description.NOT_SPECIFIED),
    (10, 2, common.Description.ACTUAL_VALUE)])
def test_generic_command(return_identifier, data_count, description):
    asdu_type = common.AsduType.GENERIC_COMMAND
    io_element_cls = common.IoElement_GENERIC_COMMAND

    assert_encode_decode(asdu_type, [io_element_cls(
        return_identifier=return_identifier,
        data=[(common.Identification(group_id=0, entry_id=0),
               description)] * data_count)])


@pytest.mark.parametrize(
    'fault_number, trip, transmitted, test, other, time', [
        (0, True, True, True, True, default_time_seven),
        (65535, False, False, False, False, default_time_seven),
        (5, True, False, True, False, default_time_seven)])
def test_list_of_recorded_disturbances(fault_number, trip, transmitted, test,
                                       other, time):
    asdu_type = common.AsduType.LIST_OF_RECORDED_DISTURBANCES
    io_element_cls = common.IoElement_LIST_OF_RECORDED_DISTURBANCES
    assert_encode_decode(asdu_type, [io_element_cls(
        fault_number=fault_number,
        trip=trip,
        transmitted=transmitted,
        test=test,
        other=other,
        time=time)])


@pytest.mark.parametrize('order_type, fault_number, channel', [
    (common.OrderType.SELECTION_OF_FAULT, 0, common.Channel.GLOBAL),
    (common.OrderType.TAGS_TRANSMITTED_NOT_SUCCESSFULLY, 65535, common.Channel.V_EN),  # NOQA
    (common.OrderType.REQUEST_FOR_DISTURBANCE_DATA, 3, common.Channel.I_L1),
    (common.OrderType.REQUEST_FOR_CHANNEL, 5, common.Channel.V_L1E)])
def test_order_for_disturbance_data_transmission(order_type, fault_number,
                                                 channel):
    asdu_type = common.AsduType.ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION
    io_element_cls = common.IoElement_ORDER_FOR_DISTURBANCE_DATA_TRANSMISSION
    assert_encode_decode(asdu_type, [io_element_cls(
        order_type=order_type,
        fault_number=fault_number,
        channel=channel)])


@pytest.mark.parametrize('order_type, fault_number, channel', [
    (common.OrderType.SELECTION_OF_FAULT, 0, common.Channel.GLOBAL),
    (common.OrderType.TAGS_TRANSMITTED_NOT_SUCCESSFULLY, 65535, common.Channel.V_EN),  # NOQA
    (common.OrderType.REQUEST_FOR_DISTURBANCE_DATA, 3, common.Channel.I_L1),
    (common.OrderType.REQUEST_FOR_CHANNEL, 5, common.Channel.V_L1E)])
def test_acknowledgement_for_disturbance_data_transmission(order_type,
                                                           fault_number,
                                                           channel):
    asdu_type = common.AsduType.ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION  # NOQA
    io_element_cls = common.IoElement_ACKNOWLEDGEMENT_FOR_DISTURBANCE_DATA_TRANSMISSION  # NOQA
    assert_encode_decode(asdu_type, [io_element_cls(
        order_type=order_type,
        fault_number=fault_number,
        channel=channel)])


@pytest.mark.parametrize('fault_number, number_of_faults, number_of_channels, '
                         'number_of_elements, interval, time', [
                             (0, 0, 0, 1, 1, default_time_four),
                             (65535, 65535, 255, 65535, 65535,
                              default_time_four),
                             (1, 2, 3, 4, 5, default_time_four)])
def test_ready_for_transmission_of_disturbance_data(
        fault_number, number_of_faults, number_of_channels,
        number_of_elements, interval, time):
    asdu_type = common.AsduType.READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA
    io_element_cls = common.IoElement_READY_FOR_TRANSMISSION_OF_DISTURBANCE_DATA  # NOQA
    assert_encode_decode(asdu_type, [io_element_cls(
        fault_number=fault_number,
        number_of_faults=number_of_faults,
        number_of_channels=number_of_channels,
        number_of_elements=number_of_elements,
        interval=interval,
        time=time)])


@pytest.mark.parametrize(
    'fault_number, channel, primary, secondary, reference', [
        (0, common.Channel.GLOBAL, -1.1, -1.1, -1.1),
        (65535, common.Channel.V_EN, 1.1, 1.1, 1.1),
        (5, common.Channel.I_L1, 0.0, 0.0, 0.0)])
def test_ready_for_transmission_of_a_channel(fault_number, channel, primary,
                                             secondary, reference):

    def assert_asdu(asdu, asdu_decoded):
        assert len(asdu_decoded.ios) == 1
        io = asdu.ios[0]
        io_decoded = asdu_decoded.ios[0]
        assert len(io.elements) == len(io_decoded.elements)
        attrs = ['primary', 'secondary', 'reference']
        for ioe, ioe_decoded in zip(io.elements, io_decoded.elements):
            assert len(ioe) == len(ioe_decoded)
            for attr in ioe._fields:
                if attr not in attrs:
                    assert getattr(ioe, attr) == getattr(ioe_decoded, attr)
                    continue
                assert math.isclose(getattr(ioe, attr).value,
                                    getattr(ioe_decoded, attr).value,
                                    rel_tol=1e-3)

    asdu_type = common.AsduType.READY_FOR_TRANSMISSION_OF_A_CHANNEL
    io_element_cls = common.IoElement_READY_FOR_TRANSMISSION_OF_A_CHANNEL
    assert_encode_decode(asdu_type, [io_element_cls(
        fault_number=fault_number,
        channel=channel,
        primary=common.Real32Value(primary),
        secondary=common.Real32Value(secondary),
        reference=common.Real32Value(reference))], assert_asdu)


@pytest.mark.parametrize('fault_number', [0, 65535, 4])
def test_ready_for_transmission_of_tags(fault_number):
    asdu_type = common.AsduType.READY_FOR_TRANSMISSION_OF_TAGS
    io_element_cls = common.IoElement_READY_FOR_TRANSMISSION_OF_TAGS
    assert_encode_decode(asdu_type,
                         [io_element_cls(fault_number=fault_number)])


@pytest.mark.parametrize('fault_number, tag_position, tag_values', [
    (0, 1, [common.DoubleValue.TRANSIENT]),
    (65535, 65535, [common.DoubleValue.TRANSIENT,
                    common.DoubleValue.OFF,
                    common.DoubleValue.ON,
                    common.DoubleValue.ERROR] * 6 +
                   [common.DoubleValue.TRANSIENT]),
    (2, 5, [common.DoubleValue.OFF,
            common.DoubleValue.ON])])
def test_transmission_of_tags(fault_number, tag_position, tag_values):
    asdu_type = common.AsduType.TRANSMISSION_OF_TAGS
    io_element_cls = common.IoElement_TRANSMISSION_OF_TAGS
    tags = []
    for tag_value in tag_values:
        tags.append((common.IoAddress(function_type=255,
                                      information_number=18),
                     tag_value))
    assert_encode_decode(asdu_type, [io_element_cls(
        fault_number=fault_number,
        tag_position=tag_position,
        values=tags)])


@pytest.mark.parametrize('fault_number, channel, element_number, values', [
    (0, common.Channel.GLOBAL, 0, [-1.0]),
    (65535, common.Channel.V_EN, 65535, [0.9999] * 25),
    (5, common.Channel.I_L1, 6, [0.0, 0.5, -0.5])])
def test_transmission_of_disturbance_values(fault_number, channel,
                                            element_number, values):

    def assert_asdu(asdu, asdu_decoded):
        assert len(asdu_decoded.ios) == 1
        assert len(asdu_decoded.ios[0].elements) == 1
        ioe = asdu.ios[0].elements[0]
        ioe_decoded = asdu_decoded.ios[0].elements[0]
        assert len(ioe) == len(ioe_decoded)
        for attr in ioe._fields:
            if attr != 'values':
                assert getattr(ioe, attr) == getattr(ioe_decoded, attr)
                continue
            assert len(ioe.values) == len(ioe_decoded.values)
            for value, decoded_val in zip(ioe.values, ioe_decoded.values):
                assert math.isclose(value, decoded_val,
                                    rel_tol=1e-3)

    asdu_type = common.AsduType.TRANSMISSION_OF_DISTURBANCE_VALUES
    io_element_cls = common.IoElement_TRANSMISSION_OF_DISTURBANCE_VALUES
    assert_encode_decode(asdu_type, [io_element_cls(
        fault_number=fault_number,
        channel=channel,
        element_number=element_number,
        values=values)], assert_asdu)


@pytest.mark.parametrize('order_type, fault_number, channel', [
    (common.OrderType.SELECTION_OF_FAULT, 0, common.Channel.GLOBAL),
    (common.OrderType.TAGS_TRANSMITTED_NOT_SUCCESSFULLY, 65535, common.Channel.V_EN),  # NOQA
    (common.OrderType.REQUEST_FOR_DISTURBANCE_DATA, 3, common.Channel.I_L1),
    (common.OrderType.REQUEST_FOR_CHANNEL, 5, common.Channel.V_L1E)])
def test_end_of_transmission(order_type, fault_number, channel):
    asdu_type = common.AsduType.END_OF_TRANSMISSION
    io_element_cls = common.IoElement_END_OF_TRANSMISSION
    assert_encode_decode(asdu_type, [io_element_cls(
        order_type=order_type,
        fault_number=fault_number,
        channel=channel)])


@pytest.mark.parametrize('data, value, bit_offset, bit_size, signed', [
    (b'\x00', 0.0, 0, 8, False),
    (b'\xFF', 0.99609375, 0, 8, False),
    (b'\x80', 0.5, 0, 8, False),
    (b'\x01', 0.00390625, 0, 8, False),
    (b'\x00', 0.0, 0, 8, True),
    (b'\x70', 0.875, 0, 8, True),
    (b'\x40', 0.5, 0, 8, True),
    (b'\x01', 0.0078125, 0, 8, True),
    (b'\x80', -1.0, 0, 8, True),
    (b'\xFF', -0.0078125, 0, 8, True),
    (b'\xC0', -0.5, 0, 8, True),
    (b'\xF8\x7F', 0.999755859375, 3, 13, True),
    (b'\x00\x40', 0.5, 3, 13, True),
    (b'\x08\x00', 0.000244140625, 3, 13, True),
    (b'\xF8\xFF', -0.000244140625, 3, 13, True),
    (b'\xF8\xFF', -0.000244140625, 3, 13, True),
    (b'\x08\x80', -0.999755859375, 3, 13, True)])
def test_encode_decode_fixed(data, value, bit_offset, bit_size, signed):
    encode = encoder._encode_fixed
    decode = encoder._decode_fixed
    decoded_value = decode(data, bit_offset, bit_size, signed)
    encoded_data = encode(value, bit_offset, bit_size, signed)
    assert value == decoded_value
    assert data == bytes(encoded_data)
