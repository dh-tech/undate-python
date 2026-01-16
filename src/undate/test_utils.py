"""
Utility decorators for unit tests that require django to be installed,
or not installed. To use, import into unit test and apply
to test method or class:

```python

from undate.test_utils import skipif_no_django, skipif_django

@skipif_no_django
def test_django_functionality():
    ....
```

"""

import pytest

try:
    import django
except ImportError:
    django = None

skipif_no_django = pytest.mark.skipif(django is None, reason="requires Django")

skipif_django = pytest.mark.skipif(django, reason="requires no Django")
