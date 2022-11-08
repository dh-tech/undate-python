# base class for date format parsers


class DateFormat:
    """Base class for parsing and formatting dates for specific formats."""

    def parse(self, value):
        # should return an undate or undate interval
        raise NotImplementedError

    def to_string(self, undate):
        # convert an undate or interval to string representation for this format
        raise NotImplementedError
