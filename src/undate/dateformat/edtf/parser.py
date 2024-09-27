import os.path

from lark import Lark

grammar_path = os.path.join(os.path.dirname(__file__), "edtf.lark")

with open(grammar_path) as grammar:
    edtf_parser = Lark(grammar.read(), start="edtf")


# testcases = [
#     "1984",
#     "1984-05",
#     "1984-12",
#     "1001-03-30",
#     "1000/2000",
#     "1000-01/2000-05-01",
#     # level 1
#     "Y170000002",
#     "2001-21",  # spring 2001
#     # qualifiers
#     "1984?",
#     "2004-06~",
#     "2004-06-11%",
#     # unspecified digits from right
#     "201X",
#     "20XX",
#     "2004-XX",
#     "1985-04-XX",
#     "1985-XX-XX",
#     # open ended intervals
#     "1985-04-12/..",
#     "1985-04/..",
#     "../1985-04-12",
#     "/1985-04-12",
#     "1984-13",
# ]

# for testcase in testcases:
#     print(f"\n{testcase}")
#     tree = edtf_parser.parse(testcase)
#     print(tree.pretty())


# error_cases = ["1984-13", "Y1702"]
