from lark import Transformer, Tree
from convertdate import islamic

from undate.undate import Undate, UndateInterval


class HijriDateTransformer(Transformer):
    """Transform a Hijri date parse tree and return an Undate or
    UndateInterval."""

    def hijri_date(self, items):
        parts = {}
        for child in items:
            if child.data in ["year", "month", "day"]:
                # in each case we expect one integer value;
                # anonymous tokens convert to their value and cast as int
                value = int(child.children[0])
                parts[str(child.data)] = value

        # if we have a year, month, day, convert to a single undate
        if len(parts.values()) == 3:
            # convertdate returns a tuple of year, month day
            converted_date = islamic.to_gregorian(**parts)
            return Undate(*converted_date)

        # if not, convert to a date range
        start, end = islamic_to_gregorian_interval(**parts)
        # TODO: should we add optional date precision / interval length
        # to UndateInteravl ?
        return UndateInterval(Undate(*start), Undate(*end))

    # this does nothing
    # def year(self, items):
    #     return Tree(data="year", children=[items[0]])

    def month(self, items):
        # month has a nested tree for the rule and the value
        # the name of the rule (month_1, month_2, etc) gives us the
        # number of the month needed for converting the date
        tree = items[0]
        month_n = tree.data.split("_")[-1]
        return Tree(data="month", children=[month_n])


MIN_MONTH, MIN_DAY = 1, 1
MAX_MONTH = 12


def islamic_to_gregorian_interval(year, month=None, day=None):
    start = (year, month or MIN_MONTH, day or MIN_DAY)
    end_month = month or MAX_MONTH
    # islamic calendar converter has month_length
    if day is None:
        day = islamic.month_length(year, end_month)
    end = (year, month or MAX_MONTH, day)
    return (islamic.to_gregorian(*start), islamic.to_gregorian(*end))
