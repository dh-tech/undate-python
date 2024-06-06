# Data from the Shakespeare and Company Project

The [Shakespeare and Company Project](https://shakespeareandco.princeton.edu/) publishes an events dataset that document lending library activities such as subscribing, renewing, and borrowing and returning books. Some of the dates for those events are only partially known.

Dates are in ISO8601 format in one of the following formats: YYYY, YYYY-MM, YYYY-MM-DD, --MM-DD.

Event dates are used for sorting, for filtering to determine if a member was active in a particular year, and for determining durations - how long a subscription lasted for, or how long a borrowed book was out. One special case is borrow events with unknown years: the Project assumes that the return was the same or successive year, so even though the years are unknown the duration can be calculated.

The dataset includes durations for subscriptions and borrow events in human readable format and number of days.

----

This dataset is included here as a convenient example. If you want use it elsewhere, please
reference the record with additional information and cite it properly.

https://doi.org/10.34770/nz90-ym25


