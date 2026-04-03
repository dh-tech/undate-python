try:
    import django
except ImportError:
    django = None

from undate.test_utils import skipif_no_django, skipif_django


@skipif_no_django
def test_django():
    assert django is not None


@skipif_django
def test_no_django():
    assert django is None
