import pathlib

from lark import Lark

grammar_path = pathlib.Path(__file__).parent / "hijri.lark"

with open(grammar_path) as grammar:
    # NOTE: LALR parser is faster but requires assumption of 3+ digit years
    hijri_parser = Lark(grammar.read(), start="date", parser="lalr")
