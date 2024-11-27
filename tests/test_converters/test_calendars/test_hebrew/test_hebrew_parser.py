import pytest
from undate.converters.calendars.hebrew.parser import hebrew_parser


# for now, just test that valid dates can be parsed

testcases = [
    # year
    "5362",
    # month + year
    # - with and without accent
    "Ṭevet 5362",
    "Tevet 5362",
    "Elul 4932",
    "Sivan 5581",
    # variant month name, with or without accent
    "Ṭeveth 5362",
    "Teveth 5362",
    "Iyyar 1526",
    "Iyar 1526",
    # day month year
    "26 Tammuz 4816",
    "7 Heshvan 5425",
    "26 Tishrei 5416",
    "26 Tishri 5416",
    "14 Adar 5403",
    "14 Adar I 5403",
    "9 Adar II 5404",
    "9 Adar Bet 5404",
    # two and 1 digit years
    "536",
    "53",
    "3",
]


@pytest.mark.parametrize("date_string", testcases)
def test_should_parse(date_string):
    assert hebrew_parser.parse(date_string)


error_cases = [
    # invalid days
    "0 Tammuz 5403",
    "31 Tishri 5403",
    # month alone
    "Tishri",
    # month day only
    "12 Heshvan",
    # invalid month
    "Foo 383",
    # wrong format
    "2024-10-02",
    # year month day not supported
    "5403 Adar",
    "5403 Adar 14",
]


@pytest.mark.parametrize("date_string", error_cases)
def test_should_error(date_string):
    with pytest.raises(Exception):
        hebrew_parser.parse(date_string)
