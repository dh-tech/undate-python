import numpy as np
import portion
import pytest

from undate.date import (
    ONE_DAY,
    ONE_YEAR,
    ONE_MONTH_MAX,
    Date,
    DatePrecision,
    Timedelta,
    Udelta,
    IntegerRange,
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


class TestIntegerRange:
    def test_init(self):
        february_days = IntegerRange(28, 29)  # 28 or 29
        assert february_days.lower == 28
        assert february_days.upper == 29
        assert february_days.left == portion.CLOSED
        assert february_days.right == portion.CLOSED
        assert 28 in february_days
        assert 29 in february_days
        assert 30 not in february_days

    def test_init_validation(self):
        with pytest.raises(
            ValueError, match=r"Lower value \(10\) must be less than upper \(4\)"
        ):
            IntegerRange(10, 4)

    # TODO: test/implement comparisons
    # NOTE: this results in a deprecation warning;
    # implement conversion to singleton in the class?
    # assert 30 > february_days


class TestUdelta:
    def test_init(self):
        # February in an unknown year in Gregorian calendar could be 28 or 29 days
        february_days = IntegerRange(28, 29)  # 28 or 29
        udelt = Udelta(28, 29)
        assert isinstance(udelt.days, IntegerRange)
        assert udelt.days.lower == 28
        assert udelt.days.upper == 29

        # NOTE: default portion interval comparison may not be what we want here,
        # since this is an unknown value within the range...
        # (maybe handled in udelta class comparison methods)
        assert udelt.days == february_days

        # do the right thing with more than one value, out of order
        unknown_month_duration = Udelta(30, 31, 28)
        assert isinstance(unknown_month_duration.days, IntegerRange)
        assert unknown_month_duration.days.lower == 28
        assert unknown_month_duration.days.upper == 31

    def test_init_validation(self):
        with pytest.raises(ValueError, match="Must specify at least two values"):
            Udelta(10)

    def test_repr(self):
        # default dataclass repr
        assert repr(Udelta(28, 29)) == "Udelta(days=[28,29])"

    def test_eq(self):
        # uncertain deltas are not equivalent
        udelt1 = Udelta(30, 31)
        udelt2 = Udelta(30, 31)
        # not equal to equivalent udelta range
        assert udelt1 != udelt2
        # equal to self
        assert udelt1 is udelt1

    def test_lt(self):
        week_or_tenday = Udelta(7, 10)
        # compare udelta with udelta
        month = Udelta(28, 31)
        # a week or ten-day is unambiguously less than a month
        assert week_or_tenday < month
        # compare udelta with Timedelta
        # NOTE: currently requires this direction, until we update Timedelta
        assert not week_or_tenday < ONE_DAY
        # an uncertain  month is unambiguously less than a year
        assert month < ONE_YEAR
        # an uncertain  month may or may not be less than one month max
        assert not month < ONE_MONTH_MAX

    def test_gt(self):
        week_or_tenday = Udelta(7, 10)
        # compare udelta with udelta
        month = Udelta(28, 31)
        # a month is unambiguously longer than week or ten-day
        assert month > week_or_tenday
        # compare udelta with Timedelta
        # NOTE: currently requires this direction, until we update Timedelta
        # to support the reverse comparison
        assert week_or_tenday > ONE_DAY
        # an uncertain month is not greater than a year
        assert not month > ONE_YEAR
        # an uncertain  month may or may not be greater than one month max
        assert not month > ONE_MONTH_MAX
