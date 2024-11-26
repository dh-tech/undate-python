import pytest

from undate.converters.calendars import HijriDateConverter
from undate.converters.calendars.hijri.transformer import HijriUndate
from undate.undate import Calendar
from undate.date import DatePrecision, Date


class TestHijriDateConverter:
    def test_parse(self):
        # day
        # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE); Jumada I = month 5
        date_str = "7 Jumādā I 1243"
        date = HijriDateConverter().parse(date_str)
        assert date == HijriUndate(1243, 5, 7)
        assert date.calendar == Calendar.HIJRI
        assert date.precision == DatePrecision.DAY
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"

        # month
        date_str = "Rajab 495"
        date = HijriDateConverter().parse(date_str)
        assert date == HijriUndate(495, 7)  # Rajab is month 7
        assert date.calendar == Calendar.HIJRI
        assert date.precision == DatePrecision.MONTH
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"
        # Gregorian earliest/ latest
        assert date.earliest == Date(1102, 4, 28)
        assert date.latest == Date(1102, 5, 27)

        # year
        date_str = "441"
        date = HijriDateConverter().parse(date_str)
        assert date == HijriUndate(441)
        assert date.calendar == Calendar.HIJRI
        assert date.precision == DatePrecision.YEAR
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"
        # Gregorian earliest/ latest
        assert date.earliest == Date(1049, 6, 11)
        assert date.latest == Date(1050, 5, 31)

    def test_gregorian_earliest_latest(self):
        # earliest/latest should be converted to Gregorian for comparison

        # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE); Jumada I = month 5
        date = HijriUndate(1243, 5, 7)
        assert date.earliest == Date(1827, 11, 26)
        assert date.latest == Date(1827, 11, 26)

        # Jumādā I 1243 : 1827-11-20 to 1827-12-19
        date = HijriUndate(1243, 5)
        assert date.earliest == Date(1827, 11, 20)
        assert date.latest == Date(1827, 12, 19)

        # Rajab 495: 1102-04-28 to 1102-05-27 (Rajab = month 7)
        date = HijriUndate(495, 7)
        assert date.earliest == Date(1102, 4, 28)
        assert date.latest == Date(1102, 5, 27)

        # 441 : 1049-06-11 to 1050-05-31
        date = HijriUndate(441)
        assert date.earliest == Date(1049, 6, 11)
        assert date.latest == Date(1050, 5, 31)

        # examples from ISMI data (reformatted to day month year)
        # 14 Rabīʿ I 901 : 1495-12-11 (Rabi 1 = month 3 )
        date = HijriUndate(901, 3, 14)
        assert date.earliest == Date(1495, 12, 11)
        assert date.latest == Date(1495, 12, 11)

        # 884 : 1479-04-03 to 1480-03-21
        date = HijriUndate(884)
        assert date.earliest == Date(1479, 4, 3)
        assert date.latest == Date(1480, 3, 21)

    def test_parse_error(self):
        # a string we can't parse should raise an error
        with pytest.raises(ValueError):
            HijriDateConverter().parse("January 2, 1991")
        # empty string should also error
        with pytest.raises(ValueError):
            HijriDateConverter().parse("")
