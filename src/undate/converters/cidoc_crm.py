import rdflib

from undate import Undate

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
        # by default, rdflib resource value method will return another Resource
        return self.value(CIDOC_CRM.P1_is_identified_by)

    @property
    def label(self):
        # for ISMI records, label is under the crm identifier/appelation
        # other examples have it directly under the time span as RDFS.label
        return self.identified_by.value(rdflib.RDFS.label)

    @property
    def calendar(self):
        # for ISMI records, calendar type is associated with identifier
        return self.identified_by.value(CIDOC_CRM.P2_has_type).identifier

    @property
    def type(self):
        # CIDOC-CRM type
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
        # convert to an undate object, if possible
        match self.type:
            # day precision
            case ISMI_DATE_TYPE.day:
                # at_some_time_within is xsd:date; use toPython method
                # to convert to datetime.date and then convert to undate
                return Undate.to_undate(self.at_some_time_within.toPython())
                # TODO: should we set label before returning?

                # for ISMI dates, could we parse the label and preserve calendar information?

    @classmethod
    def time_spans_from_graph(cls, graph):
        """Find and return all entities with CIDOC-CRM type E52 Time-Span
        within the rdflib graph and yield them as :class:`TimeSpan`
        resources."""
        for timespan_uri in graph.subjects(
            predicate=rdflib.RDF.type, object=CIDOC_CRM["E52_Time-Span"]
        ):
            yield cls(graph, timespan_uri)
