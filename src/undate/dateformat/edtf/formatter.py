from typing import Dict, List, Union

from lark.exceptions import UnexpectedCharacters

from undate.undate import Undate, UndateInterval
from undate.dateformat.base import BaseDateFormat
from undate.dateformat.edtf.parser import edtf_parser
from undate.dateformat.edtf.transformer import EDTFTransformer


EDTF_UNSPECIFIED_DIGIT: str = "X"


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

    def to_string(self, undate: Undate) -> str:
        # get year, month day - could be str, int, or None
        year, month, day = [
            # replace undate missing digit with EDTF missing digit
            # (currently the same but not guaranteed to be)
            val.replace(Undate.MISSING_DIGIT, EDTF_UNSPECIFIED_DIGIT)
            if isinstance(val, str)
            else val
            for val in (undate.year, undate.month, undate.day)
        ]
        parts = []

        if year:
            value = year  # None
            if isinstance(year, int):
                value = f"{year:04d}"
            # elif isinstance(year, str):
            # parts.append(year)  # TODO: ensure min 4 chars

            # handle years with more than 4 digits
            if value and len(value) > 4:
                value = f"Y{value}"
                # maybe here pad with zeroes if too short?
            if value:
                parts.append(value)
        if month:
            if isinstance(month, int):
                parts.append(f"{month:02d}")
            elif isinstance(month, str):
                parts.append(month)  # TODO ensure 2 chars
        if day:
            # TODO; not if month is None
            if isinstance(day, int):
                parts.append(f"{day:02d}")
            elif isinstance(day, str):
                parts.append(day)  # TODO ensure 2 chars

        return "-".join(parts)

    # TODO: can we leverage the parser for this?
    # turn into a tree and use reconstruct?
    # Tree for just a year looks like:
    # Tree(Token('RULE', 'date'), [Tree(Token('RULE', 'year'), [Token('INT', '2002')])])
    # ... let's not do that
