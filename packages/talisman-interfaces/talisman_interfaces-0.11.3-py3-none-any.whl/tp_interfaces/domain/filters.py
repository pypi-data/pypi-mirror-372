from abc import ABCMeta
from dataclasses import dataclass
from functools import singledispatch

from tdm.abstract.datamodel import AbstractValue
from tdm.datamodel.values import Coordinates, Date, DateTimeValue, DoubleValue, GeoPointValue, IntValue, StringValue, Time, TimestampValue


@dataclass(frozen=True)
class AbstractFilter(metaclass=ABCMeta):  # noqa B024: this is actually abstract class
    def __post_init__(self):
        if type(self) is AbstractFilter:
            raise TypeError("Can't instantiate abstract class")


@singledispatch
def get_filters(value: AbstractValue, **kwargs) -> AbstractFilter:
    raise NotImplementedError


@dataclass(frozen=True)
class _StringFilter:
    str: str
    exact: bool = False

    def __post_init__(self):
        object.__setattr__(self, 'str', self.str.replace('"', '?'))  # see TKL-987


@dataclass(frozen=True)
class StringFilter(AbstractFilter):
    stringFilter: _StringFilter  # noqa: N815


@get_filters.register
def _string_filter(value: StringValue, exact: bool = False) -> StringFilter:
    return StringFilter(_StringFilter(value.value, exact))


@dataclass(frozen=True)
class _IntFilter:
    start: int
    end: int


@dataclass(frozen=True)
class IntFilter(AbstractFilter):
    intFilter: _IntFilter  # noqa N815


def _int_timestamp_filter(value: IntValue | TimestampValue, **kwargs) -> IntFilter:
    return IntFilter(_IntFilter(value.value, value.value))


@get_filters.register
def _int_filter(value: IntValue, **kwargs) -> IntFilter:
    return _int_timestamp_filter(value)


@get_filters.register
def _timestamp_filter(value: TimestampValue, **kwargs) -> IntFilter:
    return _int_timestamp_filter(value)


@dataclass(frozen=True)
class _DoubleFilter:
    start: float
    end: float


@dataclass(frozen=True)
class DoubleFilter(AbstractFilter):
    doubleFilter: _DoubleFilter  # noqa N815


@get_filters.register
def _double_filter(value: DoubleValue, **kwargs) -> DoubleFilter:
    return DoubleFilter(_DoubleFilter(value.value, value.value))


@dataclass(frozen=True)
class _DateTime:
    date: Date
    time: Time | None = None


@dataclass(frozen=True)
class _DateTimeFilter:
    start: _DateTime
    end: _DateTime


@dataclass(frozen=True)
class DateTimeFilter(AbstractFilter):
    dateTimeFilter: _DateTimeFilter  # noqa N815


@get_filters.register
def _date_time_filter(value: DateTimeValue, **kwargs) -> DateTimeFilter:
    date_time = _DateTime(value.date, value.time)
    return DateTimeFilter(_DateTimeFilter(date_time, date_time))


@dataclass(frozen=True)
class _GeoFilter:
    point: Coordinates | None
    name: str | None
    radius: float


@dataclass(frozen=True)
class GeoFilter(AbstractFilter):
    geoFilter: _GeoFilter  # noqa N815


@get_filters.register
def _geo_filter(value: GeoPointValue, **kwargs) -> GeoFilter:
    return GeoFilter(_GeoFilter(value.point, value.name, 0.0001))
