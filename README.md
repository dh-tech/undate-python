# undate overview

![undate](_static/undate_logo.png)

**undate** is a python library for working with uncertain or partially known dates.

> [!NOTE]
> This is beta software; it is still in development and not fully feature complete. If you use it, please let us know and share your feedback.

Currently `undate` supports parsing, formatting, and reasoning with dates in varying precision and calendars; dates with different precision and from different original calendars can be used together. Supported formats include:

- portions of **EDTF** (Extended Date Time Format)
- **ISO8601**
- parsing and calendar conversion for dates in **Hebrew Anno Mundi** and **Islamic Hijri** calendars
- **Gregorian** dates with full or abbreviated month names in any order for multiple languages (English, Spanish, French, German, Kinyarwanda, Ganda, Tigrinya)
- **Christian liturgical** dates (fixed holidays and movable feasts)

For unambiguous dates, there is an experimental omnibus parser which combines all available dates (bare years are currently assumed to be Gregorian calendar).

For more about the origin and goals of `undate`, read our 2025 software paper:

> Rebecca Sutton Koeser, Julia Damerow, Robert Casties, and Cole Crawford. "[Undate: Humanistic Dates for Computation](https://doi.org/10.1017/chr.2025.10006)." _Computational Humanities Research_, August 5, 2025.

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

## Quick Start

An `Undate` is analogous to python’s `datetime.date` but supports varying degrees of precision and unknown information. Initialize with strings or numbers for whichever parts of the date are known:

```python
from undate import Undate, UndateInterval

november7 = Undate(2000, 11, 7)
november = Undate(2000, 11)
year2k = Undate(2000)
partially_known_year = Undate("19XX")

[str(d) for d in [november7, november, year2k, partially_known_year]]
# [‘2000-11-07’, ‘2000-11’, ‘2000’, ‘19XX’]

Undate.parse("Rajab 495", "Islamic")
# undate.Undate(year=495, month=7, label="Rajab 495 Islamic", calendar="Islamic")
```

For full examples including duration, comparison, intervals, parsing, and calendar support, see the [interactive documentation](https://undate-python.readthedocs.io/en/latest/).

## Documentation

Project documentation is [available on ReadTheDocs](https://undate-python.readthedocs.io/en/latest/).

For instructions on setting up for local development, see [Developer Notes](DEVELOPER_NOTES.md).

See [Contributors](CONTRIBUTORS.md) for more detailed information about contributors.

## Publications & Presentations

- Rebecca Sutton Koeser, Julia Damerow, Robert Casties, and Cole Crawford. “[Undate: Humanistic Dates for Computation](https://doi.org/10.1017/chr.2025.10006).” Software paper published in _Computational Humanities Research_, August 5, 2025.
- Rebecca Sutton Koeser. “[Undate: Computing with Uncertain and Partially-Unknown Dates](https://doi.org/10.5281/zenodo.17253974).” Computational notebook presented at USRSE’25. October 6, 2025.
- Rebecca Sutton Koeser. “[Undate in Action](https://rlskoeser.github.io/undate-in-action/).” Presentation at [Digital Humanities Tech Symposium](https://dh-tech.github.io/2025/06/04/digital-humanities-tech-symposium-agenda/), DH2025. July 14, 2025.
- Rebecca Sutton Koeser. 2025. “[Undate in Action](https://doi.org/10.63744/SFtXXpIE4ERh).” In Digital Humanities Tech Symposium 2025—Anthology of Computers and the Humanities, edited by Julia Damerow and Rebecca Sutton Koeser, vol. 2.
- Rebecca Sutton Koeser. [Join me for a DHTech hackathon? It’s an un-date!](https://dh-tech.github.io/blog/2023/02/09/hackathon-undate/) DHTech, February 9, 2023.

## Related Projects

- ISO8601 date support and dates with unknown years, including duration, adapted from [Shakespeare and Company Project](https://shakespeareandco.princeton.edu/) ([codebase](https://github.com/Princeton-CDH/mep-django))
- Parsing and calendar conversion for Hebrew Anno Mundi and Islamic Hijri calendars adapted from [Princeton Geniza Project (PGP)](https://geniza.princeton.edu/) ([codebase](https://github.com/Princeton-CDH/geniza/)); improved and verified with data and logic from the [Islamic Scientific Manuscripts Initiative (ISMI)](https://ismi.mpiwg-berlin.mpg.de/)
- Parsing for dates in African languages inspired by work on and partially checked against data from [MasakhaNER](https://github.com/masakhane-io/masakhane-ner)
- Parsing and calendar conversion for Christian liturgical holidays adapted from work on [Hale/Eliot Letters project](https://cdh.princeton.edu/projects/haleeliot-letters/)

## License

This software is licensed under the [Apache 2.0 License](LICENSE.md).
