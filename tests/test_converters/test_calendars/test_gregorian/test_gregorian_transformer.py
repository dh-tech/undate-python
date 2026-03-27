import pytest
from undate.converters.calendars.gregorian.parser import gregorian_parser
from undate.converters.calendars.gregorian.transformer import GregorianDateTransformer
from undate.undate import Undate, Calendar
from undate.date import DatePrecision


testcases = [
    ("2012", Undate(2012), DatePrecision.YEAR),
    ("May 13 1602", Undate(1602, 5, 13), DatePrecision.DAY),
    ("Jan 1960", Undate(1960, 1), DatePrecision.MONTH),
    ("2022 ugu. 4", Undate(2022, 11, 4), DatePrecision.DAY),
    ("2022 Ugushyingo", Undate(2022, 11), DatePrecision.MONTH),
    ("4 Novemba", Undate(month=11, day=4), DatePrecision.DAY),
    # ignores whitespace, comma, period
    ("4Novemba", Undate(month=11, day=4), DatePrecision.DAY),
    ("18 avril, 2025", Undate(2025, 4, 18), DatePrecision.DAY),
]


@pytest.mark.parametrize("date_string,expected,expected_precision", testcases)
def test_transform(date_string, expected, expected_precision):
    transformer = GregorianDateTransformer(visit_tokens=True)
    # parse the input string, then transform to undate object
    parsetree = gregorian_parser.parse(date_string)
    transformed_date = transformer.transform(parsetree)
    # use EDTF to compare so we can check dates with unknown years
    assert transformed_date.format("EDTF") == expected.format("EDTF")
    # currently only returns undate, parser doesn't support intervals
    assert transformed_date.precision == expected_precision
    assert transformed_date.calendar == Calendar.GREGORIAN
