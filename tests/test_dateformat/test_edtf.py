import pytest

from undate.dateformat.edtf import EDTFDateFormat
from undate.undate import Undate, UndateInterval


class TestEDTFDateFormat:
    def test_parse_singledate(self):
        assert EDTFDateFormat().parse("2002") == Undate(2002)
        assert EDTFDateFormat().parse("1991-05") == Undate(1991, 5)
        assert EDTFDateFormat().parse("1991-05-03") == Undate(1991, 5, 3)
        # unknown dates are not strictly equal, but string comparison should match
        assert str(EDTFDateFormat().parse("201X")) == str(Undate("201X"))
        assert str(EDTFDateFormat().parse("2004-XX")) == str(Undate(2004, "XX"))
        # missing year but month/day known
        # assert EDTFDateFormat().parse("--05-03") == Undate(month=5, day=3)

    def test_parse_singledate_unequal(self):
        assert EDTFDateFormat().parse("2002") != Undate(2003)
        assert EDTFDateFormat().parse("1991-05") != Undate(1991, 6)
        assert EDTFDateFormat().parse("1991-05-03") != Undate(1991, 5, 4)
        # missing year but month/day known
        # - does EDTF not support this or is parsing logic incorrect?
        # assert EDTFDateFormat().parse("XXXX-05-03") != Undate(month=5, day=4)

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            assert EDTFDateFormat().parse("1991-5") == Undate(1991, 5)

    def test_parse_range(self):
        assert EDTFDateFormat().parse("1800/1900") == UndateInterval(
            Undate(1800), Undate(1900)
        )

    def test_to_string(self):
        assert EDTFDateFormat().to_string(Undate(900)) == "0900"
        assert EDTFDateFormat().to_string(Undate("80")) == "0080"
        assert EDTFDateFormat().to_string(Undate(33)) == "0033"
        assert EDTFDateFormat().to_string(Undate("20XX")) == "20XX"
        assert EDTFDateFormat().to_string(Undate(17000002)) == "Y17000002"

        assert EDTFDateFormat().to_string(Undate(1991, 6)) == "1991-06"
        assert EDTFDateFormat().to_string(Undate(1991, 5, 3)) == "1991-05-03"

        assert EDTFDateFormat().to_string(Undate(1991, "0X")) == "1991-0X"
        assert EDTFDateFormat().to_string(Undate(1991, None, 3)) == "1991-XX-03"

        # TODO: override missing digit and confirm replacement
