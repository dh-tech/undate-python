from undate.converters.calendars import GregorianDateConverter


class TestGregorianDateConverter:
    def test_to_gregorian(self):
        converter = GregorianDateConverter()
        # conversion is a no-op, returns values unchanged
        assert converter.to_gregorian(2025, 6, 15) == (2025, 6, 15)

    def test_min_month(self):
        assert GregorianDateConverter().min_month() == 1

    def test_max_month(self):
        assert GregorianDateConverter().max_month(2025) == 12

    def test_max_day(self):
        converter = GregorianDateConverter()
        assert converter.max_day(2025, 1) == 31
        assert converter.max_day(2025, 2) == 28
        assert converter.max_day(converter.LEAP_YEAR, 2) == 29
        assert converter.max_day(2025, 12) == 31

    def test_representative_years(self):
        converter = GregorianDateConverter()
        # single year is not filtered
        assert converter.representative_years([2025]) == [2025]
        # multiple non-leap years, returns just the first
        assert converter.representative_years([2025, 2026]) == [2025]
        # next leap year is 2028; returns first leap year and first non-leap year, in input order
        assert converter.representative_years([2025, 2026, 2028, 2029]) == [2025, 2028]

        # if no years are provided, returns a known leap year and non-leap year
        assert converter.representative_years() == [
            converter.LEAP_YEAR,
            converter.NON_LEAP_YEAR,
        ]
        assert converter.representative_years([]) == [
            converter.LEAP_YEAR,
            converter.NON_LEAP_YEAR,
        ]
