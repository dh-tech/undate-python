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
        # The parser is inherited from HebrewDateConverter. If Seleucid has a distinct
        # string format that hebrew_parser can't handle, a seleucid_parser would be needed.
        # For now, assume string format compatibility for parsing, error message is the primary fix.

    def max_month(self, year: int = None) -> int:
        """Maximum numeric month for this calendar. Adjusted for Seleucid year."""
        if year is not None:
            am_year = year + self.SELEUCID_OFFSET
        else:
            am_year = None # Let parent handle None AM year if applicable (it defaults to non-leap)
        return super().max_month(am_year)

    def max_day(self, year: int = None, month: int = None) -> int:
        """Maximum numeric day for the specified year and month. Adjusted for Seleucid year."""
        if year is not None:
            am_year = year + self.SELEUCID_OFFSET
        else:
            am_year = None # Parent's max_day handles None year by defaulting
        
        # Parent's max_day handles None month by defaulting, so pass month as is.
        return super().max_day(am_year, month)

    def to_gregorian(self, year: int, month: int, day: int) -> tuple[int, int, int]:
        """Convert a Seleucid date, specified by year, month, and day,
        to the Gregorian equivalent date. Uses hebrew calendar conversion
        logic with :attr:`SELEUCID_OFFSET`. Returns a tuple of year, month, day.
        """
        return super().to_gregorian(year + self.SELEUCID_OFFSET, month, day)

    def parse(self, value: str): # Add type hint later if copying from parent
        """
        Parse a Seleucid date string and return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval`.
        The Seleucid date string is preserved in the undate label.
        This method overrides the parent to provide a Seleucid-specific error message.
        """
        if not value: # Copied from HebrewDateConverter.parse
            raise ValueError("Parsing empty string is not supported")

        # Import the parser used by the parent class directly
        from undate.converters.calendars.hebrew.parser import hebrew_parser
        try:
            # Uses the hebrew_parser and self.transformer (calendar set to SELEUCID in __init__)
            parsetree = hebrew_parser.parse(value) 
            undate_obj = self.transformer.transform(parsetree)
            undate_obj.label = f"{value} {self.calendar_name}"
            return undate_obj
        except Exception as err: # Catching broader Exception to be safe, can refine
            # Check if it's an UnexpectedCharacters error if lark is used by hebrew_parser
            from lark.exceptions import UnexpectedCharacters
            if isinstance(err, UnexpectedCharacters):
                 raise ValueError(f"Could not parse '{value}' as a Seleucid date") from err
            # Re-raise other errors or handle them if they are expected
            raise # Re-raise if not the specific parsing error we want to customize
