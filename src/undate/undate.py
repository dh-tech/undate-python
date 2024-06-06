import datetime
from calendar import monthrange
from enum import IntEnum
import re

# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Optional, Dict, Union
import numpy as np
from dateutil.relativedelta import relativedelta

from undate.dateformat.base import BaseDateFormat


#: duration of a single day
# ONE_DAY = datetime.timedelta(days=1)
ONE_DAY = np.timedelta64(1, "D")


class LocalDate:
    def __init__(self, year: str, month: str = None, day: str = None):
        if isinstance(year, np.datetime64):
            self._date = year
        else:
            datestr = year
            if month is not None:
                datestr = f"{year}-{month:02d}"
                if day is not None:
                    datestr = f"{datestr}-{day:02d}"
            self._date = np.datetime64(datestr)

    def __str__(self):
        return str(self._date)

    @property
    def year(self):
        return int(str(self._date.astype("datetime64[Y]")))

    @property
    def month(self):
        return int(str(self._date.astype("datetime64[M]")).split("-")[-1])

    @property
    def day(self):
        return int(str(self._date.astype("datetime64[D]")).split("-")[-1])

    def __eq__(self, other: object) -> bool:
        return self._date == other._date

    def __gt__(self, other: object) -> bool:
        # define gt ourselves so we can support > comparison with datetime.date,
        # but rely on existing less than implementation.
        # strictly greater than must rule out equals
        return not (self._date < other._date or self._date == other._date)

    def __le__(self, other: Union["Undate", datetime.date]) -> bool:
        return self._date == other._date or self._date < other._date

    def __add__(self, other):
        if isinstance(other, LocalDate):
            return LocalDate(self._date + other._date)
        if isinstance(other, np.timedelta64):
            return LocalDate(self._date + other)

    def __sub__(self, other) -> np.timedelta64:
        return self._date - other._date


class DatePrecision(IntEnum):
    """date precision, to indicate date precision independent from how much
    of the date is known."""

    # numbers should be set to allow logical greater than / less than
    # comparison, e.g. year precision > month

    #: day
    DAY = 1
    #: month
    MONTH = 2
    #: year
    YEAR = 3

    def __str__(self):
        return f"{self.name}"

    # numpy date units are years (‘Y’), months (‘M’), weeks (‘W’), and days (‘D’),


