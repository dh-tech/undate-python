from lark import Token, Transformer, Tree

from undate import Undate, UndateInterval


class EDTFTransformer(Transformer):
    """transform edtf parse tree and return Undate or UndateInterval"""

    INT = int

    def timeinterval(self, items):
        # transformed result from parser should be two undate objects;
        # combine into an interval
        return UndateInterval(*items)

    def date(self, items):
        parts = {}
        for child in items:
            if child.data in ["year", "month", "day"]:
                # in each case we expect one value;
                # anonymous tokens convert to their value
                value = child.children[0]
                # convert to integer when possible; otherwise pass as string
                try:
                    value = int(value)
                except ValueError:
                    value = str(value)
                parts[str(child.data)] = value

        return Undate(**parts)

    def extended_interval(self, items):
        # same as level 1 time interval, except one item may be None
        # for an open-ended range
        return self.timeinterval(items)

    def unknown_date(self, token):
        # unknown date for interval should be passed in as None
        return None

    def get_values(self, items):
        # get a list of values from tokens; recurses to get subtree tokens
        values = []
        for i in items:
            if isinstance(i, Token):
                values.append(str(i))
            if isinstance(i, Tree):
                values.extend(self.get_values(i.children))
        return values

    def year_unspecified(self, items):
        # combine parts (numeric & unknown) into a single string
        value = "".join(self.get_values(items))
        return Tree(data="year", children=[value])

    def month_unspecified(self, items):
        # combine multiple parts into a single string
        value = "".join(self.get_values(items))
        return Tree(data="month", children=[value])

    def day_unspecified(self, items):
        # combine multiple parts into a single string
        value = "".join(self.get_values(items))
        return Tree(data="day", children=[value])

    def date_level1(self, items):
        return self.date(items)

    # year (including negative years) use default transformation

    def year_fivedigitsplus(self, items):
        # strip off the leading Y and convert to integer
        token = items[0]
        year = int(token.value.lstrip("Y"))
        return Tree(data="year", children=[year])
