from lark import Transformer, Tree

from undate import Undate, Calendar


class HebrewUndate(Undate):
    """Undate convience subclass; sets default calendar to Hebrew."""

    calendar = Calendar.HEBREW


class HebrewDateTransformer(Transformer):
    """Transform a Hebrew date parse tree and return an Undate or
    UndateInterval."""

    calendar = Calendar.HEBREW

    def hebrew_date(self, items):
        parts = {}
        for child in items:
            if child.data in ["year", "month", "day"]:
                # in each case we expect one integer value;
                # anonymous tokens convert to their value and cast as int
                value = int(child.children[0])
                parts[str(child.data)] = value

        # initialize and return an undate with year, month, day and
        # configured calendar (hebrew by default)
        return Undate(**parts, calendar=self.calendar)

    # year translation is not needed since we want a tree with name year
    # this is equivalent to a no-op
    # def year(self, items):
    #     return Tree(data="year", children=[items[0]])

    def month(self, items):
        # month has a nested tree for the rule and the value
        # the name of the rule (month_1, month_2, etc) gives us the
        # number of the month needed for converting the date
        tree = items[0]
        month_n = tree.data.split("_")[-1]
        return Tree(data="month", children=[month_n])
