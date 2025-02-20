from undate import Undate, UndateInterval
from undate.converters.iso8601 import ISO8601DateFormat


class TestISO8601DateFormat:
    def test_parse_singledate(self):
        assert ISO8601DateFormat().parse("2002") == Undate(2002)
        assert ISO8601DateFormat().parse("1991-05") == Undate(1991, 5)
        assert ISO8601DateFormat().parse("1991-05-03") == Undate(1991, 5, 3)
        # missing year but month/day known
        assert ISO8601DateFormat().parse("--05-03") == Undate(month=5, day=3)

    def test_parse_singledate_unequal(self):
        assert ISO8601DateFormat().parse("2002") != Undate(2003)
        assert ISO8601DateFormat().parse("1991-05") != Undate(1991, 6)
        assert ISO8601DateFormat().parse("1991-05-03") != Undate(1991, 5, 4)
        # missing year but month/day known
        assert ISO8601DateFormat().parse("--05-03") != Undate(month=5, day=4)

    def test_parse_invalid(self):
        # allow but warn?
        assert ISO8601DateFormat().parse("1991-5") == Undate(1991, 5)

    def test_parse_range(self):
        assert ISO8601DateFormat().parse("1800/1900") == UndateInterval(
            Undate(1800), Undate(1900)
        )

    def test_to_string(self):
        # NOTE: iso8601 to_string currently tested more thoroughly
        # in undate str tests; may want to move those tests here
        assert ISO8601DateFormat().to_string(Undate(900)) == "0900"
        assert ISO8601DateFormat().to_string(Undate(33)) == "0033"
