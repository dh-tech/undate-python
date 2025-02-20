import datetime

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

    # TODO: let's think about adding an optional precision / length /size field
    # using DatePrecision

    def __init__(
        self,
        earliest: Optional[Undate] = None,
        latest: Optional[Undate] = None,
        label: Optional[str] = None,
    ):
        # for now, assume takes two undate objects;
        # support conversion from datetime
        if earliest and not isinstance(earliest, Undate):
            # NOTE: some overlap with Undate._comparison_type method
            # maybe support conversion from other formats later
            if isinstance(earliest, datetime.date):
                earliest = Undate.from_datetime_date(earliest)
            else:
                raise ValueError(
                    f"earliest date {earliest} cannot be converted to Undate"
                )
        if latest and not isinstance(latest, Undate):
            if isinstance(latest, datetime.date):
                latest = Undate.from_datetime_date(latest)
            else:
                raise ValueError(f"latest date {latest} cannot be converted to Undate")

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
        print(f"converter_cls == {converter_cls}")
        if converter_cls:
            return converter_cls().to_string(self)

        raise ValueError(f"Unsupported format '{format}'")

    def __repr__(self) -> str:
        if self.label:
            return "<UndateInterval '%s' (%s)>" % (self.label, self)
        return "<UndateInterval %s>" % self

    def __eq__(self, other) -> bool:
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
            return NotImplemented

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
