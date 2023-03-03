from undate.dateformat.base import BaseDateFormat
from undate.undate import Undate, UndateInterval
from typing import Dict, List, Union


class ISO8601DateFormat(BaseDateFormat):
    # NOTE: do we care about validation? could use regex
    # but maybe be permissive, warn if invalid but we can parse

    # do not change; Undate relies on this string
    name: str = "ISO8601"

    #: datetime strftime format for known part of date
    iso_format: Dict[str, str] = {
        "year": "%Y",
        "month": "%m",
        "day": "%d",
    }

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        # TODO: must return value of type "Union[Undate, UndateInterval]"
        # TODO: what happens if someone gives us a full isoformat date with time?
        # (ignore, error?)
        # TODO: what about invalid format?
        # could be YYYY, YYYY-MM, YYYY-MM-DD, --MM-DD for single date
        # or YYYY/YYYY (etc.) for an interval
        parts: List[str] = value.split("/")  # split in case we have a range
        if len(parts) == 1:
            return self._parse_single_date(parts[0])
        elif len(parts) == 2:
            return UndateInterval(*[self._parse_single_date(p) for p in parts])

    def _parse_single_date(self, value: str) -> Undate:
        # split single iso date into parts; convert to int or None
        # special case: missing year
        date_parts: List[Union[int, None]] = []
        if value.startswith("--"):
            date_parts.append(None)  # year unknown
            value = value[2:]

        date_parts.extend([int(p) if p else None for p in value.split("-")])
        # TODO: handle too many parts. Getting this error from type checking:
        # Argument of type "int | None" cannot be assigned to parameter "formatter" of type "BaseDateFormat | None" in function "__init__"
        return Undate(*date_parts)  # type: ignore

    def to_string(self, undate: Undate) -> str:
        # serialize to iso format for simplicity, for now
        date_parts: List[Union[str, None]] = []
        # for each part of the date that is known, generate the string format
        # then combine
        for date_portion, iso_format in self.iso_format.items():
            if undate.is_known(date_portion):
                # NOTE: datetime strftime for %Y for 3-digit year
                # results in leading zero in some environments
                # and not others; force year to always be 4 digits
                if date_portion == "year":
                    date_parts.append("%04d" % undate.earliest.year)
                else:
                    date_parts.append(undate.earliest.strftime(iso_format))
            elif date_portion == "year":
                # if not known but this is year, add '-' for --MM-DD unknown year format
                date_parts.append("-")
        # TODO: fix type error: "list[str | None]" is incompatible with "Iterable[str]"
        return "-".join(date_parts)  # type: ignore
