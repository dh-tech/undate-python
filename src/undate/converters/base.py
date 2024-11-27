"""
:class:`~undate.converters.BaseDateConverter` provides a base class for
implementing date converters, which can provide support for
parsing and generating dates in different formats.
The converter subclass :class:`undate.converters.BaseCalendarConverter`
provides additional functionaly needed for calendar conversion.

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
      see ``undate.converters.calendars.hijri`` for an example.
- Extend ``BaseCalendarConverter`` and implement ``parse`` and ``to_string``
  formatter methods as desired/appropriate for your converter as well as the
  additional methods for ``max_month``, ``max_day``, and convertion ``to_gregorian``
  calendar.
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

logger = logging.getLogger(__name__)


class BaseDateConverter:
    """Base class for parsing, formatting, and converting dates to handle
    specific formats and different calendars."""

    #: Converter name. Subclasses must define a unique name.
    name: str = "Base Converter"

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
    def subclasses(cls) -> list[Type["BaseDateConverter"]]:
        """
        List of available converters classes. Includes calendar convert
        subclasses.
        """
        # ensure undate converters are imported
        cls.import_converters()

        # find all direct subclasses, excluding base calendar converter
        subclasses = cls.__subclasses__()
        subclasses.remove(BaseCalendarConverter)
        # add all subclasses of calendar converter base class
        subclasses.extend(BaseCalendarConverter.__subclasses__())
        return subclasses


class BaseCalendarConverter(BaseDateConverter):
    """Base class for calendar converters, with additional methods required
    for calendars."""

    #: Converter name. Subclasses must define a unique name.
    name: str = "Base Calendar Converter"

    def max_month(self, year: int) -> int:
        """Maximum month for this calendar for this year"""
        raise NotImplementedError

    def max_day(self, year: int, month: int) -> int:
        """maximum numeric day for the specified year and month in this calendar"""
        raise NotImplementedError

    def to_gregorian(self, year, month, day) -> tuple[int, int, int]:
        """Convert a date for this calendar specified by numeric year, month, and day,
        into the Gregorian equivalent date. Should return a tuple of year, month, day.
        """
        raise NotImplementedError
