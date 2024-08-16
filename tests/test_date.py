import numpy as np

from undate.date import Date, DatePrecision, ONE_DAY, ONE_YEAR, ONE_MONTH_MAX


class TestDatePrecision:
    def test_str(self):
        assert str(DatePrecision.YEAR) == "YEAR"


class TestDate:
    def test_init_year(self):
        d = Date(2001)
        assert isinstance(d, Date)
        assert d.dtype == "datetime64[Y]"
        assert str(d) == "2001"

    def test_init_year_month(self):
        d = Date(2010, 5)
        assert isinstance(d, Date)
        assert d.dtype == "datetime64[M]"
        assert str(d) == "2010-05"

    def test_init_year_month(self):
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
        assert Date(2010, 5).day == None
        assert Date(2021, 6, 15).day == 15
