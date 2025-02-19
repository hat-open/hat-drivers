from collections.abc import Iterable
import contextlib

from hat import util
from hat.drivers import mms
from hat.drivers.tase2 import common


def encode_version(version: tuple[int, int]) -> mms.Data:
    return mms.StructureData([mms.IntegerData(version[0]),
                              mms.IntegerData(version[1])])


def decode_version(mms_data: mms.Data) -> tuple[int, int]:
    return mms_data.elements[0].value, mms_data.elements[1].value


def encode_supported_features(supported_features: Iterable[common.SupportedFeature]  # NOQA
                              ) -> mms.Data:
    value = [False] * 12

    for supported_feature in supported_features:
        value[supported_feature.value] = True

    return mms.BitStringData(value)


def decode_supported_features(mms_data: mms.Data
                              ) -> set[common.SupportedFeature]:
    supported_features = set()

    for i, value in enumerate(mms_data.value):
        if value:
            with contextlib.suppress(ValueError):
                supported_features.add(common.SupportedFeature(i))

    return supported_features


def encode_bilateral_table_id(bilateral_table_id: str) -> mms.Data:
    return mms.VisibleStringData(bilateral_table_id)


def decode_bilateral_table_id(mms_data: mms.Data) -> str:
    return mms_data.value


def encode_identifier(identifier: common.Identifier) -> mms.Data:
    if isinstance(identifier, common.VmdIdentifier):
        return mms.StructureData([
            mms.UnsignedData(0),
            mms.VisibleStringData(''),
            mms.VisibleStringData(identifier.name)])

    if isinstance(identifier, common.DomainIdentifier):
        return mms.StructureData([
            mms.UnsignedData(1),
            mms.VisibleStringData(identifier.domain),
            mms.VisibleStringData(identifier.name)])

    raise TypeError('unsupported identifier type')


def decode_identifier(mms_data: mms.Data) -> common.Identifier:
    if mms_data.elements[0].value == 0:
        return common.VmdIdentifier(mms_data.elements[2].value)

    if mms_data.elements[0].value == 1:
        return common.DomainIdentifier(
            name=mms_data.elements[2].value,
            domain=mms_data.elements[1].value)

    raise ValueError('unsupported scope value')


def encode_transferset(transferset: common.Transferset) -> mms.Data:
    return mms.StructureData([
        encode_identifier(transferset.dataset_identifier),
        mms.IntegerData(transferset.start_time),
        mms.IntegerData(transferset.interval),
        mms.IntegerData(transferset.tle),
        mms.IntegerData(transferset.buffer_time),
        mms.IntegerData(transferset.integrity_check),
        _encode_transferset_conditions(transferset.conditions),
        mms.BooleanData(transferset.block_data),
        mms.BooleanData(transferset.critical),
        mms.BooleanData(transferset.rbe),
        mms.BooleanData(transferset.all_changes_reported),
        mms.BooleanData(transferset.status),
        mms.IntegerData(transferset.event_code_requested)])


def decode_transferset(mms_data: mms.Data,
                       identifier: common.Identifier
                       ) -> common.Transferset:
    return common.Transferset(
        identifier=identifier,
        dataset_identifier=decode_identifier(mms_data.elements[0]),
        start_time=mms_data.elements[1].value,
        interval=mms_data.elements[2].value,
        tle=mms_data.elements[3].value,
        buffer_time=mms_data.elements[4].value,
        integrity_check=mms_data.elements[5].value,
        conditions=_decode_transferset_conditions(mms_data.elements[6]),
        block_data=mms_data.elements[7].value,
        critical=mms_data.elements[8].value,
        rbe=mms_data.elements[9].value,
        all_changes_reported=mms_data.elements[10].value,
        status=mms_data.elements[11].value,
        event_code_requested=mms_data.elements[12].value)


