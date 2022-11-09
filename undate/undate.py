import datetime
from calendar import monthrange

# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Optional, Dict, Union

from undate.dateformat.base import BaseDateFormat


class Undate:
    """Simple object for representing uncertain, fuzzy or partially unknown dates"""

    DEFAULT_FORMAT = "ISO8601"

    earliest: Union[datetime.date, None] = None
    latest: Union[datetime.date, None] = None
    label: Union[str, None] = None
    formatter: Union[BaseDateFormat, None] = None

    def __init__(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        formatter: Optional[BaseDateFormat] = None,
    ):
        # TODO: support initializing for unknown values in each of these
        # e.g., maybe values could be string or int; if string with
        # unknown digits, calculate min/max for unknowns

        # for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        self.earliest = datetime.date(year or datetime.MINYEAR, month or 1, day or 1)
        # if day is unknown but we have year and month, calculate max day
        if day is None and year and month:
            _, maxday = monthrange(year, month)
        elif day is None and year is None and month:
            # TODO: what to do if we don't have year and month?
            # This will produce bad data if the year is a leap year and the month is February
            # 2022 chosen below as it is not a not leap year
            # Better than just setting 31, but still not great
            _, maxday = monthrange(2022, month)
        else:
            maxday: int = 31
        self.latest = datetime.date(
            year or datetime.MAXYEAR, month or 12, day or maxday
        )
        # keep track of which values are known
        self.known_values: Dict[str, int] = {
            "year": year is not None,
            "month": month is not None,
            "day": day is not None,
        }

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
            and self.known_values == other.known_values
        )

    def duration(self) -> datetime.timedelta:
        # what is the duration of this date?
        # subtract earliest from latest, and add a day to count the starting day
        return self.latest - self.earliest + datetime.timedelta(days=1)


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
