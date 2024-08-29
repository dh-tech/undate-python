"""
Base class for date format parsing and serializing

To add support for a new date format:

- create a new file under undate/dateformat
- extend BaseDateFormat and implement parse and to_string methods
  as desired/appropriate

It should be loaded automatically and included in the formatters
returned by :meth:`BaseDateFormat.available_formatters`

"""

import importlib
import logging
import pkgutil
from typing import Dict, Type, Union
from functools import lru_cache


logger = logging.getLogger(__name__)


class BaseDateFormat:
    """Base class for parsing and formatting dates for specific formats."""

    # Subclasses should define a unique name.
    name: str = "Base Formatter"

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
    @lru_cache
    def import_formatters(cls) -> int:
        """Import all undate.dateformat formatters
        so that they will be included in available formatters
        even if not explicitly imported. Only import once.
        returns the count of modules imported."""

        logger.debug("Loading formatters under undate.dateformat")
        import undate.dateformat

        # load packages under this path with curent package prefix
        formatter_path = undate.dateformat.__path__
        formatter_prefix = f"{undate.dateformat.__name__}."

        import_count = 0
        for importer, modname, ispkg in pkgutil.iter_modules(
            formatter_path, formatter_prefix
        ):
            # import everything except the current file
            if not modname.endswith(".base"):
                importlib.import_module(modname)
                import_count += 1

        return import_count

    @classmethod
    def available_formatters(cls) -> Dict[str, Type["BaseDateFormat"]]:
        # ensure undate formatters are imported
        cls.import_formatters()
        return {c.name: c for c in cls.__subclasses__()}  # type: ignore
