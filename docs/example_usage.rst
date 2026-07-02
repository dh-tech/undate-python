
Example Usage
--------------

Often humanities and cultural data include imprecise or uncertain temporal information. We want to store that information but also work with it in a structured way, not just treat it as text for display. Different projects may need to work with or convert between different date formats or even different calendars.

An ``undate.Undate`` is analogous to python’s builtin ``datetime.date`` object, but with support for varying degrees of precision and unknown information. You can initialize an ``Undate`` with either strings or numbers for whichever parts of the date are known or partially known. An ``Undate`` can take an optional label.

.. note::
   These are examples are written to run live in the browser with `Pyodide <https://pyodide.org/>`_ and `sphinx-pyodide <https://github.com/rlskoeser/sphinx-pyodide>`_.

.. pyodide::
   :packages: ./wheels/PyMeeus-0.5.12-py3-none-any.whl,./wheels/undate-0.8.0.dev0-py3-none-any.whl

   from undate import __version__

   print(f"Running undate v{__version__}")


.. pyodide::
    from undate import Undate

    november7 = Undate(2000, 11, 7)
    november = Undate(2000, 11)
    year2k = Undate(2000)
    november7_some_year = Undate(month=11, day=7)

    partially_known_year = Undate("19XX")
    partially_known_month = Undate(2022, "1X")

    easter1916 = Undate(1916, 4, 23, label="Easter 1916")

You can convert an ``Undate`` to string using a date formatter (current default is ISO8601):


.. pyodide::
   print([str(d) for d in [november7, november, year2k, november7_some_year]])


If enough information is known, an ``Undate`` object can report on its duration:

.. pyodide::
   december = Undate(2000, 12)
   feb_leapyear = Undate(2024, 2)
   feb_regularyear = Undate(2023, 2)

   example_dates = [
        november7, november, december, year2k,
        november7_some_year, feb_regularyear, feb_leapyear
    ]
   for d in example_dates:
       print(f"{d!s:<10}  duration in days: {d.duration().days:>2}")

If enough of the date is known and the precision supports it, you can
check if one date falls within another date:

.. pyodide::
   november7 = Undate(2000, 11, 7)
   november2000 = Undate(2000, 11)
   year2k = Undate(2000)
   ad100 = Undate(100)
   november7 in november

   yes_no = {True: "✅", False: "❌"}
   for range in [november2000, year2k, ad100]:
      print(f"{november7!s:>10} within {range!s:<10}? {yes_no[november7 in range]}")
      if november2000 != range:  # don't test against itself
        print(f"{november2000!s:>10} within {range!s:<10}? {yes_no[november2000 in range]}")


For dates that are imprecise or partially known, ``undate`` calculates
earliest and latest possible dates for comparison purposes so you can
sort dates ...

.. pyodide::
   november7_2020 = Undate(2020, 11, 7)
   november_2001 = Undate(2001, 11)
   year2k = Undate(2000)
   ad100 = Undate(100)
   for date in sorted([november7_2020, november_2001, year2k, ad100]):
      # print the date in ISO/EDTF format along with the python representation
      print(f"{date!s:>10} : {repr(date)}")


You can also compare with equals, greater than, and less than. You
can also compare with python ``datetime.date`` objects.

.. pyodide::
   from datetime import date

   jan2001 = date(2001, 1, 1)

   print(f"{november7_2020!s:>10} before {november_2001!s:<10} ? {yes_no[november7_2020 > november_2001]}")
   print(f"{year2k!s:>10} before {ad100!s:<10} ? {yes_no[year2k > ad100]}")
   print(f"{year2k!s:>10}  after {jan2001} ? {yes_no[year2k > jan2001]}")


When dates cannot be compared due to ambiguity or precision, comparison
methods raise a ``NotImplementedError``.

.. pyodide::
   november_2020 = Undate(2020, 11)
   november7_2020 > november_2020
