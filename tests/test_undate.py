import pytest

from undate.undate import Undate, UndateInterval

class TestUndate:
    def test_str(self):
        assert str(Undate(2022, 11, 7)) == "2022-11-07"
        assert str(Undate(2022, 11)) == "2022-11"
        assert str(Undate(2022)) == "2022"
        assert str(Undate(month=11, day=7)) == "--11-07"


    def test_invalid_date(self):
        # invalid month should raise an error
        with pytest.raises(ValueError):
            Undate(1990, 22)

    def test_eq(self):
        assert Undate(2022) == Undate(2022)
        assert Undate(2022, 10) == Undate(2022, 10)
        assert Undate(2022, 10, 1) == Undate(2022, 10, 1)
        assert Undate(month=2, day=7) == Undate(month=2, day=7)

    def test_not_eq(self):
        assert Undate(2022) != Undate(2023)
        assert Undate(2022, 10) != Undate(2022, 11)
        assert Undate(2022, 10, 1) != Undate(2022, 10, 2)
        assert Undate(month=2, day=7) != Undate(month=2, day=8)
        assert Undate(2022) != Undate(2022, 10)
        assert Undate(2022, 10) != Undate(2022, 10, 1)


class TestUndateInterval:
    def test_str(self):
        # 2022 - 2023
        assert str(UndateInterval(Undate(2022), Undate(2023))) == "2022/2023"
        # 2022 - 2023-05
        assert str(UndateInterval(Undate(2022), Undate(2023, 5))) == "2022/2023-05"
        # 2022-11-01 to 2022-11-07
        assert (
            str(UndateInterval(Undate(2022, 11, 1), Undate(2023, 11, 7)))
            == "2022-11-01/2023-11-07"
        )


    def test_str_open_range(self):
        # 900 -
        assert str(UndateInterval(Undate(900))) == "900/"
        # - 1900
        assert str(UndateInterval(latest=Undate(1900))) == "../1900"
        # - 1900-12
        assert str(UndateInterval(latest=Undate(1900, 12))) == "../1900-12"

    def test_eq(self):
        assert UndateInterval(Undate(2022), Undate(2023)) == UndateInterval(Undate(2022), Undate(2023))
        assert UndateInterval(Undate(2022), Undate(2023, 5)) == UndateInterval(Undate(2022), Undate(2023, 5))
        assert UndateInterval(Undate(2022, 5)) == UndateInterval(Undate(2022, 5))

    def test_not_eq(self):
        assert UndateInterval(Undate(2022), Undate(2023)) != UndateInterval(Undate(2022), Undate(2024))
        assert UndateInterval(Undate(2022), Undate(2023, 5)) != UndateInterval(Undate(2022), Undate(2023, 6))
        assert UndateInterval(Undate(2022), Undate(2023, 5)) != UndateInterval(Undate(2022), Undate(2023))
        assert UndateInterval(Undate(2022, 5)) != UndateInterval(Undate(2022, 6))
