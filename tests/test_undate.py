from datetime import date, datetime
from enum import auto
from unittest import mock

import pytest

from undate import Undate, UndateInterval, Calendar
from undate.undate import StrEnum  # import whichever version is used there
from undate.converters.base import BaseCalendarConverter, BaseDateConverter
from undate.date import Date, DatePrecision, Timedelta, UnDelta, UnInt


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
        assert repr(Undate(2022, 11, 7)) == "<Undate 2022-11-07 (Gregorian)>"
        assert (
            repr(Undate(2022, 11, 7, label="A Special Day"))
            == "<Undate 'A Special Day' 2022-11-07 (Gregorian)>"
        )
        assert repr(Undate(484, calendar=Calendar.ISLAMIC)) == "<Undate 0484 (Islamic)>"

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

    def test_calendar(self):
        assert Undate(2024).calendar == Calendar.GREGORIAN
        # by name, any case
        assert Undate(848, calendar="ISLAMIC").calendar == Calendar.ISLAMIC
        assert Undate(848, calendar="islamic").calendar == Calendar.ISLAMIC
        # by enum
        assert Undate(848, calendar=Calendar.ISLAMIC).calendar == Calendar.ISLAMIC
        # invalid
        with pytest.raises(ValueError, match="Calendar `foobar` is not supported"):
            Undate(848, calendar="foobar")

    def test_as_calendar(self):
        # changes calendar *without* converting dates
        assert Undate(1243, 5, 7).as_calendar(Calendar.ISLAMIC) == Undate(
            1243, 5, 7, calendar=Calendar.ISLAMIC
        )
        # should also work with string
        assert Undate(1243, 5, 7).as_calendar("islamic") == Undate(
            1243, 5, 7, calendar=Calendar.ISLAMIC
        )

    def test_init_invalid(self):
        with pytest.raises(ValueError):
            Undate("19??")

        with pytest.raises(ValueError, match="At least one of year, month, or day"):
            Undate()

    def test_invalid_date(self):
        # invalid month should raise an error
        with pytest.raises(ValueError):
            Undate(1990, 22)

    def test_to_undate(self):
        undate_from_date = Undate.to_undate(date(2001, 3, 5))
        assert isinstance(undate_from_date, Undate)
        assert undate_from_date == Undate(2001, 3, 5)

        now = datetime.now()
        undate_from_dt = Undate.to_undate(now)
        assert isinstance(undate_from_dt, Undate)
        assert undate_from_dt == Undate(now.year, now.month, now.day)

        # from internal Date object
        y2k = Date(2000)
        y2k_to_undate = Undate.to_undate(y2k)
        assert isinstance(y2k_to_undate, Undate)
        assert int(y2k_to_undate.year) == y2k.year
        assert y2k_to_undate.month is None
        assert y2k_to_undate.day is None

        # unsupported type
        with pytest.raises(TypeError):
            Undate.to_undate("foo")

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

        # NOTE: no longer supported to inistalize undate with no date information
        # force method to hit conditional for date precision
        # some_century = Undate()
        # some_century.precision = DatePrecision.CENTURY
        # assert some_century.year is None

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
        with pytest.raises(
            NotImplementedError,
            match="one date \\(2022-05\\) falls within the other \\(2022\\)",
        ):
            assert Undate(2022) < Undate(2022, 5)

        # same if we attempt to compare in the other direction
        with pytest.raises(
            NotImplementedError,
            match="one date \\(2022-05\\) falls within the other \\(2022\\)",
        ):
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

    def test_possible_years(self):
        assert Undate(1991).possible_years == [1991]
        assert Undate("190X").possible_years == range(1900, 1910)
        assert Undate("19XX").possible_years == range(1900, 2000)
        # uses step when missing digit is not last digit
        assert Undate("19X1").possible_years == range(1901, 1992, 10)
        assert Undate("2X25").possible_years == range(2025, 2926, 100)
        assert Undate("1XXX").possible_years == range(1000, 2000)
        # completely unknown year raises value error, because the range is not useful
        with pytest.raises(
            ValueError, match="cannot be returned for completely unknown year"
        ):
            assert Undate("XXXX").possible_years

    def test_representative_years(self):
        # single year is returned as is
        assert Undate("1991").representative_years == [1991]
        # for an uncertain year, returns first leap year and non-leap year in range
        assert Undate("190X").representative_years == [1900, 1904]
        assert Undate("19XX").representative_years == [1900, 1904]
        # works for other calendars
        assert Undate("481X", calendar="Hebrew").representative_years == [
            4810,
            4811,
            4812,
            4813,
            4816,
            4818,
        ]

        # use mock to simulate a calendar without representative years filtering
        with mock.patch(
            "undate.converters.calendars.HebrewDateConverter.representative_years"
        ) as mock_representative_years:
            mock_representative_years.side_effect = NotImplementedError
            assert Undate("481X", calendar="Hebrew").representative_years == list(
                range(4810, 4820)
            )

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
        # 1X = October, November, or December = 30 or 31 days
        # should return a Undelta object
        unknown_month_duration = Undate(year=1900, month="1X").duration()
        assert isinstance(unknown_month_duration, UnDelta)
        assert unknown_month_duration.days == UnInt(30, 31)

        # completely unknown month should also return a Undelta object
        unknown_month_duration = Undate(year=1900, month="XX").duration()
        assert isinstance(unknown_month_duration, UnDelta)
        # possible range is 28 to 31 days
        assert unknown_month_duration.days == UnInt(28, 31)

        # the number of days in February of an unknown year is uncertain, since
        # it could vary with leap years; either 28 or 29 days
        feb_duration = Undate(month=2).duration()
        assert isinstance(feb_duration, UnDelta)
        assert feb_duration.days == UnInt(28, 29)

    def test_partiallyknownyear_duration(self):
        assert Undate("190X").duration().days == UnInt(365, 366)
        assert Undate("XXXX").duration().days == UnInt(365, 366)
        # if possible years don't include any leap years, duration is not ambiguous
        assert Undate("19X1").duration().days == 365
        # year duration logic should work in other calendars
        # islamic
        assert Undate("108X", calendar="Islamic").duration().days == UnInt(354, 355)
        # completely unknown years is calculated based on representative years
        assert Undate("XXXX", calendar="Islamic").duration().days == UnInt(354, 355)
        assert Undate("536X", calendar="Hebrew").duration().days == UnInt(353, 385)
        # different set of years could vary
        assert Undate("53X2", calendar="Hebrew").duration().days == UnInt(354, 385)
        # fully unknown year also works for Hebrew calendar
        assert Undate("XXX", calendar="Hebrew").duration().days == UnInt(353, 385)

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


def test_calendar_get_converter():
    # ensure we can retrieve a calendar converter for each
    # calendar named in our calendar enum
    for cal in Calendar:
        converter = Calendar.get_converter(cal)
        assert isinstance(converter, BaseCalendarConverter)
        assert converter.name.lower() == cal.name.lower()

    class BogusCalendar(StrEnum):
        """Unsupported calendars"""

        FOOBAR = auto()
        DUMMY = auto()

    # test error handling
    # ensure we raise a ValueError when an invalid calendar is requested
    with pytest.raises(ValueError, match="Unknown calendar"):
        Calendar.get_converter(BogusCalendar.FOOBAR)

    class DummyFormatter(BaseDateConverter):
        name = "Dummy"

    # also error if you request a converter that is not a calendar converter
    # NOTE: this fails because get_converter converts the enum to title case...
    # can't be tested with any of the existing non-calendar converters
    with pytest.raises(
        ValueError, match="Requested converter 'Dummy' is not a CalendarConverter"
    ):
        Calendar.get_converter(BogusCalendar.DUMMY)
