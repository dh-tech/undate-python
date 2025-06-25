from undate.converters.calendars import HebrewDateConverter
from undate.undate import Calendar


class SeleucidDateConverter(HebrewDateConverter):
    #: offset for Seleucid calendar: Seleucid year + 3449 = Anno Mundi year
    SELEUCID_OFFSET = 3449

    #: converter name: Seleucid
    name: str = "Seleucid"
    calendar_name: str = "Seleucid"

    def __init__(self):
        super().__init__()
        # override hebrew calendar to initialize undates with seleucid
        # calendar; this triggers Seleucid calendar to_gregorian method use
        self.transformer.calendar = Calendar.SELEUCID

    def to_gregorian(self, year: int, month: int, day: int) -> tuple[int, int, int]:
        """Convert a Seleucid date, specified by year, month, and day,
        to the Gregorian equivalent date. Uses hebrew calendar conversion
        logic with :attr:`SELEUCID_OFFSET`. Returns a tuple of year, month, day.
        """
        return super().to_gregorian(year + self.SELEUCID_OFFSET, month, day)

    def days_in_year(self, year: int) -> int:
        """the number of days in the specified year for this calendar"""
        return super().days_in_year(year + self.SELEUCID_OFFSET)
