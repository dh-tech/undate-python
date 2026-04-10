"""
Holiday date Converter: parse Christian liturgical dates and convert to Gregorian.
"""

import datetime

from lark import Lark, Transformer, Tree, Token
from lark.exceptions import UnexpectedInput

from convertdate import holidays
from undate import Undate, Calendar
from undate.converters.base import BaseDateConverter, GRAMMAR_FILE_PATH

# To add a new holiday:
#   1. Add a name and pattern to holidays.lark grammar file
#   2. Include the in appropriate section (fixed or movable)
#   3. Add an entry to FIXED_HOLIDAYS or MOVEABLE_FEASTS; must match grammar terminal name


# holidays that fall on the same date every year
# key must match grammar term; value is tuple of numeric month, day
FIXED_HOLIDAYS = {
    "EPIPHANY": (1, 6),  # January 6
    "CANDLEMASS": (2, 2),  # February 2; 40th day & end of epiphany
    "ST_PATRICKS": (3, 17),  # March 17
    "ALL_FOOLS": (4, 1),  # All / April fools day, April 1
    "ST_CYPRIANS": (9, 16),  # St. Cyprian's Feast day: September 16
}

# holidays that shift depending on the year; value is days relative to Easter
MOVEABLE_FEASTS = {
    "EASTER": 0,  # Easter, no offset
    "HOLY_SATURDAY": -1,  # day before Easter
    "EASTER_MONDAY": 1,  # day after Easter
    "ASCENSION": 39,  # fortieth day of Easter
    "PENTECOST": 49,  # 7 weeks after Easter
    "WHIT_MONDAY": 50,  # Monday after Pentecost
    "TRINITY": 56,  # first Sunday after Pentecost
    "ASH_WEDNESDAY": -46,  # Wednesday of the 7th week before Easter
    "SHROVE_TUESDAY": -47,  # day before Ash Wednesday
}


parser = Lark.open(
    str(GRAMMAR_FILE_PATH / "holidays.lark"), rel_to=__file__, start="holiday_date"
)


class HolidayTransformer(Transformer):
    calendar = Calendar.GREGORIAN

    def year(self, items):
        value = "".join([str(i) for i in items])
        return Token("year", value)
        # return Tree(data="year", children=[value])

    def movable_feast(self, items):
        # moveable feast day can't be calculated without the year,
        # so pass through
        return items[0]

    def fixed_date(self, items):
        item = items[0]
        holiday_name = item.type.split("__")[-1]
        # token_type = item.type
        # token type is holiday fixed-date name; use to determine month/day
        month, day = FIXED_HOLIDAYS.get(holiday_name)
        return Tree("fixed_date", [Token("month", month), Token("day", day)])
        # for key in FIXED_HOLIDAYS:
        #     if token_type == key or token_type == f"holidays__{key}":
        #         month, day = FIXED_HOLIDAYS[key]
        #         return Tree("fixed_date", [Token("month", month), Token("day", day)])
        # raise ValueError(f"Unknown fixed holiday: {item.type}")

    def holiday_date(self, items):
        parts = self._get_date_parts(items)
        return Undate(**parts)

    def _get_date_parts(self, items) -> dict[str, int | str]:
        # recursive method to take parsed tokens and trees and generate
        # a dictionary of year, month, day for initializing an undate object
        # handles nested tree with month/day (for fixed date holidays)
        # and includes movable feast logic, after year is determined.

        parts = {}
        date_parts = ["year", "month", "day"]
        movable_feast = None
        for child in items:
            field = value = None
            # if this is a token, get type and value
            if isinstance(child, Token):
                # month/day from fixed date holiday
                if child.type in date_parts:
                    field = child.type
                    value = child.value
                # check for movable feast terminal
                elif child.type in MOVEABLE_FEASTS:
                    # collect but don't handle until we know the year
                    movable_feast = child.type
                # handle namespaced token type; happens when called from combined grammar
                elif (
                    "__" in child.type and child.type.split("__")[-1] in MOVEABLE_FEASTS
                ):
                    # collect but don't handle until we know the year
                    movable_feast = child.type.split("__")[-1]

            # if a tree, check for type and anonymous token
            if isinstance(child, Tree):
                # if tree is a date field (i.e., year), get the value
                if child.data in date_parts:
                    field = child.data
                    # in this case we expect one value;
                    # convert anonymous token to value
                    value = child.children[0]
                # if tree has children, recurse to get date parts
                elif child.children:
                    parts.update(self._get_date_parts(child.children))

            # if date fields were found, add to dictionary
            if field and value:
                # currently all date parts are integer only
                parts[str(field)] = int(value)

        # if date is a movable feast, calculate relative to Easter based on the year
        if movable_feast is not None:
            offset = MOVEABLE_FEASTS[movable_feast]
            holiday_date = datetime.date(
                *holidays.easter(parts["year"])
            ) + datetime.timedelta(days=offset)
            parts.update({"month": holiday_date.month, "day": holiday_date.day})

        return parts


class HolidayDateConverter(BaseDateConverter):
    """
    Converter for Christian liturgical dates.

    Supports fixed-date holidays (Epiphany, Candlemass, etc.) and
    Easter-relative moveable feasts (Easter, Ash Wednesday, Pentecost, etc.).

    Example usage::

        Undate.parse("Easter 1942", "holidays")
        Undate.parse("Ash Wednesday 1942", "holidays")
        Undate.parse("Epiphany", "holidays")

    Does not support serialization.
    """

    name = "holidays"

    def __init__(self):
        self.transformer = HolidayTransformer()

    def parse(self, value: str) -> Undate:
        if not value:
            raise ValueError("Parsing empty string is not supported")

        try:
            parsetree = parser.parse(value)
            # transform the parse tree into an undate or undate interval
            undate_obj = self.transformer.transform(parsetree)
            # set the input holiday text as a label on the undate object
            undate_obj.label = value
            return undate_obj
        except UnexpectedInput as err:
            raise ValueError(f"Could not parse '{value}' as a holiday date") from err

    def to_string(self, undate: Undate) -> str:
        raise ValueError("Holiday converter does not support serialization")
