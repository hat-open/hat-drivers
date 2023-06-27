import enum
import typing

from hat.drivers.iec60870.msgs import iec103


AsduAddress: typing.TypeAlias = iec103.common.AsduAddress
OtherCause: typing.TypeAlias = iec103.common.OtherCause
Description: typing.TypeAlias = iec103.common.Description
IoAddress: typing.TypeAlias = iec103.common.IoAddress
Identification: typing.TypeAlias = iec103.common.Identification
TimeSize: typing.TypeAlias = iec103.common.TimeSize
Time: typing.TypeAlias = iec103.common.Time

ValueType: typing.TypeAlias = iec103.common.ValueType
NoneValue: typing.TypeAlias = iec103.common.NoneValue
TextValue: typing.TypeAlias = iec103.common.TextValue
BitstringValue: typing.TypeAlias = iec103.common.BitstringValue
UIntValue: typing.TypeAlias = iec103.common.UIntValue
IntValue: typing.TypeAlias = iec103.common.IntValue
UFixedValue: typing.TypeAlias = iec103.common.UFixedValue
FixedValue: typing.TypeAlias = iec103.common.FixedValue
Real32Value: typing.TypeAlias = iec103.common.Real32Value
Real64Value: typing.TypeAlias = iec103.common.Real64Value
DoubleValue: typing.TypeAlias = iec103.common.DoubleValue
SingleValue: typing.TypeAlias = iec103.common.SingleValue
ExtendedDoubleValue: typing.TypeAlias = iec103.common.ExtendedDoubleValue
MeasurandValue: typing.TypeAlias = iec103.common.MeasurandValue
TimeValue: typing.TypeAlias = iec103.common.TimeValue
IdentificationValue: typing.TypeAlias = iec103.common.IdentificationValue
RelativeTimeValue: typing.TypeAlias = iec103.common.RelativeTimeValue
IoAddressValue: typing.TypeAlias = iec103.common.IoAddressValue
DoubleWithTimeValue: typing.TypeAlias = iec103.common.DoubleWithTimeValue
DoubleWithRelativeTimeValue: typing.TypeAlias = iec103.common.DoubleWithRelativeTimeValue  # NOQA
MeasurandWithRelativeTimeValue: typing.TypeAlias = iec103.common.MeasurandWithRelativeTimeValue  # NOQA
TextNumberValue: typing.TypeAlias = iec103.common.TextNumberValue
ReplyValue: typing.TypeAlias = iec103.common.ReplyValue
ArrayValue: typing.TypeAlias = iec103.common.ArrayValue
IndexValue: typing.TypeAlias = iec103.common.IndexValue
Value: typing.TypeAlias = iec103.common.Value


class DataCause(enum.Enum):
    SPONTANEOUS = iec103.common.Cause.SPONTANEOUS.value
    CYCLIC = iec103.common.Cause.CYCLIC.value
    TEST_MODE = iec103.common.Cause.TEST_MODE.value
    GENERAL_INTERROGATION = iec103.common.Cause.GENERAL_INTERROGATION.value
    LOCAL_OPERATION = iec103.common.Cause.LOCAL_OPERATION.value
    REMOTE_OPERATION = iec103.common.Cause.REMOTE_OPERATION.value


class GenericDataCause(enum.Enum):
    SPONTANEOUS = iec103.common.Cause.SPONTANEOUS.value
    CYCLIC = iec103.common.Cause.CYCLIC.value
    TEST_MODE = iec103.common.Cause.TEST_MODE.value
    GENERAL_INTERROGATION = iec103.common.Cause.GENERAL_INTERROGATION.value
    LOCAL_OPERATION = iec103.common.Cause.LOCAL_OPERATION.value
    REMOTE_OPERATION = iec103.common.Cause.REMOTE_OPERATION.value
    WRITE_ACK = iec103.common.Cause.GENERIC_WRITE_COMMAND.value
    WRITE_NACK = iec103.common.Cause.GENERIC_WRITE_COMMAND_NACK.value
    READ_ACK = iec103.common.Cause.GENERIC_READ_COMMAND.value
    READ_NACK = iec103.common.Cause.GENERIC_READ_COMMAND_NACK.value
    WRITE_CONFIRMATION = iec103.common.Cause.GENERIC_WRITE_CONFIRMATION.value


class MeasurandType(enum.Enum):
    M1_I_L2 = (iec103.common.AsduType.MEASURANDS_1.value, 0)
    M1_U_L12 = (iec103.common.AsduType.MEASURANDS_1.value, 1)
    M1_P = (iec103.common.AsduType.MEASURANDS_1.value, 2)
    M1_Q = (iec103.common.AsduType.MEASURANDS_1.value, 3)
    M2_I_L1 = (iec103.common.AsduType.MEASURANDS_2.value, 0)
    M2_I_L2 = (iec103.common.AsduType.MEASURANDS_2.value, 1)
    M2_I_L3 = (iec103.common.AsduType.MEASURANDS_2.value, 2)
    M2_U_L1E = (iec103.common.AsduType.MEASURANDS_2.value, 3)
    M2_U_L2E = (iec103.common.AsduType.MEASURANDS_2.value, 4)
    M2_U_L3E = (iec103.common.AsduType.MEASURANDS_2.value, 5)
    M2_P = (iec103.common.AsduType.MEASURANDS_2.value, 6)
    M2_Q = (iec103.common.AsduType.MEASURANDS_2.value, 7)
    M2_F = (iec103.common.AsduType.MEASURANDS_2.value, 8)


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


time_from_datetime = iec103.common.time_from_datetime
time_to_datetime = iec103.common.time_to_datetime
