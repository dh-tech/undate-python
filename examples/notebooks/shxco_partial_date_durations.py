import marimo

__generated_with = "0.9.15"
app = marimo.App()


@app.cell
def __(mo):
    mo.md(
        r"""
        # Compare partial date duration logic

        Comparing `UndateInterval` with similar work from Shakespeare and Company Project (S&co for short).

        This notebook compares the `UndateInterval` duration calculation for date ranges between partially known dates with the similar logic implemented in the [Shakespeare and Company Project](https://shakespeareandco.princeton.edu/) [events dataset](https://doi.org/10.34770/nz90-ym25). Event start and end dates are in ISO8601 format and include as much precision for the date as is known; format is one of: YYYY, YYYY-MM, YYYY-MM-DD, --MM-DD

        Deciding how to calculate date ranges may be contextual; current UndateInterval logic includes both the start and the end date, while the S&co logic does not - so they are off by one. Once we make that adjustment, the borrowing durations in the S&co data match the logic in Undate.

        Subscription durations in S&co are sometimes known to be for a particular term (e.g. a year or six months) but without specific dates, perhaps only a year or year and month; Undate calculates durations based on the earliest and latest days in the range, so it overestimates these durations.

        *Notebook authored by Rebecca Sutton Koeser, 2023. Converted to Marimo, November 2024.*
        """
    )
    return


@app.cell
def __():
    import pandas as pd
    import marimo as mo

    # load the 1.2 version of S&co events dataset; we have a copy in our use-cases folder
    events_df = pd.read_csv(
        "../use-cases/shakespeare-and-company-project/SCoData_events_v1.2_2022-01.csv",
        low_memory=False,
    )
    events_df.head()
    return events_df, mo, pd


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Define a method to parse dates and calculate duration

        Define a method to initialize an `UndateInterval` from start and end date strings in ISO format as used in S&co datasets

        *Note:* There's an off-by-one discrepancy between how we currently calculate duration in Undate and in the Shakespeare and Company Project code; because S&co code counts the first day in the range but not the last (this could also be thought of as counting half of the start and end dates). For simplicity of comparison here, we subtract one day from the  result returned by `UndateInterval.duration`.
        """
    )
    return


@app.cell
def __():
    from undate.undate import UndateInterval
    from undate.dateformat.iso8601 import ISO8601DateFormat

    def undate_duration(start_date, end_date):
        isoformat = ISO8601DateFormat()

        unstart = isoformat.parse(start_date)
        unend = isoformat.parse(end_date)
        interval = UndateInterval(earliest=unstart, latest=unend)

        # subtract one here for simplicity of comparison,
        # to reconcile difference between how duration logic

        return interval.duration().days - 1

    return ISO8601DateFormat, UndateInterval, undate_duration


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Compare subscription event durations

        S&co data includes membership subscriptions with known duration; the dataset includes them in a human readable format (`subscription_duration`) and in a numeric form (`subscription_duration_days`).

        Select subscription events with available duration information to compare with Undate logic.
        """
    )
    return


@app.cell
def __():
    "Identify subscription events with duration information"
    return


@app.cell
def __(events_df):
    subs_duration = events_df[events_df.subscription_duration_days.notna()]
    # limit to fields that are relevant for this exploration
    subs_duration = subs_duration[
        [
            "member_names",
            "start_date",
            "end_date",
            "subscription_duration",
            "subscription_duration_days",
        ]
    ]
    subs_duration.head()
    return (subs_duration,)


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Subscription duration exploration

        Briefly explore the duration data information for these subscriptions.

        What do the duration day values look like? What rnage of values?
        """
    )
    return


@app.cell
def __(subs_duration):
    # What do the subscription duration day values look like?
    subs_duration.subscription_duration_days.value_counts()
    return


@app.cell
def __(subs_duration):
    subs_duration.subscription_duration_days.describe()
    return


@app.cell
def __(mo):
    mo.md(
        r"""Do we have any subscriptions with known duration but unknown start or end date?"""
    )
    return


@app.cell
def __(subs_duration):
    # events with unknown start date
    subs_duration[subs_duration.start_date.isna()]
    return


@app.cell
def __(subs_duration):
    # events with unknown end date
    subs_duration[subs_duration.end_date.isna()]
    return


@app.cell
def __(mo):
    mo.md(
        r"""There are two one-month subscriptions with known start date but end date not set. Exclude those from our comparison."""
    )
    return


@app.cell
def __(subs_duration):
    # filter out durations with missing end date
    subs_duration_nona = subs_duration[subs_duration.end_date.notna()].copy()
    return (subs_duration_nona,)


@app.cell
def __(mo):
    mo.md(r"""### Calculate durations with Undate and compare""")
    return


