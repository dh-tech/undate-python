import calendar
import datetime

import pytest

from undate import Undate, UndateInterval
from undate.date import Timedelta


class TestUndateInterval:
    def test_init_types(self):
        # datetime.date - autoconvert
        interval = UndateInterval(datetime.date(2022, 1, 1), None)
        assert isinstance(interval.earliest, Undate)
        interval = UndateInterval(None, datetime.date(2022, 1, 1))
        assert isinstance(interval.latest, Undate)

        # unsupported type should raise exception
        with pytest.raises(
            ValueError, match="earliest date 2022 cannot be converted to Undate"
        ):
            UndateInterval(2022, None)

        with pytest.raises(
            ValueError, match="latest date 1982 cannot be converted to Undate"
        ):
            UndateInterval(None, "1982")

    def test_init_validation(self):
        with pytest.raises(ValueError, match="invalid interval"):
            UndateInterval(Undate(2020), Undate(1010))

    def test_str(self):
        # 2022 - 2023
        assert str(UndateInterval(Undate(2022), Undate(2023))) == "2022/2023"
        # 2022 - 2023-05
        assert str(UndateInterval(Undate(2022), Undate(2023, 5))) == "2022/2023-05"
        # 2022-11-01 to 2022-11-07
        assert (
            str(UndateInterval(Undate(2022, 11, 1), Undate(2023, 11, 7)))
            == "2022-11-01/2023-11-07"
        )

    def test_format(self):
        interval = UndateInterval(Undate(2000), Undate(2001))
        assert interval.format("EDTF") == "2000/2001"
        assert interval.format("ISO8601") == "2000/2001"

        # Open-ended intervals
        open_start = UndateInterval(latest=Undate(2000))
        assert open_start.format("EDTF") == "../2000"
        assert open_start.format("ISO8601") == "/2000"

        open_end = UndateInterval(earliest=Undate(2000))
        assert open_end.format("EDTF") == "2000/.."
        assert open_end.format("ISO8601") == "2000/"

    def test_repr(self):
        assert (
            repr(UndateInterval(Undate(2022), Undate(2023)))
            == "<UndateInterval 2022/2023>"
        )
        assert (
            repr(UndateInterval(Undate(2022), Undate(2023), label="Fancy Epoch"))
            == "<UndateInterval 'Fancy Epoch' (2022/2023)>"
        )

    def test_str_open_range(self):
        # 900 -
        assert str(UndateInterval(Undate(900))) == "0900/"
        # - 1900
        assert str(UndateInterval(latest=Undate(1900))) == "../1900"
        # - 1900-12
        assert str(UndateInterval(latest=Undate(1900, 12))) == "../1900-12"

    def test_eq(self):
        assert UndateInterval(Undate(2022), Undate(2023)) == UndateInterval(
            Undate(2022), Undate(2023)
        )
        assert UndateInterval(Undate(2022), Undate(2023, 5)) == UndateInterval(
            Undate(2022), Undate(2023, 5)
        )
        assert UndateInterval(Undate(2022, 5)) == UndateInterval(Undate(2022, 5))

    def test_not_eq(self):
        assert UndateInterval(Undate(2022), Undate(2023)) != UndateInterval(
            Undate(2022), Undate(2024)
        )
        assert UndateInterval(Undate(2022), Undate(2023, 5)) != UndateInterval(
            Undate(2022), Undate(2023, 6)
        )
        assert UndateInterval(Undate(2022), Undate(2023, 5)) != UndateInterval(
            Undate(2022), Undate(2023)
        )
        assert UndateInterval(Undate(2022, 5)) != UndateInterval(Undate(2022, 6))

    def test_min_year_non_leapyear(self):
        assert not calendar.isleap(Undate.MIN_ALLOWABLE_YEAR)

    def test_duration(self):
        week_duration = UndateInterval(
            Undate(2022, 11, 1), Undate(2022, 11, 7)
        ).duration()
        assert isinstance(week_duration, Timedelta)
        assert week_duration.days == 7

        twomonths = UndateInterval(Undate(2022, 11), Undate(2022, 12)).duration()
        # november - december = 30 days + 31 days
        assert twomonths.days == 30 + 31

        twoyears = UndateInterval(Undate(2021), Undate(2022)).duration()
        assert twoyears.days == 365 * 2

        # special case: month/day with no year (assumes same year)
        week_noyear_duration = UndateInterval(
            Undate(None, 11, 1), Undate(None, 11, 7)
        ).duration()
        assert week_noyear_duration.days == 7
        # special case 2: month/day with no year, wrapping from december to january
        # (assumes sequential years)
        month_noyear_duration = UndateInterval(
            Undate(None, 12, 1), Undate(None, 1, 1)
        ).duration()
        assert month_noyear_duration.days == 32

        # real world test cases from Shakespeare and Company Project data;
        # second date is a year minus one day in the future
        month_noyear_duration = UndateInterval(
            Undate(None, 6, 7), Undate(None, 6, 6)
        ).duration()
        assert month_noyear_duration.days == 365

        # durations that span february in unknown years should assume
        # non-leap years
        jan_march_duration = UndateInterval(
            Undate(None, 2, 28), Undate(None, 3, 1)
        ).duration()
        assert jan_march_duration.days == 2

        # duration is not supported for open-ended intervals
        assert UndateInterval(Undate(2000), None).duration() == NotImplemented

        # one year set and the other not currently raises not implemented error
        with pytest.raises(NotImplementedError):
            UndateInterval(Undate(2000), Undate(month=10)).duration()

    def test_intersection(self):
        century11th = UndateInterval(Undate(1001), Undate(1100))
        century20th = UndateInterval(Undate(1901), Undate(2000))
        # no intersection
        assert century11th.intersection(century20th) is None
        # should work in either direction
        assert century20th.intersection(century11th) is None

        decade1990s = UndateInterval(Undate(1990), Undate(1999))
        # intersection of an interval completely contained in another
        # returns an interval equivalent to the smaller one
        assert century20th.intersection(decade1990s) == decade1990s
        assert decade1990s.intersection(century20th) == decade1990s

        # partial overlap
        nineties_oughts = UndateInterval(Undate(1990), Undate(2009))
        assert century20th.intersection(nineties_oughts) == UndateInterval(
            Undate(1990), Undate(2000)
        )

        # intersections between half open intervals
        after_c11th = UndateInterval(Undate(1001), None)
        assert after_c11th.intersection(century20th) == century20th
        assert after_c11th.intersection(decade1990s) == decade1990s

        before_20th = UndateInterval(None, Undate(1901))
        assert before_20th.intersection(decade1990s) is None
        assert before_20th.intersection(century11th) == century11th
        assert before_20th.intersection(after_c11th) == UndateInterval(
            Undate(1001), Undate(1901)
        )
