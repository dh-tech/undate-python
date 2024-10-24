from typing import Dict, List, Union, Optional

from lark import Tree, Token
from lark.exceptions import UnexpectedCharacters
from lark.reconstruct import Reconstructor

from undate.date import DatePrecision
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

    def _convert_missing_digits(
        self, value: Optional[str], old_missing_digit: str
    ) -> Optional[str]:
        if value:
            return value.replace(old_missing_digit, EDTF_UNSPECIFIED_DIGIT)
        return None

    def to_string(self, undate: Union[Undate, UndateInterval]) -> str:
        if isinstance(undate, Undate):
            return self._undate_to_string(undate)
        elif isinstance(undate, UndateInterval):
            # NOTE: what is the difference between an open interval and unknown start/end?
            # spec distinguishes between these, open is ".." but unknown is ""
            start = self._undate_to_string(undate.earliest) if undate.earliest else ".."
            end = self._undate_to_string(undate.latest) if undate.latest else ".."
            return f"{start}/{end}"

    def _undate_to_string(self, undate: Undate) -> str:
        # in theory it's possible to use the parser and reconstruct using a tree,
        # but that seems much more complicated and would be harder to read
        parts = []

        if undate.precision >= DatePrecision.YEAR:
            year = self._convert_missing_digits(undate.year, undate.MISSING_DIGIT)
            # years with more than 4 digits should be prefixed with Y
            negative_year = ""
            if year.startswith("-"):
                negative_year = "-"
                year = year[1:]
            if year and len(year) > 4:
                year = f"{negative_year}Y{year}"
            # TODO: handle uncertain / approximate
            parts.append(year or EDTF_UNSPECIFIED_DIGIT * 4)

        # beware when we add more date precisions,
        # week-level won't necessarily mean we know the month

        if undate.precision >= DatePrecision.MONTH:
            # TODO: handle uncertain / approximate
            parts.append(
                self._convert_missing_digits(undate.month, undate.MISSING_DIGIT)
                or EDTF_UNSPECIFIED_DIGIT * 2
            )

        if undate.precision >= DatePrecision.DAY:
            # TODO: handle uncertain / approximate
            parts.append(
                self._convert_missing_digits(undate.day, undate.MISSING_DIGIT)
                or EDTF_UNSPECIFIED_DIGIT * 2
            )

        if parts:
            return "-".join(parts)

        # how can we have an empty string? probably shouldn't get here
        return ""
