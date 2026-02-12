from calendar import monthrange, isleap

from lark.exceptions import UnexpectedCharacters

from undate.undate import Undate
from undate.converters.base import BaseCalendarConverter
from undate.converters.calendars.gregorian.parser import gregorian_parser
from undate.converters.calendars.gregorian.transformer import GregorianDateTransformer


class GregorianDateConverter(BaseCalendarConverter):
    """
    Calendar converter class for Gregorian calendar.
    """

    #: converter name: Gregorian
    name: str = "Gregorian"
    #: calendar
    calendar_name: str = "Gregorian"

    #: arbitrary known non-leap year
    NON_LEAP_YEAR: int = 2022
    #: arbitrary known leap year
    LEAP_YEAR: int = 2024

    def __init__(self):
        self.transformer = GregorianDateTransformer()

    def min_month(self) -> int:
        """First month for the Gregorian calendar."""
        return 1

    def max_month(self, year: int) -> int:
        """maximum numeric month for the specified year in the Gregorian calendar"""
        return 12

    def max_day(self, year: int, month: int) -> int:
        """maximum numeric day for the specified year and month in this calendar"""
        # if month is known, use that to calculate
        if month:
            # if year is known, use it; otherwise use a known non-leap year
            # (only matters for February)
            year = year or self.NON_LEAP_YEAR

            # Use monthrange from python builtin calendar module.
            # returns first day of the month and number of days in the month
            # for the specified year and month.
            _, max_day = monthrange(year, month)
        else:
            # if year and month are unknown, return maximum possible
            # TODO: should this return an IntervalRange?
            max_day = 31

        return max_day

    def representative_years(self, years: None | list[int] = None) -> list[int]:
        """Takes a list of years and returns a subset with one leap year and one non-leap year.
        If no years are specified, returns a known leap year and non-leap year.
        """

        # if years is unset or list is empty
        if not years:
            return [self.LEAP_YEAR, self.NON_LEAP_YEAR]

        found_leap = False
        found_non_leap = False
        rep_years = []
        for year in years:
            if isleap(year):
                if not found_leap:
                    found_leap = True
                    rep_years.append(year)
            else:
                if not found_non_leap:
                    found_non_leap = True
                    rep_years.append(year)
            # stop as soon as we've found one example of each type of year
            if found_leap and found_non_leap:
                break

        return rep_years

    def to_gregorian(self, year, month, day) -> tuple[int, int, int]:
        """Convert to Gregorian date. This returns the specified by year, month,
        and day unchanged, but is provided for consistency since all calendar
        converters need to support conversion to Gregorian calendar for
        a common point of comparison.
        """
        return (year, month, day)

    def parse(self, value: str) -> Undate:
        """
        Parse a Gregorian date string of any supported precision in any
        supported language and return an :class:`~undate.undate.Undate`.
        The input date string is preserved in the label of the resulting
        Undate object.
        """
        if not value:
            raise ValueError("Parsing empty string is not supported")

        # parse the input string, then transform to undate object
        try:
            # parse the string with our Hebrew date parser
            parsetree = gregorian_parser.parse(value)
            # transform the parse tree into an undate object
            undate_obj = self.transformer.transform(parsetree)
            # set the original date string as the label
            undate_obj.label = value
            return undate_obj
        except UnexpectedCharacters as err:
            raise ValueError(f"Could not parse '{value}' as a Gregorian date") from err
