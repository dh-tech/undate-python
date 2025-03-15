import rdflib


#: CIDOC-CRM namespace
CIDOC_CRM = rdflib.Namespace("http://www.cidoc-crm.org/cidoc-crm/")
ISMI_DATE_TYPE = rdflib.Namespace(
    "http://content.mpiwg-berlin.mpg.de/ns/ismi/type/date/"
)
ISMI_CALENDAR_TYPE = rdflib.Namespace(
    "http://content.mpiwg-berlin.mpg.de/ns/ismi/type/calendar/"
)


class TimeSpan(rdflib.resource.Resource):
    @property
    def identified_by(self):
        return self.value(CIDOC_CRM.P1_is_identified_by)

    @property
    def label(self):
        return self.identified_by.value(rdflib.RDFS.label)

    @property
    def calendar(self):
        return self.identified_by.value(CIDOC_CRM.P2_has_type).identifier

    @property
    def type(self):
        return self.value(CIDOC_CRM.P2_has_type).identifier

    @property
    def at_some_time_within(self):
        return self.value(CIDOC_CRM.P82_at_some_time_within)

    @property
    def begin_of_the_begin(self):
        return self.value(CIDOC_CRM.P82a_begin_of_the_begin)

    @property
    def end_of_the_end(self):
        return self.value(CIDOC_CRM.P82b_end_of_the_end)

    @property
    def note(self):
        return self.value(CIDOC_CRM.P3_has_note)

    def to_undate(self):
        # day precision
        if self.type == ISMI_DATE_TYPE.day:
            return self.at_some_time_within.toPython()

    @classmethod
    def time_spans_from_graph(cls, graph):
        """Class method to find and return all CIDOC-CRM timespans in an rdflib graph
        and yield them as :class:`TimeSpan` resource objects."""
        for timespan_uri in graph.subjects(
            predicate=rdflib.RDF.type, object=CIDOC_CRM["E52_Time-Span"]
        ):
            yield cls(graph, timespan_uri)


#  # crm:P2_has_type datetype:day ;
#   crm:P82_at_some_time_within "1495-12-11"^^xsd:date ;
#   crm:P3_has_note "day-precision date in islamic calendar" ;
#   crm:P1_is_identified_by :date1-label .
# :date1-label a crm:E41_Appellation ;
#   crm:P2_has_type calendartype:islamic ;
#   rdfs:label "901 Rabīʿ I 14 (islamic)" .
