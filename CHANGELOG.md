# Change Log

## 0.3.1

Update readthedocs config for current installation

## 0.3

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

Performance differences seem to be negligible, but it does increase payload size.  The virtualenv for installing version 0.2 was 14MB; when installing the newer version with numpy, the virtualenv is 46MB (the numpy folder in site packages is 31MB on its own).

## 0.2

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
