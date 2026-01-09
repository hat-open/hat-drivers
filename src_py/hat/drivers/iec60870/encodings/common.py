import datetime
import enum
import time
import typing


class AsduTypeError(Exception):
    pass


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
    invalid: bool | None
    """available for size THREE, FOUR, SEVEN"""
    substituted: bool | None
    """available for size THREE, FOUR, SEVEN"""
    minutes: int | None
    """available for size THREE, FOUR, SEVEN (minutes in range [0, 59])"""
    summer_time: bool | None
    """available for size FOUR, SEVEN"""
    hours: int | None
    """available for size FOUR, SEVEN (hours in range [0, 23])"""
    day_of_week: int | None
    """available for size SEVEN (day_of_week in range [1, 7])"""
    day_of_month: int | None
    """available for size SEVEN (day_of_month in range [1, 31])"""
    months: int | None
    """available for size SEVEN (months in range [1, 12])"""
    years: int | None
    """available for size SEVEN (years in range [0, 99])"""


class IO(typing.NamedTuple):
    address: int
    elements: list
    time: Time | None


class ASDU(typing.NamedTuple):
    type: int
    cause: int
    address: int
    ios: list[IO]


def time_from_datetime(dt: datetime.datetime,
                       invalid: bool = False,
                       substituted: bool = False
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
        substituted=substituted,
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
    # TODO support TimeSize.FOUR
    if t.size == TimeSize.TWO:
        local_now = datetime.datetime.now()
        local_dt = local_now.replace(
            second=int(t.milliseconds / 1000),
            microsecond=(t.milliseconds % 1000) * 1000)

        local_seconds = local_now.second + local_now.microsecond / 1_000_000
        t_seconds = t.milliseconds / 1_000

        if abs(local_seconds - t_seconds) > 30:
            if local_seconds < t_seconds:
                local_dt = local_dt - datetime.timedelta(minutes=1)

            else:
                local_dt = local_dt + datetime.timedelta(minutes=1)

    elif t.size == TimeSize.THREE:
        local_now = datetime.datetime.now()
        local_dt = local_now.replace(
            minute=t.minutes,
            second=int(t.milliseconds / 1000),
            microsecond=(t.milliseconds % 1000) * 1000)

        local_minutes = (local_now.minute +
                         local_now.second / 60 +
                         local_now.microsecond / 60_000_000)
        t_minutes = t.minutes + t.milliseconds / 60_000

        if abs(local_minutes - t_minutes) > 30:
            if local_minutes < t_minutes:
                local_dt = local_dt - datetime.timedelta(hours=1)

            else:
                local_dt = local_dt + datetime.timedelta(hours=1)

    elif t.size == TimeSize.SEVEN:
        local_dt = datetime.datetime(
            year=2000 + t.years if t.years < 70 else 1900 + t.years,
            month=t.months,
            day=t.day_of_month,
            hour=t.hours,
            minute=t.minutes,
            second=int(t.milliseconds / 1000),
            microsecond=(t.milliseconds % 1000) * 1000,
            fold=not t.summer_time)

    else:
        raise ValueError('unsupported time size')

    return local_dt.astimezone(tz=datetime.timezone.utc)
