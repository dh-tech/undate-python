from undate.undate import Undate, UndateInterval


def test_single_date():
    assert str(Undate(2022, 11, 7)) == "2022-11-07"
    assert str(Undate(2022, 11)) == "2022-11"
    assert str(Undate(2022)) == "2022"
    assert str(Undate(month=11, day=7)) == "--11-07"


def test_range():
    # 2022 - 2023
    assert str(UndateInterval(Undate(2022), Undate(2023))) == "2022/2023"
    # 2022 - 2023-05
    assert str(UndateInterval(Undate(2022), Undate(2023, 5))) == "2022/2023-05"
    # 2022-11-01 to 2022-11-07
    assert (
        str(UndateInterval(Undate(2022, 11, 1), Undate(2023, 11, 7)))
        == "2022-11-01/2023-11-07"
    )


def test_open_range():
    # 900 -
    assert str(UndateInterval(Undate(900))) == "900/"
    # - 1900
    assert str(UndateInterval(latest=Undate(1900))) == "../1900"
    # - 1900-12
    assert str(UndateInterval(latest=Undate(1900, 12))) == "../1900-12"
