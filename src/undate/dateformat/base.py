# base class for date format parsers
from typing import Dict
import pkgutil
import importlib

"""Base class for date format parsing and serializing

To add support for a new date format:

- create a new file under undate/dateformat
- extend BaseDateFormat and implement parse and to_string methods
  as desired/appropriate
- Add your new formatter to [... details TBD ...]
  so that it will be included in the available formatters

"""


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

    _formatters_imported = False

    @classmethod
    def import_formatters(cls):
        # dynamically import all undate.dateformat formatters
        # so that they will be included in available formatters
        # even if not explicitly imported. Only import once.
        if not cls._formatters_imported:
            # TODO: add debug loading; confirm in test that not called again
            import undate.dateformat

            # load packages under this path with curent package prefix
            formatter_path = undate.dateformat.__path__
            formatter_prefix = f"{undate.dateformat.__name__}."

            for importer, modname, ispkg in pkgutil.iter_modules(
                formatter_path, formatter_prefix
            ):
                # import everything except the current file
                if not modname.endswith(".base"):
                    importlib.import_module(modname)

            cls._formatters_imported = True

    @classmethod
    def available_formatters(cls) -> Dict[str, "BaseDateFormat"]:
        # ensure undate formatters are imported
        cls.import_formatters()
        return {c.name: c for c in cls.__subclasses__()}  # type: ignore
