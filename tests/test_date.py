import numpy as np
from uncertainties import ufloat

from undate.date import ONE_YEAR, Date, DatePrecision, Timedelta, Udelta


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


class TestUdelta:
    def test_init(self):
        # february in an unknown year in Gregorian calendar could be 28 or 29 days
        february_days = ufloat(28.5, 0.5)  # 28 or 29
        udelt = Udelta(28, 29)
        # two ufloat values don't actually compare as equal, due to the variance
        assert udelt != february_days
        # so inspect the expected values
        assert udelt.days.nominal_value == 28.5
        assert udelt.days.std_dev == 0.5
