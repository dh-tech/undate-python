import datetime
from calendar import monthrange

class Undate:
    """Simple object for representing uncertain, fuzzy or partially unknown dates"""

    earliest = None
    latest = None
    label = None

    #: datetime strftime format for known part of date
    iso_format = {
        "year": "%Y",
        "month": "%m",
        "day": "%d",
    }

    def __init__(self, year=None, month=None, day=None):
        # for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        self.earliest = datetime.date(year or datetime.MINYEAR, month or 1, day or 1)
        # if day is unknown but we have year and month, calculate max day
        if day is None and year and month:
            _, maxday = monthrange(year, month)
        else:
            maxday = 31  # ???
        self.latest = datetime.date(year or datetime.MAXYEAR, month or 12, day or maxday)
        # keep track of which values are known
        self.known_values = {
            "year": year is not None,
            "month": month is not None,
            "day": day is not None
        }

    def __str__(self):
        # serialize to iso format for simplicity, for now
        date_parts = []
        # for each part of the date that is known, generate the string format
        # then combine
        for date_portion, known in self.known_values.items():
            if known:
                date_parts.append(self.earliest.strftime(self.iso_format[date_portion]))
            elif date_portion == "year":
                # if not known but this is year, add '-' for --MM-DD unknown year format
                date_parts.append("-")
        return "-".join(date_parts)


class UndateInterval:
    # date range between two uncertain dates

    def __init__(self, earliest=None, latest=None):
        # for now, assume takes two undate objects
        self.earliest = earliest
        self.latest = latest

    def __str__(self):
        # using EDTF syntax for open ranges
        return "%s/%s" % (self.earliest or "..", self.latest or "")