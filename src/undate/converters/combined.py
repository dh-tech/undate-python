from lark import Lark
from lark.visitors import Transformer, merge_transformers

from undate.converters.edtf.transformer import EDTFTransformer
from undate.converters.calendars.hebrew.transformer import HebrewDateTransformer
from undate.converters.calendars.hijri.transformer import HijriDateTransformer


class CombinedDateTransformer(Transformer):
    def start(self, children):
        return children


# NOTE: we can't support year-only dates in combined parser because calendar
# is ambiguous, unless we want to add a calendar indicator

combined_transformer = merge_transformers(
    CombinedDateTransformer(),
    edtf__edtf=EDTFTransformer(),  # nested prefix due to nested import path
    hebrew=HebrewDateTransformer(),
    hijri=HijriDateTransformer(),
)


parser = Lark.open("combined.lark", rel_to=__file__, strict=True)
