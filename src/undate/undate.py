from __future__ import annotations

import datetime
from enum import auto

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from undate.interval import UndateInterval

try:
    # StrEnum was only added in python 3.11
    from enum import StrEnum
except ImportError:
    # for python 3.10 or earlier, use third-party package
    from strenum import StrEnum  # type: ignore

# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Dict, Optional, Union

from undate.converters.base import BaseCalendarConverter, BaseDateConverter
from undate.date import ONE_DAY, Date, DatePrecision, Timedelta, UnDelta


class Calendar(StrEnum):
    """Supported calendars"""

    GREGORIAN = auto()
    HEBREW = auto()
    ISLAMIC = auto()
    SELEUCID = auto()

    @staticmethod
    def get_converter(calendar) -> BaseCalendarConverter:
        # calendar converter must be available with a name matching
        # the title-case name of the calendar enum entry
        try:
            converter_cls = BaseDateConverter.available_converters()[
                calendar.value.title()
            ]
        except KeyError as err:
            raise ValueError(f"Unknown calendar '{calendar}'") from err
        if not issubclass(converter_cls, BaseCalendarConverter):
            raise ValueError(
                f"Requested converter '{calendar.value.title()}' is not a CalendarConverter"
            )
        return converter_cls()


class Undate:
    """object for representing uncertain, fuzzy or partially unknown dates"""

    DEFAULT_CONVERTER: str = "ISO8601"

    #: symbol for unknown digits within a date value
    MISSING_DIGIT: str = "X"

    earliest: Date
    latest: Date
    #: A string to label a specific undate, e.g. "German Unity Date 2022" for Oct. 3, 2022.
    #: Labels are not taken into account when comparing undate objects.
    label: Union[str, None] = None
    converter: BaseDateConverter
    #: precision of the date (day, month, year, etc.)
    precision: DatePrecision
    #: the calendar this date is using; Gregorian by default
    calendar: Calendar = Calendar.GREGORIAN

    # numpy datetime is stored as 64-bit integer, so min/max
    # depends on the time unit; assume days for now
    # See https://numpy.org/doc/stable/reference/arrays.datetime.html#datetime-units
    # It just so happens that int(2.5e16) is a leap year, which is a weird default,
    # so let's increase our lower bound by one year.
    MIN_ALLOWABLE_YEAR = int(-2.5e16) + 1
    MAX_ALLOWABLE_YEAR = int(2.5e16)

    def __init__(
        self,
        year: Optional[Union[int, str]] = None,
        month: Optional[Union[int, str]] = None,
        day: Optional[Union[int, str]] = None,
        converter: Optional[BaseDateConverter] = None,
        label: Optional[str] = None,
        calendar: Optional[Union[str, Calendar]] = None,
    ):
        # everything is optional but something is required
        if all([val is None for val in [year, month, day]]):
            raise ValueError("At least one of year, month, or day must be specified")

        # keep track of initial values and which values are known
        # TODO: add validation: if str, must be expected length
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

        self.label = label
        if calendar is not None:
            self.set_calendar(calendar)
        self.calendar_converter = Calendar.get_converter(self.calendar)
        self.calculate_earliest_latest(year, month, day)

        if converter is None:
            #  import all subclass definitions; initialize the default
            converter_cls = BaseDateConverter.available_converters()[
                self.DEFAULT_CONVERTER
            ]
            converter = converter_cls()
        self.converter = converter

    def calculate_earliest_latest(self, year, month, day):
        # special case: treat year = XXXX as unknown/none
        if year == "XXXX":
            year = None
        if year is not None:
            # could we / should we use str.isnumeric here?
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
            # if we don't have any other bounds,
            # use calendar-specific min year if there is one, otherwise use
            # the configured min/max allowable years
            min_year = self.calendar_converter.MIN_YEAR or self.MIN_ALLOWABLE_YEAR
            max_year = self.calendar_converter.MAX_YEAR or self.MAX_ALLOWABLE_YEAR

        # if month is passed in as a string but completely unknown,
        # treat as unknown/none (date precision already set in init)
        if month == "XX":
            month = None

        # get first and last month from the calendar (not always 1 and 12)
        # as well as min/max months
        earliest_month = self.calendar_converter.first_month()
        latest_month = self.calendar_converter.last_month(max_year)

        min_month = self.calendar_converter.min_month()
        max_month = self.calendar_converter.max_month(max_year)
        if month is not None:
            try:
                # treat as an integer if we can
                month = int(month)
                # update initial value
                self.initial_values["month"] = month
                earliest_month = latest_month = month
            except ValueError:
                # if not, calculate min/max for missing digits
                earliest_month, latest_month = self._missing_digit_minmax(
                    str(month), min_month, max_month
                )
        # similar to month above — unknown day, but day-level granularity
        if day == "XX":
            day = None

        # if day is numeric, use as is
        if isinstance(day, int) or isinstance(day, str) and day.isnumeric():
            day = int(day)
            # update initial value - fully known day
            self.initial_values["day"] = day
            min_day = max_day = day
        else:
            # if we have no day or partial day, calculate min / max
            min_day = 1  # is min day ever anything other than 1 ?
            rel_year = year if year and isinstance(year, int) else max_year
            # use month if it is an integer; otherwise use previusly determined
            # max month (which may not be 12 depending if partially unknown)
            rel_month = month if month and isinstance(month, int) else latest_month

            max_day = self.calendar_converter.max_day(rel_year, rel_month)

            # if day is partially specified, narrow min/max further
            if day is not None:
                min_day, max_day = self._missing_digit_minmax(day, min_day, max_day)

        # TODO: special case, if we get a Feb 29 date with unknown year,
        # should switch the min/max years to known leap years!

        # for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        # convert to Gregorian calendar so earliest/latest can always
        # be used for comparison
        self.earliest = Date(
            *self.calendar_converter.to_gregorian(min_year, earliest_month, min_day)
        )
        self.latest = Date(
            *self.calendar_converter.to_gregorian(max_year, latest_month, max_day)
        )

    def set_calendar(self, calendar: Union[str, Calendar]):
        """Find calendar by name if passed as string and set on the object.
        Only intended for use at initialization time; use :meth:`as_calendar`
        to change calendar."""
        if calendar is not None:
            # if not passed as a Calendar instance, do a lookup
            if isinstance(calendar, str):
                # look for calendar by upper-case name
                try:
                    calendar = Calendar[calendar.upper()]
                except KeyError as err:
                    raise ValueError(f"Calendar `{calendar}` is not supported") from err
            self.calendar = calendar

    def as_calendar(self, calendar: Union[str, Calendar]):
        """Return a new :class:`Undate` object with the same year, month, day, and labels
        used to initialize the current object, but with a different calendar.  Note that this
        does NOT do calendar conversion, but reinterprets current numeric year, month, day values
        according to the new calendar."""
        return Undate(
            year=self.initial_values.get("year"),
            month=self.initial_values.get("month"),
            day=self.initial_values.get("day"),
            label=self.label,
            calendar=calendar,
        )

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
            return "-".join([str(p) for p in parts if p is not None])

        return self.converter.to_string(self)

    def __repr__(self) -> str:
        label_str = f" '{self.label}'" if self.label else ""
        return f"<Undate{label_str} {self} ({self.calendar.name.title()})>"

    @classmethod
    def parse(cls, date_string, format) -> Union["Undate", UndateInterval]:
        """parse a string to an undate or undate interval using the specified format;
        for now, only supports named converters"""
        converter_cls = BaseDateConverter.available_converters().get(format, None)
        if converter_cls:
            # NOTE: some parsers may return intervals; is that ok here?
            return converter_cls().parse(date_string)

        raise ValueError(f"Unsupported format '{format}'")

    def format(self, format) -> str:
        """format this undate as a string using the specified format;
        for now, only supports named converters"""
        converter_cls = BaseDateConverter.available_converters().get(format, None)
        if converter_cls is not None:
            # NOTE: some parsers may return intervals; is that ok here?
            return converter_cls().to_string(self)

        raise ValueError(f"Unsupported format '{format}'")

    @classmethod
    def _comparison_type(cls, other: object) -> "Undate":
        """Common logic for type handling in comparison methods.
        Converts to Undate object if possible, otherwise raises
        NotImplementedError exception.  Uses :meth:`to_undate` for conversion.
        """
        # convert if possible; return NotImplemented if not
        try:
            return cls.to_undate(other)
        except TypeError:
            # recommended to support comparison with arbitrary objects
            return NotImplemented

    def __eq__(self, other: object) -> bool:
        # Note: assumes label differences don't matter for comparing dates

        # only a day-precision fully known undate can be equal to a datetime.date
        if isinstance(other, datetime.date):
            return self.earliest == other and self.latest == other

        other = self._comparison_type(other)
        if other is NotImplemented:
            # return NotImplemented to indicate comparison is not supported
            # with this type
            return NotImplemented

        # if both dates are fully known, then earliest/latest check
        # is sufficient (and will work across calendars!)

        # check for apparent equality
        # - earliest/latest match and both have the same precision
        looks_equal = (
            self.earliest == other.earliest
            and self.latest == other.latest
            and self.precision == other.precision
        )
        # if everything looks the same, check for any unknowns in initial values
        # the same unknown date should NOT be considered equal
        # (but do we need a different equivalence check for this?)

        # NOTE: assumes that partially known values can only be written
        # in one format (i.e. X for missing digits).
        # If we support other formats, will need to normalize to common
        # internal format for comparison
        if looks_equal and (
            # if any part of either date that is known is _partially_ known,
            # then these dates are not equal
            any([self.is_partially_known(p) for p in self.initial_values.keys()])
            or any([other.is_partially_known(p) for p in other.initial_values.keys()])
        ):
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
            # sort by precision, most precise first
            by_precision = sorted(
                [self, other], key=lambda x: x.precision, reverse=True
            )
            raise NotImplementedError(
                f"Can't compare when one date ({by_precision[0]}) falls within the other ({by_precision[1]})"
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

    def __le__(self, other: object) -> bool:
        return self == other or self < other

    def __contains__(self, other: object) -> bool:
        # if the two dates are strictly equal, don't consider
        # either one as containing the other
        other = self._comparison_type(other)

        if self == other:
            return False

        return all(
            [
                self.earliest <= other.earliest,
                self.latest >= other.latest,
                # is precision sufficient for comparing partially known dates?
                # checking based on less precise /less granular time unit,
                # e.g. a day or month could be contained in a year
                # but not the reverse
                self.precision < other.precision,
            ]
        )

    @classmethod
    def to_undate(cls, other: object) -> "Undate":
        """Convert arbitrary object to Undate, if possible. Raises TypeError
        if conversion is not possible.

        Currently supports:
            - :class:`datetime.date` or :class:`datetime.datetime`
            - :class:`undate.date.Date`

        """
        match other:
            case Undate():
                return other
            case datetime.date() | datetime.datetime():
                return Undate(other.year, other.month, other.day)
            case Date():
                # handle conversion from internal Date class
                return Undate(other.year, other.month, other.day)

            case _:
                raise TypeError(f"Conversion from {type(other)} is not supported")

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
        # TODO: should XX / XXXX really be considered partially known? other code seems to assume this, so we'll preserve the behavior
        return isinstance(self.initial_values[part], str)
        # and self.initial_values[part].replace(self.MISSING_DIGIT, "") != ""

    @property
    def year(self) -> Optional[str]:
        "year as string (minimum 4 characters), if year is known"
        year = self._get_date_part("year")
        if year:
            return f"{year:0>4}"
        # if value is unset but date precision is year or greater, return unknown year
        elif self.precision >= DatePrecision.YEAR:
            return self.MISSING_DIGIT * 4
        return None

    @property
    def month(self) -> Optional[str]:
        "month as 2-character string, or None if unknown/unset"
        # TODO: do we allow None for unknown month with day-level granularity?
        # TODO: need to distinguish between unknown (XX) and unset/not part of the date due to granularity
        month = self._get_date_part("month")
        if month:
            return f"{month:0>2}"
        # if value is unset but date precision is month or greater, return unknown month
        elif self.precision >= DatePrecision.MONTH:
            return self.MISSING_DIGIT * 2
        return None

    @property
    def day(self) -> Optional[str]:
        "day as 2-character string or None if unset"
        day = self._get_date_part("day")
        if day:
            return f"{day:0>2}"
        # if value is unset but date precision is day, return unknown day
        # (may not be possible to have day precision with day part set in normal use)
        elif self.precision == DatePrecision.DAY:
            return self.MISSING_DIGIT * 2
        return None

    def _get_date_part(self, part: str) -> Optional[str]:
        value = self.initial_values.get(part)
        return str(value) if value else None

    @property
    def possible_years(self) -> list[int] | range:
        """A list or range of possible years for this date in the original calendar.
        Returns a list with a single year for dates with fully-known years."""
        if self.known_year:
            return [self.earliest.year]

        step = 1
        if (
            self.is_partially_known("year")
            and str(self.year).replace(self.MISSING_DIGIT, "") != ""
        ):
            # determine the smallest step size for the missing digit
            earliest_year = int(str(self.year).replace(self.MISSING_DIGIT, "0"))
            latest_year = int(str(self.year).replace(self.MISSING_DIGIT, "9"))
            missing_digit_place = len(str(self.year)) - str(self.year).rfind(
                self.MISSING_DIGIT
            )
            # convert place to 1, 10, 100, 1000, etc.
            step = 10 ** (missing_digit_place - 1)
            return range(earliest_year, latest_year + 1, step)

        # otherwise, year is fully unknown
        # returning range from min year to max year is not useful in any scenario!
        raise ValueError(
            "Possible years cannot be returned for completely unknown year"
        )

    @property
    def representative_years(self) -> list[int]:
        """A list of representative years for this date."""
        try:
            # todo: filter by calendar to minimum needed
            try:
                return self.calendar_converter.representative_years(
                    list(self.possible_years)
                )
            except NotImplementedError:
                # if calendar converter does not support representative years, return all years
                return list(self.possible_years)
        except ValueError:
            return [
                self.calendar_converter.LEAP_YEAR,
                self.calendar_converter.NON_LEAP_YEAR,
            ]

    def duration(self) -> Timedelta | UnDelta:
        """What is the duration of this date?
        Calculate based on earliest and latest date within range,
        taking into account the precision of the date even if not all
        parts of the date are known. Note that durations are inclusive
        (i.e., a closed interval)  and include both the earliest and latest
        date rather than the difference between them.  Returns a :class:`undate.date.Timedelta` when
        possible, and an :class:`undate.date.UnDelta` when the duration is uncertain."""

        # if precision is a single day, duration is one day
        # no matter when it is or what else is known
        if self.precision == DatePrecision.DAY:
            return ONE_DAY

        possible_max_days = set()

        # if precision is month and year is unknown,
        # calculate month duration within a single year (not min/max)
        if self.precision == DatePrecision.MONTH:
            # for every possible month and year, get max days for that month,
            # appease mypy, which says month values could be None here;
            # Date object allows optional month, but earliest/latest initialization
            # should always be day-precision dates
            if self.earliest.month is not None and self.latest.month is not None:
                for possible_month in range(self.earliest.month, self.latest.month + 1):
                    for year in self.representative_years:
                        possible_max_days.add(
                            self.calendar_converter.max_day(year, possible_month)
                        )

        # if precision is year but year is unknown, return an uncertain delta
        elif self.precision == DatePrecision.YEAR:
            # this is currently hebrew-specific due to the way the start/end of year wraps for that calendar
            # with contextlib.suppress(NotImplementedError):
            possible_max_days = {
                self.calendar_converter.days_in_year(y)
                for y in self.representative_years
            }

        # if there is more than one possible value for number of days
        # due to range including lear year / non-leap year, return an uncertain delta
        if possible_max_days:
            if len(possible_max_days) > 1:
                return UnDelta(*possible_max_days)
            return Timedelta(possible_max_days.pop())

        # otherwise, subtract earliest from latest and add a day to include start day in the count
        return self.latest - self.earliest + ONE_DAY

    def _missing_digit_minmax(
        self, value: str, min_val: int, max_val: int
    ) -> tuple[int, int]:
        # given a possible range, calculate min/max values for a string
        # with a missing digit

        # TODO: test this method directly

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
