# Change Log

## [0.8] - 2026-07-30

- **Documentation update**: examples are now rendered with [sphinx-pyodide](https://rlskoeser.github.io/sphinx-pyodide/)

  - Readme now provides a quick start and a link to usage examples in the documentation
  - Usage examples provide better coverage of current functionality

- Now tested against python 3.14
- Updates to pre-commit hook versions, GitHub Action versions
- Updates to comply with new version of ruff linter

## [0.7] - 2026-05-07

- Add parsing to Gregorian date converter; supports month names (full or abbreviated)
  in English, French, German, Spanish, Kinyarwanda, Ganda, and Tigrinya
- Add support for parsing Christian liturgical dates (fixed holidays and movable feasts)
- Include Gregorian dates and holidays in omnibus parser
- Updates to pyproject.toml, pre-commit hooks, ruff rules, dependabot configuration

## [0.6.1] - 2026-03-30

- Updated Read the Docs build to use Ubuntu 24.04

## [0.6] - 2026-01-16

- Experimental omnibus date converter + parser (EDTF, Hebrew, Hijri)
  - Reorganized Lark grammar files to a common location
- Improved documentation for converter class parsing and serialization
- Update action versions in GitHub Workflows (contributed by @rettinghaus)

## [0.5.2] - 2025-10-02

- repr for Undate, UndateInterval, and UnDelta now produce fully-qualified, constructor-style strings with deterministic field ordering.
- Added Undate.unknown_year property and is_unknown() method to check for fully-unknown year/month/day.
- bugfix: comparisons (eq, gt, lt) and contains (in) now return False when year is unknown
- bugfix: month durations for non-Gregorian dates now returns an integer when month length is known

## [0.5.1] - 2025-07-22

- Correct license identifier in CITATION.cff so it is valid

## [0.5] - 2025-06-26

- New `UnDelta` and `UnInt` classes for uncertain durations
  - `Undate.duration` now returns either a `Timedelta` or an `UnDelta` if the duration is ambiguous
- New properties `possible_years` and `representative_years` on `Undate` class, used for calculating durations for uncertain years and months
- New `weekday` method on class `undate.date.Date`
- Calendar converter improvements:
  - Calendar converter classes can optional provide minimum and maximum years for uncertain dates
  - New calendar methods `days_in_year` and `representative_years`
  - Hebrew date parser now allows for week days, along with additional month variants
  - Preliminary Seleucide calendar converter class, based on Hebrew calendar with a year offset
  - New method `as_calendar` on `Undate` class, to set calendar without doing any conversion
- Readme examples have been improved and extended
- New example notebook testing Hebrew, Islamic, and Seleucid date parsing and conversion with Princeton Geniza Project data
- bugfix: duration for uncertain years previously returned the duration from earliest to latest possible dates in range; now returns an `UnDelta` with the possible durations for the possible years in the given calendar

## [0.4] - 2025-04-11

- Undate is now Calendar aware / Calendar explicit; default is Gregorian
  - New `BaseCalendarConverter` class, with additional methods required for calendar converters
  - `HebrewDateConverter`: Parsing and calendar conversion for Hebrew/Anno Mundi
  - `IslamicDateConverter`: Parsing and calendar conversion for Islamic/Hijri
  - `GregorianDateConverter`: basic Gregorian calendar logic
  - `undate.Calendar` class to track `Undate` object calendar, and match with calendar converters
- BaseDateConverter class now includes nested/descendant subclasses when looking
  for available converters
- `Undate.to_undate` method to convert supported date objects to `Undate` (`datetime.date`, `datetime.datetime`, and internal `undate.date.Date` class)
- `UndateInterval` improvements
  - Can be initialized with `Undate` objects or any type supported by `Undate.to_undate`
  - New method for contains (`in`), to determine if another interval or date is contained by an interval
  - New method `intersection` to determine the overlap between two `UndateInterval` objects
- EDTF parser : fixed day parsing for some unsupported cases
- Dropped support for Python 3.9
- Reorganized examples folder to avoid unnecessary nesting
  - ISMI data has been updated from older JSON data to examples in RDF (turtle)

## [0.3.1] - 2024-11-18

Update readthedocs config for current installation

## [0.3] - 2024-11-18

- Updated to use numpy `datetime64` to support a greater range of years beyond the 4-digit years supported by python's builtin `datetime.date`
  - Custom `Date` and `Timedelta` objects as shims to make numpy datetime64 and timedelta64 act more like python `datetime` objects
- Renamed formatters to converters for more flexibility / scope
- Support using different converters with new `format` and `parse` methods on `Undate`
- Improved EDTF support:
  - Support 5+ digit years with leading Y (thanks to numpy.datetime64)
  - Jupyter notebook demonstrating / validating EDTF support
    - Full support for Level 0 Date and Time Interval (no Date and Time support)
    - Level 1:
      - Letter-prefixed calendar year
      - Unspecified digit from the right
      - Partial support for extended interval
    - Level 2: unspecified digit anywhere in the date
- Improved readme with example usage and disclaimers about current functionality
- Improved documentation for adding new converters
- Improved documentation for branching guidelines in contributing
- Restructured sphinx documentation and added more code documentation
- Added a project logo
- Switch from black to ruff for pre-commit formatting

### numpy impact

Performance differences seem to be negligible, but it does increase payload size. The virtualenv for installing version 0.2 was 14MB; when installing the newer version with numpy, the virtualenv is 46MB (the numpy folder in site packages is 31MB on its own).

## [0.2] - 2024-04-25

- Undate and UndateInterval now include an optional label for named dates or time periods
- Support partially known dates with missing digits (e.g. 1991-1?-10)
- Rich comparison checks for Undate
  - improved equality check; now supports comparing Undate object with day precision to datetime.date
  - implementations and tests for comparison, sorting and contains (`>`, `<`, `>=`, `<=`, and `in`)
- static method to initialize an Undate object from a datetime.date (used for comparisons)
- Example Jupyter notebook comparing Undate duration calculation against
  dates and durations in the [Shakespeare and Company Project](https://shakespeareandco.princeton.edu/) [events dataset](https://doi.org/10.34770/nz90-ym25)
- Preliminary support for parsing Extended Date Time Format (EDTF) level 0 and some of level 1 and transforming into Undate objects
- Dropped support for python 3.8; added python 3.12
- Python type improvements and preliminary type checking with mypy

## 0.1

Pre-alpha version with preliminary `Undate` and `UndateInterval` classes
with support for ISO8601 date format

[0.2]: https://github.com/dh-tech/undate-python/releases/tag/0.2
[0.3]: https://github.com/dh-tech/undate-python/releases/tag/0.3
[0.3.1]: https://github.com/dh-tech/undate-python/releases/tag/0.3.1
[0.4]: https://github.com/dh-tech/undate-python/releases/tag/0.4
[0.5]: https://github.com/dh-tech/undate-python/releases/tag/0.5
[0.5.1]: https://github.com/dh-tech/undate-python/releases/tag/0.5.1
[0.5.2]: https://github.com/dh-tech/undate-python/releases/tag/0.5.2
[0.6]: https://github.com/dh-tech/undate-python/releases/tag/0.6
[0.6.1]: https://github.com/dh-tech/undate-python/releases/tag/0.6.1
[0.7]: https://github.com/dh-tech/undate-python/releases/tag/0.7
[0.8]: https://github.com/dh-tech/undate-python/releases/tag/0.8
