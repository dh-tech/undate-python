import pathlib

from lark import Lark

grammar_path = pathlib.Path(__file__).parent / "islamic.lark"

with open(grammar_path) as grammar:
    # NOTE: LALR parser is faster but can't be used due to ambiguity between years and days
    islamic_parser = Lark(grammar.read(), start="islamic_date", strict=True)
