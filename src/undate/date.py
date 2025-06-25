from enum import IntEnum
from dataclasses import dataclass, replace
import operator

# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Optional, Union, Iterable

import numpy as np


class Timedelta(np.ndarray):
    """Convenience class to make :class:`numpy.timedelta64` act
    more like the built-in python :class:`datetime.timedelta`."""

    def __new__(cls, deltadays: Union[np.timedelta64, int]):
        if isinstance(deltadays, int):
            deltadays = np.timedelta64(deltadays, "D")
        data = np.asarray(deltadays, dtype="timedelta64")
        return data.view(cls)

    def Export(self):
        return self

    def __array_finalize__(self, obj):
        if obj is None:
            return

    @property
    def days(self) -> int:
        """number of days, as an integer"""
        return int(self.astype("datetime64[D]").astype("int"))


@dataclass
class UnInt:
    """An uncertain integer intended for use with uncertain durations (:class:`UnDelta`),
    to convey a range of possible integer values between an upper
    and lower bound (both inclusive). Supports comparison, addition and subtraction,
    checking if a value is included in the range, and iterating over numbers
    included in the range.
    """

    lower: int
    upper: int

    def __post_init__(self):
        # validate that lower value is less than upper
        if not self.lower < self.upper:
            raise ValueError(
                f"Lower value ({self.lower}) must be less than upper ({self.upper})"
            )

    def __iter__(self) -> Iterable:
        # yield all integers in range from lower to upper, inclusive
        yield from range(self.lower, self.upper + 1)

    def __gt__(self, other: object) -> bool:
        match other:
            case int():
                return self.lower > other
            case UnInt():
                return self.lower > other.upper
            case _:
                return NotImplemented

    def __lt__(self, other: object) -> bool:
        match other:
            case int():
                return self.upper < other
            case UnInt():
                return self.upper < other.lower
            case _:
                return NotImplemented

    def __contains__(self, other: object) -> bool:
        match other:
            case int():
                return other >= self.lower and other <= self.upper
            case UnInt():
                return other.lower >= self.lower and other.upper <= self.upper
            case _:
                # unsupported type: return false
                return False

    def _replace_with(self, other_lower, other_upper, op):
        """Create and return a new instance of UnInt using the specified
        operator (e.g. add, subtract) and other values to modify the values in
        the current UnInt instance."""
        return replace(
            self, lower=op(self.lower, other_lower), upper=op(self.upper, other_upper)
        )

    def __add__(self, other: object) -> "UnInt":
        match other:
            case int():
                # increase both values by the added amount
                add_values = (other, other)
            case UnInt():
                # add other lower value to current lower and other upper
                # to current upper to include the largest range of possible values
                # (when calculating with uncertain values, the uncertainty increases)
                add_values = (other.lower, other.upper)
            case _:
                return NotImplemented

        return self._replace_with(*add_values, operator.add)

    def __sub__(self, other) -> "UnInt":
        match other:
            case int():
                # decrease both values by the subtracted amount
                sub_values = (other, other)
            case UnInt():
                # to determine the largest range of possible values,
                # subtract the other upper value from current lower
                # and other lower value from current upper
                sub_values = (other.upper, other.lower)
            case _:
                return NotImplemented

        return self._replace_with(*sub_values, operator.sub)


@dataclass
class UnDelta:
    """
    An uncertain timedelta, for durations where the number of days is uncertain.
    Initialize with a list of possible durations in days as integers, which are used
    to calculate a value for duration in :attr:`days` as an
    instance of :class:`UnInt`.
    """

    # NOTE: we will probably need other timedelta-like logic here besides days...

    #: possible durations days, as an instance of :class:`UnInt`
    days: UnInt

    def __init__(self, *days: int):
        if len(days) < 2:
            raise ValueError(
                "Must specify at least two values for an uncertain duration"
            )
        self.days = UnInt(min(days), max(days))

    def __repr__(self):
        # customize string representation  for simpler notation; default
        # specifies full UnInt initialization with upper and lower keywords
        return f"{self.__class__.__name__}(days=[{self.days.lower},{self.days.upper}])"

    def __eq__(self, other: object) -> bool:
        # is an uncertain duration ever *equal* another, even if the values are the same?
        # for now, make the assumption that we only want identity equality
        # and not value equality; perhaps in future we can revisit
        # or add functions to check value equality / equivalence / similarity
        return other is self

    def __lt__(self, other: object) -> bool:
        match other:
            case Timedelta() | UnDelta():
                return self.days < other.days
            case _:
                return NotImplemented

    def __gt__(self, other: object) -> bool:
        match other:
            case Timedelta() | UnDelta():
                return self.days > other.days
            case _:
                return NotImplemented


