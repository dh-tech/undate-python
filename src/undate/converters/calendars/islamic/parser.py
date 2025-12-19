from lark import Lark

from undate.converters import GRAMMAR_FILE_PATH

grammar_path = GRAMMAR_FILE_PATH / "islamic.lark"

with open(grammar_path) as grammar:
    # NOTE: LALR parser is faster but can't be used due to ambiguity between years and days
    islamic_parser = Lark(grammar.read(), start="islamic_date", strict=True)
