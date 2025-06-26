# undate overview

![undate](_static/undate_logo.png)

**undate** is a python library for working with uncertain or partially known dates.

> [!WARNING]
> This is beta software and is not yet feature complete! Use with caution and give us feedback.
> Currently `undate` supports parsing and formatting dates in ISO8601, some
> portions of EDTF (Extended Date Time Format), and parsing and conversion for dates in Hebrew Anno Mundi and Islamic Hijri calendars.

_Undate was initially created as part of a [DH-Tech](https://dh-tech.github.io/) hackathon in November 2022._

---

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11068867.svg)](https://doi.org/10.5281/zenodo.11068867)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/undate-python/badge/?version=latest)](https://undate-python.readthedocs.io/en/latest/?badge=latest)
[![unit tests](https://github.com/dh-tech/undate-python/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/dh-tech/undate-python/actions/workflows/unit_tests.yml)
[![codecov](https://codecov.io/gh/dh-tech/undate-python/branch/main/graph/badge.svg?token=GE7HZE8C9D)](https://codecov.io/gh/dh-tech/undate-python)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](CONTRIBUTORS.md)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

Read [Contributors](CONTRIBUTORS.md) for detailed contribution information.

## Installation

_Recommended_: use pip to install the latest published version from PyPI:

```console
pip install undate
```

To install a development version or specific tag or branch, you can install from GitHub.
Use the `@name` notation to specify the branch or tag; e.g., to install development version:

```console
pip install git+https://github.com/dh-tech/undate-python@develop#egg=undate
```

## Example Usage

Often humanities and cultural data include imprecise or uncertain
temporal information. We want to store that information but also work
with it in a structured way, not just treat it as text for display.
Different projects may need to work with or convert between different
date formats or even different calendars.

An `undate.Undate` is analogous to python’s builtin `datetime.date`
object, but with support for varying degrees of precision and unknown
information. You can initialize an `Undate` with either strings or
numbers for whichever parts of the date are known or partially known.
An `Undate` can take an optional label.

```python
from undate import Undate

november7 = Undate(2000, 11, 7)
november = Undate(2000, 11)
year2k = Undate(2000)
november7_some_year = Undate(month=11, day=7)

partially_known_year = Undate("19XX")
partially_known_month = Undate(2022, "1X")

easter1916 = Undate(1916, 4, 23, label="Easter 1916")
```

You can convert an `Undate` to string using a date formatter (current default is ISO8601):

```python
>>> [str(d) for d in [november7, november, year2k, november7_some_year]]
['2000-11-07', '2000-11', '2000', '--11-07']
```

If enough information is known, an `Undate` object can report on its duration:

```python
>>> december = Undate(2000, 12)
>>> feb_leapyear = Undate(2024, 2)
>>> feb_regularyear = Undate(2023, 2)
>>> for d in [november7, november, december, year2k, november7_some_year, feb_regularyear, feb_leapyear]:
...    print(f"{d}  - duration in days: {d.duration().days}")
...
2000-11-07  - duration in days: 1
2000-11  - duration in days: 30
2000-12  - duration in days: 31
2000  - duration in days: 366
--11-07  - duration in days: 1
2023-02  - duration in days: 28
2024-02  - duration in days: 29
```

If enough of the date is known and the precision supports it, you can
check if one date falls within another date:

```python
>>> november7 = Undate(2000, 11, 7)
>>> november2000 = Undate(2000, 11)
>>> year2k = Undate(2000)
>>> ad100 = Undate(100)
>>> november7 in november
True
>>> november2000 in year2k
True
>>> november7 in year2k
True
>>> november2000 in ad100
False
>>> november7 in ad100
False
```

For dates that are imprecise or partially known, `undate` calculates
earliest and latest possible dates for comparison purposes so you can
sort dates and compare with equals, greater than, and less than. You
can also compare with python `datetime.date` objects.

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

When dates cannot be compared due to ambiguity or precision, comparison
methods raise a `NotImplementedError`.

```python
>>> november_2020 = Undate(2020, 11)
>>> november7_2020 > november_2020
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/rkoeser/workarea/github/undate-python/src/undate/undate.py", line 262, in __gt__
    return not (self < other or self == other)
  File "/Users/rkoeser/workarea/github/undate-python/src/undate/undate.py", line 245, in __lt__
    raise NotImplementedError(
NotImplementedError: Can't compare when one date falls within the other
```

An `UndateInterval` is a date range between two `Undate` objects.
Intervals can be open-ended, allow for optional labels, and can
calculate duration if enough information is known. `UndateIntervals`
are inclusive (i.e., a closed interval), and include both the earliest
and latest date as part of the range.

```python
>>> from undate import UndateInterval
>>> UndateInterval(Undate(1900), Undate(2000))
<UndateInterval 1900/2000>
>>> UndateInterval(Undate(1801), Undate(1900), label="19th century")
>>> UndateInterval(Undate(1801), Undate(1900), label="19th century").duration().days
36524
<UndateInterval '19th century' (1801/1900)>
>>> UndateInterval(Undate(1901), Undate(2000), label="20th century")
<UndateInterval '20th century' (1901/2000)>
>>> UndateInterval(latest=Undate(2000))  # before 2000
<UndateInterval ../2000>
>>> UndateInterval(Undate(1900))  # after 1900
<UndateInterval 1900/>
>>> UndateInterval(Undate(1900), Undate(2000), label="19th century").duration().days
36890
>>> UndateInterval(Undate(2000, 1, 1), Undate(2000, 1,31)).duration().days
31
```

You can initialize `Undate` or `UndateInterval` objects by parsing a
date string with a specific converter, and you can also output an
`Undate` object in those formats. Currently available converters
are "ISO8601" and "EDTF" and supported calendars.

```python
>>> from undate import Undate
>>> Undate.parse("2002", "ISO8601")
<Undate 2002>
>>> Undate.parse("2002-05", "EDTF")
<Undate 2002-05>
>>> Undate.parse("--05-03", "ISO8601")
<Undate --05-03>
>>> Undate.parse("--05-03", "ISO8601").format("EDTF")
'XXXX-05-03'
>>> Undate.parse("1800/1900")
<UndateInterval 1800/1900>
```

### Calendars

All `Undate` objects are calendar aware, and date converters include
support for parsing and working with dates from other calendars. The
Gregorian calendar is used by default; currently `undate` supports the
Islamic Hijri calendar and the Hebrew Anno Mundi calendar based on
calendar conversion logic implemented in the
[convertdate](https://convertdate.readthedocs.io/en/latest/) package.

Dates are stored with the year, month, day and appropriate precision for
the original calendar; internally, earliest and latest dates are
calculated in Gregorian / Proleptic Gregorian calendar for standardized
comparison across dates from different calendars.

```python
>>> from undate import Undate
>>> tammuz4816 = Undate.parse("26 Tammuz 4816", "Hebrew")
>>> tammuz4816
<Undate '26 Tammuz 4816 Anno Mundi' 4816-04-26 (Hebrew)>
>>> rajab495 = Undate.parse("Rajab 495", "Islamic")
>>> rajab495
<Undate 'Rajab 495 Hijrī' 0495-07 (Islamic)>
>>> y2k = Undate.parse("2001", "EDTF")
>>> y2k
<Undate 2001 (Gregorian)>
>>> [str(d.earliest) for d in [rajab495, tammuz4816, y2k]]
['1102-04-28', '1056-07-17', '2001-01-01']
>>> [str(d.precision) for d in [rajab495, tammuz4816, y2k]]
['MONTH', 'DAY', 'YEAR']
>>> sorted([rajab495, tammuz4816, y2k])
[<Undate '26 Tammuz 4816 Anno Mundi' 4816-04-26 (Hebrew)>, <Undate 'Rajab 495 Hijrī' 0495-07 (Islamic)>, <Undate 2001 (Gregorian)>]
```

---

For more examples, refer to the code notebooks included in the[examples]
(https://github.com/dh-tech/undate-python/tree/main/examples/) in this
repository.

## Documentation

Project documentation is [available on ReadTheDocs](https://undate-python.readthedocs.io/en/latest/).

For instructions on setting up for local development, see [Developer Notes](DEVELOPER_NOTES.md).

## License

This software is licensed under the [Apache 2.0 License](LICENSE.md).
