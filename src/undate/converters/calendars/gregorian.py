from calendar import monthrange
from typing import Optional

from undate.converters.base import BaseDateConverter


class GregorianDateConverter(BaseDateConverter):
    """
    Converter class for Gregorian calendar.
    """

    #: converter name: Gregorian
    name: str = "Gregorian"
    calendar_name: str = "Gregorian"

    #: known non-leap year
    NON_LEAP_YEAR: int = 2022

    def max_month(self, year: int) -> int:
        """Maximum month for this calendar for this year"""
        return 12

    def max_day(self, year: Optional[int] = None, month: Optional[int] = None) -> int:
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
        return (year, month, day)
