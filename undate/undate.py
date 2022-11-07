from datetime import date

class Undate:
    """Simple object for representing uncertain or partially unknown dates"""

    earliest = None
    latest = None
    label = None

    #: ISO format based on date precision
    iso_format = {
        "year": "%Y",
        "month": "%m",
        "day": "%d",
    }

    def __init__(self, year=None, month=None, day=None):
        # TODO: for unknowns, assume smallest possible value for earliest and
        # largest valid for latest
        self.earliest = date(year or self._default, month or self._default, day or self._default)
        self.latest = self.earliest  # TODO: needs to be a copy, not same object
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
    # date range between two undates

    def __init__(self, earliest, latest):
        # for now, assume takes two undate objects
        self.earliest = earliest
        self.latest = latest

    def __str__(self):
        return "%s/%s" % (self.earliest, self.latest)