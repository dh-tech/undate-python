from enum import IntEnum

# Pre 3.10 requires Union for multiple types, e.g. Union[int, None] instead of int | None
from typing import Optional, Union

import numpy as np

#: timedelta for single day
ONE_DAY = np.timedelta64(1, "D")  # ~ equivalent to datetime.timedelta(days=1)
#: timedelta for a single  year (non-leap year)
ONE_YEAR = np.timedelta64(365, "D")  # ~ relativedelta(years=1)
#: timedelta for a month, assuming maximum month length (31 days)
ONE_MONTH_MAX = np.timedelta64(31, "D")


class Date(np.ndarray):
    """This class is a shim to make :class:`numpy.datetime64` act
    more like the built-in python :class:`datetime.date`."""

    # extend np.datetime64 datatype
    # adapted from https://stackoverflow.com/a/27129510/9706217

    def __new__(
        cls,
        year: Union[int, np.datetime64],
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        if isinstance(year, np.datetime64):
            _data = year
        else:
            datestr = str(year)
            if month is not None:
                datestr = f"{year}-{month:02d}"
                if day is not None:
                    datestr = f"{datestr}-{day:02d}"
            _data = np.datetime64(datestr)

        data = np.asarray(_data, dtype="datetime64")

        # expected dtype depends on date unit / how much of date is known
        expected_unit = "Y"
        if day is not None and month is not None:
            expected_unit = "D"
        elif month:
            expected_unit = "M"
        expected_dtype = f"datetime64[{expected_unit}]"

        if data.dtype != expected_dtype:
            raise ValueError(
                f"Unable to parse dates adequately as {expected_dtype}: {data}"
            )
        obj = data.view(cls)
        return obj

    def Export(self):
        return self

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # custom properties to access year, month, day

    @property
    def year(self):
        return int(str(self.astype("datetime64[Y]")))

    @property
    def month(self):
        # if date unit is year, don't return a month (only M/D)
        if self.dtype != "datetime64[Y]":
            return int(str(self.astype("datetime64[M]")).split("-")[-1])

    @property
    def day(self):
        # only return a day if date unit is in days
        if self.dtype == "datetime64[D]":
            return int(str(self.astype("datetime64[D]")).split("-")[-1])


class DatePrecision(IntEnum):
    """date precision, to indicate date precision independent from how much
    of the date is known."""

    # NOTE: values MUST be ordered based on the relative size or
    # precison of the time unit. That is, the smaller the unit, the more precise
    # it is: a day is more precise than a month, a month is more precise than a year,
    # (DatePrecision.year < DatePrecision.month)

    #: year
    YEAR = 1
    #: month
    MONTH = 2
    #: day
    DAY = 3

    def __str__(self):
        return f"{self.name}"

    # NOTE: consider harmonizing / using numpy date units:
    # years (‘Y’), months (‘M’), weeks (‘W’), and days (‘D’)
