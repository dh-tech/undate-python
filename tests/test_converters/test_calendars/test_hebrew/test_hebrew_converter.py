import pytest

from undate.converters.calendars import HebrewDateConverter
from undate.converters.calendars.hebrew.transformer import HebrewUndate
from undate.undate import Calendar, Undate
from undate.date import DatePrecision, Date
from convertdate import hebrew # For constants and leap year checks


class TestHebrewDateConverter:
    converter = HebrewDateConverter()

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

    # --- Tests for BaseCalendarConverter method implementations ---

    def test_min_month(self):
        assert self.converter.min_month() == 1 # Nisan is the first month numerically

    def test_max_month(self):
        # 5784 is a Hebrew leap year (13 months)
        assert self.converter.max_month(year=5784) == 13
        # 5783 is a Hebrew non-leap year (12 months)
        assert self.converter.max_month(year=5783) == 12
        # Test with None year, should default to non-leap year behavior for max_month
        assert self.converter.max_month(year=None) == 12


    def test_first_month(self):
        # As per current implementation, first_month() is TISHRI (7)
        assert self.converter.first_month() == hebrew.TISHRI # Tishri is 7

    def test_last_month(self):
        # As per current implementation, last_month() is ELUL (6) for any year
        assert self.converter.last_month(year=5784) == hebrew.ELUL # Elul is 6
        assert self.converter.last_month(year=5783) == hebrew.ELUL
        assert self.converter.last_month(year=None) == hebrew.ELUL

    def test_max_day(self):
        # Iyar (month 2) always has 29 days
        assert self.converter.max_day(year=5783, month=hebrew.IYYAR) == 29 # Iyar = 2
        assert self.converter.max_day(year=5784, month=hebrew.IYYAR) == 29

        # Nisan (month 1) always has 30 days
        assert self.converter.max_day(year=5783, month=hebrew.NISAN) == 30 # Nisan = 1
        assert self.converter.max_day(year=5784, month=hebrew.NISAN) == 30

        # Adar I (month 12) in a leap year (e.g., 5784) has 30 days.
        assert hebrew.leap(5784) # Confirm 5784 is a leap year
        assert self.converter.max_day(year=5784, month=12) == 30 # Use month number 12 for Adar I

        # Adar (month 12) in a non-leap year (e.g., 5783) has 29 days.
        # hebrew.ADAR is 6 for convertdate, but converter uses 1-based months 1-12/13.
        # In a non-leap year, the 12th month is Adar.
        assert not hebrew.leap(5783) # Confirm 5783 is not a leap year
        # The converter's month 12 in a non-leap year corresponds to hebrew.ADAR (which is 6 in convertdate's system for non-leap)
        # The converter itself maps its internal 1-12/13 month system to convertdate's system.
        # We need to use the converter's own month numbering for the test.
        # Month 12 in a non-leap year for the converter is Adar.
        assert self.converter.max_day(year=5783, month=12) == 29


        # Adar II (month 13) in a leap year (e.g., 5784) has 29 days.
        # hebrew.ADAR_II is 13 (or 7 in convertdate's system for leap years, but converter uses 13)
        assert self.converter.max_day(year=5784, month=13) == 29
        
        # Test with None for year and/or month (should use defaults)
        # Default for month (if None) is 1 (Nisan), which has 30 days.
        assert self.converter.max_day(year=5783, month=None) == 30
        # Default for year (if None) is non-leap. Default for month is 1 (Nisan).
        assert self.converter.max_day(year=None, month=None) == 30
        # Default for year (non-leap), specific month Iyar (29 days)
        assert self.converter.max_day(year=None, month=hebrew.IYYAR) == 29


    def test_direct_to_gregorian(self):
        # 1 Tishri 5782 corresponds to September 7, 2021
        # Tishri is month 7 for the converter (aligns with hebrew.TISHRI)
        gregorian_date = self.converter.to_gregorian(5782, hebrew.TISHRI, 1)
        assert gregorian_date == (2021, 9, 7)

        # 15 Nisan 5783 corresponds to April 6, 2023
        # Nisan is month 1 for the converter (aligns with hebrew.NISAN)
        gregorian_date_2 = self.converter.to_gregorian(5783, hebrew.NISAN, 15)
        assert gregorian_date_2 == (2023, 4, 6)

        # Test a date in Adar I during a leap year
        # 10 Adar I 5784 corresponds to February 19, 2024
        # Adar I is month 12 for the converter in a leap year
        assert hebrew.leap(5784)
        gregorian_date_3 = self.converter.to_gregorian(5784, 12, 10) # month 12 = Adar I
        assert gregorian_date_3 == (2024, 2, 19)

        # Test a date in Adar II during a leap year
        # 10 Adar II 5784 corresponds to March 20, 2024
        # Adar II is month 13 for the converter in a leap year
        gregorian_date_4 = self.converter.to_gregorian(5784, 13, 10) # month 13 = Adar II
        assert gregorian_date_4 == (2024, 3, 20)

        # Test a date in Adar during a non-leap year
        # 10 Adar 5783 corresponds to March 3, 2023
        # Adar is month 12 for the converter in a non-leap year
        assert not hebrew.leap(5783)
        gregorian_date_5 = self.converter.to_gregorian(5783, 12, 10) # month 12 = Adar
        assert gregorian_date_5 == (2023, 3, 3)
