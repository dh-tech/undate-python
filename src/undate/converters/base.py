"""
:class:`~undate.converters.BaseDateConverter` provides a base class for
implementing date converters, which can provide support for
parsing and generating dates in different formats.
The converter subclass :class:`undate.converters.BaseCalendarConverter`
provides additional functionality needed for calendar conversion.

To add support for a new date converter:

- Create a new file under ``undate/converters/``
    - For converters with sufficient complexity, you may want to create a submodule;
      see ``undate.converters.edtf`` for an example.
- Extend ``BaseDateConverter`` and implement ``parse`` and ``to_string`` methods
  as desired/appropriate for your converter
- Add unit tests for the new converter in ``tests/test_converters/``
- Optionally, you may want to create a notebook to demonstrate the use and value
  of the new converter.

The new subclass should be loaded automatically and included in the converters
returned by :meth:`BaseDateConverter.available_converters`

To add support for a new calendar converter:

- Create a new file under ``undate/converters/calendars/``
    - For converters with sufficient complexity, you may want to create a submodule;
      see ``undate.converters.calendars.islamic`` for an example.
- Extend ``BaseCalendarConverter`` and implement ``parse`` and ``to_string``
  formatter methods as desired/appropriate for your converter as well as the
  additional methods for ``max_month``, ``max_day``, and conversion ``to_gregorian``
  calendar.
- Import your calendar in ``undate/converters/calendars/__init__.py`` and include in `__all__``
- Add unit tests for the new calendar logic under ``tests/test_converters/calendars/``
- Add the new calendar to the ``Calendar`` enum of supported calendars in
  ``undate/undate.py`` and confirm that the `get_converter` method loads your
  calendar converter correctly (an existing unit test should cover this).
- Consider creating a notebook to demonstrate the use of the calendar
  converter.

Calendar converter subclasses are also automatically loaded and included
in the list of available converters.

-------------------
"""

import importlib
import logging
import pkgutil
from functools import cache
from typing import Dict, Type

from undate.date import Date

logger = logging.getLogger(__name__)


class BaseDateConverter:
    """Base class for parsing, formatting, and converting dates to handle
    specific formats and different calendars."""

    #: Converter name. Subclasses must define a unique name.
    name: str = "Base Converter"

    # provisional...
    LEAP_YEAR = 0
    NON_LEAP_YEAR = 0

    def parse(self, value: str):
        """
        Parse a string and return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval`. Must be implemented by
        subclasses.
        """
        # can't add type hint here because of circular import
        # should return an undate or undate interval
        raise NotImplementedError

    def to_string(self, undate) -> str:
        """
        Convert an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval` to string.
        Must be implemented by subclasses.
        """

        # undate param should be of type Union[Undate, UndateInterval] but can't add type hint here because of circular import
        # convert an undate or interval to string representation for this format
        raise NotImplementedError

    # cache import class method to ensure we only import once
    @classmethod
    @cache
    def import_converters(cls) -> int:
        """Import all undate converters
        so that they will be included in available converters
        even if not explicitly imported. Only import once.
        returns the count of modules imported."""

        logger.debug("Loading converters under undate.converters")
        import undate.converters

        # load packages under this path with curent package prefix
        converter_path = undate.converters.__path__
        converter_prefix = f"{undate.converters.__name__}."

        import_count = 0
        for importer, modname, ispkg in pkgutil.iter_modules(
            converter_path, converter_prefix
        ):
            # import everything except the current file
            if not modname.endswith(".base"):
                importlib.import_module(modname)
                import_count += 1

        return import_count

    @classmethod
    def available_converters(cls) -> Dict[str, Type["BaseDateConverter"]]:
        """
        Dictionary of available converters keyed on name.
        """
        return {c.name: c for c in cls.subclasses()}  # type: ignore

    @classmethod
    def subclasses(cls) -> set[Type["BaseDateConverter"]]:
        """
        Set of available converters classes. Includes descendant
        subclasses, including calendar converters, but does not include
        :class:`BaseCalendarConverter`.
        """
        # ensure undate converters are imported
        cls.import_converters()

        # find all direct subclasses, excluding base calendar converter
        direct_subclasses = cls.__subclasses__()
        all_subclasses = set(direct_subclasses)
        # recurse to find nested subclasses
        for subc in direct_subclasses:
            all_subclasses |= subc.subclasses()

        # omit the calendar converter base class, which is not itself a converter
        all_subclasses -= {BaseCalendarConverter}
        return all_subclasses


class BaseCalendarConverter(BaseDateConverter):
    """Base class for calendar converters, with additional methods required
    for calendars."""

    #: Converter name. Subclasses must define a unique name.
    name: str = "Base Calendar Converter"

    #: arbitrary known non-leap year
    NON_LEAP_YEAR: int
    #: arbitrary known leap year
    LEAP_YEAR: int

    # minimum year for this calendar, if there is one
    MIN_YEAR: None | int = None
    # maximum year for this calendar, if there is one
    MAX_YEAR: None | int = None

    def min_month(self) -> int:
        """Smallest numeric month for this calendar."""
        raise NotImplementedError

    def max_month(self, year: int) -> int:
        """Maximum numeric month for this calendar"""
        raise NotImplementedError

    def first_month(self) -> int:
        """first month in this calendar; by default, returns :meth:`min_month`."""
        return self.min_month()

    def last_month(self, year: int) -> int:
        """last month in this calendar; by default, returns :meth:`max_month`."""
        return self.max_month(year)

    def max_day(self, year: int, month: int) -> int:
        """maximum numeric day for the specified year and month in this calendar"""
        raise NotImplementedError

    def days_in_year(self, year: int) -> int:
        """Number of days in the specified year in this calendar. The default implementation
        uses min and max month and max day methods along with Gregorian conversion method
        to calculate the number of days in the specified year.
        """
        year_start = Date(*self.to_gregorian(year, self.min_month(), 1))
        last_month = self.max_month(year)
        year_end = Date(
            *self.to_gregorian(year, last_month, self.max_day(year, last_month))
        )
        # add 1 because the difference doesn't include the end point
        return (year_end - year_start).days + 1

    def representative_years(self, years: None | list[int] = None) -> list[int]:
        """Returns a list of representative years within the specified list.
        Result should include one for each type of variant year for this
        calendar (e.g., leap year and non-leap year). If no years are specified,
        returns a list of representative years for the current calendar.
        """
        raise NotImplementedError

    def to_gregorian(self, year, month, day) -> tuple[int, int, int]:
        """Convert a date for this calendar specified by numeric year, month, and day,
        into the Gregorian equivalent date. Should return a tuple of year, month, day.
        """
        raise NotImplementedError
