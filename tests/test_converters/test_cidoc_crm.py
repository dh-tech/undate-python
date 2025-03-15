import types

import rdflib

from undate.converters import cidoc_crm


# TODO: maybe copy full example ismi data as fixture
# so we have examples of all types to test against

sample_data = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# prefix for date and calendar type URIs
@prefix datetype: <http://content.mpiwg-berlin.mpg.de/ns/ismi/type/date/> .
@prefix calendartype: <http://content.mpiwg-berlin.mpg.de/ns/ismi/type/calendar/> .
# prefix for sample data
@prefix : <http://content.mpiwg-berlin.mpg.de/ns/ismi/> .

# day-precision date in islamic calendar
:date1 a crm:E52_Time-Span ;
  crm:P2_has_type datetype:day ;
  crm:P82_at_some_time_within "1495-12-11"^^xsd:date ;
  crm:P3_has_note "day-precision date in islamic calendar" ;
  crm:P1_is_identified_by :date1-label .
:date1-label a crm:E41_Appellation ;
  crm:P2_has_type calendartype:islamic ;
  rdfs:label "901 Rabīʿ I 14 (islamic)" .
"""

ISMI_NS = rdflib.Namespace("http://content.mpiwg-berlin.mpg.de/ns/ismi/")
DATE1_URI = rdflib.URIRef("http://content.mpiwg-berlin.mpg.de/ns/ismi/date1")


class TestTimeSpan:
    def test_properties(self):
        # initialize a time span rdflib.resource for date1 in the sample data
        g = rdflib.Graph()
        g.parse(data=sample_data)

        time_span = cidoc_crm.TimeSpan(g, DATE1_URI)
        assert time_span.type == cidoc_crm.ISMI_DATE_TYPE.day
        assert time_span.label == rdflib.term.Literal("901 Rabīʿ I 14 (islamic)")
        assert time_span.calendar == cidoc_crm.ISMI_CALENDAR_TYPE.islamic
        assert time_span.at_some_time_within == rdflib.term.Literal(
            "1495-12-11", datatype=rdflib.XSD.date
        )
        assert time_span.note == rdflib.term.Literal(
            "day-precision date in islamic calendar"
        )

    def test_time_spans_from_graph(self):
        g = rdflib.Graph()
        g.parse(data=sample_data)

        time_spans = cidoc_crm.TimeSpan.time_spans_from_graph(g)
        assert isinstance(time_spans, types.GeneratorType)
        time_spans = list(time_spans)
        assert len(time_spans) == 1
        assert isinstance(time_spans[0], cidoc_crm.TimeSpan)
        assert time_spans[0].identifier == DATE1_URI
