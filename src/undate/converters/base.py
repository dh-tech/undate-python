"""
Base class for converting date between different formats and calendars.

To add support for a new date format or conversion:

- create a new file or module under undate/converters
- extend BaseDateConverter and implement parse and to_string methods
  as desired/appropriate

The new subclass should be loaded automatically and included in the converters
returned by :meth:`BaseDateConverter.available_converters`

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

    # Subclasses should define a unique name.
    name: str = "Base Converter"

    def parse(self, value: str):
        # can't add type hint here because of circular import
        # should return an undate or undate interval
        raise NotImplementedError

    def to_string(self, undate) -> str:
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
        # ensure undate converters are imported
        cls.import_converters()
        return {c.name: c for c in cls.__subclasses__()}  # type: ignore
