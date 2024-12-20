from calendar import monthrange

from undate.converters.base import BaseCalendarConverter


class GregorianDateConverter(BaseCalendarConverter):
    """
    Calendar converter class for Gregorian calendar.
    """

    #: converter name: Gregorian
    name: str = "Gregorian"
    #: calendar
    calendar_name: str = "Gregorian"

    #: known non-leap year
    NON_LEAP_YEAR: int = 2022

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
            max_day = 31

        return max_day

    def to_gregorian(self, year, month, day) -> tuple[int, int, int]:
        """Convert to Gregorian date. This returns the specified by year, month,
        and day unchanged, but is provided for consistency since all calendar
        converters need to support conversion to Gregorian calendar for
        a common point of comparison.
        """
        return (year, month, day)
