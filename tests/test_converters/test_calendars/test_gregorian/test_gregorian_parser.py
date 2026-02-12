import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF

from undate.converters.calendars.gregorian.parser import gregorian_parser


# for now, just test that valid dates can be parsed

testcases = [
    # year
    "2012",
    # month + year
    "Jan 1960",
    "Feb 1801",
    "1900 Feb",
    # day + month + year
    "Feb 5 1602",
    # "1602 February 5",
    # day + month
    "January 5",
    "5 Jan",
    # three digit year
]


@pytest.mark.parametrize("date_string", testcases)
def test_should_parse(date_string):
    assert gregorian_parser.parse(date_string)


error_cases = [
    # # invalid days
    ("0 Tammuz 5403", UnexpectedCharacters),
    # ("31 Tishri 5403", UnexpectedCharacters),
    # # month alone
    # ("Tishri", UnexpectedEOF),
    # # month day only
    ("12 ", UnexpectedEOF),
    # # invalid month
    # ("Foo 383", UnexpectedCharacters),
    # # wrong format
    # ("2024-10-02", UnexpectedCharacters),
    # # year month day not supported
    # ("5403 Adar", UnexpectedCharacters),
    # ("5403 Adar 14", UnexpectedCharacters),
]


@pytest.mark.parametrize("date_string,exception", error_cases)
def test_should_error(date_string, exception):
    with pytest.raises(exception):
        gregorian_parser.parse(date_string)
