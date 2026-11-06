import enum
import typing

from hat import util

from hat.drivers.tls import common
from hat.drivers.tls.l4 import fg1, fg254


class Status(typing.NamedTuple):
    overcharge_protection_not_addressed: bool
    total_discharge_protection_not_waiting: bool


class DataType(enum.Enum):
    ERROR = 1
    ADDITIONAL_ERROR = 14
    NEGATIVE_ACKNOWLEDGEMENT = 16
    CHANNEL_CONTROL = 29
    TIME_STAMP = 30
    OPERATING_PARAMETERS = 32
    GEOGRAPHICAL_CHARACTERISTICS = 36
    DOOR_CONTACT = 48
    TEMPERATURE_MONITORING = 49
    LIGHT = 50
    POWER_SUPPLY = 51
    HEATING = 52
    VENTILATION = 53
    EXCESS_VOLTAGE_PROTECTION = 54
    THEFT_VANDALISM_PROTECTION = 55
    REMOTE_MONITORING_SOLAR_UNITS = 56


ErrorData: typing.TypeAlias = fg254.ErrorData


AdditionalErrorData: typing.TypeAlias = fg254.AdditionalErrorData


NegativeAcknowledgementData: typing.TypeAlias = fg254.NegativeAcknowledgementData # NOQA


ChannelControlData: typing.TypeAlias = fg1.ChannelControlData


TimeStampData: typing.TypeAlias = fg254.TimeStampData


class OperatingParametersData(typing.NamedTuple):
    acquisition_period_seconds: common.UInt16
    transmission_procedure: common.UInt8


GeographicalCharacteristicsData: typing.TypeAlias = fg254.GeographicalCharacteristicsData # NOQA


class DoorContactData(typing.NamedTuple):
    open: bool


class TemperatureMonitoringData(typing.NamedTuple):
    monitoring_defective: bool
    above_range: bool
    below_range: bool


class LightData(typing.NamedTuple):
    switched_on: bool


class PowerSupplyData(typing.NamedTuple):
    power_failed: bool
    ups_defective: bool
    battery_empty: bool
    battery_overcharged: bool
    FI_protective_switch_triggered: bool


class HeatingData(typing.NamedTuple):
    defective: bool
    switched_on: bool


class VentilationData(typing.NamedTuple):
    defective: bool
    switched_on: bool


class ExcessVoltageProtectionData(typing.NamedTuple):
    defective: bool


class TheftVandalismProtectionData(typing.NamedTuple):
    alarm: bool


class RemoteMonitoringSolarUnitsData(typing.NamedTuple):
    status: Status
    charging_voltage: common.UInt8
    charging_current: common.UInt8


Data: typing.TypeAlias = (ErrorData |
                          AdditionalErrorData |
                          NegativeAcknowledgementData |
                          ChannelControlData |
                          TimeStampData |
                          OperatingParametersData |
                          GeographicalCharacteristicsData |
                          DoorContactData |
                          TemperatureMonitoringData |
                          LightData |
                          PowerSupplyData |
                          HeatingData |
                          VentilationData |
                          ExcessVoltageProtectionData |
                          TheftVandalismProtectionData |
                          RemoteMonitoringSolarUnitsData)


def encode(data: Data) -> util.Bytes:
    if isinstance(data, ErrorData):
        return fg254.encode(data)

    if isinstance(data, AdditionalErrorData):
        return fg254.encode(data)

    if isinstance(data, NegativeAcknowledgementData):
        return fg254.encode(data)

    if isinstance(data, ChannelControlData):
        return fg1.encode(data)

    if isinstance(data, TimeStampData):
        return fg254.encode(data)

    if isinstance(data, OperatingParametersData):
        return bytes([data.acquisition_period_seconds & 0xFF,
                      data.acquisition_perdio_seconds >> 8,
                      data.transmission_procedure])

    if isinstance(data, GeographicalCharacteristicsData):
        return fg254.encode(data)

    if isinstance(data, DoorContactData):
        return bytes([data.status])

    if isinstance(data, TemperatureMonitoringData):
        return bytes([data.monitoring_defective,
                      data.above_range << 1,
                      data.below_range << 2])

    if isinstance(data, LightData):
        return bytes([data.switched_on])

    if isinstance(data, PowerSupplyData):
        return bytes([data.power_failed,
                      data.ups_defective << 1,
                      data.battery_empty << 2,
                      data.battery_overcharged << 3,
                      data.FI_protective_switch_triggered << 4])

    if isinstance(data, HeatingData):
        return bytes([data.defective,
                      data.switched_on << 1])

    if isinstance(data, VentilationData):
        return bytes([data.defective,
                      data.switched_on << 1])

    if isinstance(data, ExcessVoltageProtectionData):
        return bytes([data.defective])

    if isinstance(data, TheftVandalismProtectionData):
        return bytes([data.alarm])

    if isinstance(data, RemoteMonitoringSolarUnitsData):
        return bytes([data.status.overcharge_protection_not_addressed,
                      data.status.total_discharge_protection_not_waiting << 1,
                      data.charging_voltage << 2,
                      data.charging_current << 3])

    raise ValueError('unsupported data type')


