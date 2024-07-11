# Sample data from the ISMI project database

The [Islamic Scientific Manuscript Initiative project](https://ismi.mpwig-berlin.mpg.de) aims to collect information about all Islamic Manuscripts in the exact sciences from the 9th to the 19th centuries CE.

The old [ISMI database](https://gitlab.gwdg.de/MPIWG/Department-II/ismi-project) database OpenMind (OM4) stores historical dates as JSON objects with the following structure:

- `state`
  - "unknown": no date
  - "not checked": unparsed date in `date_in_text`
  - "known": date or date range entered in specified calendar
    - `calendar_type`: calendar the date was entered in
      - "Julian", "Islamic", "Gregorian"
    - `input_form`: date type
      - "Year"
        - `from`: first day, `until`: last day of year (dates in Gregorian calendar, ambiguity of +-2 days when entered in Islamic calendar)
      - "Range"
        - `from`: first day, `until`: last day of range (dates in Gregorian calendar, ambiguity of +-2 days when entered in Islamic calendar)
      - "Date"
         - `date`: given day (date in Gregorian calendar, ambiguity of +-2 days when entered in Islamic calendar)
    - `additional_info`: textual note with additional information

We plan to extract as much as possible of this data in the migration to the new RDF database with a CIDOC-CRM-based data model.

A sample file with dates of each type can be found in `data/ismi-om4-date-samples.json`
