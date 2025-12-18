import pytest

from undate.converters.calendars import HebrewDateConverter
from undate.converters.calendars.hebrew.transformer import HebrewUndate
from undate.undate import Calendar, Undate
from undate.date import DatePrecision, Date


class TestHebrewDateConverter:
    def test_parse(self):
        # day
        # 26 Tammuz 4816: Tammuz = month 4 (17 July, 1056 Gregorian)
        date_str = "26 Tammuz 4816"
        date = HebrewDateConverter().parse(date_str)
        assert date == HebrewUndate(4816, 4, 26)
        assert date.calendar == Calendar.HEBREW
        assert date.precision == DatePrecision.DAY
        assert date.label == f"{date_str} {HebrewDateConverter.calendar_name}"

        # month
        date_str = "Ṭevet 5362"
        date = HebrewDateConverter().parse(date_str)
        assert date == HebrewUndate(5362, 10)  # Teveth = month 10
        assert date.calendar == Calendar.HEBREW
        assert date.precision == DatePrecision.MONTH
        assert date.label == f"{date_str} {HebrewDateConverter.calendar_name}"

        # year
        date_str = "4932"
        date = HebrewDateConverter().parse(date_str)
        assert date == HebrewUndate(4932)
        assert date.calendar == Calendar.HEBREW
        assert date.precision == DatePrecision.YEAR
        assert date.label == f"{date_str} {HebrewDateConverter.calendar_name}"

    def test_gregorian_earliest_latest(self):
        # earliest/latest should be converted to Gregorian for comparison

        # full date

        # 26 Tammuz 4816: 17 July, 1056; Tammuz = month 4
        date = HebrewUndate(4816, 4, 26)
        assert date.earliest == Date(1056, 7, 17)
        assert date.latest == Date(1056, 7, 17)
        # 13 Tishrei 5416 Anno Mundi (1655-10-14)
        date = HebrewUndate(5416, 7, 13)  # Tishrei = month 7
        assert date.earliest == Date(1655, 10, 14)
        assert date.latest == Date(1655, 10, 14)

        # month

        # Ṭevet 5362 Anno Mundi (25 December, 1601 – 22 January, 1602)
        date = HebrewUndate(5362, 10)
        assert date.earliest == Date(1601, 12, 25)
        assert date.latest == Date(1602, 1, 22)

        # year
        # 5416 : October 1655 to September 1656
        date = HebrewUndate(5416)
        assert date.earliest == Date(1655, 10, 2)
        assert date.latest == Date(1656, 9, 18)

    def test_parse_error(self):
        # a string we can't parse should raise an error
        with pytest.raises(ValueError):
            HebrewDateConverter().parse("January 2, 1991")
        # empty string should also error
        with pytest.raises(ValueError):
            HebrewDateConverter().parse("")

        # non-string input should raise a type error
        with pytest.raises(TypeError):
            HebrewDateConverter().parse(42)

        with pytest.raises(TypeError):
            HebrewDateConverter().parse({"foo": "bar"})

    def test_partially_known(self):
        # hebrew dates get existing partially unknown behavior

        converter = HebrewDateConverter()

        # hebrew first/last month are not the same as min/max
        unknown_month = HebrewUndate(1243, "XX")
        assert unknown_month.precision == DatePrecision.MONTH
        assert unknown_month.earliest == Date(
            *converter.to_gregorian(1243, converter.first_month(), 1)
        )
        last_month = converter.last_month(year=1243)
        assert unknown_month.latest == Date(
            *converter.to_gregorian(
                1243, last_month, converter.max_day(1243, last_month)
            )
        )

        partially_unknown_month = HebrewUndate(1243, "1X")
        assert partially_unknown_month.precision == DatePrecision.MONTH
        assert partially_unknown_month.earliest == Date(
            *converter.to_gregorian(1243, 10, 1)
        )
        # for unknown digit, assume largest possible value instead
        # of last semantic monthin the year
        last_month = converter.max_month(year=1243)
        last_day = converter.max_day(1243, last_month)
        assert partially_unknown_month.latest == Date(
            *converter.to_gregorian(1243, last_month, last_day)
        )

        # second month has 29 days
        unknown_day = HebrewUndate(1243, 2, "XX")
        assert unknown_day.precision == DatePrecision.DAY
        assert unknown_day.earliest == Date(*converter.to_gregorian(1243, 2, 1))
        assert unknown_day.latest == Date(*converter.to_gregorian(1243, 2, 29))

        partially_unknown_day = HebrewUndate(1243, 2, "2X")
        assert partially_unknown_day.precision == DatePrecision.DAY
        assert partially_unknown_day.earliest == Date(
            *converter.to_gregorian(1243, 2, 20)
        )
        assert partially_unknown_day.latest == Date(
            *converter.to_gregorian(1243, 2, 29)
        )

    def test_compare_across_calendars(self):
        # only day-precision dates can be exactly equal across calendars

        # 26 Tammuz 4816: Tammuz = month 4 (17 July, 1056 Gregorian)
        assert HebrewUndate(4816, 4, 26) == Undate(1056, 7, 17)
        # 13 Tishrei 5416; Tieshrei = month 7 (1655-10-14)
        assert HebrewUndate(5416, 7, 13) == Undate(1655, 10, 14)

        # greater than / less than
        assert HebrewUndate(4816) < Undate(1060)
        assert HebrewUndate(5416) < Undate(1660)
        assert HebrewUndate(5416, 7) > Undate(1655, 1)
        assert HebrewUndate(4816, 4, 26) > Undate(1055, 5)

        # 26 Tammuz 4816: Tammuz = month 4 (17 July, 1056)
        # so it falls within or is c ontained by July 1056
        assert HebrewUndate(4816, 4, 26) in Undate(1056, 7)
        assert HebrewUndate(4816, 4, 26) not in Undate(1054)

        # sorting
        sorted_dates = sorted(
            [
                HebrewUndate(4816, 4, 26),  # 1056-07-17
                HebrewUndate(5416),  # 1655
                HebrewUndate(500),  # -3261
                Undate(1995),
                Undate(33),
                Undate(1350),
            ]
        )
        expected_gregorian_years = [-3261, 33, 1056, 1350, 1655, 1995]
        assert [d.earliest.year for d in sorted_dates] == expected_gregorian_years

    def test_days_in_year(self):
        converter = HebrewDateConverter()
        assert converter.days_in_year(4816) == 353
        assert converter.days_in_year(4817) == 355
        assert converter.days_in_year(4818) == 384
        assert converter.days_in_year(4819) == 355

    def test_representative_years(self):
        converter = HebrewDateConverter()
        # single year is not filtered
        assert converter.representative_years([4816]) == [4816]
        # 4816 has 353 days; 4817 has 355; 4818 has 384; 4819 has 355
        assert converter.representative_years([4816, 4817, 4818, 4819]) == [
            4816,
            4817,
            4818,
        ]
        assert converter.representative_years([4816, 4817, 4818, 4819, 4837]) == [
            4816,
            4817,
            4818,
            4837,
        ]

        # if no years are provided, returns a known leap year and non-leap years
        assert converter.representative_years() == [
            converter.LEAP_YEAR,
            converter.NON_LEAP_YEAR,
        ]
        assert converter.representative_years([]) == [
            converter.LEAP_YEAR,
            converter.NON_LEAP_YEAR,
        ]
