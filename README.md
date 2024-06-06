# undate-python

**undate** is a python library for working with uncertain or partially known dates.

It was initially created as part of a [DH-Tech](https://dh-tech.github.io/) hackathon in November 2022.

---

⚠️ **WARNING:** this is pre-alpha software and is **NOT** feature complete! Use with caution. ⚠️

---

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11068867.svg)](https://doi.org/10.5281/zenodo.11068867)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/undate-python/badge/?version=latest)](https://undate-python.readthedocs.io/en/latest/?badge=latest)
[![unit tests](https://github.com/dh-tech/undate-python/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/dh-tech/undate-python/actions/workflows/unit_tests.yml)
[![codecov](https://codecov.io/gh/dh-tech/undate-python/branch/main/graph/badge.svg?token=GE7HZE8C9D)](https://codecov.io/gh/dh-tech/undate-python)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Read [Contributors](CONTRIBUTORS.md) for detailed contribution information.

## Example Usage

Often humanities and cultural data includes imprecise or uncertain temporal information. We want to store that information but also work with it in a structured way, not just treat it as text for display.  Different projects may need to work with or convert between different date formats or even different calendars.

An `undate.Undate` is analogous to python's builtin `datetime.date` object, but with support for varying degrees of precision and unknown information.  You can initialize an undate with either strings or numbers for whichever parts of the date are known or partially known.  An `Undate` can take an optional label.
```python
from undate.undate import Undate

november7 = Undate(2000, 11, 7)
november = Undate(2000, 11)
year2k = Undate(2000)
unknown_year = Undate(month=11, day=7)

partially_known_year = Undate("19XX")
partially_known_month = Undate(2022, "1X")

easter1916 = Undate(1916, 4, 23, label="Easter 1916")
```

If enough of the date is known and the precision supports it, you can check if one date falls within another date:
```python
>>> november7 = Undate(2000, 11, 7)
>>> november = Undate(2000, 11)
>>> year2k = Undate(2000)
>>> ad100 = Undate(100)
>>> november7 in november
True
>>> november in year2k
True
>>> november7 in year2k
True
>>> november in ad100
False
>>> november7 in ad100
False
```

For dates that are imprecise are partially known, `undate` calculates earliest and latest possible dates for comparison purposes so you can sort dates and compare with greater than or less than. You can also compare with python `datetime.date` objects

```python
>>> november7_2020 = Undate(2020, 11, 7)
>>> november_2001 = Undate(2001, 11)
>>> year2k = Undate(2000)
>>> ad100 = Undate(100)
>>> sorted([november7_2020, november_2001, year2k, ad100])
[<Undate 0100>, <Undate 2000>, <Undate 2001-11>, <Undate 2020-11-07>]
>>> november7_2020 > november_2001
True
>>> year2k < ad100
False
>>> from datetime import date
>>> year2k > date(2001, 1, 1)
False
```

When dates cannot be compared due to ambiguity or precision, comparison methods raise a `NotImplementedError`.




## Documentation

Project documentation is available on ReadTheDocs https://undate-python.readthedocs.io/en/latest/

For instructions on setting up for local development, see [Developer Notes](DEVELOPER_NOTES.md).

## License

This software is licensed under the [Apache 2.0 License](LICENSE.md).