#: timedelta for single day
ONE_DAY = Timedelta(1)  # ~ equivalent to datetime.timedelta(days=1)
#: timedelta for a single  year (non-leap year)
ONE_YEAR = Timedelta(365)  # ~ relativedelta(years=1)
#: timedelta for a month, assuming maximum month length (31 days)
ONE_MONTH_MAX = Timedelta(31)


class Date(np.ndarray):
    """Convenience class to make :class:`numpy.datetime64` act
    more like the built-in python :class:`datetime.date`."""

    # extend np.datetime64 datatype
    # adapted from https://stackoverflow.com/a/27129510/9706217

    def __new__(
        cls,
        year: Union[int, np.datetime64],
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        if isinstance(year, np.datetime64):
            _data = year
        else:
            datestr = str(year)
            if month is not None:
                datestr = f"{year}-{month:02d}"
                if day is not None:
                    datestr = f"{datestr}-{day:02d}"
            _data = np.datetime64(datestr)

        data = np.asarray(_data, dtype="datetime64")

        # expected dtype depends on date unit / how much of date is known
        expected_unit = "Y"
        if day is not None and month is not None:
            expected_unit = "D"
        elif month:
            expected_unit = "M"
        expected_dtype = f"datetime64[{expected_unit}]"

        if data.dtype != expected_dtype:
            raise ValueError(
                f"Unable to parse dates adequately as {expected_dtype}: {data}"
            )
        obj = data.view(cls)
        return obj

    def Export(self):
        return self

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # custom properties to access year, month, day

    @property
    def year(self) -> int:
        return int(str(self.astype("datetime64[Y]")))

    @property
    def month(self) -> Optional[int]:
        # if date unit is year, don't return a month (only M/D)
        if self.dtype != "datetime64[Y]":
            return int(str(self.astype("datetime64[M]")).split("-")[-1])
        return None

    @property
    def day(self) -> Optional[int]:
        # only return a day if date unit is in days
        if self.dtype == "datetime64[D]":
            return int(str(self.astype("datetime64[D]")).split("-")[-1])
        return None

    @property
    def weekday(self) -> Optional[int]:
        """Equivalent to :meth:`datetime.date.weekday`; returns day of week as an
        integer where Monday is 0 and Sunday is 6. Only supported for dates
        with date unit in days.
        """
        # only return a weekday if date unit is in days
        if self.dtype == "datetime64[D]":
            # calculate based on difference between current day and week start
            # numpy datetime weeks start on thursdays - presumably since
            # unix epoch day zero was a thursday...

            # implementation inspired in part by https://stackoverflow.com/a/54264187

            thursday_week = self.astype("datetime64[W]")
            days_from_thursday = (self - thursday_week).astype(int)
            # if monday is 0, thursday is 3
            return (days_from_thursday + 3) % 7

        return None

    def __sub__(self, other):
        # modify to conditionally return a timedelta object instead of a
        # Date object with dtype timedelta64[D] (default behavior)

        result = super().__sub__(other)
        # if the result has a timedelta type (i.e., date minus date = timedelta),
        # cast to local Timedelta object; otherwise, leave as is
        # (i.e., date minus timedelta = date)
        if result.dtype == "timedelta64[D]":
            result = Timedelta(result)
        return result

    # NOTE: add should not be subclassed because we want to return a Date, not a delta


class DatePrecision(IntEnum):
    """date precision, to indicate date precision independent from how much
    of the date is known."""

    # NOTE: values MUST be ordered based on the relative size or
    # precison of the time unit. That is, the smaller the unit, the more precise
    # it is: a day is more precise than a month, a month is more precise than a year,
    # (DatePrecision.year < DatePrecision.month)

    #: century
    CENTURY = 1
    #: decade
    DECADE = 2
    #: year
    YEAR = 3
    # TBD: season ?
    #: month
    MONTH = 4
    #: day
    DAY = 5

    def __str__(self):
        return f"{self.name}"

    # NOTE: consider harmonizing / using numpy date units:
    # years (‘Y’), months (‘M’), weeks (‘W’), and days (‘D’)
