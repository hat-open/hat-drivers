import enum
import typing

from hat.drivers.iec60870.msgs import iec103


Bytes = iec103.common.Bytes
AsduAddress = iec103.common.AsduAddress
OtherCause = iec103.common.OtherCause
Description = iec103.common.Description
IoAddress = iec103.common.IoAddress
Identification = iec103.common.Identification
TimeSize = iec103.common.TimeSize
Time = iec103.common.Time

ValueType = iec103.common.ValueType
NoneValue = iec103.common.NoneValue
TextValue = iec103.common.TextValue
BitstringValue = iec103.common.BitstringValue
UIntValue = iec103.common.UIntValue
IntValue = iec103.common.IntValue
UFixedValue = iec103.common.UFixedValue
FixedValue = iec103.common.FixedValue
Real32Value = iec103.common.Real32Value
Real64Value = iec103.common.Real64Value
DoubleValue = iec103.common.DoubleValue
SingleValue = iec103.common.SingleValue
ExtendedDoubleValue = iec103.common.ExtendedDoubleValue
MeasurandValue = iec103.common.MeasurandValue
TimeValue = iec103.common.TimeValue
IdentificationValue = iec103.common.IdentificationValue
RelativeTimeValue = iec103.common.RelativeTimeValue
IoAddressValue = iec103.common.IoAddressValue
DoubleWithTimeValue = iec103.common.DoubleWithTimeValue
DoubleWithRelativeTimeValue = iec103.common.DoubleWithRelativeTimeValue
MeasurandWithRelativeTimeValue = iec103.common.MeasurandWithRelativeTimeValue
TextNumberValue = iec103.common.TextNumberValue
ReplyValue = iec103.common.ReplyValue
ArrayValue = iec103.common.ArrayValue
IndexValue = iec103.common.IndexValue
Value = iec103.common.Value


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
    values: typing.Dict[MeasurandType, MeasurandValue]


class Data(typing.NamedTuple):
    asdu_address: AsduAddress
    io_address: IoAddress
    cause: typing.Union[DataCause, OtherCause]
    value: typing.Union[DoubleWithTimeValue,
                        DoubleWithRelativeTimeValue,
                        MeasurandValues,
                        MeasurandWithRelativeTimeValue]


class GenericData(typing.NamedTuple):
    asdu_address: AsduAddress
    io_address: IoAddress
    cause: typing.Union[GenericDataCause, OtherCause]
    identification: Identification
    description: Description
    value: ArrayValue


time_from_datetime = iec103.common.time_from_datetime
time_to_datetime = iec103.common.time_to_datetime
