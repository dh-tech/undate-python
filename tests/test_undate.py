from datetime import timedelta

import pytest

from undate.undate import Undate, UndateInterval


class TestUndate:
    def test_str(self):
        assert str(Undate(2022, 11, 7)) == "2022-11-07"
        assert str(Undate(2022, 11)) == "2022-11"
        assert str(Undate(2022)) == "2022"
        assert str(Undate(month=11, day=7)) == "--11-07"

    def test_init_str(self):
        assert Undate("2000").earliest.year == 2000
        # single or double digit string month should be ok
        assert Undate("2000", "2").earliest.month == 2
        assert Undate("2000", "02").earliest.month == 2

    def test_init_partially_known_year(self):
        uncertain1900s = Undate("19XX")
        assert uncertain1900s.earliest.year == 1900
        assert uncertain1900s.latest.year == 1999

        uncertain1x = Undate("1X05")
        assert uncertain1x.earliest.year == 1005
        assert uncertain1x.latest.year == 1905

        uncertain18x7 = Undate("18X7")
        assert uncertain18x7.earliest.year == 1807
        assert uncertain18x7.latest.year == 1897

    def test_init_partially_known_month(self):
        uncertain_fall = Undate(1900, "1X")
        assert uncertain_fall.earliest.month == 10
        assert uncertain_fall.latest.month == 12

        uncertain_notfall = Undate(1900, "0X")
        assert uncertain_notfall.earliest.month == 1
        assert uncertain_notfall.latest.month == 9

        # treat as unknown but allow
        unknown_month = Undate(1900, "XX")
        assert unknown_month.earliest.month == 1
        assert unknown_month.latest.month == 12
        assert str(unknown_month) == "1900"  # NOT 1900-XX ?

    def test_init_partially_known_day(self):
        uncertain_day = Undate(1900, 1, "XX")  # treat as None
        assert uncertain_day.earliest.day == 1
        assert uncertain_day.latest.day == 31

        uncertain_day = Undate(1900, 1, "1X")
        assert uncertain_day.earliest.day == 10
        assert uncertain_day.latest.day == 19

        uncertain_day = Undate(1900, 1, "0X")
        assert uncertain_day.earliest.day == 1
        assert uncertain_day.latest.day == 9
        uncertain_day = Undate(1900, 1, "2X")
        assert uncertain_day.earliest.day == 20
        assert uncertain_day.latest.day == 29
        uncertain_day = Undate(1900, 1, "3X")
        assert uncertain_day.earliest.day == 30
        assert uncertain_day.latest.day == 31

        uncertain_day = Undate(1900, 1, "X5")
        assert uncertain_day.earliest.day == 5
        assert uncertain_day.latest.day == 25

        uncertain_day = Undate(1900, 1, "X1")
        assert uncertain_day.earliest.day == 1
        assert uncertain_day.latest.day == 31

        # TODO: handle months with only 30 days

        # month with only 30 days
        uncertain_day = Undate(1900, 6, "X1")
        assert uncertain_day.earliest.day == 1
        assert uncertain_day.latest.day == 30
        uncertain_day = Undate(1900, 6, "3X")
        assert uncertain_day.earliest.day == 30
        assert uncertain_day.latest.day == 30

        # special cases
        # february! TODO
        # uncertain_day = Undate(1900, 2, "2X")

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            Undate("19xx")

        with pytest.raises(ValueError):
            Undate(1900, "X1")

    def test_invalid_date(self):
        # invalid month should raise an error
        with pytest.raises(ValueError):
            Undate(1990, 22)

    def test_eq(self):
        assert Undate(2022) == Undate(2022)
        assert Undate(2022, 10) == Undate(2022, 10)
        assert Undate(2022, 10, 1) == Undate(2022, 10, 1)
        assert Undate(month=2, day=7) == Undate(month=2, day=7)

    def test_not_eq(self):
        assert Undate(2022) != Undate(2023)
        assert Undate(2022, 10) != Undate(2022, 11)
        assert Undate(2022, 10, 1) != Undate(2022, 10, 2)
        assert Undate(month=2, day=7) != Undate(month=2, day=8)
        assert Undate(2022) != Undate(2022, 10)
        assert Undate(2022, 10) != Undate(2022, 10, 1)

    def test_duration(self):
        day_duration = Undate(2022, 11, 7).duration()
        assert isinstance(day_duration, timedelta)
        assert day_duration.days == 1

        january_duration = Undate(2022, 1).duration()
        assert january_duration.days == 31
        feb_duration = Undate(2022, 2).duration()
        assert feb_duration.days == 28
        # next leap year will be 2024
        leapyear_feb_duration = Undate(2024, 2).duration()
        assert leapyear_feb_duration.days == 29

        year_duration = Undate(2022).duration()
        assert year_duration.days == 365
        leapyear_duration = Undate(2024).duration()
        assert leapyear_duration.days == 366

    def test_known_year(self):
        assert Undate(2022).known_year is True
        assert Undate(month=2, day=5).known_year is False
        # partially known year is not known
        assert Undate("19XX").known_year is False


class TestUndateInterval:
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

    def test_duration(self):
        week_duration = UndateInterval(
            Undate(2022, 11, 1), Undate(2022, 11, 7)
        ).duration()
        assert isinstance(week_duration, timedelta)
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
        assert month_noyear_duration.days == 31
