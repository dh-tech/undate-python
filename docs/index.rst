undate
======

.. image:: _static/undate_logo.svg
   :alt: undate
   :width: 350px
   :class: only-light

.. image:: _static/undate_logo_dark.svg
   :alt: undate
   :width: 350px
   :class: only-dark

**undate** is a Python library for working with uncertain or partially known dates.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.11068867.svg
   :target: https://doi.org/10.5281/zenodo.11068867
.. image:: https://img.shields.io/badge/License-Apache_2.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
.. image:: https://readthedocs.org/projects/undate-python/badge/?version=latest
   :target: https://undate-python.readthedocs.io/en/latest/?badge=latest
.. image:: https://github.com/dh-tech/undate-python/actions/workflows/unit_tests.yml/badge.svg
   :target: https://github.com/dh-tech/undate-python/actions/workflows/unit_tests.yml
.. image:: https://codecov.io/gh/dh-tech/undate-python/branch/main/graph/badge.svg?token=GE7HZE8C9D
   :target: https://codecov.io/gh/dh-tech/undate-python

.. note::
   This is beta software; it is still in development and not fully feature complete.
   If you use it, please let us know and share your feedback.

``undate`` supports parsing, formatting, and reasoning with dates in varying
precision and calendars. Dates with different precision and from different original
calendars can be used together. Supported formats include:

- portions of EDTF (Extended Date Time Format)
- ISO8601
- parsing and calendar conversion for dates in Hebrew Anno Mundi and Islamic Hijri calendars
- Gregorian dates with full or abbreviated month names in any order for multiple languages
  (English, Spanish, French, German, Kinyarwanda, Ganda, Tigrinya)
- Christian liturgical dates (fixed holidays and movable feasts)

For unambiguous dates, there is an experimental omnibus parser which combines all available parsers.

For more about the origin and goals of ``undate``, read our 2025 software paper:

   Rebecca Sutton Koeser, Julia Damerow, Robert Casties, and Cole Crawford.
   "`Undate: Humanistic Dates for Computation <https://doi.org/10.1017/chr.2025.10006>`_."
   *Computational Humanities Research*, August 5, 2025.

Quick Start
-----------

An ``Undate`` is analogous to Python's ``datetime.date``, but with support for
varying precision and unknown information:

.. code-block:: python

   from undate import Undate, UndateInterval

   november = Undate(2000, 11)        # year and month known
   year2k = Undate(2000)              # year only
   partially_known = Undate("19XX")   # partially unknown year

   print([str(d) for d in [november, year2k, partially_known]])
   # ['2000-11', '2000', '19XX']

Dates can be parsed from multiple formats and calendars, sorted, and compared
even when precision differs. See :doc:`example_usage` for interactive examples.

Installation
------------

Install the latest published version from PyPI:

.. code-block:: console

   pip install undate

To install a development version or specific branch:

.. code-block:: console

   pip install git+https://github.com/dh-tech/undate-python@develop#egg=undate

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   example_usage
   undate/index
   CONTRIBUTING
   DEVELOPER_NOTES
   CONTRIBUTORS
   LICENSE

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
