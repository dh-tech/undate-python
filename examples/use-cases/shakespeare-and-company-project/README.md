# Data from the Shakespeare and Company Project

Rebecca Sutton Koeser, Center for Digital Humanities at Princeton

The [Shakespeare and Company Project](https://shakespeareandco.princeton.edu/) publishes an events dataset that documents lending library activities such as subscribing, renewing, and borrowing and returning books. Some of the dates for those events are only partially known.

Dates are in ISO8601 format in one of the following formats: YYYY, YYYY-MM, YYYY-MM-DD, --MM-DD.

Event dates are used for sorting, for filtering to determine if a member was active in a particular year, and for determining durations - how long a subscription lasted for, or how long a borrowed book was out. One special case is borrow events with unknown years: the Project assumes that the return was the same or successive year, so even though the years are unknown the duration can be calculated.

The dataset includes durations for subscriptions and borrow events in human readable format and number of days.

The [Shakespeare and Company Project codebase](https://github.com/Princeton-CDH/mep-django) that generated these datasets includes code for working with "partial dates" (this work is a precursor to `undate`). When working with the web application and database, it's possible to perform calculations and filtering that makes use of whatever parts of the date are known. Because we anticipated this would be difficult or impossible without that custom code, the datasets include the dates in ISO8601 as well as certain calculations based on those dates, including years of library membership or book circulation and duration of borrowing events and subscriptions in both human readable and machine readable form (text and count by days). 

Data analysis tasks that take these kinds of dates into account currently require either ignoring partially known dates or coercing them to a specific date, e.g. the first day of the month or year. (For an example of analytic time-based work on this data, see ["Missing Data, Speculative Reading"](https://doi.org/10.22148/001c.116926) by Koeser and LeBlanc, and [accompanying research code](https://github.com/rlskoeser/shxco-missingdata-specreading)). Our hope is that in the future, `undate` will make it possible to work with those partial dates instead of ignoring them.

----

This dataset is included here as an example for convenience. If you want to use it elsewhere, please
reference the record with additional information, cite it properly, and make sure you're using the most recent published version.

https://doi.org/10.34770/nz90-ym25


