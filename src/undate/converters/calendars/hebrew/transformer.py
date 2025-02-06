from lark import Transformer, Tree

from undate.undate import Undate, Calendar


class HebrewUndate(Undate):
    """Undate convience subclass; sets default calendar to Hebrew."""

    calendar = Calendar.HEBREW


class HebrewDateTransformer(Transformer):
    """Transform a Hebrew date parse tree and return an Undate or
    UndateInterval."""

    def hebrew_date(self, items):
        parts = {}
        for child in items:
            if child.data in ["year", "month", "day"]:
                # in each case we expect one integer value;
                # anonymous tokens convert to their value and cast as int
                value = int(child.children[0])
                parts[str(child.data)] = value

        # initialize and return an undate with year, month, day in
        # hebrew calendar
        return HebrewUndate(**parts)

    def year(self, items):
        # combine multiple parts into a single string
        value = "".join([str(i) for i in items])
        return Tree(data="year", children=[value])

    def month(self, items):
        # month has a nested tree for the rule and the value
        # the name of the rule (month_1, month_2, etc) gives us the
        # number of the month needed for converting the date
        tree = items[0]
        month_n = tree.data.split("_")[-1]
        return Tree(data="month", children=[month_n])
