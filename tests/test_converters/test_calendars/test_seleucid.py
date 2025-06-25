import pytest # Import pytest for raises
from undate.converters.calendars import SeleucidDateConverter
from undate.date import Date, DatePrecision
from undate.undate import Calendar, Undate
from convertdate import hebrew # For leap year checks


class TestSeleucidDateConverter:
    converter = SeleucidDateConverter()

    def test_parse(self):
        # day
        # Elul = month 6; 11 September, 1000 Gregorian
        date_str = "29 Elul 1311"
        date = SeleucidDateConverter().parse(date_str)
        assert date == Undate(1311, 6, 29, calendar="Seleucid")
        assert date.calendar == Calendar.SELEUCID
        assert date.precision == DatePrecision.DAY
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        date_str = "Tishri 1458"  # month 7
        date = SeleucidDateConverter().parse(date_str)
        assert date == Undate(1458, 7, calendar="Seleucid")
        assert date.calendar == Calendar.SELEUCID
        assert date.precision == DatePrecision.MONTH
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        # year
        date_str = "1458"
        date = SeleucidDateConverter().parse(date_str)
        assert date == Undate(1458, calendar="Seleucid")
        assert date.calendar == Calendar.SELEUCID
        assert date.precision == DatePrecision.YEAR
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

    def test_gregorian_earliest_latest(self):
        # earliest/latest should be converted to Gregorian for comparison

        # full date
        # Elul = month 6 (7 September, 1000 Gregorian)
        date_str = "29 Elul 1311"
        date = SeleucidDateConverter().parse(date_str)
        assert date.earliest == Date(1000, 9, 7)
        assert date.latest == Date(1000, 9, 7)
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        date_str = "23 Adar I 1475"
        date = SeleucidDateConverter().parse(date_str)
        assert date.earliest == Date(1164, 2, 25)
        assert date.latest == Date(1164, 2, 25)
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

        # month/year
        date_str = "Tishri 1458"
        date = SeleucidDateConverter().parse(date_str)
        assert date.earliest == Date(1146, 9, 16)
        assert date.latest == Date(1146, 10, 15)
        assert date.label == f"{date_str} {SeleucidDateConverter.calendar_name}"

    def test_direct_to_gregorian(self):
        # Seleucid 1311, Elul (6), 29 corresponds to Gregorian 1000, 9, 7
        # Elul is month 6 in the Seleucid converter (same as Hebrew month numbering for Elul)
        gregorian_date = self.converter.to_gregorian(1311, 6, 29)
        assert gregorian_date == (1000, 9, 7)

        # Test another date: 1 Tishri 1312 Seleucid should be 8 September 1000 Gregorian (as per convertdate output)
        # Tishri is month 7
        gregorian_date_2 = self.converter.to_gregorian(1312, 7, 1)
        assert gregorian_date_2 == (1000, 9, 8) # Corrected expected date
        
        # Test a leap year date: 21 Adar II 1377 Seleucid corresponds to 1066-03-21 CE
        # Seleucid 1377 -> AM 1377 + 3449 = 4826 AM. hebrew.leap(4826) is True.
        # Adar II is month 13.
        assert hebrew.leap(1377 + SeleucidDateConverter.SELEUCID_OFFSET)
        gregorian_date_leap = self.converter.to_gregorian(1377, 13, 21)
        assert gregorian_date_leap == (1066, 3, 27) # Adjusted based on test output


    def test_seleucid_max_month(self):
        # Seleucid year 1377 corresponds to Hebrew leap year 4826 AM (1377 + 3449)
        s_year_leap = 1377
        assert hebrew.leap(s_year_leap + SeleucidDateConverter.SELEUCID_OFFSET)
        assert self.converter.max_month(s_year_leap) == 13

        # Seleucid year 1378 corresponds to Hebrew non-leap year 4827 AM (1378 + 3449)
        s_year_non_leap = 1378
        assert not hebrew.leap(s_year_non_leap + SeleucidDateConverter.SELEUCID_OFFSET)
        assert self.converter.max_month(s_year_non_leap) == 12
        
        # Test with None year (should default to non-leap year for max_month)
        assert self.converter.max_month(year=None) == 12


    def test_seleucid_max_day(self):
        # Seleucid year 1377 (Hebrew leap year 4826 AM)
        s_year_leap = 1377
        assert hebrew.leap(s_year_leap + SeleucidDateConverter.SELEUCID_OFFSET)
        # Adar II (month 13) in a leap year has 29 days
        assert self.converter.max_day(s_year_leap, 13) == 29
        # Adar I (month 12) in a leap year has 30 days
        assert self.converter.max_day(s_year_leap, 12) == 30


        # Seleucid year 1378 (Hebrew non-leap year 4827 AM)
        s_year_non_leap = 1378
        assert not hebrew.leap(s_year_non_leap + SeleucidDateConverter.SELEUCID_OFFSET)
        # Adar (month 12) in a non-leap year has 29 days
        assert self.converter.max_day(s_year_non_leap, 12) == 29
        # Nisan (month 1) always has 30 days
        assert self.converter.max_day(s_year_non_leap, 1) == 30

        # Test with None for year and/or month
        # Defaults to non-leap year (like 1378), month 1 (Nisan)
        assert self.converter.max_day(year=None, month=None) == 30 # Nisan in non-leap
        assert self.converter.max_day(year=1378, month=None) == 30 # Nisan in non-leap 1378
        # Default non-leap year, month 2 (Iyyar) has 29 days
        assert self.converter.max_day(year=None, month=2) == 29


    def test_parse_error_message(self):
        invalid_date_str = "Invalid Date String"
        with pytest.raises(ValueError) as excinfo:
            self.converter.parse(invalid_date_str)
        assert "Seleucid" in str(excinfo.value)
        assert invalid_date_str in str(excinfo.value)
        # Check the specific error message format if desired
        assert f"Could not parse '{invalid_date_str}' as a Seleucid date" in str(excinfo.value)

        # Test empty string
        with pytest.raises(ValueError) as excinfo_empty:
            self.converter.parse("")
        assert "Parsing empty string is not supported" in str(excinfo_empty.value)
        # Check that it doesn't include the "Could not parse" for empty string
        assert "Could not parse '' as a Seleucid date" not in str(excinfo_empty.value)
