import pytest
from undate.converters.calendars.hijri.parser import hijri_parser
from undate.converters.calendars.hijri.transformer import HijriDateTransformer
from undate.undate import Undate, UndateInterval
from undate.date import DatePrecision

testcases = [
    # examples from Princeton Geniza Project
    # date conversions checked with https://www.muqawwim.com/
    # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE)
    ("7 Jumādā I 1243", Undate(1827, 11, 26), DatePrecision.DAY),
    (
        "Jumādā I 1243",
        UndateInterval(Undate(1827, 11, 20), Undate(1827, 12, 19)),
        DatePrecision.MONTH,
    ),
    (
        "1243",
        UndateInterval(Undate(1827, 7, 25), Undate(1828, 7, 13)),
        DatePrecision.YEAR,
    ),
    ("27 Dhū l-Qaʿda 632", Undate(1235, 8, 20), DatePrecision.DAY),
    (
        "Rajab 495",
        UndateInterval(Undate(1102, 4, 28), Undate(1102, 5, 27)),
        DatePrecision.MONTH,
    ),
    (
        "441",
        UndateInterval(Undate(1049, 6, 11), Undate(1050, 5, 31)),
        DatePrecision.YEAR,
    ),
    # examples from ISMI data
    ("901 Rabīʿ I 14", Undate(1495, 12, 11), DatePrecision.DAY),
    (
        "884",
        UndateInterval(Undate(1479, 4, 3), Undate(1480, 3, 21)),
        DatePrecision.YEAR,
    ),
    # add when we support parsing ranges:
    # 900 Muḥarram 1 - 999 Ḏu al-Ḥijjaẗ 29 : 1494-10-11 to 1591-10-18
]


@pytest.mark.parametrize("date_string,expected,expected_precision", testcases)
def test_transform(date_string, expected, expected_precision):
    transformer = HijriDateTransformer(visit_tokens=True)
    # parse the input string, then transform to undate object
    parsetree = hijri_parser.parse(date_string)
    transformed_date = transformer.transform(parsetree)
    assert transformed_date == expected
    # currently only undates have date precision
    if isinstance(transformed_date, Undate):
        assert transformed_date.precision == expected_precision
    # transformer doesn't have access to date string,
    # label will need to be set by the converter class
