import logging

import pytest
from undate.converters.base import BaseDateConverter, BaseCalendarConverter
from undate.converters.calendars import (
    GregorianDateConverter,
    HebrewDateConverter,
    IslamicDateConverter,
)


class TestBaseDateConverter:
    def test_available_converters(self):
        available_converters = BaseDateConverter.available_converters()
        assert isinstance(available_converters, dict)

        # NOTE: import _after_ generating available formatters
        # so we can confirm it gets loaded
        from undate.converters.iso8601 import ISO8601DateFormat

        assert ISO8601DateFormat.name in available_converters
        assert available_converters[ISO8601DateFormat.name] == ISO8601DateFormat

    def test_converters_are_unique(self):
        assert len(BaseDateConverter.available_converters()) == len(
            BaseDateConverter.subclasses()
        ), "Formatter names have to be unique."

    def test_parse_not_implemented(self):
        with pytest.raises(NotImplementedError):
            BaseDateConverter().parse("foo bar baz")

    def test_parse_to_string(self):
        with pytest.raises(NotImplementedError):
            BaseDateConverter().to_string(1991)

    def test_subclasses(self):
        # define a nested subclass
        class SubSubConverter(IslamicDateConverter):
            pass

        subclasses = BaseDateConverter.subclasses()
        assert BaseCalendarConverter not in subclasses
        assert IslamicDateConverter in subclasses
        assert HebrewDateConverter in subclasses
        assert GregorianDateConverter in subclasses
        assert SubSubConverter in subclasses


def test_import_converters_import_only_once(caplog):
    # clear the cache, since any instantiation of an Undate
    # object anywhere in the test suite will populate it
    BaseDateConverter.import_converters.cache_clear()

    # run first, and confirm it runs and loads formatters
    with caplog.at_level(logging.DEBUG):
        import_count = BaseDateConverter.import_converters()
    # should import at least one thing (iso8601)
    assert import_count >= 1
    # should have log entry
    assert "Loading converters" in caplog.text

    # if we clear the log and run again, should not do anything
    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        BaseDateConverter.import_converters()
    assert "Loading converters" not in caplog.text


@pytest.mark.last
def test_converters_unique_error():
    # confirm that unique converter check fails when it should

    # run this test last because we can't undefine the subclass
    # once it exists...
    class ISO8601DateFormat2(BaseDateConverter):
        name = "ISO8601"  # duplicates existing formatter

    assert len(BaseDateConverter.available_converters()) != len(
        BaseDateConverter.subclasses()
    )


class TestBaseCalendarConverter:
    def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            BaseCalendarConverter().min_month()
        with pytest.raises(NotImplementedError):
            BaseCalendarConverter().max_month(1900)
        with pytest.raises(NotImplementedError):
            BaseCalendarConverter().max_day(1900, 12)
        with pytest.raises(NotImplementedError):
            BaseCalendarConverter().to_gregorian(1900, 12, 31)
        with pytest.raises(NotImplementedError):
            BaseCalendarConverter().representative_years([1900, 1901])
