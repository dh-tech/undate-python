import datetime
from calendar import monthrange
import re

# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Optional, Dict, Union

from dateutil.relativedelta import relativedelta

from undate.dateformat.base import BaseDateFormat


# duration of a single day
ONE_DAY = datetime.timedelta(days=1)


class Undate:
    """Simple object for representing uncertain, fuzzy or partially unknown dates"""

    DEFAULT_FORMAT = "ISO8601"

    #: symbol for unknown digits within a date value
    MISSING_DIGIT = "X"

    earliest: Union[datetime.date, None] = None
    latest: Union[datetime.date, None] = None
    label: Union[str, None] = None
    formatter: Union[BaseDateFormat, None] = None

    def __init__(
        self,
        year: Optional[Union[int, str]] = None,
        month: Optional[Union[int, str]] = None,
        day: Optional[Union[int, str]] = None,
        formatter: Optional[BaseDateFormat] = None,
    ):
        # keep track of initial values and which values are known
        self.initial_values: Dict[str, Union[int, str]] = {
            "year": year,
            "month": month,
            "day": day,
        }

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
                min_year = int(year.replace(self.MISSING_DIGIT, "0"))
                max_year = int(year.replace(self.MISSING_DIGIT, "9"))
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
                # determine the range of possible values
                possible_values = [f"{n:02}" for n in range(min_month, max_month + 1)]
                # generate regex where missing digit matches anything
                # make sure month is two-digit string
                month = "%02s" % month
                month_pattern = re.compile(month.replace(self.MISSING_DIGIT, "."))
                # identify all possible matches, then get min and max
                matches = [val for val in possible_values if month_pattern.match(val)]
                min_match = min(matches)
                max_match = max(matches)

                # split input month string into a list so we can update digits
                min_month = list(month)
                max_month = list(month)
                for i, digit in enumerate(month):
                    if digit == self.MISSING_DIGIT:
                        min_month[i] = min_match[i]
                        max_month[i] = max_match[i]

                # combine the lists of digits back together and convert to int
                min_month = int("".join(min_month))
                max_month = int("".join(max_month))

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
                _, max_day = monthrange(year, max_month)
            elif year is None and month:
                # TODO: what to do if we don't have year and month?
                # This will produce bad data if the year is a leap year and the month is February
                # 2022 chosen below as it is not a not leap year
                # Better than just setting 31, but still not great
                _, max_day = monthrange(2022, max_month)
            else:
                max_day: int = 31

            # if day is partially specified, narrow min/max further
            if day is not None:
                possible_values = [f"{n:02}" for n in range(min_day, max_day + 1)]
                day = "%02s" % day
                # generate regex where missing digit matches anything
                day_pattern = re.compile(day.replace(self.MISSING_DIGIT, "."))
                # identify all possible matches, then get min and max
                matches = [val for val in possible_values if day_pattern.match(val)]
                min_match = min(matches)
                max_match = max(matches)

                # split input string into a list so we can update digits
                min_day = list(day)
                max_day = list(day)
                for i, digit in enumerate(day):
                    if digit == self.MISSING_DIGIT:
                        min_day[i] = min_match[i]
                        max_day[i] = max_match[i]

                # combine the lists of digits back together and convert to int
                min_day = int("".join(min_day))
                max_day = int("".join(max_day))

        # for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        self.earliest = datetime.date(min_year, min_month, min_day)
        self.latest = datetime.date(max_year, max_month, max_day)

        if not formatter:
            # TODO subclass definitions not available unless they are imported where Undate() is called
            formatter = BaseDateFormat.available_formatters()[self.DEFAULT_FORMAT]()
        self.formatter = formatter

    def __str__(self) -> str:
        return self.formatter.to_string(self)

    def __repr__(self) -> str:
        return "<Undate %s>" % self

    def __eq__(self, other: "Undate") -> bool:
        # question: should label be taken into account when checking equality?
        # for now, assuming label differences don't matter for comparing dates
        return (
            self.earliest == other.earliest
            and self.latest == other.latest
            # NOTE: assumes that partially known values can only be written
            # in one format (i.e. X for missing digits).
            # If we support other formats, may need to normalize to common
            # internal format for comparison
            and self.initial_values == other.initial_values
        )

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

    def duration(self) -> datetime.timedelta:
        # what is the duration of this date?
        # subtract earliest from latest, and add a day to count the starting day

        # TODO: update to account for partially known values;
        # can it be based on known granularity somehow?
        # 1900-11-2X => one day
        # 1900-1X  => one month ? (30? 31?)
        # maybe go with the maximum possible value?
        # if granularity == month but not known month, duration = 31

        return self.latest - self.earliest + ONE_DAY


class UndateInterval:
    # date range between two uncertain dates

    def __init__(
        self, earliest: Union[Undate, None] = None, latest: Union[Undate, None] = None
    ):
        # for now, assume takes two undate objects
        self.earliest = earliest
        self.latest = latest

    def __str__(self) -> str:
        # using EDTF syntax for open ranges
        return "%s/%s" % (self.earliest or "..", self.latest or "")

    def __eq__(self, other) -> bool:
        # consider interval equal if both dates are equal
        return self.earliest == other.earliest and self.latest == other.latest

    def duration(self) -> datetime.timedelta:
        # what is the duration of this date range?

        # if both years are known, subtract end of range from beginning of start
        if self.latest.known_year and self.earliest.known_year:
            return self.latest.latest - self.earliest.earliest + ONE_DAY

        # if neither year is known...
        elif not self.latest.known_year and not self.earliest.known_year:
            # under what circumstances can we assume that if both years
            # are unknown the dates are in the same year or sequential?
            duration = self.latest.earliest - self.earliest.earliest + ONE_DAY
            # if we get a negative, we've wrapped from end of one year
            # to the beginning of the next
            if duration.days < 0:
                end = self.latest.earliest + relativedelta(years=1)
                duration = end - self.earliest.earliest

            return duration

        else:
            # is there any meaningful way to calculate duration
            # if one year is known and the other is not?
            raise NotImplementedError
