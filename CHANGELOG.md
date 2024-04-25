# Change Log

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
