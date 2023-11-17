import pytest

from undate.undate import Undate, UndateInterval
from undate.dateformat.edtf.parser import edtf_parser
from undate.dateformat.edtf.transformer import EDTFTransformer

# for now, just test that valid dates can be parsed

testcases = [
    ("1984", Undate(1984)),
    ("1984-05", Undate(1984, 5)),
    ("1984-12", Undate(1984, 12)),
    ("1001-03-30", Undate(1001, 3, 30)),
    ("1000/2000", UndateInterval(Undate(1000), Undate(2000))),
    ("1000-01/2000-05-01", UndateInterval(Undate(1000, 1), Undate(2000, 5, 1))),
    # # level 1
    # NOTE: undate currently doesn't most of the level 1 functionality
    # NOTE: undate currently doesn't support years beyond 9999 (datetime.MAXYEAR)
    # ("Y17000002", Undate(17000002)),
    # "2001-21",  # spring 2001
    # # qualifiers
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
]


def test_transform():
    transformer = EDTFTransformer()

    for testinput, output in testcases:
        parsetree = edtf_parser.parse(testinput)
        assert transformer.transform(parsetree) == output


# error_cases = ["1984-13", "Y1702"]


# def test_should_error():
#     for error_case in error_cases:
#         with pytest.raises(Exception):
#             edtf_parser.parse(error_cases)
