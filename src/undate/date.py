from enum import IntEnum

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

    def __new__(cls, year: str, month: str = None, day: str = None):
        if isinstance(year, np.datetime64):
            data = year
        else:
            datestr = year
            if month is not None:
                datestr = f"{year}-{month:02d}"
                if day is not None:
                    datestr = f"{datestr}-{day:02d}"
            data = np.datetime64(datestr)

        data = np.asarray(data, dtype="datetime64")
        if data.dtype != "datetime64[D]":
            raise Exception(
                "Unable to parse dates adequately to datetime64[D]: %s" % data
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
        return int(str(self.astype("datetime64[M]")).split("-")[-1])

    @property
    def day(self):
        return int(str(self.astype("datetime64[D]")).split("-")[-1])


class DatePrecision(IntEnum):
    """date precision, to indicate date precision independent from how much
    of the date is known."""

    # numbers should be set to allow logical greater than / less than
    # comparison, e.g. year precision > month

    #: day
    DAY = 1
    #: month
    MONTH = 2
    #: year
    YEAR = 3

    def __str__(self):
        return f"{self.name}"

    # NOTE: consider harmonizing / using numpy units
    # numpy date units are years (‘Y’), months (‘M’), weeks (‘W’), and days (‘D’)
