from lark import Lark

from undate.converters import GRAMMAR_FILE_PATH

grammar_path = GRAMMAR_FILE_PATH / "hijri.lark"

with open(grammar_path) as grammar:
    # NOTE: LALR parser is faster but can't be used to ambiguity between years and dates
    hijri_parser = Lark(grammar.read(), start="hijri_date", strict=True)
