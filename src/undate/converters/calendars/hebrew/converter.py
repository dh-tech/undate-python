from typing import Union

from convertdate import hebrew  # type: ignore
from lark.exceptions import UnexpectedCharacters

from undate import Undate, UndateInterval
from undate.converters.base import BaseCalendarConverter
from undate.converters.calendars.hebrew.parser import hebrew_parser
from undate.converters.calendars.hebrew.transformer import HebrewDateTransformer


class HebrewDateConverter(BaseCalendarConverter):
    """
    Converter for Hebrew Anno Mundicalendar.

    Support for parsing Anno Mundi dates and converting to Undate and UndateInterval
    objects in the Gregorian calendar.
    """

    #: converter name: Hebrew
    name: str = "Hebrew"
    calendar_name: str = "Anno Mundi"

    def __init__(self):
        self.transformer = HebrewDateTransformer()

    def min_month(self) -> int:
        """Smallest numeric month for this calendar."""
        return 1

    def max_month(self, year: int = None) -> int: # Added default None for year
        """Maximum numeric month for this calendar. In Hebrew calendar, this is 12 or 13
        depending on whether it is a leap year.
        If year is None, defaults to 12 (non-leap year)."""
        if year is None:
            # Default to a non-leap year's number of months if year is not specified
            return 12 
        return hebrew.year_months(year)

    def first_month(self) -> int:
        """First month in this calendar. The Hebrew civil year starts in Tishri."""
        return hebrew.TISHRI

    def last_month(self, year: int) -> int:
        """Last month in this calendar. Hebrew civil year starts in Tishri,
        Elul is the month before Tishri."""
        return hebrew.ELUL

    def max_day(self, year: int = None, month: int = None) -> int: # Added default None
        """maximum numeric day for the specified year and month in this calendar"""
        # NOTE: unreleased v2.4.1 of convertdate standardizes month_days to month_length
        
        # Handle None year/month by defaulting to a common non-leap scenario
        # Default year to a known non-leap year if None, e.g. 5783
        # Default month to Nisan (1) if None, as it's the first biblical month and always has 30 days.
        effective_year = year if year is not None else 5783 # 5783 is a non-leap year
        effective_month = month if month is not None else hebrew.NISAN # Nisan is 1

        # Ensure year is not None for leap check if month is Adar related and year was originally None
        if year is None and (effective_month == 12 or effective_month == 13): # Adar, Adar I or Adar II
             # hebrew.month_days needs a concrete year to determine leap month lengths correctly.
             # We've defaulted to 5783 (non-leap).
             pass


        return hebrew.month_days(effective_year, effective_month)

    def to_gregorian(self, year: int, month: int, day: int) -> tuple[int, int, int]:
        """Convert a Hebrew date, specified by year, month, and day,
        to the Gregorian equivalent date. Returns a tuple of year, month, day.
        """
        return hebrew.to_gregorian(year, month, day)

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        """
        Parse a Hebrew date string and return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval`.
        The Hebrew date string is preserved in the undate label.
        """
        if not value:
            raise ValueError("Parsing empty string is not supported")

        # parse the input string, then transform to undate object
        try:
            # parse the string with our Hebrew date parser
            parsetree = hebrew_parser.parse(value)
            # transform the parse tree into an undate or undate interval
            undate_obj = self.transformer.transform(parsetree)
            # set the original date as a label, with the calendar name
            undate_obj.label = f"{value} {self.calendar_name}"
            return undate_obj
        except UnexpectedCharacters as err:
            raise ValueError(f"Could not parse '{value}' as a Hebrew date") from err

    # do we need to support conversion the other direction?
    # i.e., generate a Hebrew date from an abitrary undate or undate interval?
