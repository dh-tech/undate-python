from typing import Union

from lark.exceptions import UnexpectedCharacters

from undate.converters.base import BaseDateConverter
from undate.converters.calendars.hijri.parser import hijri_parser
from undate.converters.calendars.hijri.transformer import HijriDateTransformer
from undate.undate import Undate, UndateInterval


class HijriDateConverter(BaseDateConverter):
    """
    Converter for Hijri / Islamic calendar.

    Support for parsing Hijri dates and converting to Undate and UndateInterval
    objects in the Gregorian calendar.
    """

    #: converter name: Hijri
    name: str = "Hijri"
    calendar_name: str = "Hijrī"

    def __init__(self):
        self.transformer = HijriDateTransformer()

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        """
        Parse a Hijri date string and return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval` in Gregorian calendar.
        The Hijri date string is preserved in the undate label
        """
        if not value:
            raise ValueError("Parsing empty string is not supported")

        # parse the input string, then transform to undate object
        try:
            # parse the string with our Hijri date parser
            parsetree = hijri_parser.parse(value)
            # transform the parse tree into an undate or undate interval
            undate_obj = self.transformer.transform(parsetree)
            # set the original date as a label, with the calendar name
            undate_obj.label = f"{value} {self.calendar_name}"
            return undate_obj
        except UnexpectedCharacters as err:
            raise ValueError(f"Could not parse '{value}' as a Hijri date") from err

    # do we need to support conversion the other direction?
    # i.e., generate a Hijri date from an abitrary undate or undate interval?
