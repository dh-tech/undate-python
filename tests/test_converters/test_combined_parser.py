import pytest

from undate.converters.combined import parser, combined_transformer

from undate import Undate, UndateInterval

# test that valid dates can be parsed

testcases = [
    # EDTF
    ("1984", Undate(1984)),
    ("201X", Undate("201X")),
    ("20XX", Undate("20XX")),
    ("2004-XX", Undate(2004, "XX")),
    ("1000/2000", UndateInterval(Undate(1000), Undate(2000))),
    # Hebrew / Anno Mundi calendar
    ("Tammuz 4816", Undate(4816, 4, calendar="Hebrew")),
    # Islamic / Hijri calendar
    ("Jumādā I 1243", Undate(1243, 5, calendar="Islamic")),
    ("7 Jumādā I 1243", Undate(1243, 5, 7, calendar="Islamic")),
    ("14 Rabīʿ I 901", Undate(901, 3, 14, calendar="Islamic")),
    # Gregorian with non-numeric month (full or abbreviated)
    ("June 1602", Undate(1602, 6, calendar="Gregorian")),
    ("13 Jan 1602", Undate(1602, 1, 13, calendar="Gregorian")),
    ("2022 ugu. 4", Undate(2022, 11, 4, calendar="Gregorian")),
    ("18 avril", Undate(month=4, day=18, calendar="Gregorian")),
    # Christian liturgical dates
    ("Easter 1942", Undate(1942, 4, 5)),
    ("Epiphany 1921", Undate(1921, 1, 6)),
    ("Pentecost 2016", Undate(2016, 5, 15)),
    ("Ash Wednesday 2000", Undate(2000, 3, 8)),
    ("Whit Monday 2023", Undate(2023, 5, 29)),
]


@pytest.mark.parametrize("date_string,expected", testcases)
def test_transform(date_string, expected):
    # test the transformer directly
    transformer = combined_transformer
    # parse the input string, then transform to undate object
    parsetree = parser.parse(date_string)
    # since the same unknown date is not considered strictly equal,
    # compare object representations
    transformed_date = transformer.transform(parsetree)
    assert repr(transformed_date[0]) == repr(expected)


@pytest.mark.parametrize("date_string,expected", testcases)
def test_converter(date_string, expected):
    # should work the same way when called through the converter class
    assert repr(Undate.parse(date_string, "omnibus")) == repr(expected)


def test_parse_errors():
    # empty string not supported
    with pytest.raises(ValueError, match="not supported"):
        Undate.parse("", "omnibus")

    with pytest.raises(ValueError, match="not in a recognized date format"):
        Undate.parse("Monday 2023", "omnibus")


def test_no_serialize():
    with pytest.raises(ValueError, match="does not support"):
        Undate("2022").format("omnibus")
