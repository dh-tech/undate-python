"""
**Experimental** combined parser. Supports EDTF, Hebrew, and Hijri
where dates are unambiguous. (Year-only dates are parsed as EDTF in
Gregorian calendar.)
"""

from typing import Union

from lark import Lark
from lark.exceptions import UnexpectedCharacters
from lark.visitors import Transformer, merge_transformers

from undate import Undate, UndateInterval
from undate.converters import BaseDateConverter, GRAMMAR_FILE_PATH
from undate.converters.edtf.transformer import EDTFTransformer
from undate.converters.calendars.hebrew.transformer import HebrewDateTransformer
from undate.converters.calendars.islamic.transformer import IslamicDateTransformer


class CombinedDateTransformer(Transformer):
    def start(self, children):
        # trigger the transformer for the appropriate part of the grammar
        return children


# NOTE: currently year-only dates in combined parser are interpreted as
# EDTF and use Gregorian calendar.
# In future, we could refine by adding calendar names & abbreviations
# to the parser in order to recognize years from other calendars.

combined_transformer = merge_transformers(
    CombinedDateTransformer(),
    edtf=EDTFTransformer(),
    hebrew=HebrewDateTransformer(),
    islamic=IslamicDateTransformer(),
)


# open based on filename so we can specify relative import path based on grammar file
parser = Lark.open(
    str(GRAMMAR_FILE_PATH / "combined.lark"), rel_to=__file__, strict=True
)


class OmnibusDateConverter(BaseDateConverter):
    """
    Combination parser that aggregates existing parser grammars.
    Currently supports EDTF, Hebrew, and Hijri  where dates are unambiguous.
    (Year-only dates are parsed as EDTF in Gregorian calendar.)

    Does not support serialization.

    Example usage::

        Undate.parse("Tammuz 4816", "omnibus")

    """

    #: converter name: omnibus
    name: str = "omnibus"

    def __init__(self):
        self.transformer = combined_transformer

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        """
        Parse a string in a supported format and return an :class:`~undate.undate.Undate`
        or :class:`~undate.undate.UndateInterval`.
        """
        if not value:
            raise ValueError("Parsing empty/unset string is not supported")

        # parse the input string, then transform to undate object
        try:
            parsetree = parser.parse(value)
            # transform returns a list; we want the first item in the list
            return self.transformer.transform(parsetree)[0]
        except UnexpectedCharacters:
            raise ValueError(
                "Parsing failed: '%s' is not in a recognized date format" % value
            )

    def to_string(self, undate: Union[Undate, UndateInterval]) -> str:
        "Not supported by this converter. Will raise :class:`ValueError`"
        raise ValueError("Omnibus converter does not support serialization")
