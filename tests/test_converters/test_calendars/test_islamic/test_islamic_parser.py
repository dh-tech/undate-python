import pytest
from lark.exceptions import LarkError

from undate.converters.calendars.islamic.parser import islamic_parser


# for now, just test that valid dates can be parsed

testcases = [
    # year
    "521",
    # month + year
    # - with and without accent
    "al-Muḥarram 900",
    "al-Muharram 900",
    "Safar 581",
    "Ṣafar 581",
    # variant month name, with or without accent
    "Muharram 900",
    "Muḥarram 900",
    "Rabīʿ al-ʾAwwal 901",
    "Rabi' I 901",
    "Rabīʿ ath-Thānī 343",
    "Rabīʿ II 343",
    "Jumādā al-ʾAwwal 1081",
    "Jumada al-`Awwal 1081",
    "Jumādā I 1081",
    "Jumādā ath-Thāniyah 901",
    "Jumada ath-Thaniyah 901",
    "Jumādā II 981",
    "Rajab 942",
    "Shaʿbān 900",
    "Sha'ban 900",
    "Ramaḍān 903",
    "Ramadan 903",
    "Shawwāl 1042",
    "Shawwal 1042",
    "Zū al-Qaʿdah 124",
    "Dhu l-Qa'da 124",
    # day month year
    "7 Jumādā I 1243",
    "29 Muḥarram 1243",
    "30 Muḥarram 1243",
    "Rabīʿ I 901",
    "12 Rabīʿ I 901",
    # two and 1 digit years
    "12 Rabīʿ I 90",
    "12 Rabīʿ I 9",
]


@pytest.mark.parametrize("date_string", testcases)
def test_should_parse(date_string):
    assert islamic_parser.parse(date_string)


error_cases = [
    # invalid days
    "0 Muḥarram 1243",
    "31 Muḥarram 1243",
    # month alone
    "Shawwal",
    # month day only
    "12 Shawwal",
    # invalid month
    "Foo 383",
    # wrong format
    "2024-10-02",
    # year month day not supported
    "901 Rabīʿ I",
    "901 Rabīʿ I 12",
]


@pytest.mark.parametrize("date_string", error_cases)
def test_should_error(date_string):
    with pytest.raises(LarkError):
        islamic_parser.parse(date_string)
