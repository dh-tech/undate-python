# base class for date format parsers
from typing import Union, Dict


class BaseDateFormat:
    """Base class for parsing and formatting dates for specific formats."""

    # Subclasses should define a unique name.
    name: str = "Base Formatter"

    def parse(self, value: str):
        # can't add type hint here because of circular import
        # should return an undate or undate interval
        raise NotImplementedError

    def to_string(self, undate) -> str:
        # undate param should be of type Union[Undate, UndateInterval but can't add type hint here because of circular import
        # convert an undate or interval to string representation for this format
        raise NotImplementedError

    @classmethod
    def available_formatters(cls) -> Dict[str, "BaseDateFormat"]:
        # TODO: fix type error
        # Expression of type "dict[str, Type[BaseDateFormat]]" cannot be assigned to return type "Dict[str, BaseDateFormat]"
        # "dict[str, Type[BaseDateFormat]]" is incompatible with "Dict[str, BaseDateFormat]"
        return {c.name: c for c in cls.__subclasses__()}  # type: ignore