class Undate:
    """Simple object for representing uncertain, fuzzy or partially unknown dates"""

    DEFAULT_FORMAT: str = "ISO8601"

    #: symbol for unknown digits within a date value
    MISSING_DIGIT: str = "X"

    earliest: datetime.date
    latest: datetime.date
    #: A string to label a specific undate, e.g. "German Unity Date 2022" for Oct. 3, 2022.
    #: Labels are not taken into account when comparing undate objects.
    label: Union[str, None] = None
    formatter: BaseDateFormat
    #: precision of the date (day, month, year, etc.)
    precision: DatePrecision

    #: known non-leap year
    NON_LEAP_YEAR: int = 2022

    def __init__(
        self,
        year: Optional[Union[int, str]] = None,
        month: Optional[Union[int, str]] = None,
        day: Optional[Union[int, str]] = None,
        formatter: Optional[BaseDateFormat] = None,
        label: Optional[str] = None,
    ):
        # keep track of initial values and which values are known
        self.initial_values: Dict[str, Optional[Union[int, str]]] = {
            "year": year,
            "month": month,
            "day": day,
        }
        if day:
            self.precision = DatePrecision.DAY
        elif month:
            self.precision = DatePrecision.MONTH
        elif year:
            self.precision = DatePrecision.YEAR

        # TODO: refactor partial date min/max calculations

        if year is not None:
            try:
                year = int(year)
                # update initial value since it is used to determine
                # whether or not year is known
                self.initial_values["year"] = year
                min_year = max_year = year
            except ValueError:
                # year is a string that can't be converted to int
                min_year = int(str(year).replace(self.MISSING_DIGIT, "0"))
                max_year = int(str(year).replace(self.MISSING_DIGIT, "9"))
        else:
            min_year = datetime.MINYEAR
            max_year = datetime.MAXYEAR

        # if month is passed in as a string but completely unknown,
        # treat as none
        # TODO: we should preserve this information somehow;
        # difference between just a year and and an unknown month within a year
        # maybe in terms of granularity / size ?
        if month == "XX":
            month = None

        min_month = 1
        max_month = 12
        if month is not None:
            try:
                # treat as an integer if we can
                month = int(month)
                # update initial value
                self.initial_values["month"] = month
                min_month = max_month = month
            except ValueError:
                # if not, calculate min/max for missing digits
                min_month, max_month = self._missing_digit_minmax(
                    str(month), min_month, max_month
                )

        # similar to month above — unknown day, but day-level granularity
        if day == "XX":
            day = None

        if isinstance(day, int) or isinstance(day, str) and day.isnumeric():
            day = int(day)
            # update initial value - fully known day
            self.initial_values["day"] = day
            min_day = max_day = day
        else:
            # if we have no day or partial day, calculate min / max
            min_day = 1
            # if we know year and month (or max month), calculate exactly
            if year and month:
                _, max_day = monthrange(int(year), max_month)
            elif year is None and month:
                # If we don't have year and month,
                # calculate based on a known non-leap year
                # (better than just setting 31, but still not great)
                _, max_day = monthrange(self.NON_LEAP_YEAR, max_month)
            else:
                max_day = 31

            # if day is partially specified, narrow min/max further
            if day is not None:
                min_day, max_day = self._missing_digit_minmax(day, min_day, max_day)

        # for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        # self.earliest = datetime.date(min_year, min_month, min_day)
        # self.latest = datetime.date(max_year, max_month, max_day)

        self.earliest = LocalDate(min_year, min_month, min_day)
        self.latest = LocalDate(max_year, max_month, max_day)

        if formatter is None:
            #  import all subclass definitions; initialize the default
            formatter_cls = BaseDateFormat.available_formatters()[self.DEFAULT_FORMAT]
            formatter = formatter_cls()
        self.formatter = formatter

        self.label = label

    def __str__(self) -> str:
        # if any portion of the date is partially known, construct
        # pseudo ISO8601 format here, since ISO8601 doesn't support unknown digits
        # (temporary, should switch to default format that can handle it, e.g. EDTF)
        if any(self.is_partially_known(part) for part in ["year", "month", "day"]):
            # initial values could be either string or int
            year = self.initial_values["year"]
            month = self.initial_values["month"]
            day = self.initial_values["day"]
            # if integer, convert to string with correct number of digits
            # replace unknown year with - for --MM or --MM-DD format
            parts = [
                f"{year:04d}" if isinstance(year, int) else year or "-",
                f"{month:02d}" if isinstance(month, int) else month,
                f"{day:02d}" if isinstance(day, int) else day,
            ]
            # combine, skipping any values that are None
            return "-".join([str(p) for p in parts if p != None])

        return self.formatter.to_string(self)

    def __repr__(self) -> str:
        if self.label:
            return "<Undate '%s' (%s)>" % (self.label, self)
        return "<Undate %s>" % self

    def _comparison_type(self, other: object) -> "Undate":
        """Common logic for type handling in comparison methods.
        Converts to Undate object if possible, otherwise raises
        NotImplemented error.  Currently only supports conversion
        from :class:`datetime.date`
        """

        # support datetime.date by converting to undate
        if isinstance(other, datetime.date):
            other = Undate.from_datetime_date(other)

        # recommended to support comparison with arbitrary objects
        if not isinstance(other, Undate):
            return NotImplemented

        return other

    def __eq__(self, other: object) -> bool:
        # Note: assumes label differences don't matter for comparing dates

        other = self._comparison_type(other)

        # only a day-precision fully known undate can be equal to a datetime.date
        if isinstance(other, datetime.date):
            return self.earliest == other and self.latest == other

        # check for apparent equality
        looks_equal = (
            self.earliest == other.earliest
            and self.latest == other.latest
            and self.initial_values == other.initial_values
        )
        # if everything looks the same, check for any unknowns in initial values
        # the same unknown date should NOT be considered equal
        # (but do we need a different equivalence check for this?)

        # NOTE: assumes that partially known values can only be written
        # in one format (i.e. X for missing digits).
        # If we support other formats, will need to normalize to common
        # internal format for comparison
        if looks_equal and any("X" in str(val) for val in self.initial_values.values()):
            return False

        return looks_equal

    def __lt__(self, other: object) -> bool:
        other = self._comparison_type(other)

        # if this date ends before the other date starts,
        # return true (this date is earlier, so it is less)
        if self.latest < other.earliest:
            return True

        # if the other one ends before this one starts,
        # return false (this date is later, so it is not less)
        if other.latest < self.earliest:
            return False

        # if it does not, check if one is included within the other
        # (e.g., single date within the same year)
        # comparison for those cases is not currently supported
        elif other in self or self in other:
            raise NotImplementedError(
                "Can't compare when one date falls within the other"
            )
        # NOTE: unsupported comparisons are supposed to return NotImplemented
        # However, doing that in this case results in a confusing TypeError!
        #   TypeError: '<' not supported between instances of 'Undate' and 'Undate'
        # How to handle when the comparison is ambiguous / indeterminate?
        # we may need a tribool / ternary type (true, false, unknown),
        # but not sure what python builtin methods will do with it (unknown = false?)

        # for any other case (i.e., self == other), return false
        return False

    def __gt__(self, other: object) -> bool:
        # define gt ourselves so we can support > comparison with datetime.date,
        # but rely on existing less than implementation.
        # strictly greater than must rule out equals
        return not (self < other or self == other)

    def __le__(self, other: Union["Undate", datetime.date]) -> bool:
        return self == other or self < other

    def __contains__(self, other: object) -> bool:
        # if the two dates are strictly equal, don't consider
        # either one as containing the other
        other = self._comparison_type(other)

        if self == other:
            return False

        return (
            self.earliest <= other.earliest
            and self.latest >= other.latest
            # is precision sufficient for comparing partially known dates?
            and self.precision > other.precision
        )

    @staticmethod
    def from_datetime_date(dt_date):
        """Initialize an :class:`Undate` object from a :class:`datetime.date`"""
        return Undate(dt_date.year, dt_date.month, dt_date.day)

    @property
    def known_year(self) -> bool:
        return self.is_known("year")

    def is_known(self, part: str) -> bool:
        """Check if a part of the date (year, month, day) is known.
        Returns False if unknown or only partially known."""
        # TODO: should we use constants or enum for values?

        # if we have an integer, then consider the date known
        # if we have a string, then it is only partially known; return false
        return isinstance(self.initial_values[part], int)

    def is_partially_known(self, part: str) -> bool:
        return isinstance(self.initial_values[part], str)

    def duration(self) -> datetime.timedelta:
        """What is the duration of this date?
        Calculate based on earliest and latest date within range,
        taking into account the precision of the date even if not all
        parts of the date are known."""

        # if precision is a single day, duration is one day
        # no matter when it is or what else is known
        if self.precision == DatePrecision.DAY:
            return ONE_DAY

        # if precision is month and year is unknown,
        # calculate month duration within a single year (not min/max)
        if self.precision == DatePrecision.MONTH:
            latest = self.latest
            if not self.known_year:
                # if year is unknown, calculate month duration in
                # a single year
                latest = LocalDate(
                    self.earliest.year, self.latest.month, self.latest.day
                )

                # latest = datetime.date(
                #     self.earliest.year, self.latest.month, self.latest.day
                # )
            delta = latest - self.earliest + ONE_DAY
            # month duration can't ever be more than 31 days
            # (could we ever know if it's smaller?)

            # if granularity == month but not known month, duration = 31
            if delta.astype(int) > 31:
                # return datetime.timedelta(days=31)
                return np.timedelta64(31, "D")
            return delta

        # otherwise, calculate based on earliest/latest range

        # subtract earliest from latest and add a day to count start day
        return self.latest - self.earliest + ONE_DAY

    def _missing_digit_minmax(
        self, value: str, min_val: int, max_val: int
    ) -> tuple[int, int]:
        # given a possible range, calculate min/max values for a string
        # with a missing digit

        # assuming two digit only (i.e., month or day)
        possible_values = [f"{n:02}" for n in range(min_val, max_val + 1)]
        # ensure input value has two digits
        value = "%02s" % value
        # generate regex where missing digit matches anything
        val_pattern = re.compile(value.replace(self.MISSING_DIGIT, "."))
        # identify all possible matches, then get min and max
        matches = [val for val in possible_values if val_pattern.match(val)]
        min_match = min(matches)
        max_match = max(matches)

        # split input string into a list so we can update individually
        new_min_val = list(value)
        new_max_val = list(value)
        for i, digit in enumerate(value):
            # replace the corresponding digit with our min and max
            if digit == self.MISSING_DIGIT:
                new_min_val[i] = min_match[i]
                new_max_val[i] = max_match[i]

        # combine the lists of digits back together and convert to int
        min_val = int("".join(new_min_val))
        max_val = int("".join(new_max_val))
        return (min_val, max_val)


