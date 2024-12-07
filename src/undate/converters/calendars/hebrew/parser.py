import pathlib

from lark import Lark

grammar_path = pathlib.Path(__file__).parent / "hebrew.lark"

with open(grammar_path) as grammar:
    # NOTE: LALR parser is faster but can't be used to ambiguity between years and dates
    hebrew_parser = Lark(grammar.read(), start="hebrew_date", strict=True)
