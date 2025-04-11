from lark import Transformer, Tree

from undate import Undate, Calendar


class IslamicUndate(Undate):
    """Undate convience subclass; sets default calendar to Islamic."""

    calendar = Calendar.ISLAMIC


class IslamicDateTransformer(Transformer):
    """Transform an Islamic Hijri date parse tree and return an Undate or
    UndateInterval."""

    def islamic_date(self, items):
        parts = {}
        for child in items:
            if child.data in ["year", "month", "day"]:
                # in each case we expect one integer value;
                # anonymous tokens convert to their value and cast as int
                value = int(child.children[0])
                parts[str(child.data)] = value

        # initialize and return an undate with islamic year, month, day and
        # islamic calendar
        return IslamicUndate(**parts)

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
