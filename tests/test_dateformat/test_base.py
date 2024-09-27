import logging

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

    def test_parse_not_implemented(self):
        with pytest.raises(NotImplementedError):
            BaseDateFormat().parse("foo bar baz")

    def test_parse_to_string(self):
        with pytest.raises(NotImplementedError):
            BaseDateFormat().to_string(1991)


def test_import_formatters_import_only_once(caplog):
    # clear the cache, since any instantiation of an Undate
    # object anywhere in the test suite will populate it
    BaseDateFormat.import_formatters.cache_clear()

    # run first, and confirm it runs and loads formatters
    with caplog.at_level(logging.DEBUG):
        import_count = BaseDateFormat.import_formatters()
    # should import at least one thing (iso8601)
    assert import_count >= 1
    # should have log entry
    assert "Loading formatters" in caplog.text

    # if we clear the log and run again, should not do anything
    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        BaseDateFormat.import_formatters()
    assert "Loading formatters" not in caplog.text


@pytest.mark.last
def test_formatters_unique_error():
    # confirm that our uniqe formatters check fails when it should

    # run this test last because we can't undefine the subclass
    # once it exists...
    class ISO8601DateFormat2(BaseDateFormat):
        name = "ISO8601"  # duplicates existing formatter

    assert len(BaseDateFormat.available_formatters()) != len(
        BaseDateFormat.__subclasses__()
    )