@app.cell
def __(subs_duration_nona, undate_duration):
    subs_duration_nona["undate_duration"] = subs_duration_nona.apply(
        lambda row: undate_duration(str(row.start_date), str(row.end_date)), axis=1
    )
    subs_duration_nona.head()
    return


@app.cell
def __(subs_duration_nona):
    subs_duration_nona.head()
    return


@app.cell
def __(subs_duration_nona):
    subs_duration_nona["duration_diff"] = subs_duration_nona.apply(
        lambda row: row.undate_duration - row.subscription_duration_days, axis=1
    )
    subs_duration_nona
    return


@app.cell
def __(subs_duration_nona):
    subs_duration_nona["duration_diff"].value_counts()
    return


@app.cell
def __(mo):
    mo.md(r"""### Investigate discrepancies""")
    return


@app.cell
def __(subs_duration_nona):
    subset_subdurations = subs_duration_nona[subs_duration_nona.duration_diff != 0]
    subset_subdurations.head(10)
    return (subset_subdurations,)


@app.cell
def __(subset_subdurations):
    # too many to lok at once, can we segment by subscription duration?
    subset_subdurations.subscription_duration.value_counts()
    return


@app.cell
def __(subset_subdurations):
    # lots of one-month subscriptions, what do the discrepancies look like?
    subset_subdurations[subset_subdurations.subscription_duration == "1 month"].head(15)
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        The first set of these are calculated differently because they are partial dates; undate logic calculates based on earliest possible date through last possible date, but we have additional information in these cases that is project-specific and undate can't take into account, i.e. subscription duration is one month starting sometime in a known year or month.

        The handful towards the end that are off by one in either direction (+/-) are a little more concerning... (potential bug in S&co code? or value calculated based on known semantic duration?)
        """
    )
    return


@app.cell
def __(subset_subdurations):
    # durations other than one month
    subset_subdurations[subset_subdurations.subscription_duration != "1 month"].head(15)
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Compare Borrow event durations

        S&co data also includes borrowing events with known duration; it uses the same format as subscriptions (`subscription_duration` and `subscription_duration_days`.

        Select borrow events with available duration information to compare with Undate logic.
        """
    )
    return


@app.cell
def __(events_df):
    borrow_duration = events_df[events_df.borrow_duration_days.notna()]
    # limit to fields we care about for this check
    borrow_duration = borrow_duration[
        ["member_names", "start_date", "end_date", "borrow_duration_days"]
    ]
    borrow_duration.head()
    return (borrow_duration,)


@app.cell
def __(borrow_duration):
    borrow_duration.tail()
    return


@app.cell
def __(borrow_duration, undate_duration):
    # add a new field for duration as calculated by undate
    borrow_duration["undate_duration"] = borrow_duration.apply(
        lambda row: undate_duration(str(row.start_date), str(row.end_date)), axis=1
    )
    borrow_duration.head(10)
    return


@app.cell
def __(borrow_duration):
    # what's the difference between the two?
    borrow_duration["duration_diff"] = borrow_duration.apply(
        lambda row: row.undate_duration - row.borrow_duration_days, axis=1
    )
    borrow_duration.head(10)
    return


@app.cell
def __(borrow_duration):
    # what do the duration differences look like?
    borrow_duration.duration_diff.value_counts()
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        Woohoo, everything matches! 🎉

        In a previous run, there were two borrow events where the calculation did not match; this was due to an error in undate duration method when the start and end dates have unknown years and dates wrap to the following year (e.g., december to january), which has now been corrected.

        **Note:** One of those events has a range (--06-07/--06-06) that looks like a data error in S&co, but the data matches what is [written on the lending card](https://shakespeareandco.princeton.edu/members/davet-yvonne/cards/cf96d38f-e651-491c-a575-131ea32ce425/#).
        """
    )
    return


@app.cell
def __(borrow_duration):
    borrow_duration[borrow_duration.duration_diff != 0]
    return


if __name__ == "__main__":
    app.run()
