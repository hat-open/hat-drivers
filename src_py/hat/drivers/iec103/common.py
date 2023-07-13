import enum
import typing

from hat.drivers.iec60870.encodings import iec103


AsduAddress: typing.TypeAlias = iec103.AsduAddress
OtherCause: typing.TypeAlias = iec103.OtherCause
Description: typing.TypeAlias = iec103.Description
IoAddress: typing.TypeAlias = iec103.IoAddress
Identification: typing.TypeAlias = iec103.Identification
TimeSize: typing.TypeAlias = iec103.TimeSize
Time: typing.TypeAlias = iec103.Time

ValueType: typing.TypeAlias = iec103.ValueType
NoneValue: typing.TypeAlias = iec103.NoneValue
TextValue: typing.TypeAlias = iec103.TextValue
BitstringValue: typing.TypeAlias = iec103.BitstringValue
UIntValue: typing.TypeAlias = iec103.UIntValue
IntValue: typing.TypeAlias = iec103.IntValue
UFixedValue: typing.TypeAlias = iec103.UFixedValue
FixedValue: typing.TypeAlias = iec103.FixedValue
Real32Value: typing.TypeAlias = iec103.Real32Value
Real64Value: typing.TypeAlias = iec103.Real64Value
DoubleValue: typing.TypeAlias = iec103.DoubleValue
SingleValue: typing.TypeAlias = iec103.SingleValue
ExtendedDoubleValue: typing.TypeAlias = iec103.ExtendedDoubleValue
MeasurandValue: typing.TypeAlias = iec103.MeasurandValue
TimeValue: typing.TypeAlias = iec103.TimeValue
IdentificationValue: typing.TypeAlias = iec103.IdentificationValue
RelativeTimeValue: typing.TypeAlias = iec103.RelativeTimeValue
IoAddressValue: typing.TypeAlias = iec103.IoAddressValue
DoubleWithTimeValue: typing.TypeAlias = iec103.DoubleWithTimeValue
DoubleWithRelativeTimeValue: typing.TypeAlias = iec103.DoubleWithRelativeTimeValue  # NOQA
MeasurandWithRelativeTimeValue: typing.TypeAlias = iec103.MeasurandWithRelativeTimeValue  # NOQA
TextNumberValue: typing.TypeAlias = iec103.TextNumberValue
ReplyValue: typing.TypeAlias = iec103.ReplyValue
ArrayValue: typing.TypeAlias = iec103.ArrayValue
IndexValue: typing.TypeAlias = iec103.IndexValue
Value: typing.TypeAlias = iec103.Value


class DataCause(enum.Enum):
    SPONTANEOUS = iec103.Cause.SPONTANEOUS.value
    CYCLIC = iec103.Cause.CYCLIC.value
    TEST_MODE = iec103.Cause.TEST_MODE.value
    GENERAL_INTERROGATION = iec103.Cause.GENERAL_INTERROGATION.value
    LOCAL_OPERATION = iec103.Cause.LOCAL_OPERATION.value
    REMOTE_OPERATION = iec103.Cause.REMOTE_OPERATION.value


class GenericDataCause(enum.Enum):
    SPONTANEOUS = iec103.Cause.SPONTANEOUS.value
    CYCLIC = iec103.Cause.CYCLIC.value
    TEST_MODE = iec103.Cause.TEST_MODE.value
    GENERAL_INTERROGATION = iec103.Cause.GENERAL_INTERROGATION.value
    LOCAL_OPERATION = iec103.Cause.LOCAL_OPERATION.value
    REMOTE_OPERATION = iec103.Cause.REMOTE_OPERATION.value
    WRITE_ACK = iec103.Cause.GENERIC_WRITE_COMMAND.value
    WRITE_NACK = iec103.Cause.GENERIC_WRITE_COMMAND_NACK.value
    READ_ACK = iec103.Cause.GENERIC_READ_COMMAND.value
    READ_NACK = iec103.Cause.GENERIC_READ_COMMAND_NACK.value
    WRITE_CONFIRMATION = iec103.Cause.GENERIC_WRITE_CONFIRMATION.value


class MeasurandType(enum.Enum):
    M1_I_L2 = (iec103.AsduType.MEASURANDS_1.value, 0)
    M1_U_L12 = (iec103.AsduType.MEASURANDS_1.value, 1)
    M1_P = (iec103.AsduType.MEASURANDS_1.value, 2)
    M1_Q = (iec103.AsduType.MEASURANDS_1.value, 3)
    M2_I_L1 = (iec103.AsduType.MEASURANDS_2.value, 0)
    M2_I_L2 = (iec103.AsduType.MEASURANDS_2.value, 1)
    M2_I_L3 = (iec103.AsduType.MEASURANDS_2.value, 2)
    M2_U_L1E = (iec103.AsduType.MEASURANDS_2.value, 3)
    M2_U_L2E = (iec103.AsduType.MEASURANDS_2.value, 4)
    M2_U_L3E = (iec103.AsduType.MEASURANDS_2.value, 5)
    M2_P = (iec103.AsduType.MEASURANDS_2.value, 6)
    M2_Q = (iec103.AsduType.MEASURANDS_2.value, 7)
    M2_F = (iec103.AsduType.MEASURANDS_2.value, 8)


class MeasurandValues(typing.NamedTuple):
    values: dict[MeasurandType, MeasurandValue]


class Data(typing.NamedTuple):
    asdu_address: AsduAddress
    io_address: IoAddress
    cause: DataCause | OtherCause
    value: (DoubleWithTimeValue |
            DoubleWithRelativeTimeValue |
            MeasurandValues |
            MeasurandWithRelativeTimeValue)


class GenericData(typing.NamedTuple):
    asdu_address: AsduAddress
    io_address: IoAddress
    cause: GenericDataCause | OtherCause
    identification: Identification
    description: Description
    value: ArrayValue


time_from_datetime = iec103.time_from_datetime
time_to_datetime = iec103.time_to_datetime
