import datetime
from calendar import monthrange

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
        # TODO: support initializing for unknown values in each of these
        # e.g., maybe values could be string or int; if string with
        # unknown digits, calculate min/max for unknowns

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

        if month is not None:
            try:
                month = int(month)
                # update initial value
                self.initial_values["month"] = month
                min_month = max_month = month
            except ValueError:
                min_month = max_month = None
                if len(month) == 2:
                    # if two digit month is 1x, range is 10 - 12
                    if month[0] == "1":
                        min_month = int(month.replace(self.MISSING_DIGIT, "0"))
                        max_month = int(month.replace(self.MISSING_DIGIT, "2"))
                    # if two digit month is 0x, range is 01 - 09
                    elif month[0] == "0":
                        min_month = int(month.replace(self.MISSING_DIGIT, "1"))
                        max_month = int(month.replace(self.MISSING_DIGIT, "9"))

                # are these possible/plausible ? X1 X2
                # assuming not
                if not min_month and not max_month:
                    raise ValueError

        else:
            min_month = 1
            max_month = 12

        # similar to month above — unknown day, but day-level granularity
        if day == "XX":
            day = None

        if day is not None:
            try:
                day = int(day)
                # update initial value
                self.initial_values["day"] = day
                min_day = max_day = day
            except ValueError:
                min_day = max_day = None
                if len(day) == 2:
                    # special case since most months only go up to 30/31
                    if day[0] == "3":
                        min_day = int(day.replace(self.MISSING_DIGIT, "0"))
                        # TODO: possibly max is 0 depending on the month
                        max_day = int(day.replace(self.MISSING_DIGIT, "1"))
                    # if second digit is missing, e.g. 1X or 2X
                    elif day[1] == self.MISSING_DIGIT:
                        if day[0] == "0":
                            # can't have 00
                            min_day = int(day.replace(self.MISSING_DIGIT, "1"))
                        else:
                            min_day = int(day.replace(self.MISSING_DIGIT, "0"))
                        max_day = int(day.replace(self.MISSING_DIGIT, "9"))
                    # if first digit is missing
                    elif day[0] == self.MISSING_DIGIT:
                        min_day = int(day.replace(self.MISSING_DIGIT, "0"))
                        if int(day[1]) > 1:
                            max_day = int(day.replace(self.MISSING_DIGIT, "2"))
                        else:
                            max_day = int(day.replace(self.MISSING_DIGIT, "3"))

        else:
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
