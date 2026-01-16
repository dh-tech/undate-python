from lark import Lark

from undate.converters import GRAMMAR_FILE_PATH

grammar_path = GRAMMAR_FILE_PATH / "edtf.lark"

with open(grammar_path) as grammar:
    edtf_parser = Lark(grammar.read(), start="edtf")
