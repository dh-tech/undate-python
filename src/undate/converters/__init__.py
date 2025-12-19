"""
Converter classes add support for parsing and serializing dates
in a variety of formats. A subset of these are calendar converters
(:mod:`undate.converters.calendar`), which means they support both parsing
and conversion from an alternate calendar to a common Gregorian
for comparison across dates.

To parse a date with a supported converter, use the ``Undate`` class method
:meth:`~undate.undate.Undate.parse` and specify the date as a string
with the desired format or calendar, e.g.

.. code-block::

  Undate.parse("2001-05", "EDTF")
  Undate.parse("7 Heshvan 5425", "Hebrew")

For converters that support it, you can also serialize a date in a specified
format with ``Undate`` class method :meth:`~undate.undate.Undate.format`:

.. code-block::

  Undate.parse("Rabīʿ ath-Thānī 343", "Islamic").format("EDTF")


"""

from undate.converters.base import BaseDateConverter, GRAMMAR_FILE_PATH

__all__ = ["BaseDateConverter", "GRAMMAR_FILE_PATH"]
