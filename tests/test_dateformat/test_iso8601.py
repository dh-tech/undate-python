from undate.dateformat.iso8601 import ISO8601DateFormat
from undate.undate import Undate, UndateInterval


def test_parse_singledate():
    assert ISO8601DateFormat().parse("2002") == Undate(2002)
    assert ISO8601DateFormat().parse("1991-05") == Undate(1991, 5)
    assert ISO8601DateFormat().parse("1991-05-03") == Undate(1991, 5, 3)
    # missing year but month/day known
    assert ISO8601DateFormat().parse("--05-03") == Undate(month=5, day=3)


def test_parse_invalid():
    # allow but warn?
    assert ISO8601DateFormat().parse("1991-5") == Undate(1991, 5)


def test_parse_range():
    assert ISO8601DateFormat().parse("1800/1900") == UndateInterval(
        Undate(1800), Undate(1900)
    )
