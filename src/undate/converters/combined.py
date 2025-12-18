from lark import Lark
from lark.visitors import Transformer, merge_transformers

from undate.converters import GRAMMAR_FILE_PATH
from undate.converters.edtf.transformer import EDTFTransformer
from undate.converters.calendars.hebrew.transformer import HebrewDateTransformer
from undate.converters.calendars.hijri.transformer import HijriDateTransformer


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
    hijri=HijriDateTransformer(),
)


# open based on filename so we can specify relative import path based on grammar file
parser = Lark.open(
    str(GRAMMAR_FILE_PATH / "combined.lark"), rel_to=__file__, strict=True
)
