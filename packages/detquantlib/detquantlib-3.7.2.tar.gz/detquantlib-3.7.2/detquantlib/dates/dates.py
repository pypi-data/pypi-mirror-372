# Python built-in packages
from datetime import datetime
from typing import Literal

# Third-party packages
import pandas as pd
from dateutil.relativedelta import *


def count_delivery_periods(
    start_date: datetime,
    end_date: datetime,
    delivery_frequency: str,
    full_periods_only: bool = False,
    timezone: str = None,
) -> int:
    """
    Counts the number of delivery periods within a time interval.

    Note: When the end date is exactly equal to the start of the next delivery period, that next
    period is not included (because it has not yet started). For example, if the end date is
    15-Jan-2025 00:00:00 and the delivery frequency is daily, then the period
    15-Jan-2025 00:00:00 to 16-Jan-2025 00:00:00 is not included.

    Args:
        start_date: Delivery start date
        end_date: Delivery end date
        delivery_frequency: Delivery frequency, expressed as Pandas offset aliases
        full_periods_only: Indicates whether to count only fully elapsed periods.
            For example, suppose that start date is 15-Jan-2025 00:15:00, end date is
            3-Feb-2025 03:45:00, and delivery frequency is hourly. Then:
            - If full_periods_only=True, the number of periods is 2 (01:00:00-02:00:00 and
                02:00:00-03:00:00), because the hours 00:00:00-01:00:00 and 00:03:00-04:00:00
                are not full.
            - If full_periods_only=False, the number of periods is 4, because incomplete hours
                00:00:00-01:00:00 and 00:03:00-04:00:00 are also included. Note:
                - If end date is 3-Feb-2025 04:00:00, hour 04:00:00-05:00:00 is not included.
                - If end date is 3-Feb-2025 04:00:01, hour 04:00:00-05:00:00 is included.
        timezone: Timezone (needed to account for DST switches)

    Returns:
        Number of delivery periods in the interval
    """
    # Convert to pandas timestamp
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    if full_periods_only:
        start_date = start_date.ceil(delivery_frequency)
        end_date = end_date.floor(delivery_frequency)
    else:
        start_date = start_date.floor(delivery_frequency)

    periods = pd.date_range(
        start=start_date,
        end=end_date,
        freq=delivery_frequency,
        inclusive="left",
        tz=timezone,
    )
    nr_periods = len(periods)
    return nr_periods


def calc_months_diff(
    start_date: datetime,
    end_date: datetime,
    diff_method: Literal["month", "time", "full_months_only"] = "month",
) -> int:
    """
    Calculate the month difference between 2 dates.

    Args:
        start_date: Start date
        end_date: End date
        diff_method: Method to count the month difference.
            - diff_method="month": Counts the month difference based on the months of the start
                date and end date, irrespective of the day. For example, suppose that start date
                is 15-Jan-2025 and end date is 3-Mar-2025. Then, the month difference between
                Jan-2025 and Mar-2025 is 2.
            - diff_method="time": Counts the month difference, accounting for the day and time
                of the start and end dates. For example:
                - Suppose that start date is 15-Jan-2025 and end date is 3-Mar-2025. Then:
                    - start date + 1 months = 15-Feb-2025
                    - start date + 2 months = 15-Mar-2025
                    - The month difference is 1, because
                        [start date + 1 months] <= end date < [start date + 2 months].
                - Suppose that start date is 15-Jan-2025 and end date is 16-Mar-2025. Then:
                    - start date + 2 months = 15-Mar-2025
                    - start date + 3 months = 15-Apr-2025
                    - The month difference is 2, because
                        [start date + 2 months] <= end date < [start date + 3 months].
            - diff_method="full_months_only": Counts the number of fully elapsed months between
                the start date and the end date. For example, suppose that start date
                is 15-Jan-2025 and end date is 3-Mar-2025. Then, the month difference is 1,
                because only Feb-2025 was elapsed from start to finish.

    Returns:
        Month difference between 2 dates

    Raises:
        ValueError: Raises an error when end_date < start_date
        ValueError: Raises an error when the input argument 'diff_method' is invalid
    """
    # Input validation
    if end_date < start_date and diff_method != "month":
        raise ValueError("End date cannot be smaller than start date.")

    # Calculate month difference
    start_mc = datetime_to_month_code(start_date)
    end_mc = datetime_to_month_code(end_date)

    if diff_method == "month":
        diff = end_mc - start_mc
    elif diff_method == "time":
        # Check month difference, accounting for day and time. For example, suppose that start
        # date is 10-Jan-2025 14:00:00. Then:
        # - If end date is 10-Mar-2025 14:00:00, month difference is 2.
        # - If end date is 10-Mar-2025 13:55:00, month difference is 1.
        start_day = start_date + relativedelta(year=2000, month=1)
        end_day = end_date + relativedelta(year=2000, month=1)
        diff = end_mc - start_mc
        if end_day < start_day:
            diff -= 1
    elif diff_method == "full_months_only":
        # Calculate number of fully elapsed months
        # Note: We need to use the max operator, otherwise diff = -1 when start month = end month.
        if start_date > datetime(start_date.year, start_date.month, 1):
            start_mc += 1
        diff = max(end_mc - start_mc, 0)
    else:
        raise ValueError("Invalid value of input argument 'diff_method'.")

    return diff


def datetime_to_month_code(d: datetime) -> int:
    """
    Converts a datetime to its corresponding month code. A month code is calculated as the number
    of months since 1 January 1900 (including the month of the input datetime).

    Args:
        d: Datetime

    Returns:
        Corresponding month code

    Raises:
        ValueError: Raises an error if the input datetime is before 1 January 1900
    """
    if d < datetime(1900, 1, 1):
        raise ValueError("Input date cannot be before 1 January 1900.")
    month_code = (d.year - 1900) * 12 + d.month
    return month_code
