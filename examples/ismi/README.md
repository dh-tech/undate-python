# Sample data from the ISMI project database

The [Islamic Scientific Manuscript Initiative project](https://ismi.mpwig-berlin.mpg.de) aims to collect information about all Islamic Manuscripts in the exact sciences from the 9th to the 19th centuries CE.

The new [ISMI database](https://gitlab.gwdg.de/MPIWG/Department-II/ismi-project) stores historical dates as CIDOC-CRM RDF objects with the following structure:

- `crm:E52_Time-Span`
  - `crm:P2_has_type`: date type
    - "datetype:day"
      - `crm:P82_at_some_time_within`: given day (xsd:date)
    - "datetype:year"
      - `crm:P82a_begin_of_the_begin`: first day (xsd:date), `crm:P82b_end_of_the_end`: last day of year (xsd:date)
    - "datetype:range"
      - `crm:P82a_begin_of_the_begin`: first day (xsd:date), `crm:P82b_end_of_the_end`: last day of range (xsd:date)
  - `crm:P1_is_identified_by`
    - `crm:E41_Appellation`
    - `rdfs:label`: textual representation of timespan (e.g. "901 Rabīʿ I 14 (islamic)")
    - `crm:P2_has_type`: calendar type (calendar the date was entered in)
      - "calendartype:julian", "calendartype:islamic", "calendartype:gregorian"
    - `crm:P3_has_note`: textual note with additional information

A sample file with dates of each type can be found in `data/ismi-crm-date-samples.ttl`
