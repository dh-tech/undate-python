import pytest

from lark import Token, Tree

from undate import Undate, Calendar
from undate.date import Weekday
from undate.converters.holidays import HolidayDateConverter, HolidayTransformer


class TestHolidayConverter:
    converter = HolidayDateConverter()

    @pytest.mark.parametrize(
        "input_string,expected",
        [
            ("Epiphany 1921", Undate(1921, 1, 6)),
            ("candlemas 1913", Undate(1913, 2, 2)),
            ("Candlemass 1862", Undate(1862, 2, 2)),
            ("st. patrick's day 1823", Undate(1823, 3, 17)),
            ("st patrick's day 1901", Undate(1901, 3, 17)),
            ("all fools day 1933", Undate(1933, 4, 1)),
            ("st. cyprian's day 1902", Undate(1902, 9, 16)),
        ],
    )
    def test_fixed_holidays(self, input_string, expected):
        assert self.converter.parse(input_string) == expected

    @pytest.mark.parametrize(
        "input_string,expected,expected_weekday",
        [
            ("Easter 1900", Undate(1900, 4, 15), Weekday.SUNDAY),
            ("easter monday 1925", Undate(1925, 4, 13), Weekday.MONDAY),
            ("holy saturday 2018", Undate(2018, 3, 31), Weekday.SATURDAY),
            ("Ash Wednesday 2000", Undate(2000, 3, 8), Weekday.WEDNESDAY),
            ("shrove tuesday 1940", Undate(1940, 2, 6), Weekday.TUESDAY),
            ("Ascension 1988", Undate(1988, 5, 12), Weekday.THURSDAY),
            ("Ascension Day 1999", Undate(1999, 5, 13), Weekday.THURSDAY),
            ("Pentecost 2016", Undate(2016, 5, 15), Weekday.SUNDAY),
            ("whit monday 2005", Undate(2005, 5, 16), Weekday.MONDAY),
            ("whitsun monday 2023", Undate(2023, 5, 29), Weekday.MONDAY),
            ("trinity 1978", Undate(1978, 5, 21), Weekday.SUNDAY),
            ("Trinity Sunday 1967", Undate(1967, 5, 21), Weekday.SUNDAY),
        ],
    )
    def test_moveable_feasts(self, input_string, expected, expected_weekday):
        result = self.converter.parse(input_string)
        assert result == expected
        assert result.label == input_string
        assert result.earliest.weekday == expected_weekday

    def test_holiday_without_year(self):
        result = self.converter.parse("Epiphany")
        assert result.label == "Epiphany"
        assert result.format("EDTF") == "XXXX-01-06"
        assert not result.known_year
        assert result.calendar == Calendar.GREGORIAN

    def test_undate_parse(self):
        # accessible through main undate parse method
        assert Undate.parse("Epiphany 1942", "holidays") == Undate(1942, 1, 6)

    def test_parse_empty(self):
        with pytest.raises(ValueError, match="empty string"):
            self.converter.parse("")

    def test_parse_error(self):
        with pytest.raises(ValueError, match="Could not parse"):
            self.converter.parse("Not a holiday")

    def test_moveable_without_year(self):
        with pytest.raises(ValueError, match="Could not parse"):
            self.converter.parse("Easter")

    def test_to_string_error(self):
        with pytest.raises(ValueError, match="does not support"):
            self.converter.to_string(Undate(1916))


# edge cases  - should not happen from parser input but possible


class TestHolidayTransformer:
    def test_fixed_date(self):
        transformer = HolidayTransformer()
        result = transformer.fixed_date([Token("EPIPHANY", "")])
        assert isinstance(result, Tree)
        assert len(result.children) == 2
        assert all(isinstance(child, Token) for child in result.children)
        assert result.children[0].type == "month"
        assert result.children[0].value == 1
        assert result.children[1].type == "day"
        assert result.children[1].value == 6

        # namespaced token
        result = transformer.fixed_date([Token("holiday__EPIPHANY", "")])
        assert isinstance(result, Tree)
        assert len(result.children) == 2
        assert all(isinstance(child, Token) for child in result.children)
        assert result.children[0].type == "month"
        assert result.children[0].value == 1
        assert result.children[1].type == "day"
        assert result.children[1].value == 6

        # unknown fixed holiday should raise value error
        with pytest.raises(ValueError, match="Unknown fixed holiday"):
            transformer.fixed_date([Token("epiphany", "")])

    def test_get_date_parts(self):
        transformer = HolidayTransformer()
        # movable feast without year is not supported
        with pytest.raises(ValueError, match="Year is required"):
            transformer._get_date_parts([Token("EASTER", "")])