def decode(data_type: DataType, data: util.Bytes) -> Data:
    if data_type == DataType.ERROR:
        return fg254.decode(fg254.DataType.ERROR, data)

    if data_type == DataType.ADDITIONAL_ERROR:
        return fg254.decode(fg254.DataType.ADDITIONAL_ERROR, data)

    if data_type == DataType.NEGATIVE_ACKNOWLEDGEMENT:
        return fg254.decode(fg254.DataType.NEGATIVE_ACKNOWLEDGEMENT, data)

    if data_type == DataType.CHANNEL_CONTROL:
        return fg1.decode(fg1.DataType.CHANNEL_CONTROL, data)

    if data_type == DataType.TIME_STAMP:
        return fg254.decode(fg254.DataType.TIME_STAMP, data)

    if data_type == DataType.OPERATING_PARAMETERS:
        acquisition_period_seconds = (data[1] << 8) | data[0]
        transmission_procedure = data[2]

        return OperatingParametersData(
                acquisition_period_seconds=acquisition_period_seconds,
                transmission_procedure=transmission_procedure)

    if data_type == DataType.GEOGRAPHICAL_CHARACTERISTICS:
        return fg254.decode(fg254.DataType.GEOGRAPHICAL_CHARACTERISTICS, data)

    if data_type == DataType.DOOR_CONTACT:
        open = bool(data[0] & 0x01)

        return DoorContactData(open=open)

    if data_type == DataType.TEMPERATURE_MONITORING:
        monitoring_defective = bool(data[0] & 0x01)
        above_range = bool(data[0] & 0x02)
        below_range = bool(data[0] & 0x04)

        return TemperatureMonitoringData(
                monitoring_defective=monitoring_defective,
                above_range=above_range,
                below_range=below_range)

    if data_type == DataType.LIGHT:
        switched_on = bool(data[0] & 0x01)

        return LightData(switched_on=switched_on)

    if data_type == DataType.POWER_SUPPLY:
        power_failed = bool(data[0] & 0x01)
        ups_defective = bool(data[0] & 0x02)
        battery_empty = bool(data[0] & 0x04)
        battery_overcharged = bool(data[0] & 0x08)
        FI_protective_switch_triggered = bool(data[0] & 0x10)

        return PowerSupplyData(
                power_failed=power_failed,
                ups_defective=ups_defective,
                battery_empty=battery_empty,
                battery_overcharged=battery_overcharged,
                FI_protective_switch_triggered=FI_protective_switch_triggered)

    if data_type == DataType.HEATING:
        heating_defective = bool(data[0] & 0x01)
        switched_on = bool(data[0] & 0x02)

        return HeatingData(defective=heating_defective,
                           switched_on=switched_on)

    if data_type == DataType.VENTILATION:
        ventilation_defective = bool(data[0] & 0x01)
        switched_on = bool(data[0] & 0x02)

        return VentilationData(defective=ventilation_defective,
                               switched_on=switched_on)

    if data_type == DataType.EXCESS_VOLTAGE_PROTECTION:
        defective = bool(data[0] & 0x01)

        return ExcessVoltageProtectionData(defective=defective)

    if data_type == DataType.THEFT_VANDALISM_PROTECTION:
        alarm = bool(data[0] & 0x01)

        return TheftVandalismProtectionData(alarm=alarm)

    if data_type == DataType.REMOTE_MONITORING_SOLAR_UNITS:
        overcharge_protection_not_addressed = bool(data[0] & 0x01)
        total_discharge_protection_not_waiting = bool(data[0] & 0x02)
        charging_voltage = data[1]
        charging_current = data[2]

        return RemoteMonitoringSolarUnitsData(
                status=Status(overcharge_protection_not_addressed,
                              total_discharge_protection_not_waiting),
                charging_voltage=charging_voltage,
                charging_current=charging_current)

    raise ValueError('unsupported data type')
