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
