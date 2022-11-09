import datetime
from calendar import monthrange

from undate.dateformat.base import BaseDateFormat


class Undate:
    """Simple object for representing uncertain, fuzzy or partially unknown dates"""

    DEFAULT_FORMAT = "ISO8601"

    earliest = None
    latest = None
    label = None
    formatter = None

    def __init__(self, year=None, month=None, day=None, formatter=None):
        # TODO: support initializing for unknown values in each of these
        # e.g., maybe values could be string or int; if string with
        # unknown digits, calculate min/max for unknowns

        # for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        self.earliest = datetime.date(year or datetime.MINYEAR, month or 1, day or 1)
        # if day is unknown but we have year and month, calculate max day
        if day is None and year and month:
            _, maxday = monthrange(year, month)
        else:
            maxday = 31  # ???
        self.latest = datetime.date(
            year or datetime.MAXYEAR, month or 12, day or maxday
        )
        # keep track of which values are known
        self.known_values = {
            "year": year is not None,
            "month": month is not None,
            "day": day is not None,
        }

        if not formatter:
            formatter = BaseDateFormat.available_formatters()[self.DEFAULT_FORMAT]()
        self.formatter = formatter

    def __str__(self):
        return self.formatter.to_string(self)

    def __repr__(self):
        return "<Undate %s>" % self

    def __eq__(self, other):
        # question: should label be taken into account when checking equality?
        # for now, assuming label differences don't matter for comparing dates
        return (
            self.earliest == other.earliest
            and self.latest == other.latest
            and self.known_values == other.known_values
        )


class UndateInterval:
    # date range between two uncertain dates

    def __init__(self, earliest=None, latest=None):
        # for now, assume takes two undate objects
        self.earliest = earliest
        self.latest = latest

    def __str__(self):
        # using EDTF syntax for open ranges
        return "%s/%s" % (self.earliest or "..", self.latest or "")

    def __eq__(self, other):
        # consider interval equal if both dates are equal
        return self.earliest == other.earliest and self.latest == other.latest
