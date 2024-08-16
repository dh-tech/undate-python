from typing import Dict, List, Union

from lark.exceptions import UnexpectedCharacters

from undate.undate import Undate, UndateInterval
from undate.dateformat.base import BaseDateFormat
from undate.dateformat.edtf.parser import edtf_parser
from undate.dateformat.edtf.transformer import EDTFTransformer


class EDTFDateFormat(BaseDateFormat):
    name: str = "EDTF"

    def __init__(self):
        self.transformer = EDTFTransformer()

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        # parse the input string, then transform to undate object
        try:
            parsetree = edtf_parser.parse(value)
            return self.transformer.transform(parsetree)
        except UnexpectedCharacters as err:
            raise ValueError("Parsing failed due to UnexpectedCharacters: %s" % err)

    # def to_string(self, undate: Undate) -> str:
    # TODO: how do we leverage the parser for this?
