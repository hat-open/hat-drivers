import enum
import typing

from hat.drivers.iec60870 import app


Bytes = app.iec103.common.Bytes
AsduAddress = app.iec103.common.AsduAddress
OtherCause = app.iec103.common.OtherCause
Description = app.iec103.common.Description
IoAddress = app.iec103.common.IoAddress
Identification = app.iec103.common.Identification
TimeSize = app.iec103.common.TimeSize
Time = app.iec103.common.Time

ValueType = app.iec103.common.ValueType
NoneValue = app.iec103.common.NoneValue
TextValue = app.iec103.common.TextValue
BitstringValue = app.iec103.common.BitstringValue
UIntValue = app.iec103.common.UIntValue
IntValue = app.iec103.common.IntValue
UFixedValue = app.iec103.common.UFixedValue
FixedValue = app.iec103.common.FixedValue
Real32Value = app.iec103.common.Real32Value
Real64Value = app.iec103.common.Real64Value
DoubleValue = app.iec103.common.DoubleValue
SingleValue = app.iec103.common.SingleValue
ExtendedDoubleValue = app.iec103.common.ExtendedDoubleValue
MeasurandValue = app.iec103.common.MeasurandValue
TimeValue = app.iec103.common.TimeValue
IdentificationValue = app.iec103.common.IdentificationValue
RelativeTimeValue = app.iec103.common.RelativeTimeValue
IoAddressValue = app.iec103.common.IoAddressValue
DoubleWithTimeValue = app.iec103.common.DoubleWithTimeValue
DoubleWithRelativeTimeValue = app.iec103.common.DoubleWithRelativeTimeValue
MeasurandWithRelativeTimeValue = app.iec103.common.MeasurandWithRelativeTimeValue  # NOQA
TextNumberValue = app.iec103.common.TextNumberValue
ReplyValue = app.iec103.common.ReplyValue
ArrayValue = app.iec103.common.ArrayValue
IndexValue = app.iec103.common.IndexValue
Value = app.iec103.common.Value


class DataCause(enum.Enum):
    SPONTANEOUS = app.iec103.common.Cause.SPONTANEOUS.value
    CYCLIC = app.iec103.common.Cause.CYCLIC.value
    TEST_MODE = app.iec103.common.Cause.TEST_MODE.value
    GENERAL_INTERROGATION = app.iec103.common.Cause.GENERAL_INTERROGATION.value
    LOCAL_OPERATION = app.iec103.common.Cause.LOCAL_OPERATION.value
    REMOTE_OPERATION = app.iec103.common.Cause.REMOTE_OPERATION.value


class GenericDataCause(enum.Enum):
    SPONTANEOUS = app.iec103.common.Cause.SPONTANEOUS.value
    CYCLIC = app.iec103.common.Cause.CYCLIC.value
    TEST_MODE = app.iec103.common.Cause.TEST_MODE.value
    GENERAL_INTERROGATION = app.iec103.common.Cause.GENERAL_INTERROGATION.value
    LOCAL_OPERATION = app.iec103.common.Cause.LOCAL_OPERATION.value
    REMOTE_OPERATION = app.iec103.common.Cause.REMOTE_OPERATION.value
    WRITE_ACK = app.iec103.common.Cause.GENERIC_WRITE_COMMAND.value
    WRITE_NACK = app.iec103.common.Cause.GENERIC_WRITE_COMMAND_NACK.value
    READ_ACK = app.iec103.common.Cause.GENERIC_READ_COMMAND.value
    READ_NACK = app.iec103.common.Cause.GENERIC_READ_COMMAND_NACK.value
    WRITE_CONFIRMATION = app.iec103.common.Cause.GENERIC_WRITE_CONFIRMATION.value  # NOQA


class MeasurandType(enum.Enum):
    M1_I_L2 = (app.iec103.common.AsduType.MEASURANDS_1.value, 0)
    M1_U_L12 = (app.iec103.common.AsduType.MEASURANDS_1.value, 1)
    M1_P = (app.iec103.common.AsduType.MEASURANDS_1.value, 2)
    M1_Q = (app.iec103.common.AsduType.MEASURANDS_1.value, 3)
    M2_I_L1 = (app.iec103.common.AsduType.MEASURANDS_2.value, 0)
    M2_I_L2 = (app.iec103.common.AsduType.MEASURANDS_2.value, 1)
    M2_I_L3 = (app.iec103.common.AsduType.MEASURANDS_2.value, 2)
    M2_U_L1E = (app.iec103.common.AsduType.MEASURANDS_2.value, 3)
    M2_U_L2E = (app.iec103.common.AsduType.MEASURANDS_2.value, 4)
    M2_U_L3E = (app.iec103.common.AsduType.MEASURANDS_2.value, 5)
    M2_P = (app.iec103.common.AsduType.MEASURANDS_2.value, 6)
    M2_Q = (app.iec103.common.AsduType.MEASURANDS_2.value, 7)
    M2_F = (app.iec103.common.AsduType.MEASURANDS_2.value, 8)


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


time_from_datetime = app.iec103.common.time_from_datetime
time_to_datetime = app.iec103.common.time_to_datetime
