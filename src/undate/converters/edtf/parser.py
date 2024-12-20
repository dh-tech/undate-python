import pathlib

from lark import Lark

grammar_path = pathlib.Path(__file__).parent / "edtf.lark"

with open(grammar_path) as grammar:
    edtf_parser = Lark(grammar.read(), start="edtf")
