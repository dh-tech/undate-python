from undate.dateformat.base import DateFormat
from undate.undate import Undate, UndateInterval


class ISO8601DateFormat(DateFormat):

    # NOTE: do we care about validation? could use regex
    # but maybe be permissive, warn if invalid but we can parse

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

    # def to_string(self, undate):
