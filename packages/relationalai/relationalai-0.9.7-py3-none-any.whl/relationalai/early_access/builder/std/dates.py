from __future__ import annotations
from typing import Any, Union, Literal
import datetime as dt

from .. import std
from .. import builder as b

_Date = Union[b.Producer, dt.date]
_DateTime = Union[b.Producer, dt.datetime]
_Period = Union[b.Producer, int]
# TODO support DateTime below as well, but this needs e.g. Rel `datetime_year`

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

def year(date: _Date) -> b.Expression:
    return _make_expr("date_year", date, b.Int64.ref("res"))

def month(date: _Date) -> b.Expression:
    return _make_expr("date_month", date, b.Int64.ref("res"))

def day(date: _Date) -> b.Expression:
    return _make_expr("date_day", date, b.Int64.ref("res"))

def dates_period_days(start: _Date, end: _Date) -> b.Expression:
    return _make_expr("dates_period_days", start, end, b.Int64.ref("res"))

def datetimes_period_milliseconds(start: _DateTime, end: _DateTime) -> b.Expression:
    return _make_expr("datetimes_period_milliseconds", start, end, b.Int64.ref("res"))
#--------------------------------------------------
# Periods
#--------------------------------------------------
def milliseconds(period: _Period) -> b.Expression:
    return _make_expr("millisecond", period, b.Int64.ref("res"))

def seconds(period: _Period) -> b.Expression:
    return _make_expr("second", period, b.Int64.ref("res"))

def minutes(period: _Period) -> b.Expression:
    return _make_expr("minute", period, b.Int64.ref("res"))

def hours(period: _Period) -> b.Expression:
    return _make_expr("hour", period, b.Int64.ref("res"))

def days(period: _Period) -> b.Expression:
    return _make_expr("day", period, b.Int64.ref("res"))

def weeks(period: _Period) -> b.Expression:
    return _make_expr("week", period, b.Int64.ref("res"))

def months(period: _Period) -> b.Expression:
    return _make_expr("month", period, b.Int64.ref("res"))

def years(period: _Period) -> b.Expression:
    return _make_expr("year", period, b.Int64.ref("res"))

def date_to_datetime(date: _Date, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0, tz: str = "UTC") -> b.Expression:
    _year = year(date)
    _month = month(date)
    _day = day(date)
    return _make_expr("construct_datetime_ms_tz", _year, _month, _day, hour, minute, second, millisecond, tz, b.DateTime.ref("res"))

#--------------------------------------------------
# Arithmetic
#--------------------------------------------------
def date_add(date: _Date, period: b.Producer) -> b.Expression:
    return _make_expr("date_add", date, period, b.Date.ref("res"))

def date_subtract(date: _Date, period: b.Producer) -> b.Expression:
    return _make_expr("date_subtract", date, period, b.Date.ref("res"))

def datetime_add(date: _DateTime, period: b.Producer) -> b.Expression:
    return _make_expr("datetime_add", date, period, b.DateTime.ref("res"))

def datetime_subtract(date: _DateTime, period: b.Producer) -> b.Expression:
    return _make_expr("datetime_subtract", date, period, b.DateTime.ref("res"))


Frequency = Union[
    Literal["ms"],
    Literal["s"],
    Literal["m"],
    Literal["H"],
    Literal["D"],
    Literal["W"],
    Literal["M"],
    Literal["Y"],
]

_periods = {
    "ms": milliseconds,
    "s": seconds,
    "m": minutes,
    "H": hours,
    "D": days,
    "W": weeks,
    "M": months,
    "Y": years,
}

def date_range(start: _Date | None = None, end: _Date | None = None, periods: int = 1, freq: Frequency = "D") -> b.Expression:
    if start is None and end is None:
        raise ValueError("Invalid start/end date for date_range. Must provide at least start date or end date")
    _days = {
        "D": 1,
        "W": 1/7,
        "M": 1/(365/12),
        "Y": 1/365,
    }
    if freq not in _days.keys():
        raise ValueError(f"Frequency '{freq}' is not allowed for date_range. List of allowed frequencies: {list(_days.keys())}")
    date_func = date_add
    if start is None:
        start = end
        end = None
        date_func = date_subtract
    assert start is not None
    if end is not None:
        num_days = std.dates.dates_period_days(start, end)
        if freq in ["W", "M", "Y"]:
            range_end = std.cast(b.Int64, std.math.floor(num_days * _days[freq]))
        else:
            range_end = num_days
        # date_range is inclusive. add 1 since std.range is exclusive
        ix = std.range(0, range_end + 1, 1)
    else:
        ix = std.range(0, periods, 1)
    _date = date_func(start, _periods[freq](ix))
    if end is not None:
        assert _date <= end
    return _date

def datetime_range(start: _DateTime | None = None, end: _DateTime | None = None, periods: int = 1, freq: Frequency = "D") -> b.Expression:
    if start is None and end is None:
        raise ValueError("Invalid start/end datetime for datetime_range. Must provide at least start datetime or end datetime")
    _milliseconds = {
        "ms": 1,
        "s": 1 / 1_000,
        "m": 1 / 60_000,
        "H": 1 / 3_600_000,
        "D": 1 / 86_400_000,
        "W": 1 / (86_400_000 * 7),
        "M": 1 / (86_400_000 * (365 / 12)),
        "Y": 1 / (86_400_000 * 365),
    }
    date_func = datetime_add
    if start is None:
        start = end
        end = None
        date_func = datetime_subtract
    assert start is not None
    if end is not None:
        num_ms = datetimes_period_milliseconds(start, end)
        if freq == "ms":
            _end = num_ms
        else:
            _end = std.cast(b.Int64, std.math.ceil(num_ms * _milliseconds[freq]))
        # datetime_range is inclusive. add 1 since std.range is exclusive
        ix = std.range(0, _end + 1, 1)
    else:
        ix = std.range(0, periods, 1)
    _date = date_func(start, _periods[freq](ix))
    if end is not None:
        assert _date <= end
    return _date
