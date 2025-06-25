import datetime

import numpy as np
import pytest

from undate.date import (
    ONE_DAY,
    ONE_YEAR,
    ONE_MONTH_MAX,
    Date,
    DatePrecision,
    Timedelta,
    UnDelta,
    UnInt,
)


class TestDatePrecision:
    def test_str(self):
        assert str(DatePrecision.YEAR) == "YEAR"

    def test_precision_comparison(self):
        assert DatePrecision.DAY > DatePrecision.MONTH
        assert DatePrecision.MONTH > DatePrecision.YEAR


class TestDate:
    def test_init_year(self):
        d = Date(2001)
        assert isinstance(d, Date)
        assert d.dtype == "datetime64[Y]"
        assert str(d) == "2001"

    def test_init_year_np_datetime64(self):
        d = Date(np.datetime64("2024"))
        assert isinstance(d, Date)
        assert d.dtype == "datetime64[Y]"
        assert str(d) == "2024"

    def test_init_year_month(self):
        d = Date(2010, 5)
        assert isinstance(d, Date)
        assert d.dtype == "datetime64[M]"
        assert str(d) == "2010-05"

    def test_init_year_month_day(self):
        d = Date(2021, 6, 15)
        assert isinstance(d, Date)
        assert d.dtype == "datetime64[D]"
        assert str(d) == "2021-06-15"

    def test_properties_year(self):
        assert Date(2001).year == 2001
        assert Date(2010, 5).year == 2010
        assert Date(2021, 6, 15).year == 2021

    def test_properties_month(self):
        assert Date(2001).month is None
        assert Date(2010, 5).month == 5
        assert Date(2021, 6, 15).month == 6

    def test_properties_day(self):
        assert Date(2001).day is None
        assert Date(2010, 5).day is None
        assert Date(2021, 6, 15).day == 15

    def test_weekday(self):
        # thursday
        assert Date(2025, 1, 2).weekday == 3
        assert Date(2025, 1, 2).weekday == datetime.date(2025, 1, 2).weekday()
        # friday
        assert Date(2025, 1, 3).weekday == 4
        assert Date(2025, 1, 3).weekday == datetime.date(2025, 1, 3).weekday()
        # saturday
        assert Date(2025, 1, 4).weekday == 5
        assert Date(2025, 1, 4).weekday == datetime.date(2025, 1, 4).weekday()
        # sunday
        assert Date(2025, 1, 5).weekday == 6
        assert Date(2025, 1, 5).weekday == datetime.date(2025, 1, 5).weekday()
        # monday
        assert Date(2025, 1, 6).weekday == 0
        assert Date(2025, 1, 6).weekday == datetime.date(2025, 1, 6).weekday()
        # tuesday
        assert Date(2025, 1, 7).weekday == 1
        assert Date(2025, 1, 7).weekday == datetime.date(2025, 1, 7).weekday()

        # when a date is not day-level precision, no weekday is returned
        yearonly_date = Date(2025)
        assert yearonly_date.dtype == "datetime64[Y]"
        assert yearonly_date.weekday is None

    def test_substract(self):
        # date - date = timedelta
        date_difference = Date(2024, 1, 2) - Date(2024, 1, 1)
        assert isinstance(date_difference, Timedelta)
        assert date_difference.days == 1

        # date - timedelta = date
        year_prior = Date(2024, 1, 2) - ONE_YEAR
        assert isinstance(year_prior, Date)


class TestTimeDelta:
    def test_init_from_int(self):
        td = Timedelta(31)
        assert isinstance(td, Timedelta)
        assert td.dtype == "timedelta64[D]"
        assert td.astype("int") == 31

    def test_init_from_np_timedelta64(self):
        td = Timedelta(np.timedelta64(12, "D"))
        assert isinstance(td, Timedelta)
        assert td.dtype == "timedelta64[D]"
        assert td.astype("int") == 12

    def test_days(self):
        assert Timedelta(10).days == 10


