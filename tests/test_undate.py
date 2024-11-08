import calendar
from datetime import date

import pytest
from undate.date import DatePrecision, Timedelta
from undate.undate import Undate, UndateInterval


class TestUndate:
    def test_str(self):
        assert str(Undate(2022, 11, 7)) == "2022-11-07"
        assert str(Undate(2022, 11)) == "2022-11"
        assert str(Undate(2022)) == "2022"
        assert str(Undate(month=11, day=7)) == "--11-07"

    def test_partially_known_str(self):
        assert str(Undate("19XX")) == "19XX"
        assert str(Undate(2022, "1X")) == "2022-1X"
        assert str(Undate(2022, 11, "2X")) == "2022-11-2X"
        assert str(Undate(month="1X", day=7)) == "--1X-07"

        # TODO: should not allow initializing year/day without month;
        # should we infer unknown month? or raise an exception?
        # assert str(Undate(2022, day="2X")) == "2022-XX-2X"  # currently returns 2022-2X
        # assert str(Undate(2022, day=7)) == "2022-XX-07"   @ currently returns 2022-07

    def test_repr(self):
        assert repr(Undate(2022, 11, 7)) == "<Undate 2022-11-07>"
        assert (
            repr(Undate(2022, 11, 7, label="A Special Day"))
            == "<Undate 'A Special Day' (2022-11-07)>"
        )

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

        # unlikely case, but now possible to calculate
        assert Undate(1900, "X1").earliest.month == 1
        assert Undate(1900, "X1").latest.month == 11

        # treat as unknown but allow
        unknown_month = Undate(1900, "XX")
        assert unknown_month.earliest.month == 1
        assert unknown_month.latest.month == 12
        assert str(unknown_month) == "1900-XX"

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

        # month with only 30 days
        uncertain_day = Undate(1900, 6, "X1")
        assert uncertain_day.earliest.day == 1
        assert uncertain_day.latest.day == 21  # doesn't go to 31
        uncertain_day = Undate(1900, 6, "3X")
        assert uncertain_day.earliest.day == 30
        assert uncertain_day.latest.day == 30

        # special cases
        # february! 28 days usually
        uncertain_day = Undate(1900, 2, "2X")
        assert uncertain_day.earliest.day == 20
        assert uncertain_day.latest.day == 28
        # february in a leap year
        uncertain_day = Undate(2024, 2, "2X")
        assert uncertain_day.latest.day == 29

        # TODO: handle leap day in an unknown year
        # (currently causes an exception because min/max years are not leap years)
        # Undate(None, 2, 29)

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            Undate("19xx")

    def test_invalid_date(self):
        # invalid month should raise an error
        with pytest.raises(ValueError):
            Undate(1990, 22)

    def test_from_datetime_date(self):
        undate_from_date = Undate.from_datetime_date(date(2001, 3, 5))
        assert isinstance(undate_from_date, Undate)
        assert undate_from_date == Undate(2001, 3, 5)

    # test properties for accessing parts of date
    def test_year_property(self):
        # two, three, four five digit years; numeric and string
        assert Undate(33).year == "0033"
        assert Undate(567).year == "0567"
        assert Undate("1984").year == "1984"
        assert Undate(23055).year == "23055"
        # partially known year
        assert Undate("19XX").year == "19XX"
        # unset year
        assert Undate(month=12, day=31).year == "XXXX"

        # force method to hit conditional for date precision
        some_century = Undate()
        some_century.precision = DatePrecision.CENTURY
        assert some_century.year is None

    def test_month_property(self):
        # one, two digit month
        assert Undate(2023, 1).month == "01"
        assert Undate(2023, 12).month == "12"
        # partially unknown month (first/second digit unknown)
        assert Undate(2023, "1X").month == "1X"
        assert Undate(2023, "X2").month == "X2"
        # fully unknown month
        assert Undate(2023, "XX").month == "XX"
        # unset month, year precision
        assert Undate(2023).month is None
        # unset month, day precision (= some unknown month, not no month)
        assert Undate(day=15).month == "XX"

    def test_day_property(self):
        # one, two digit day
        assert Undate(2023, 1, 9).day == "09"
        assert Undate(2023, 1, 31).day == "31"
        # partially unknown day
        assert Undate(2023, 1, "1X").day == "1X"
        assert Undate(2023, 1, "X5").day == "X5"
        # fully unknown day
        assert Undate(2023, 1, "XX").day == "XX"
        # unset day
        assert Undate(2023).day is None
        assert Undate(2023, 1).day is None
        # Day without year or month
        assert Undate(day=15).day == "15"

        # force str based on date precision without day part set
        someday = Undate(2023)
        someday.precision = DatePrecision.DAY
        assert someday.day == "XX"

    def test_eq(self):
        assert Undate(2022) == Undate(2022)
        assert Undate(2022, 10) == Undate(2022, 10)
        assert Undate(2022, 10, 1) == Undate(2022, 10, 1)
        assert Undate(month=2, day=7) == Undate(month=2, day=7)

        # something we can't convert for comparison should return NotImplemented
        assert Undate(2022).__eq__("not a date") == NotImplemented

    def test_eq_datetime_date(self):
        # support comparisons with datetime objects for full day-precision
        assert Undate(2022, 10, 1) == date(2022, 10, 1)
        assert Undate(2022, 10, 1) != date(2022, 10, 2)
        assert Undate(1980, 10, 1) != date(2022, 10, 1)

        # other date precisions are not equal
        assert Undate(2022) != date(2022, 10, 1)
        assert Undate(2022, 10) != date(2022, 10, 1)

    def test_not_eq(self):
        assert Undate(2022) != Undate(2023)
        assert Undate(2022, 10) != Undate(2022, 11)
        assert Undate(2022, 10, 1) != Undate(2022, 10, 2)
        assert Undate(month=2, day=7) != Undate(month=2, day=8)
        assert Undate(2022) != Undate(2022, 10)
        assert Undate(2022, 10) != Undate(2022, 10, 1)

        # partially unknown dates should NOT be considered equal
        assert Undate("19XX") != Undate("19XX")
        assert Undate(1980, "XX") != Undate(1980, "XX")

    testdata_lt_gt = [
        # dates to test for gt/lt comparison: earlier date, later date
        # - simple cases: same precision where one date is clearly earlier
        (Undate(2022), Undate(2023)),
        (Undate(1991, 1), Undate(1991, 5)),
        (Undate(1856, 3, 3), Undate(1856, 3, 21)),
        # - mixed precision where one date is clearly earlier
        (Undate(1991, 1), Undate(2000)),
        (Undate(1856, 3, 3), Undate(1901)),
        # partially known digits where comparison is possible
        (Undate("19XX"), Undate("20XX")),
        (Undate(1900, "0X"), Undate(1900, "1X")),
        # compare with datetime.date objects
        (Undate("19XX"), date(2020, 1, 1)),
        (Undate(1991, 1), date(1992, 3, 4)),
    ]

    @pytest.mark.parametrize("earlier,later", testdata_lt_gt)
    def test_lt(self, earlier, later):
        assert earlier < later
        assert later > earlier

    testdata_lte_gte = testdata_lt_gt.copy()
    # add a few exactly equal cases
    testdata_lte_gte.extend(
        [
            (Undate(1601), Undate(1601)),
            (Undate(1991, 1), Undate(1991, 1)),
            (Undate(1492, 5, 3), Undate(1492, 5, 3)),
            # compare with datetime.date also
            (Undate(1492, 5, 3), date(1492, 5, 3)),
        ]
    )

    def test_lt_when_eq(self):
        # strict less than / greater should return false when equal
        assert not Undate(1900) > Undate(1900)
        assert not Undate(1900) < Undate(1900)
        # same for datetime.date
        assert not Undate(1903, 1, 5) < date(1903, 1, 5)
        assert not Undate(1903, 1, 5) > date(1903, 1, 5)

    @pytest.mark.parametrize("earlier,later", testdata_lte_gte)
    def test_lte(self, earlier, later):
        assert earlier <= later
        assert later >= earlier

    def test_lt_notimplemented(self):
        # how to compare mixed precision where dates overlap?
        # if the second date falls *within* earliest/latest,
        # then it is not clearly less; not implemented?
        with pytest.raises(NotImplementedError, match="date falls within the other"):
            assert Undate(2022) < Undate(2022, 5)

        # same if we attempt to compare in the other direction
        with pytest.raises(NotImplementedError, match="date falls within the other"):
            assert Undate(2022, 5) < Undate(2022)

    testdata_contains = [
        # first date falls within the range of the other
        # dates within range: middle, start, end, varying precision
        (Undate(2022, 6), Undate(2022)),
        (Undate(2022, 1, 1), Undate(2022)),
        (Undate(2022, 12, 31), Undate(2022)),
        (Undate(2022, 6, 15), Undate(2022, 6)),
        # support contains with datetime.date
        (date(2022, 6, 1), Undate(2022)),
        (date(2022, 6, 1), Undate(2022, 6)),
    ]

    @pytest.mark.parametrize("date1,date2", testdata_contains)
    def test_contains(self, date1, date2):
        assert date1 in date2

    testdata_not_contains = [
        # dates not in range
        (Undate(1980), Undate(2020)),
        (Undate(1980), Undate(2020, 6)),
        (Undate(1980, 6), Undate(2020, 6)),
        # support contains with datetime.date
        (date(1980, 6, 1), Undate(2022)),
        (date(3001, 6, 1), Undate(2022, 6)),
        # partially known dates that are similar but same precision,
        # so one does not contain the other
        (Undate("199X"), Undate("19XX")),
        # - specific month to unknown month
        (Undate(1980, 6), Undate(1980, "XX")),
        # some of these might overlap, but we don't have enough
        # information to determine
        # - unknown month to unknown month
        (Undate(1980, "XX"), Undate(1980, "XX")),
        # - partially unknown month to unknown month
        (Undate(1801, "1X"), Undate(1801, "XX")),
    ]

    @pytest.mark.parametrize("date1,date2", testdata_not_contains)
    def test_not_contains(self, date1, date2):
        assert date1 not in date2

    def test_sorting(self):
        # sorting should be possible based on gt/lt
        # test simple cases for sorting
        d1980 = Undate(1980)
        d2002_10 = Undate(2002, 10)
        d2002_12 = Undate(2002, 12)
        d2012_05_01 = Undate(2012, 5, 1)

        assert sorted([d2012_05_01, d2002_12, d2002_10, d1980]) == [
            d1980,
            d2002_10,
            d2002_12,
            d2012_05_01,
        ]

        # what about semi-ambigous cases?
        d1991_XX = Undate(1991, "XX")
        d1992_01_XX = Undate(1992, 1, "XX")
        assert sorted([d1992_01_XX, d1991_XX, d1980]) == [d1980, d1991_XX, d1992_01_XX]

        # what about things we can't compare?
        d1991 = Undate(1991)
        d1991_02 = Undate(1991, 2)
        # for now, this will raise a not implemented error
        with pytest.raises(NotImplementedError):
            sorted([d1991_02, d1991, d1991_XX])

        # TODO: partially known year?
        # someyear = Undate("1XXX")
        # assert sorted([d1991, someyear]) == [someyear, d1991]

    def test_duration(self):
        day_duration = Undate(2022, 11, 7).duration()
        assert isinstance(day_duration, Timedelta)
        assert day_duration.days == 1

        january_duration = Undate(2022, 1).duration()
        assert january_duration.days == 31
        feb_duration = Undate(2022, 2).duration()
        assert feb_duration.days == 28
        # 2024 is a known leap year
        leapyear_feb_duration = Undate(2024, 2).duration()
        assert leapyear_feb_duration.days == 29

        year_duration = Undate(2022).duration()
        assert year_duration.days == 365
        leapyear_duration = Undate(2024).duration()
        assert leapyear_duration.days == 366

    def test_partiallyknown_duration(self):
        # day in unknown month/year
        # assert Undate(day=5).duration().days == 1
        assert Undate(day=5).duration().days == 1
        assert Undate(year=1900, month=11, day="2X").duration().days == 1

        # month in unknown year
        assert Undate(month=6).duration().days == 30
        # partially known month
        assert Undate(year=1900, month="1X").duration().days == 31
        # what about february?
        # could vary with leap years, but assume non-leapyear
        assert Undate(month=2).duration().days == 28

    def test_known_year(self):
        assert Undate(2022).known_year is True
        assert Undate(month=2, day=5).known_year is False
        # partially known year is not known
        assert Undate("19XX").known_year is False
        # fully known string year should be known
        assert Undate("1900").known_year is True

    def test_is_known_month(self):
        assert Undate(2022).is_known("month") is False
        assert Undate(2022, 2).is_known("month") is True
        assert Undate(2022, "5").is_known("month") is True
        assert Undate(2022, "1X").is_known("month") is False
        assert Undate(2022, "XX").is_known("month") is False

    def test_is_known_day(self):
        assert Undate(1984).is_known("day") is False
        assert Undate(month=1, day=3).is_known("day") is True
        assert Undate(month=1, day="5").is_known("day") is True
        assert Undate(month=1, day="X5").is_known("day") is False
        assert Undate(month=1, day="XX").is_known("day") is False

    def test_parse(self):
        assert Undate.parse("1984", "EDTF") == Undate(1984)
        assert Undate.parse("1984-04", "EDTF") == Undate(1984, 4)
        assert Undate.parse("1984-04", "EDTF") == Undate(1984, 4)
        assert Undate.parse("2000/2001", "EDTF") == UndateInterval(
            Undate(2000), Undate(2001)
        )

        assert Undate.parse("1984", "ISO8601") == Undate(1984)
        assert Undate.parse("1984-04", "ISO8601") == Undate(1984, 4)
        assert Undate.parse("--12-31", "ISO8601") == Undate(month=12, day=31)

        # unsupported format
        with pytest.raises(ValueError, match="Unsupported format"):
            Undate.parse("1984", "foobar")
        with pytest.raises(ValueError, match="Unsupported format"):
            Undate.parse("1984", "%Y-%m")

    def test_format(self):
        # EDTF format
        assert Undate(1984).format("EDTF") == "1984"
        assert Undate(1984, 4).format("EDTF") == "1984-04"
        assert Undate(1984, 4, 15).format("EDTF") == "1984-04-15"
        assert Undate("19XX").format("EDTF") == "19XX"
        assert Undate(1984, "XX").format("EDTF") == "1984-XX"
        assert Undate(1984, 4, "XX").format("EDTF") == "1984-04-XX"
        assert Undate(month=12, day=31).format("EDTF") == "XXXX-12-31"

        # ISO8601 format
        assert Undate(1984).format("ISO8601") == "1984"
        assert Undate(1984, 4).format("ISO8601") == "1984-04"
        assert Undate(1984, 4, 15).format("ISO8601") == "1984-04-15"
        assert Undate(month=12, day=31).format("ISO8601") == "--12-31"

        # unsupported format
        with pytest.raises(ValueError, match="Unsupported format"):
            Undate(1984).format("foobar")
        with pytest.raises(ValueError, match="Unsupported format"):
            Undate(1984).format("%Y-%m")


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
            UndateInterval(Undate(2000), Undate()).duration()
