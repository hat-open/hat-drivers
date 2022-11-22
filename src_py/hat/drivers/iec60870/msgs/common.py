import datetime
import enum
import time
import typing


Bytes = typing.Union[bytes, bytearray, memoryview]


class CauseSize(enum.Enum):
    ONE = 1
    TWO = 2


class AsduAddressSize(enum.Enum):
    ONE = 1
    TWO = 2


class IoAddressSize(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class TimeSize(enum.Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    SEVEN = 7


class Time(typing.NamedTuple):
    size: TimeSize
    milliseconds: int
    """milliseconds in range [0, 59999]"""
    invalid: typing.Optional[bool]
    """available for size THREE, FOUR, SEVEN"""
    minutes: typing.Optional[int]
    """available for size THREE, FOUR, SEVEN (minutes in range [0, 59])"""
    summer_time: typing.Optional[bool]
    """available for size FOUR, SEVEN"""
    hours: typing.Optional[int]
    """available for size FOUR, SEVEN (hours in range [0, 23])"""
    day_of_week: typing.Optional[int]
    """available for size SEVEN (day_of_week in range [1, 7])"""
    day_of_month: typing.Optional[int]
    """available for size SEVEN (day_of_month in range [1, 31])"""
    months: typing.Optional[int]
    """available for size SEVEN (months in range [1, 12])"""
    years: typing.Optional[int]
    """available for size SEVEN (years in range [0, 99])"""


class IO(typing.NamedTuple):
    address: int
    elements: typing.List
    time: typing.Optional[Time]


class ASDU(typing.NamedTuple):
    type: int
    cause: int
    address: int
    ios: typing.List[IO]


def time_from_datetime(dt: datetime.datetime,
                       invalid: bool = False
                       ) -> Time:
    """Create Time from datetime.datetime"""
    # TODO document edge cases (local time, os implementation, ...)
    #  rounding microseconds to the nearest millisecond
    dt_rounded = (
        dt.replace(microsecond=0) +
        datetime.timedelta(milliseconds=round(dt.microsecond / 1000)))
    local_time = time.localtime(dt_rounded.timestamp())
    return Time(
        size=TimeSize.SEVEN,
        milliseconds=(local_time.tm_sec * 1000 +
                      dt_rounded.microsecond // 1000),
        invalid=invalid,
        minutes=local_time.tm_min,
        summer_time=bool(local_time.tm_isdst),
        hours=local_time.tm_hour,
        day_of_week=local_time.tm_wday + 1,
        day_of_month=local_time.tm_mday,
        months=local_time.tm_mon,
        years=local_time.tm_year % 100)


def time_to_datetime(t: Time
                     ) -> datetime.datetime:
    """Convert Time to datetime.datetime"""
    # TODO document edge cases (local time, os implementation, ...)
    # TODO maybe allow diferent time size (use now for time)
    if t.size != TimeSize.SEVEN:
        raise ValueError('unsupported time size')
    local_dt = datetime.datetime(
        year=2000 + t.years if t.years < 70 else 1900 + t.years,
        month=t.months,
        day=t.day_of_month,
        hour=t.hours,
        minute=t.minutes,
        second=int(t.milliseconds / 1000),
        microsecond=(t.milliseconds % 1000) * 1000,
        fold=not t.summer_time)
    return local_dt.astimezone(tz=datetime.timezone.utc)
