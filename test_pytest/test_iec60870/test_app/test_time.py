from hat.drivers.iec60870.app.iec101 import common
from hat.drivers.iec60870.app.encoder import decode_time, encode_time


def test_time():
    time = common.Time(size=common.TimeSize.SEVEN,
                       milliseconds=1,
                       invalid=False,
                       minutes=42,
                       summer_time=True,
                       hours=12,
                       day_of_week=1,
                       day_of_month=13,
                       months=12,
                       years=22)
    time_enc = bytes(encode_time(time, time_size=common.TimeSize.SEVEN))
    assert time == decode_time(time_enc, time_size=common.TimeSize.SEVEN)
