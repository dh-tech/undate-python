import pytest

from undate.dateformat.base import BaseDateFormat


class TestBaseDateFormat:
    def test_available_formatters(self):
        available_formatters = BaseDateFormat.available_formatters()
        assert type(available_formatters) == dict

        # NOTE: import _after_ generating available formatters
        # so we can confirm it gets loaded
        from undate.dateformat.iso8601 import ISO8601DateFormat

        assert ISO8601DateFormat.name in available_formatters
        assert available_formatters[ISO8601DateFormat.name] == ISO8601DateFormat

    def test_formatters_are_unique(self):
        assert len(BaseDateFormat.available_formatters()) == len(
            BaseDateFormat.__subclasses__()
        ), "Formatter names have to be unique."

        # TODO: order tests, so this test is run last; otherwise formatter names won't be unique
        # class ISO8601DateFormat2(BaseDateFormat):
        #     # NOTE: do we care about validation? could use regex
        #     # but maybe be permissive, warn if invalid but we can parse

        #     name = "ISO8601"

        # assert len(BaseDateFormat.available_formatters()) != len(BaseDateFormat.__subclasses__())

    def test_parse_not_implemented(self):
        with pytest.raises(NotImplementedError):
            BaseDateFormat().parse("foo bar baz")

    def test_parse_to_string(self):
        with pytest.raises(NotImplementedError):
            BaseDateFormat().to_string(1991)
