# base class for date format parsers
from typing import Dict

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

    @classmethod
    def available_formatters(cls) -> Dict[str, "BaseDateFormat"]:
        # FIXME: workaround for circular import problem"

        from undate.dateformat.iso8601 import ISO8601DateFormat

        return {c.name: c for c in cls.__subclasses__()}  # type: ignore
