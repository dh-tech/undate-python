import pytest

from undate import Undate, UndateInterval
from undate.converters.edtf.parser import edtf_parser
from undate.converters.edtf.transformer import EDTFTransformer

# for now, just test that valid dates can be parsed

testcases = [
    ("1984", Undate(1984)),
    ("1984-05", Undate(1984, 5)),
    ("1984-12", Undate(1984, 12)),
    ("1001-03-30", Undate(1001, 3, 30)),
    ("1000/2000", UndateInterval(Undate(1000), Undate(2000))),
    ("1000-01/2000-05-01", UndateInterval(Undate(1000, 1), Undate(2000, 5, 1))),
    # level 1
    ("Y17000002", Undate(17000002)),
    ("Y-17000002", Undate(-17000002)),
    # negative year
    ("-1985", Undate(-1985)),
    # "2001-21",  # spring 2001
    # qualifiers TODO - not yet supported by undate
    # "1984?",
    # "2004-06~",
    # "2004-06-11%",
    # # unspecified digits from right
    ("201X", Undate("201X")),
    ("20XX", Undate("20XX")),
    ("2004-XX", Undate(2004, "XX")),
    ("1985-04-XX", Undate(1985, 4, "XX")),
    ("1985-XX-XX", Undate(1985, "XX", "XX")),
    # # open ended intervals
    ("1985-04-12/..", UndateInterval(Undate(1985, 4, 12), None)),
    ("1985-04/..", UndateInterval(Undate(1985, 4), None)),
    ("../1985-04-12", UndateInterval(None, Undate(1985, 4, 12))),
    ("/1985-04-12", UndateInterval(None, Undate(1985, 4, 12))),
    # level 2 unspecified digits
    ("156X-12-25", Undate("156X", 12, 25)),
    ("XXXX-12-XX", Undate("XXXX", 12, "XX")),
    ("1XXX-XX", Undate("1XXX", "XX")),
    ("1984-1X", Undate(1984, "1X")),
]


@pytest.mark.parametrize("date_string,expected", testcases)
def test_transform(date_string, expected):
    transformer = EDTFTransformer()
    # parse the input string, then transform to undate object
    parsetree = edtf_parser.parse(date_string)
    # since the same unknown date is not considered strictly equal,
    # compare object representations
    assert repr(transformer.transform(parsetree)) == repr(expected)
