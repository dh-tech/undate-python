from typing import Union

from convertdate import islamic  # type: ignore
from lark.exceptions import UnexpectedCharacters

from undate import Undate, UndateInterval
from undate.converters.base import BaseCalendarConverter
from undate.converters.calendars.islamic.parser import islamic_parser
from undate.converters.calendars.islamic.transformer import IslamicDateTransformer


class IslamicDateConverter(BaseCalendarConverter):
    """
    Converter for Islamic Hijri calendar.

    Support for parsing Islamic Hijri dates and converting to Undate and UndateInterval
    objects in the Gregorian calendar.
    """

    #: converter name: Islamic
    name: str = "Islamic"
    calendar_name: str = "Islamic"

    def __init__(self):
        self.transformer = IslamicDateTransformer()

    def max_day(self, year: int, month: int) -> int:
        """maximum numeric day for the specified year and month in this calendar"""
        return islamic.month_length(year, month)

    def min_month(self) -> int:
        """smallest numeric month for this calendar."""
        return 1

    def max_month(self, year: int) -> int:
        """maximum numeric month for this calendar"""
        return 12

    def to_gregorian(self, year: int, month: int, day: int) -> tuple[int, int, int]:
        """Convert a Hijri date, specified by year, month, and day,
        to the Gregorian equivalent date. Returns a tuple of year, month, day.
        """
        return islamic.to_gregorian(year, month, day)

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        """
        Parse an Islamic/Hijri date string and return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval`.
        The Islamic/Hijri date string is preserved in the undate label.
        """
        if not value:
            raise ValueError("Parsing empty string is not supported")

        # parse the input string, then transform to undate object
        try:
            # parse the string with our Islamic Hijri date parser
            parsetree = islamic_parser.parse(value)
            # transform the parse tree into an undate or undate interval
            undate_obj = self.transformer.transform(parsetree)
            # set the original date as a label, with the calendar name
            undate_obj.label = f"{value} {self.calendar_name}"
            return undate_obj
        except UnexpectedCharacters as err:
            raise ValueError(f"Could not parse '{value}' as an Islamic date") from err

    # do we need to support conversion the other direction?
    # i.e., generate an Islamic Hijri date from an arbitrary undate or undate interval?
