import pytest
from undate.converters.edtf import EDTFDateConverter
from undate import Undate, UndateInterval


class TestEDTFDateConverter:
    def test_parse_singledate(self):
        assert EDTFDateConverter().parse("2002") == Undate(2002)
        assert EDTFDateConverter().parse("1991-05") == Undate(1991, 5)
        assert EDTFDateConverter().parse("1991-05-03") == Undate(1991, 5, 3)
        # unknown dates are not strictly equal, but string comparison should match
        assert str(EDTFDateConverter().parse("201X")) == str(Undate("201X"))
        assert str(EDTFDateConverter().parse("2004-XX")) == str(Undate(2004, "XX"))
        assert str(EDTFDateConverter().parse("XXXX-05-03")) == Undate(
            month=5, day=3
        ).format("EDTF")

    def test_parse_singledate_error(self):
        # missing year but month/day known - this format should cause an error
        with pytest.raises(ValueError):
            EDTFDateConverter().parse("--05-03")

    def test_parse_singledate_unequal(self):
        assert EDTFDateConverter().parse("2002") != Undate(2003)
        assert EDTFDateConverter().parse("1991-05") != Undate(1991, 6)
        assert EDTFDateConverter().parse("1991-05-03") != Undate(1991, 5, 4)
        # missing year but month/day known
        # - does EDTF not support this or is parsing logic incorrect?
        # assert EDTFDateConverter().parse("XXXX-05-03") != Undate(month=5, day=4)

    invalid_inputs = [
        "1991-13",  # invalid month
        "1991-12-32",  # invalid day
        "199A",  # invalid year format
        "",  # empty string
        None,  # None input
    ]

    @pytest.mark.parametrize("invalid_input", invalid_inputs)
    def test_parse_invalid(self, invalid_input):
        with pytest.raises(ValueError):
            EDTFDateConverter().parse(invalid_input)

    def test_parse_range(self):
        assert EDTFDateConverter().parse("1800/1900") == UndateInterval(
            Undate(1800), Undate(1900)
        )

    def test_to_string(self):
        assert EDTFDateConverter().to_string(Undate(900)) == "0900"
        assert EDTFDateConverter().to_string(Undate("80")) == "0080"
        assert EDTFDateConverter().to_string(Undate(33)) == "0033"
        assert EDTFDateConverter().to_string(Undate("20XX")) == "20XX"
        assert EDTFDateConverter().to_string(Undate(17000002)) == "Y17000002"
        assert EDTFDateConverter().to_string(Undate(-17000002)) == "Y-17000002"

        assert EDTFDateConverter().to_string(Undate(1991, 6)) == "1991-06"
        assert EDTFDateConverter().to_string(Undate(1991, 5, 3)) == "1991-05-03"

        assert EDTFDateConverter().to_string(Undate(1991, "0X")) == "1991-0X"
        assert EDTFDateConverter().to_string(Undate(1991, None, 3)) == "1991-XX-03"
        assert EDTFDateConverter().to_string(Undate(-1984)) == "-1984"

        # if converter can't generate a string for the date,
        # it should return a value error
        # empty_undate = Undate()   # undate with no date information no longer supported
        # empty_undate.precision = DatePrecision.DECADE
        # with pytest.raises(ValueError):
        #     EDTFDateConverter().to_string(empty_undate)
        # TODO: override missing digit and confirm replacement