class UndateInterval:
    """A date range between two uncertain dates.

    :param earliest: Earliest undate
    :type earliest: `undate.Undate`
    :param latest: Latest undate
    :type latest:  `undate.Undate`
    :param label: A string to label a specific undate interval, similar to labels of `undate.Undate`.
    :type label: `str`
    """

    # date range between two uncertain dates
    earliest: Union[Undate, None]
    latest: Union[Undate, None]
    label: Union[str, None]

    def __init__(
        self,
        earliest: Optional[Undate] = None,
        latest: Optional[Undate] = None,
        label: Optional[str] = None,
    ):
        # for now, assume takes two undate objects
        self.earliest = earliest
        self.latest = latest
        self.label = label

    def __str__(self) -> str:
        # using EDTF syntax for open ranges
        return "%s/%s" % (self.earliest or "..", self.latest or "")

    def __repr__(self) -> str:
        if self.label:
            return "<UndateInterval '%s' (%s)>" % (self.label, self)
        return "<UndateInterval %s>" % self

    def __eq__(self, other) -> bool:
        # consider interval equal if both dates are equal
        return self.earliest == other.earliest and self.latest == other.latest

    def duration(self) -> datetime.timedelta:
        """Calculate the duration between two undates.

        :returns: A duration
        :rtype: timedelta
        """
        # what is the duration of this date range?

        # if range is open-ended, can't calculate
        if self.earliest is None or self.latest is None:
            return NotImplemented

        # if both years are known, subtract end of range from beginning of start
        if self.latest.known_year and self.earliest.known_year:
            return self.latest.latest - self.earliest.earliest + ONE_DAY

        # if neither year is known...
        elif not self.latest.known_year and not self.earliest.known_year:
            # under what circumstances can we assume that if both years
            # are unknown the dates are in the same year or sequential?
            duration = self.latest.earliest - self.earliest.earliest
            # if we get a negative, we've wrapped from end of one year
            # to the beginning of the next;
            # recalculate assuming second date is in the subsequent year
            if duration.astype("int") < 0:
                # end = self.latest.earliest + relativedelta(years=1)
                end = self.latest.earliest + np.timedelta64(365, "D")
                duration = end - self.earliest.earliest

            # add the additional day *after* checking for a negative
            # or after recalculating with adjusted year
            duration += ONE_DAY

            return duration

        else:
            # is there any meaningful way to calculate duration
            # if one year is known and the other is not?
            raise NotImplementedError
