# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Optional, Union


from undate import Undate
from undate.date import ONE_DAY, ONE_YEAR, Timedelta
from undate.converters.base import BaseDateConverter


class UndateInterval:
    """A date range between two uncertain dates.

    :param earliest: Earliest undate
    :type earliest: `undate.Undate`
    :param latest: Latest undate
    :type latest:  `undate.Undate`
    :param label: A string to label a specific undate interval, similar to labels of `undate.Undate`.
    :type label: `str`
    """

    # date range between two undates
    earliest: Union[Undate, None]
    latest: Union[Undate, None]
    label: Union[str, None]

    # TODO: think about adding an optional precision / length /size field
    # using DatePrecision for intervals of any standard duration (decade, century)

    def __init__(
        self,
        earliest: Optional[Undate] = None,
        latest: Optional[Undate] = None,
        label: Optional[str] = None,
    ):
        # takes two undate objects; allows conversion from supported types
        if earliest:
            try:
                earliest = Undate.to_undate(earliest)
            except TypeError as err:
                raise ValueError(
                    f"earliest date {earliest} cannot be converted to Undate"
                ) from err
        if latest:
            try:
                latest = Undate.to_undate(latest)
            except TypeError as err:
                raise ValueError(
                    f"latest date {latest} cannot be converted to Undate"
                ) from err

        # check that the interval is valid
        if latest and earliest and latest <= earliest:
            raise ValueError(f"invalid interval {earliest}-{latest}")

        self.earliest = earliest
        self.latest = latest
        self.label = label

    def __str__(self) -> str:
        # using EDTF syntax for open ranges
        return "%s/%s" % (self.earliest or "..", self.latest or "")

    def format(self, format) -> str:
        """format this undate interval as a string using the specified format;
        for now, only supports named converters"""
        converter_cls = BaseDateConverter.available_converters().get(format, None)
        if converter_cls:
            return converter_cls().to_string(self)

        raise ValueError(f"Unsupported format '{format}'")

    def __repr__(self) -> str:
        if self.label:
            return "<UndateInterval '%s' (%s)>" % (self.label, self)
        return "<UndateInterval %s>" % self

    def __eq__(self, other) -> bool:
        # currently doesn't support comparison with any other types
        if not isinstance(other, UndateInterval):
            return NotImplemented
        # consider interval equal if both dates are equal
        return self.earliest == other.earliest and self.latest == other.latest

    def duration(self) -> Timedelta:
        """Calculate the duration between two undates.
        Note that durations are inclusive (i.e., a closed interval), and
        include both the earliest and latest date rather than the difference
        between them.

        :returns: A duration
        :rtype: Timedelta
        """
        # what is the duration of this date range?

        # if range is open-ended, can't calculate
        if self.earliest is None or self.latest is None:
            raise NotImplementedError(
                "Cannot calculate duration for open-ended interval"
            )

        # if both years are known, subtract end of range from beginning of start
        if self.latest.known_year and self.earliest.known_year:
            return self.latest.latest - self.earliest.earliest + ONE_DAY

        # if neither year is known...
        elif not self.latest.known_year and not self.earliest.known_year:
            # under what circumstances can we assume that if both years
            # are unknown the dates are in the same year or sequential?
            duration = self.latest.earliest - self.earliest.earliest
            # if we get a negative, we've wrapped from end of one year
            # to the beginning of the next;
            # recalculate assuming second date is in the subsequent year
            if duration.days < 0:
                end = self.latest.earliest + ONE_YEAR
                duration = end - self.earliest.earliest

            # add the additional day *after* checking for a negative
            # or after recalculating with adjusted year
            duration += ONE_DAY

            return duration

        else:
            # is there any meaningful way to calculate duration
            # if one year is known and the other is not?
            raise NotImplementedError

    def __contains__(self, other: object) -> bool:
        """Determine if another interval or date falls within this
        interval.  Supports comparison with :class:`UndateInterval`
        or anything that can be converted with :meth:`Undate.to_undate`."""
        # support comparison with another interval or anything
        # that can be converted to an Undate
        if isinstance(other, UndateInterval):
            # compare based on earliest/latest bounds
            other_earliest = other.earliest
            other_latest = other.latest
        else:
            # otherwise, try to convert to an Undate
            try:
                other = Undate.to_undate(other)
                other_latest = other_earliest = other
            except TypeError:
                # if conversion fails, then we don't support comparison
                raise

        # if either bound of the current interval is None,
        # then it is an open interval and we don't need to check the other value.
        # if the other value is set, then check that it falls within the
        # bounds of this interval
        return (
            self.earliest is None
            or other_earliest is not None
            and other_earliest >= self.earliest
        ) and (
            self.latest is None
            or other_latest is not None
            and other_latest <= self.latest
        )

    def intersection(self, other: "UndateInterval") -> Optional["UndateInterval"]:
        """Determine the intersection or overlap between two :class:`UndateInterval`
        objects and return a new interval. Returns None if there is no overlap.
        """
        try:
            # when both values are defined, return the inner bounds;
            # if not, return whichever is not None, or None
            earliest = (
                max(self.earliest, other.earliest)
                if self.earliest and other.earliest
                else self.earliest or other.earliest
            )
            latest = (
                min(self.latest, other.latest)
                if self.latest and other.latest
                else self.latest or other.latest
            )

            # if this results in an invalid interval, initialization
            # will throw an exception
            return UndateInterval(earliest, latest)
        except ValueError:
            return None
