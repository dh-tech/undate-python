import pytest

from undate.converters.calendars.gregorian import GregorianDateConverter

class TestGregorianDateConverter:
    converter = GregorianDateConverter()

    def test_min_month(self):
        assert self.converter.min_month() == 1

    def test_max_month(self):
        # Should always be 12 for Gregorian, regardless of year
        assert self.converter.max_month(year=2023) == 12
        assert self.converter.max_month(year=2024) == 12 # Leap year
        assert self.converter.max_month(year=None) == 12


    def test_first_month(self):
        # Default implementation calls min_month
        assert self.converter.first_month() == 1

    def test_last_month(self):
        # Default implementation calls max_month
        assert self.converter.last_month(year=2023) == 12
        assert self.converter.last_month(year=None) == 12

    # Test cases for max_day(self, year: int, month: int)
    @pytest.mark.parametrize(
        "year, month, expected_days",
        [
            # Known year, known month
            (2023, 1, 31),  # Jan
            (2023, 2, 28),  # Feb, non-leap year
            (2024, 2, 29),  # Feb, leap year
            (2023, 4, 30),  # Apr, 30-day month
            (2023, 12, 31), # Dec
            # Unknown year (should default to non-leap for Feb)
            (None, 1, 31),
            (None, 2, 28), # Feb, unknown year -> non-leap
            (None, 4, 30),
            # Known year, unknown month (should default to 31)
            (2023, None, 31),
            (2024, None, 31), # Leap year, unknown month
            # Unknown year, unknown month (should default to 31)
            (None, None, 31),
        ],
    )
    def test_max_day(self, year, month, expected_days):
        assert self.converter.max_day(year=year, month=month) == expected_days

    @pytest.mark.parametrize(
        "year, month, day",
        [
            (2023, 1, 15),
            (2024, 2, 29), # Leap day
            (1900, 2, 28), # Non-leap century
            (2000, 2, 29), # Leap century
        ]
    )
    def test_to_gregorian(self, year, month, day):
        # For Gregorian converter, it should return the same date
        assert self.converter.to_gregorian(year, month, day) == (year, month, day)
