from typing import Optional, Union

from lark.exceptions import UnexpectedCharacters

from undate import Undate, UndateInterval
from undate.converters.base import BaseDateConverter
from undate.converters.edtf.parser import edtf_parser
from undate.converters.edtf.transformer import EDTFTransformer
from undate.date import DatePrecision


#: character for unspecified digits
EDTF_UNSPECIFIED_DIGIT: str = "X"


class EDTFDateConverter(BaseDateConverter):
    """
    Converter for Extended Date/Time Format (EDTF).

    Supports parsing and serializing dates and date ranges in EDTF format.
    Does not support all of EDTF, and only supports dates and not times.
    """

    #: converter name: EDTF
    name: str = "EDTF"

    def __init__(self):
        self.transformer = EDTFTransformer()

    def parse(self, value: str) -> Union[Undate, UndateInterval]:
        """
        Parse a string in a supported EDTF date or date interval format and
        return an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval`.
        """
        if not value:
            raise ValueError("Parsing empty/unset string is not supported")

        # parse the input string, then transform to undate object
        try:
            parsetree = edtf_parser.parse(value)
            return self.transformer.transform(parsetree)
        except UnexpectedCharacters:
            raise ValueError(
                "Parsing failed: '%s' is not a supported EDTF date format" % value
            )

    def _convert_missing_digits(
        self, value: Optional[str], old_missing_digit: str
    ) -> Optional[str]:
        if value:
            return value.replace(old_missing_digit, EDTF_UNSPECIFIED_DIGIT)
        return None

    def to_string(self, undate: Union[Undate, UndateInterval]) -> str:
        """
        Convert an :class:`~undate.undate.Undate` or
        :class:`~undate.undate.UndateInterval` to EDTF format.
        """
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
            # (don't count minus sign when checking digits)
            if year and len(year.lstrip("-")) > 4:
                year = f"Y{year}"

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
        raise ValueError("Failed to generate an EDTF string from %r", undate)
