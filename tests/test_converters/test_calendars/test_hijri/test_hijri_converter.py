import pytest

from undate.converters.calendars import HijriDateConverter
from undate.undate import Undate, Calendar
from undate.date import DatePrecision


class TestHijriDateConverter:
    def test_parse_(self):
        # day
        # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE); Jumada I = month 5
        date_str = "7 Jumādā I 1243"
        date = HijriDateConverter().parse(date_str)
        assert date == Undate(1243, 5, 7)
        assert date.calendar == Calendar.HIJRI
        assert date.precision == DatePrecision.DAY
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"
        # TODO: earliest/latest should be converted to Gregorian
        # assert date.earliest == Date(1827, 11, 26)
        # assert date.latest == Date(1827, 11, 26)

        # month
        date_str = "Rajab 495"
        date = HijriDateConverter().parse(date_str)
        assert date == Undate(495, 7)  # Rajab is month 7
        assert date.calendar == Calendar.HIJRI
        assert date.precision == DatePrecision.MONTH
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"
        # TODO: Gregorian earliest/ latest
        # assert date == UndateInterval(Undate(1102, 4, 28), Undate(1102, 5, 27))

        # year
        date_str = "441"
        date = HijriDateConverter().parse(date_str)
        assert date == Undate(441)
        assert date.calendar == Calendar.HIJRI
        assert date.precision == DatePrecision.YEAR
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"
        # TODO: Gregorian earliest/ latest
        # assert date == UndateInterval(Undate(1049, 6, 11), Undate(1050, 5, 31))

    def test_parse_error(self):
        # a string we can't parse should raise an error
        with pytest.raises(ValueError):
            HijriDateConverter().parse("January 2, 1991")
        # empty string should also error
        with pytest.raises(ValueError):
            HijriDateConverter().parse("")
