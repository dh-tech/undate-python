from undate.dateformat.base import BaseDateFormat
from undate.undate import Undate, UndateInterval


class ISO8601DateFormat(BaseDateFormat):

    # NOTE: do we care about validation? could use regex
    # but maybe be permissive, warn if invalid but we can parse

    # do not change; Undate relies on this string
    name = "ISO8601"

    #: datetime strftime format for known part of date
    iso_format = {
        "year": "%Y",
        "month": "%m",
        "day": "%d",
    }

    def parse(self, value):
        # TODO: what happens if someone gives us a full isoformat date with time?
        # (ignore, error?)
        # TODO: what about invalid format?
        # could be YYYY, YYYY-MM, YYYY-MM-DD, --MM-DD for single date
        # or YYYY/YYYY (etc.) for an interval
        parts = value.split("/")  # split in case we have a range
        if len(parts) == 1:
            return self._parse_single_date(parts[0])
        elif len(parts) == 2:
            return UndateInterval(*[self._parse_single_date(p) for p in parts])

    def _parse_single_date(self, value):
        # split single iso date into parts; convert to int or None
        # special case: missing year
        date_parts = []
        if value.startswith("--"):
            date_parts.append(None)  # year unknown
            value = value[2:]

        date_parts.extend([int(p) if p else None for p in value.split("-")])
        return Undate(*date_parts)

    def to_string(self, undate):
        # serialize to iso format for simplicity, for now
        date_parts = []
        # for each part of the date that is known, generate the string format
        # then combine
        for date_portion, known in undate.known_values.items():
            if known:
                date_parts.append(
                    undate.earliest.strftime(self.iso_format[date_portion])
                )
            elif date_portion == "year":
                # if not known but this is year, add '-' for --MM-DD unknown year format
                date_parts.append("-")
        return "-".join(date_parts)
