from lark import Lark

from undate.converters import GRAMMAR_FILE_PATH

grammar_path = GRAMMAR_FILE_PATH / "islamic.lark"

# open based on filename to allow relative imports based on grammar file
islamic_parser = Lark.open(
    str(grammar_path), rel_to=__file__, start="islamic_date", strict=True
)
