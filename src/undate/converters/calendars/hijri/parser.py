import pathlib

from lark import Lark

grammar_path = pathlib.Path(__file__).parent / "hijri.lark"

with open(grammar_path) as grammar:
    # NOTE: LALR parser is faster but can't be used to ambiguity between years and dates
    hijri_parser = Lark(grammar.read(), start="hijri_date", strict=True)
