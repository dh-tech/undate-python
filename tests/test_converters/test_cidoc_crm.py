import pathlib
import types

import pytest
import rdflib

from undate import Undate, DatePrecision
from undate.converters import cidoc_crm


# TODO: move or copy example ismi data to test for use as a fixture
ISMI_DATA_PATH = (
    pathlib.Path(__file__)
    / ".."
    / ".."
    / ".."
    / "examples"
    / "use-cases"
    / "ismi"
    / "data"
    / "ismi-crm-date-samples.ttl"
)

DATE1_URI = rdflib.URIRef("http://content.mpiwg-berlin.mpg.de/ns/ismi/date1")


@pytest.fixture
def ismi_data():
    g = rdflib.Graph()
    g.parse(ISMI_DATA_PATH)
    return g


class TestTimeSpan:
    def test_properties(self, ismi_data):
        # initialize a time span rdflib.resource for date1 in the sample data
        # TODO: convert to a fixture
        # g = rdflib.Graph()
        # g.parse(ISMI_DATA_PATH)
        # g.parse(data=sample_data)

        time_span = cidoc_crm.TimeSpan(ismi_data, DATE1_URI)
        assert time_span.type == cidoc_crm.ISMI_DATE_TYPE.day
        assert time_span.label == rdflib.term.Literal("901 Rabīʿ I 14 (islamic)")
        assert time_span.calendar == cidoc_crm.ISMI_CALENDAR_TYPE.islamic
        assert time_span.at_some_time_within == rdflib.term.Literal(
            "1495-12-11", datatype=rdflib.XSD.date
        )
        assert time_span.note == rdflib.term.Literal(
            "day-precision date in islamic calendar"
        )

    def test_time_spans_from_graph(self, ismi_data):
        time_spans = cidoc_crm.TimeSpan.time_spans_from_graph(ismi_data)
        assert isinstance(time_spans, types.GeneratorType)
        time_spans = list(time_spans)
        # fixture has 9 time spans
        assert len(time_spans) == 9
        assert isinstance(time_spans[0], cidoc_crm.TimeSpan)
        assert time_spans[0].identifier == DATE1_URI

    def test_to_undate(self, ismi_data):
        time_span = cidoc_crm.TimeSpan(ismi_data, DATE1_URI)
        ts_undate = time_span.to_undate()
        assert isinstance(ts_undate, Undate)
        # 1495-12-11"^^xsd:date ;
        assert ts_undate.year == "1495"
        assert ts_undate.month == "12"
        assert ts_undate.day == "11"
        assert ts_undate.precision == DatePrecision.DAY

        # if we round trip the date it comes out the same
        assert ts_undate.format("ISO8601") == str(time_span.at_some_time_within)
