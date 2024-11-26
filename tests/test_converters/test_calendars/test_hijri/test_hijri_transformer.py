import pytest
from undate.converters.calendars.hijri.parser import hijri_parser
from undate.converters.calendars.hijri.transformer import (
    HijriDateTransformer,
    HijriUndate,
)
from undate.undate import Undate, Calendar
from undate.date import DatePrecision


def test_hijri_undate():
    assert HijriUndate(848).calendar == Calendar.HIJRI


testcases = [
    # examples from Princeton Geniza Project
    # date conversions checked with https://www.muqawwim.com/
    # Monday, 7 Jumādā I 1243 Hijrī (26 November, 1827 CE); Jumada I = month 5
    ("7 Jumādā I 1243", HijriUndate(1243, 5, 7), DatePrecision.DAY),
    ("Jumādā I 1243", HijriUndate(1243, 5), DatePrecision.MONTH),
    ("1243", HijriUndate(1243), DatePrecision.YEAR),
    # Gregorian:  UndateInterval(Undate(1827, 7, 25), Undate(1828, 7, 13)),
    # Zū al-Qaʿdah / Dhu l-Qa'da = month 11
    ("27 Dhū l-Qaʿda 632", HijriUndate(632, 11, 27), DatePrecision.DAY),
    # Rajab = month 7
    ("Rajab 495", HijriUndate(495, 7), DatePrecision.MONTH),
    ("441", HijriUndate(441), DatePrecision.YEAR),
    # examples from ISMI data (reformatted to day month year)
    # Rabi 1 = month 3
    ("14 Rabīʿ I 901", HijriUndate(901, 3, 14), DatePrecision.DAY),
    ("884", HijriUndate(884), DatePrecision.YEAR),
    # Gregorian:  UndateInterval(Undate(1479, 4, 3), Undate(1480, 3, 21)),
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