import pytest
from undate.converters.calendars.hebrew.parser import hebrew_parser
from undate.converters.calendars.hebrew.transformer import (
    HebrewDateTransformer,
    HebrewUndate,
)
from undate.undate import Undate, Calendar
from undate.date import DatePrecision


def test_hebrew_undate():
    assert HebrewUndate(848).calendar == Calendar.HEBREW


testcases = [
    # examples from Princeton Geniza Project
    # date conversions checked with https://www.muqawwim.com/
    # 26 Tammuz 4816; Tammuz  = month 4
    ("26 Tammuz 4816", HebrewUndate(4816, 4, 26), DatePrecision.DAY),
    ("Tammuz 4816", HebrewUndate(4816, 4), DatePrecision.MONTH),
    ("4816", HebrewUndate(4816), DatePrecision.YEAR),
    # 26 Tishrei 5416: Tishrei = month 7
    ("26 Tishrei 5416", HebrewUndate(5416, 7, 26), DatePrecision.DAY),
    # Ṭeveth = month 10
    ("Ṭevet 5362", HebrewUndate(5362, 10), DatePrecision.MONTH),
    ("5362", HebrewUndate(5362), DatePrecision.YEAR),
    # add when we support parsing ranges:
    # Adar I and Adar II 5453 : (1693 CE)
    # support weekdays included in text
    ("Thursday, 12 Sivan 4795", HebrewUndate(4795, 3, 12), DatePrecision.DAY),
    # with or without comma
    ("Thursday 12 Sivan 4795", HebrewUndate(4795, 3, 12), DatePrecision.DAY),
    # huh, current parsing completely ignores whitespace; do we want that?
    ("Thursday12Sivan4795", HebrewUndate(4795, 3, 12), DatePrecision.DAY),
]


@pytest.mark.parametrize("date_string,expected,expected_precision", testcases)
def test_transform(date_string, expected, expected_precision):
    transformer = HebrewDateTransformer(visit_tokens=True)
    # parse the input string, then transform to undate object
    parsetree = hebrew_parser.parse(date_string)
    transformed_date = transformer.transform(parsetree)
    assert transformed_date == expected
    # currently only undates have date precision
    if isinstance(transformed_date, Undate):
        assert transformed_date.precision == expected_precision
    # transformer doesn't have access to date string,
    # label will need to be set by the converter class
