import datetime

import pytest

from hat.drivers.iec60870.app.iec101 import common
from hat.drivers.iec60870.app.encoder import decode_time, encode_time


def create_time(size, milliseconds, invalid, minutes, summer_time, hours,
                day_of_week, day_of_month, months, years):
    return common.Time(
        size=size,
        milliseconds=milliseconds,
        invalid=invalid if size in [common.TimeSize.THREE,
                                    common.TimeSize.FOUR,
                                    common.TimeSize.SEVEN] else None,
        minutes=minutes if size in [common.TimeSize.THREE,
                                    common.TimeSize.FOUR,
                                    common.TimeSize.SEVEN] else None,
        summer_time=summer_time if size in [common.TimeSize.FOUR,
                                            common.TimeSize.SEVEN] else None,
        hours=hours if size in [common.TimeSize.FOUR,
                                common.TimeSize.SEVEN] else None,
        day_of_week=day_of_week if size == common.TimeSize.SEVEN else None,
        day_of_month=day_of_month if size == common.TimeSize.SEVEN else None,
        months=months if size == common.TimeSize.SEVEN else None,
        years=years if size == common.TimeSize.SEVEN else None)


@pytest.mark.parametrize('size', list(common.TimeSize))
@pytest.mark.parametrize('encode_size', list(common.TimeSize))
@pytest.mark.parametrize('decode_size', list(common.TimeSize))
@pytest.mark.parametrize(
    "milliseconds, invalid, minutes, summer_time, hours, day_of_week, "
    "day_of_month, months, years", [
        (1, False, 42, True, 12, 1, 13, 12, 22),
        (0, True, 0, True, 0, 1, 1, 1, 0),
        (59999, False, 59, False, 23, 7, 31, 12, 99),
        ])
def test_time(size, encode_size, decode_size, milliseconds, invalid, minutes,
              summer_time, hours, day_of_week, day_of_month, months, years):
    time = create_time(size, milliseconds, invalid, minutes, summer_time,
                       hours, day_of_week, day_of_month, months, years)
    time_exp = create_time(
        decode_size, milliseconds, invalid, minutes, summer_time,
        hours, day_of_week, day_of_month, months, years)

    if encode_size.value > size.value:
        with pytest.raises(ValueError):
            bytes(encode_time(time, time_size=encode_size))
    else:
        time_enc = bytes(encode_time(time, time_size=encode_size))
        if decode_size.value > encode_size.value:
            with pytest.raises(Exception):
                decode_time(time_enc, time_size=decode_size)
        else:
            time_decoded = decode_time(time_enc, time_size=decode_size)
            assert time_decoded == time_exp


@pytest.mark.parametrize("invalid", [True, False])
def test_time_from_to_datetime(invalid):
    dtime_local = datetime.datetime.now()
    dtime = dtime_local.astimezone(datetime.timezone.utc)
    dtime = dtime.replace(
        microsecond=round(dtime.microsecond / 1000) * 1000)
    t_60870 = common.time_from_datetime(dtime, invalid=invalid)
    assert t_60870.invalid is invalid
    assert t_60870.minutes == dtime_local.minute
    assert t_60870.hours == dtime_local.hour
    assert t_60870.months == dtime_local.month
    assert t_60870.size is common.TimeSize.SEVEN

    dt_from_to = common.time_to_datetime(t_60870)
    assert dtime == dt_from_to


def test_time_to_datetime_exception():
    t_60870 = common.time_from_datetime(
        datetime.datetime.now(datetime.timezone.utc))
    for size in [common.TimeSize.TWO,
                 common.TimeSize.THREE,
                 common.TimeSize.FOUR]:
        with pytest.raises(ValueError):
            common.time_to_datetime(t_60870._replace(size=size))
