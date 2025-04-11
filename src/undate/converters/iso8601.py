from typing import Dict, List, Union

from undate import Undate, UndateInterval
from undate.converters.base import BaseDateConverter


class ISO8601DateFormat(BaseDateConverter):
    # NOTE: do we care about validation? could use regex
    # but maybe be permissive, warn if invalid but we can parse

    #: converter name: ISO8601
    name: str = "ISO8601"
    # do not change; Undate relies on this string

    #: datetime strftime format for known part of date
    iso_format: Dict[str, str] = {
        "year": "%Y",
        "month": "%m",
        "day": "%d",
    }

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        """
        Parse an ISO88601 string and return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval`. Currently supports
        YYYY, YYYY-MM, YYYY-MM-DD, --MM-DD for single date
        and interval format (YYYY/YYYY in any supported single date format).
        """
        # TODO: what happens if someone gives us a full isoformat date with time?
        # (ignore, error?)
        # TODO: what about invalid format?
        parts: List[str] = value.split("/")  # split in case we have a range
        if len(parts) == 1:
            return self._parse_single_date(parts[0])
        elif len(parts) == 2:
            # date range; parse both parts and initialize an interval
            start, end = [self._parse_single_date(p) for p in parts]
            return UndateInterval(start, end)
        else:
            # more than two parts = unexpected input
            raise ValueError

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

    def to_string(self, undate: Union[Undate, UndateInterval]) -> str:
        """
        Convert an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval` to ISO8601 string format.
        """
        if isinstance(undate, Undate):
            return self._undate_to_string(undate)
        elif isinstance(undate, UndateInterval):
            # strictly speaking I don't think ISO8601 supports open-ended ranges
            # should we add an exception for dates that can't be represented by a particular format?
            # (we'll likely need it for uncertain/approx, which ISO8601 doesn't handle')
            start = self._undate_to_string(undate.earliest) if undate.earliest else ""
            end = self._undate_to_string(undate.latest) if undate.latest else ""
            return f"{start}/{end}"

    def _undate_to_string(self, undate: Undate) -> str:
        # serialize to iso format for simplicity, for now
        date_parts: List[Union[str, None]] = []
        # for each part of the date that is known, generate the string format
        # then combine
        # TODO: should error if we have year and day but no month
        # TODO: may want to refactor and take advantage of the year/month/day properties
        # added for use in EDTF formatter code
        for date_portion, iso_format in self.iso_format.items():
            # is known means fully known, means guaranteed integer
            if undate.is_known(date_portion):
                # NOTE: datetime strftime for %Y for 3-digit year
                # results in leading zero in some environments
                # and not others; force year to always be 4 digits
                if date_portion == "year" and undate.year:
                    try:
                        date_parts.append("%04d" % int(undate.year))
                    except ValueError:
                        # shouldn't happen because of is_known
                        date_parts.append(undate.year)
                elif date_portion == "month" and undate.month:
                    try:
                        date_parts.append("%02d" % int(undate.month))
                    except ValueError:
                        # shouldn't happen because of is_known
                        date_parts.append(undate.month)
                elif date_portion == "day" and undate.day:
                    try:
                        date_parts.append("%02d" % int(undate.day))
                    except ValueError:
                        # shouldn't happen because of is_known
                        date_parts.append(undate.day)

            elif date_portion == "year":
                # if year is not known, add '-' for year portion,
                # to genereate --MM-DD unknown year format
                date_parts.append("-")
        # TODO: fix type error: "list[str | None]" is incompatible with "Iterable[str]"
        return "-".join(date_parts)  # type: ignore
