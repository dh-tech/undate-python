import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF

from undate.converters.calendars.gregorian.parser import gregorian_parser


# test that valid dates can be parsed to confirm parser is working correctly

testcases = [
    # year
    "2012",
    # three digit year
    "566",
    # month + year
    "Jan 1960",
    "Feb 1801",
    "1900 Feb",
    # day + month + year in any order
    "May 5 1602",
    "5 May 1602",
    "1602 October 5",
    # day + month
    "December 5",
    "5 December",
    # Kinyarwanda (rw)
    "2025 ugu. 4",
    "2025 Ugushyingo 4",
    "2025 ugu",
    "2025 Ugushyingo",
    # Ganda (lg)
    "4 Novemba 2025",
    "4 Nov 2025",
    "Novemba 2025",
    "4 Novemba",
    # Tigrinya (ti)
    "ሕዳ 4, 2025",
    "ሕዳር 4 2025",
    # French
    "18 avril 2025",
    "18 avr. 2025",
    # case-insensitive
    "18 JUNE 2025",
    "Avril 2025",
]


@pytest.mark.parametrize("date_string", testcases)
def test_should_parse(date_string):
    assert gregorian_parser.parse(date_string)


error_cases = [
    # invalid days
    ("0 June 1006", UnexpectedCharacters),
    ("42 March 1206", UnexpectedCharacters),
    # month alone
    ("Juin", UnexpectedEOF),
    # day only
    ("12 ", UnexpectedEOF),
    # non-Gregorian month
    ("5 Tammuz 5403", UnexpectedCharacters),
    ("31 Tishri 5403", UnexpectedCharacters),
    # invalid month
    ("Foo 383", UnexpectedCharacters),
    # wrong format
    ("2024-10-02", UnexpectedCharacters),
]


@pytest.mark.parametrize("date_string,exception", error_cases)
def test_should_error(date_string, exception):
    with pytest.raises(exception):
        gregorian_parser.parse(date_string)
