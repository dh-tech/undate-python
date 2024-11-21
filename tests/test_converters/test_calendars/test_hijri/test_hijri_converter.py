import pytest
from undate.converters.calendars import HijriDateConverter
from undate.undate import Undate, UndateInterval


class TestHijriDateConverter:
    def test_parse_(self):
        # day
        date_str = "7 Jumādā I 1243"
        date = HijriDateConverter().parse(date_str)
        assert date == Undate(1827, 11, 26)
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"

        # month
        date_str = "Rajab 495"
        date = HijriDateConverter().parse(date_str)
        assert date == UndateInterval(Undate(1102, 4, 28), Undate(1102, 5, 27))
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"

        # year
        date_str = "441"
        date = HijriDateConverter().parse(date_str)
        assert date == UndateInterval(Undate(1049, 6, 11), Undate(1050, 5, 31))
        assert date.label == f"{date_str} {HijriDateConverter.calendar_name}"

    def test_parse_error(self):
        # a string we can't parse should raise an error
        with pytest.raises(ValueError):
            HijriDateConverter().parse("January 2, 1991")
        # empty string should also error
        with pytest.raises(ValueError):
            HijriDateConverter().parse("")