class TestUnInt:
    def test_init(self):
        february_days = UnInt(28, 29)  # 28 or 29
        assert february_days.lower == 28
        assert february_days.upper == 29

        # also supports keyword args
        anymonth_days = UnInt(lower=28, upper=31)
        assert anymonth_days.lower == 28
        assert anymonth_days.upper == 31

    def test_init_validation(self):
        with pytest.raises(
            ValueError, match=r"Lower value \(10\) must be less than upper \(4\)"
        ):
            UnInt(10, 4)

    def test_contains(self):
        anymonth_days = UnInt(lower=28, upper=31)
        # integer
        assert 28 in anymonth_days
        assert 29 in anymonth_days
        assert 31 in anymonth_days
        assert 32 not in anymonth_days
        # unint
        assert UnInt(28, 29) in anymonth_days

        # other types are assumed not in range
        assert "twenty-eight" not in anymonth_days

    def test_gt(self):
        ten_twelve = UnInt(10, 12)
        # compare with integer
        assert ten_twelve > 9
        assert not ten_twelve > 12
        assert not ten_twelve > 15
        # compare with unint
        assert ten_twelve > UnInt(2, 4)
        assert not ten_twelve > UnInt(12, 24)
        assert not ten_twelve > UnInt(13, 23)
        # unsupported type
        with pytest.raises(TypeError):
            ten_twelve > "three"

    def test_lt(self):
        ten_twelve = UnInt(10, 12)
        # compare with integer
        assert ten_twelve < 13
        assert not ten_twelve < 12
        assert not ten_twelve < 9
        # compare with unint
        assert ten_twelve < UnInt(13, 23)
        assert not ten_twelve < UnInt(12, 24)
        assert not ten_twelve < UnInt(2, 4)
        # unsupported type
        with pytest.raises(TypeError):
            ten_twelve < "three"

    def test_iterable(self):
        anymonth_days = UnInt(lower=28, upper=31)
        assert list(anymonth_days) == [28, 29, 30, 31]

    def test_add(self):
        february_days = UnInt(28, 29)
        # add integer
        assert february_days + 1 == UnInt(29, 30)
        # add UnInt - minimum is 28 + 1, maximum is 29 + 2
        assert february_days + UnInt(1, 2) == UnInt(29, 31)
        # other types are not supported
        with pytest.raises(TypeError, match="unsupported operand"):
            february_days + "two"

    def test_subtract(self):
        february_days = UnInt(28, 29)
        # subtract integer
        assert february_days - 10 == UnInt(18, 19)
        # subtract UnInt - minimum is lower - largest value, maximum is upper - smallest value
        # difference between number of days in any month and the month of February?
        # [28,31] - [28,29] = [-1, 3]
        anymonth_days = UnInt(lower=28, upper=31)
        assert anymonth_days - february_days == UnInt(-1, 3)
        # what if we go the other direction?
        assert february_days - anymonth_days == UnInt(-3, 1)
        # other types are not supported
        with pytest.raises(TypeError, match="unsupported operand"):
            february_days - "two"


class TestUnDelta:
    def test_init(self):
        # February in an unknown year in Gregorian calendar could be 28 or 29 days
        february_days = UnInt(28, 29)  # 28 or 29
        udelt = UnDelta(28, 29)
        assert isinstance(udelt.days, UnInt)
        assert udelt.days.lower == 28
        assert udelt.days.upper == 29

        # NOTE: default portion interval comparison may not be what we want here,
        # since this is an unknown value within the range...
        # (maybe handled in undelta class comparison methods)
        assert udelt.days == february_days

        # do the right thing with more than one value, out of order
        unknown_month_duration = UnDelta(30, 31, 28)
        assert isinstance(unknown_month_duration.days, UnInt)
        assert unknown_month_duration.days.lower == 28
        assert unknown_month_duration.days.upper == 31

    def test_init_validation(self):
        with pytest.raises(ValueError, match="Must specify at least two values"):
            UnDelta(10)

    def test_repr(self):
        # customized string representation
        assert repr(UnDelta(28, 29)) == "UnDelta(days=[28,29])"

    def test_eq(self):
        # uncertain deltas are not equivalent
        udelt1 = UnDelta(30, 31)
        udelt2 = UnDelta(30, 31)
        # not equal to equivalent undelta range
        assert udelt1 != udelt2
        # equal to self
        assert udelt1 is udelt1

    def test_lt(self):
        week_or_tenday = UnDelta(7, 10)
        # compare undelta with undelta
        month = UnDelta(28, 31)
        # a week or ten-day is unambiguously less than a month
        assert week_or_tenday < month
        # compare undelta with Timedelta
        # NOTE: currently requires this direction, until we update Timedelta
        assert not week_or_tenday < ONE_DAY
        # an uncertain  month is unambiguously less than a year
        assert month < ONE_YEAR
        # an uncertain  month may or may not be less than one month max
        assert not month < ONE_MONTH_MAX

    def test_gt(self):
        week_or_tenday = UnDelta(7, 10)
        # compare undelta with undelta
        month = UnDelta(28, 31)
        # a month is unambiguously longer than week or ten-day
        assert month > week_or_tenday
        # compare undelta with Timedelta
        # NOTE: currently requires this direction, until we update Timedelta
        # to support the reverse comparison
        assert week_or_tenday > ONE_DAY
        # an uncertain month is not greater than a year
        assert not month > ONE_YEAR
        # an uncertain  month may or may not be greater than one month max
        assert not month > ONE_MONTH_MAX