def encode_data(data: common.Data,
                data_type: common.DataType
                ) -> mms.Data:
    value = data.value
    quality = (
        data.quality if data.quality is not None
        else common.Quality(
            validity=common.Validity.VALID,
            source=common.Source.TELEMETERED,
            value=common.ValueQuality.NORMAL,
            timestamp=(common.TimestampQuality.VALID
                       if data.timestamp is not None
                       else common.TimestampQuality.INVALID)))
    timestamp = data.timestamp if data.timestamp is not None else 0
    cov = data.cov if data.cov is not None else 0

    if data_type.value == common.ValueType.REAL:
        mms_value = mms.FloatingPointData(value)

    elif data_type.value == common.ValueType.STATE:
        mms_value = mms.BitStringData([
            bool(int(value) & 2),
            bool(int(value) & 1),
            bool(quality.validity.value & 2),
            bool(quality.validity.value & 1),
            bool(quality.source.value & 2),
            bool(quality.source.value & 1),
            bool(quality.value.value),
            bool(quality.timestamp.value)])

    elif data_type.value == common.ValueType.DISCRETE:
        mms_value = mms.IntegerData(int(value))

    else:
        raise ValueError('unsupported value type')

    if data_type.quality == common.QualityType.NO_QUALITY:
        mms_quality = None

    elif data_type.value == common.ValueType.STATE:
        mms_quality = mms_value

    elif data_type.quality == common.QualityType.QUALITY:
        mms_quality = mms.BitStringData([
            False,
            False,
            bool(quality.validity.value & 2),
            bool(quality.validity.value & 1),
            bool(quality.source.value & 2),
            bool(quality.source.value & 1),
            bool(quality.value.value),
            bool(quality.timestamp.value)])

    else:
        raise ValueError('unsupported quality type')

    if data_type.timestamp == common.TimestampType.NO_TIMESTAMP:
        mms_timestamp = None

    elif data_type.timestamp == common.TimestampType.TIMESTAMP:
        mms_timestamp = mms.IntegerData(int(timestamp))

    elif data_type.timestamp == common.TimestampType.TIMESTAMP_EXTENDED:
        mms_timestamp = mms.StructureData([
            mms.IntegerData(int(timestamp)),
            mms.IntegerData(round((timestamp - int(timestamp)) * 1000))])

    else:
        raise ValueError('unsupported timestamp type')

    if data_type.cov == common.CovType.NO_COV:
        mms_cov = None

    elif data_type.cov == common.CovType.COV:
        mms_cov = mms.IntegerData(cov)

    else:
        raise ValueError('unsupported cov type')

    if (data_type.quality == common.QualityType.NO_QUALITY or
            (data_type.value == common.ValueType.STATE and
             data_type.timestamp == common.TimestampType.NO_TIMESTAMP)):
        return mms_value

    elements = []

    if data_type.value != common.ValueType.STATE:
        elements.append(mms_value)

    if mms_timestamp:
        elements.append(mms_timestamp)

    if mms_quality:
        elements.append(mms_quality)

    if mms_cov:
        elements.append(mms_cov)

    return mms.StructureData(elements)


def decode_data(mms_data: mms.Data,
                name: str,
                data_type: common.DataType
                ) -> common.Data:

    def get_element(index):
        if not isinstance(mms_data, mms.StructureData):
            raise TypeError('mms data is not structure')

        return mms_data.elements[index]

    if (data_type.quality == common.QualityType.NO_QUALITY or
            (data_type.value == common.ValueType.STATE and
             data_type.timestamp == common.TimestampType.NO_TIMESTAMP)):
        mms_value = mms_data

    elif data_type.value == common.ValueType.STATE:
        mms_value = get_element(1)

    else:
        mms_value = get_element(0)

    if (data_type.quality == common.QualityType.NO_QUALITY and
            data_type.value != common.ValueType.STATE):
        mms_quality = None

    elif (data_type.value == common.ValueType.STATE and
            data_type.timestamp == common.TimestampType.NO_TIMESTAMP):
        mms_quality = mms_data

    elif (data_type.value == common.ValueType.STATE or
            data_type.timestamp == common.TimestampType.NO_TIMESTAMP):
        mms_quality = get_element(1)

    else:
        mms_quality = get_element(2)

    if data_type.timestamp == common.TimestampType.NO_TIMESTAMP:
        mms_timestamp = None

    elif data_type.value == common.ValueType.STATE:
        mms_timestamp = get_element(0)

    else:
        mms_timestamp = get_element(1)

    if data_type.cov == common.CovType.NO_COV:
        mms_cov = None

    elif data_type.value == common.ValueType.STATE:
        mms_cov = get_element(2)

    else:
        mms_cov = get_element(3)

    if isinstance(mms_value, mms.FloatingPointData):
        value = mms_value.value

    elif isinstance(mms_value, mms.BitStringData):
        value = mms_value.value + ([False] * 2)
        value = (2 if value[0] else 0) | (1 if value[1] else 0)

    elif isinstance(mms_value, mms.IntegerData):
        value = mms_value.value

    else:
        raise TypeError('unsupported data value mms type')

    if isinstance(mms_quality, mms.BitStringData):
        quality = mms_quality.value + ([False] * 8)
        quality = common.Quality(
            validity=common.Validity((2 if quality[2] else 0) |
                                     (1 if quality[3] else 0)),
            source=common.Source((2 if quality[4] else 0) |
                                 (1 if quality[5] else 0)),
            value=common.ValueQuality(1 if quality[6] else 0),
            timestamp=common.TimestampQuality(1 if quality[6] else 0))

    else:
        quality = None

    timestamp = None

    if isinstance(mms_timestamp, mms.IntegerData):
        timestamp = mms_timestamp.value

    elif isinstance(mms_timestamp, mms.StructureData):
        timestamp = (mms_timestamp.elements[0].value +
                     mms_timestamp.elements[1].value / 1000)

    else:
        timestamp = None

    if isinstance(mms_cov, mms.IntegerData):
        cov = mms_cov.value

    else:
        cov = None

    return common.Data(name=name,
                       value=value,
                       quality=quality,
                       timestamp=timestamp,
                       cov=cov)


