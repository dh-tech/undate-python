from lark import Lark

from undate.converters import GRAMMAR_FILE_PATH

grammar_path = GRAMMAR_FILE_PATH / "edtf.lark"

with grammar_path.open() as grammar:
    edtf_parser = Lark(grammar.read(), start="edtf")
