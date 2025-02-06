import pytest

from undate.converters.combined import parser, combined_transformer

from undate.undate import Undate, UndateInterval

# for now, just test that valid dates can be parsed

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
    ("Jumādā I 1243", Undate(1243, 5, calendar="Hijri")),
    ("7 Jumādā I 1243", Undate(1243, 5, 7, calendar="Hijri")),
    ("14 Rabīʿ I 901", Undate(901, 3, 14, calendar="Hijri")),
]


@pytest.mark.parametrize("date_string,expected", testcases)
def test_transform(date_string, expected):
    transformer = combined_transformer
    # parse the input string, then transform to undate object
    parsetree = parser.parse(date_string)
    print(parsetree)
    # since the same unknown date is not considered strictly equal,
    # compare object representations
    transformed_date = transformer.transform(parsetree)
    print(transformed_date)
    assert repr(transformed_date[0]) == repr(expected)