def encode_data_type(data_type: common.DataType) -> mms.Data:
    value = data_type.value
    quality = data_type.quality
    timestamp = data_type.timestamp
    cov = data_type.cov

    if value == common.ValueType.REAL:
        mms_value = mms.FloatingPointTypeDescription(format_width=32,
                                                     exponent_width=8)

    elif value == common.ValueType.STATE:
        mms_value = mms.BitStringTypeDescription(8)

    elif value == common.ValueType.DISCRETE:
        mms_value = mms.IntegerTypeDescription(32)

    else:
        raise ValueError('unsupported value type')

    if quality == common.QualityType.NO_QUALITY:
        mms_quality = None

    elif quality == common.QualityType.QUALITY:
        mms_quality = mms.BitStringTypeDescription(8)

    else:
        raise ValueError('unsupported quality type')

    if timestamp == common.TimestampType.NO_TIMESTAMP:
        mms_timestamp = None

    elif timestamp == common.TimestampType.TIMESTAMP:
        mms_timestamp = mms.IntegerTypeDescription(32)

    elif timestamp == common.TimestampType.TIMESTAMP_EXTENDED:
        mms_timestamp = mms.StructureTypeDescription([
            ('GMTBasedS', mms.IntegerTypeDescription(32)),
            ('Milliseconds', mms.IntegerTypeDescription(16))])

    else:
        raise ValueError('unsupported timestamp type')

    if cov == common.CovType.NO_COV:
        mms_cov = None

    elif cov == common.CovType.COV:
        mms_cov = mms.UnsignedTypeDescription(16)

    else:
        raise ValueError('unsupported cov type')

    if (not mms_quality or
            (value == common.ValueType.STATE and
             timestamp == common.TimestampType.NO_TIMESTAMP)):
        return mms_value

    components = []

    if value != common.ValueType.STATE:
        components.append(('Value', mms_value))

    if mms_timestamp:
        components.append(('TimeStamp', mms_timestamp))

    components.append(('Flags', mms_quality))

    if mms_cov:
        components.append(('COV', mms_cov))

    return mms.StructureTypeDescription(components)


def decode_data_type(mms_type: mms.Data) -> common.DataType:

    def get_component_type(components, name):
        component = util.first(components, lambda i: i[0] == name)
        return component[1] if component else None

    if isinstance(mms_type, mms.StructureTypeDescription):
        components = mms_type.components
        mms_value = get_component_type(components, 'Value')
        mms_quality = get_component_type(components, 'Flags')
        mms_timestamp = get_component_type(components, 'TimeStamp')

        if not mms_timestamp:
            mms_timestamp = get_component_type(components, 'TimeStampEx')

        if not mms_timestamp:
            mms_timestamp = get_component_type(components, 'XSTimeStamp')

        mms_cov = get_component_type(components, 'COV')

        if not mms_value:
            mms_value = mms_quality

    else:
        mms_value = mms_type
        mms_quality = mms_type
        mms_timestamp = None
        mms_cov = None

    if mms_value == mms.FloatingPointTypeDescription(format_width=32,
                                                     exponent_width=8):
        value = common.ValueType.REAL

    elif mms_value == mms.BitStringTypeDescription(8):
        value = common.ValueType.STATE

    elif mms_value == mms.IntegerTypeDescription(32):
        value = common.ValueType.DISCRETE

    else:
        raise Exception('unsupported value type')

    if mms_quality == mms.BitStringTypeDescription(8):
        quality = common.QualityType.QUALITY

    else:
        quality = common.QualityType.NO_QUALITY

    if mms_timestamp == mms.IntegerTypeDescription(32):
        timestamp = common.TimestampType.TIMESTAMP

    elif mms_timestamp == mms.StructureTypeDescription([
            ('GMTBasedS', mms.IntegerTypeDescription(32)),
            ('Milliseconds', mms.IntegerTypeDescription(16))]):
        timestamp = common.TimestampType.TIMESTAMP_EXTENDED

    elif mms_timestamp == mms.StructureTypeDescription([
            ('XSGMTBasedS', mms.IntegerTypeDescription(32)),
            ('Milliseconds', mms.IntegerTypeDescription(16))]):
        timestamp = common.TimestampType.TIMESTAMP_EXTENDED

    else:
        timestamp = common.TimestampType.NO_TIMESTAMP

    if mms_cov == mms.UnsignedTypeDescription(16):
        cov = common.CovType.COV

    else:
        cov = common.CovType.NO_COV

    return common.DataType(value=value,
                           quality=quality,
                           timestamp=timestamp,
                           cov=cov)


def _encode_transferset_conditions(conditions):
    value = [False] * 5

    for supported_feature in conditions:
        value[supported_feature.value] = True

    return mms.BitStringData(value)


def _decode_transferset_conditions(mms_data):
    conditions = set()

    for i, value in enumerate(mms_data.value):
        if value:
            with contextlib.suppress(ValueError):
                conditions.add(common.TransfersetCondition(i))

    return conditions
