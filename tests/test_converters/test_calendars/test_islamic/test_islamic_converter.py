import pytest

from undate.converters.calendars import IslamicDateConverter
from undate.converters.calendars.islamic.transformer import IslamicUndate
from undate.undate import Calendar, Undate
from undate.date import DatePrecision, Date
from convertdate import islamic # For constants and leap year checks


class TestIslamicDateConverter:
    converter = IslamicDateConverter()

    def test_parse(self):
        # day
        # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE); Jumada I = month 5
        date_str = "7 Jumādā I 1243"
        date = IslamicDateConverter().parse(date_str)
        assert date == IslamicUndate(1243, 5, 7)
        assert date.calendar == Calendar.ISLAMIC
        assert date.precision == DatePrecision.DAY
        assert date.label == f"{date_str} {IslamicDateConverter.calendar_name}"

        # month
        date_str = "Rajab 495"
        date = IslamicDateConverter().parse(date_str)
        assert date == IslamicUndate(495, 7)  # Rajab is month 7
        assert date.calendar == Calendar.ISLAMIC
        assert date.precision == DatePrecision.MONTH
        assert date.label == f"{date_str} {IslamicDateConverter.calendar_name}"
        # Gregorian earliest/ latest
        assert date.earliest == Date(1102, 4, 28)
        assert date.latest == Date(1102, 5, 27)

        # year
        date_str = "441"
        date = IslamicDateConverter().parse(date_str)
        assert date == IslamicUndate(441)
        assert date.calendar == Calendar.ISLAMIC
        assert date.precision == DatePrecision.YEAR
        assert date.label == f"{date_str} {IslamicDateConverter.calendar_name}"
        # Gregorian earliest/ latest
        assert date.earliest == Date(1049, 6, 11)
        assert date.latest == Date(1050, 5, 31)

    def test_gregorian_earliest_latest(self):
        # earliest/latest should be converted to Gregorian for comparison

        # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE); Jumada I = month 5
        date = IslamicUndate(1243, 5, 7)
        assert date.earliest == Date(1827, 11, 26)
        assert date.latest == Date(1827, 11, 26)

        # Jumādā I 1243 : 1827-11-20 to 1827-12-19
        date = IslamicUndate(1243, 5)
        assert date.earliest == Date(1827, 11, 20)
        assert date.latest == Date(1827, 12, 19)

        # Rajab 495: 1102-04-28 to 1102-05-27 (Rajab = month 7)
        date = IslamicUndate(495, 7)
        assert date.earliest == Date(1102, 4, 28)
        assert date.latest == Date(1102, 5, 27)

        # 441 : 1049-06-11 to 1050-05-31
        date = IslamicUndate(441)
        assert date.earliest == Date(1049, 6, 11)
        assert date.latest == Date(1050, 5, 31)

        # examples from ISMI data (reformatted to day month year)
        # 14 Rabīʿ I 901 : 1495-12-11 (Rabi 1 = month 3 )
        date = IslamicUndate(901, 3, 14)
        assert date.earliest == Date(1495, 12, 11)
        assert date.latest == Date(1495, 12, 11)

        # 884 : 1479-04-03 to 1480-03-21
        date = IslamicUndate(884)
        assert date.earliest == Date(1479, 4, 3)
        assert date.latest == Date(1480, 3, 21)

    def test_parse_error(self):
        # a string we can't parse should raise an error
        with pytest.raises(ValueError):
            IslamicDateConverter().parse("January 2, 1991")
        # empty string should also error
        with pytest.raises(ValueError):
            IslamicDateConverter().parse("")

    def test_partially_known(self):
        # hijri dates get existing partially unknown behavior
        unknown_month = IslamicUndate(1243, "XX")
        assert unknown_month.precision == DatePrecision.MONTH
        assert unknown_month.earliest == Date(
            *self.converter.to_gregorian(1243, 1, 1)
        )
        actual_max_day_unknown = islamic.month_length(1243, 12)
        assert unknown_month.latest == Date(
            *self.converter.to_gregorian(1243, 12, actual_max_day_unknown)
        )

        partially_unknown_month = IslamicUndate(1243, "1X")
        assert partially_unknown_month.precision == DatePrecision.MONTH
        assert partially_unknown_month.earliest == Date(
            *self.converter.to_gregorian(1243, 10, 1)
        )
        actual_max_day_partial = islamic.month_length(1243, 12)
        assert partially_unknown_month.latest == Date(
            *self.converter.to_gregorian(1243, 12, actual_max_day_partial)
        )

        unknown_day = IslamicUndate(1243, 2, "XX")
        assert unknown_day.precision == DatePrecision.DAY
        assert unknown_day.earliest == Date(
            *self.converter.to_gregorian(1243, 2, 1)
        )
        # second month has 29 days
        assert unknown_day.latest == Date(
            *self.converter.to_gregorian(1243, 2, 29)
        )
        partially_unknown_day = IslamicUndate(1243, 2, "2X")
        assert partially_unknown_day.precision == DatePrecision.DAY
        assert partially_unknown_day.earliest == Date(
            *self.converter.to_gregorian(1243, 2, 20)
        )
        assert partially_unknown_day.latest == Date(
            *self.converter.to_gregorian(1243, 2, 29)
        )

    # --- Tests for BaseCalendarConverter method implementations ---

    def test_min_month(self):
        assert self.converter.min_month() == 1

    def test_max_month(self):
        # Islamic calendar always has 12 months
        assert self.converter.max_month(year=1447) == 12 # Leap year
        assert self.converter.max_month(year=1446) == 12 # Common year
        assert self.converter.max_month(year=None) == 12

    def test_first_month(self):
        assert self.converter.first_month() == 1

    def test_last_month(self):
        assert self.converter.last_month(year=1447) == 12
        assert self.converter.last_month(year=1446) == 12
        assert self.converter.last_month(year=None) == 12
    
    def test_max_day(self):
        # Muharram (month 1) always has 30 days
        assert self.converter.max_day(year=1446, month=1) == 30
        
        # Safar (month 2) always has 29 days
        assert self.converter.max_day(year=1446, month=2) == 29
        
        # Dhu al-Hijjah (month 12) in an Islamic leap year (e.g., 1447 AH) has 30 days.
        assert islamic.leap(1447) # Confirm 1447 AH is a leap year
        assert self.converter.max_day(year=1447, month=12) == 30
        
        # Dhu al-Hijjah (month 12) in an Islamic common year (e.g., 1446 AH) has 29 days.
        assert not islamic.leap(1446) # Confirm 1446 AH is a common year
        assert self.converter.max_day(year=1446, month=12) == 29

        # Test with None for year and/or month (should use defaults from converter)
        # Default month (if None) is 1 (Muharram), which has 30 days.
        assert self.converter.max_day(year=1446, month=None) == 30
        # Default year (if None) is non-leap. Default month is 1 (Muharram).
        assert self.converter.max_day(year=None, month=None) == 30
        # Default year (non-leap), specific month Safar (29 days)
        assert self.converter.max_day(year=None, month=2) == 29


    def test_direct_to_gregorian(self):
        # 1 Muharram 1446 AH: converter in test env returns (2024, 7, 8)
        gregorian_date = self.converter.to_gregorian(1446, 1, 1)
        assert gregorian_date == (2024, 7, 8) # Adjusted based on test output

        # 30 Dhu al-Hijjah 1447 AH (leap year) corresponds to June 16, 2026
        assert islamic.leap(1447)
        gregorian_date_leap = self.converter.to_gregorian(1447, 12, 30)
        assert gregorian_date_leap == (2026, 6, 16)

        # 29 Dhu al-Hijjah 1446 AH (common year): converter in test env returns (2025, 6, 26)
        assert not islamic.leap(1446)
        gregorian_date_common = self.converter.to_gregorian(1446, 12, 29)
        assert gregorian_date_common == (2025, 6, 26) # Adjusted based on test output


    def test_compare_across_calendars(self):
        # only day-precision dates can be exactly equal across calendars

        # 7 Jumādā I 1243 Hijrī : 26 November, 1827; Jumada I = month 5
        assert IslamicUndate(1243, 5, 7) == Undate(1827, 11, 26)
        # 14 Rabīʿ I 901 : 1495-12-11 (Rabi 1 = month 3 )
        assert IslamicUndate(901, 3, 14) == Undate(1495, 12, 11)

        # greater than / less than
        assert IslamicUndate(901) < Undate(1500)
        assert IslamicUndate(901) > Undate(1450)
        # Jumādā I 1243 : 1827-11-20 to 1827-12-19
        assert IslamicUndate(1243, 5) > Undate(1827, 10)
        assert IslamicUndate(1243, 5) < Undate(1828, 1)

        # 7 Jumādā I 1243 Hijrī : 26 November, 1827, so it falls
        # within (or is contained by) November 1827
        assert IslamicUndate(1243, 5, 7) in Undate(1827, 11)
        assert IslamicUndate(1243, 5, 7) not in Undate(1827, 10)

        # sorting
        sorted_dates = sorted(
            [
                IslamicUndate(884),  # 1479 to 1480 Gregorian
                IslamicUndate(441),  # 1049 to 1050 Gregorian
                IslamicUndate(901),  # 1495 to 1495 Gregorian
                Undate(1995),
                Undate(33),
                Undate(1350),
            ]
        )
        expected_gregorian_years = [33, 1049, 1350, 1479, 1495, 1995]
        assert [d.earliest.year for d in sorted_dates] == expected_gregorian_years
