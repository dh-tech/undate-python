# base class for date format parsers


class BaseDateFormat:
    """Base class for parsing and formatting dates for specific formats."""

    # Subclasses should define a unique name.
    name = "Base Formatter"

    def parse(self, value):
        # should return an undate or undate interval
        raise NotImplementedError

    def to_string(self, undate):
        # convert an undate or interval to string representation for this format
        raise NotImplementedError

    @classmethod
    def available_formatters(cls):
        return {c.name: c for c in cls.__subclasses__()}
