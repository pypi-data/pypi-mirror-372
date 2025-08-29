from typing import Union, Optional, List, Callable
import dateutil
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import re

import numpy as np
import pandas as pd

__all__ = [
    "get_zulu_isoformat",
    "floor_date",
    "get_iso_period",
    "expand_dataframe_column",
    "concat_pages_to_dataframe",
    "Duration",
    "join_list_query_param",
]


def get_zulu_isoformat(date: Optional[Union[str, datetime]]):
    # Manage None
    if pd.isna(date):
        return None

    # Parse date if it is a string
    if isinstance(date, str):
        date = dateutil.parser.parse(date)

    # Serialize date
    return date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def floor_date(date, period, pivot_date="2018-01-01"):
    """
    Floors a date using a period and a pivot date, in order to stabilize the timestamps.
    It is floored to the closest previous datetime being 'pivot_date' + n * 'period'.
    The default pivot date is '2018-01-01' since it was a monday.

    Parameters
    ----------
    date: datetime
        The date to be floored. Must have a timezone (UTC will ease the setting of the 'pivot_date')
    period: str
        ISO period used to floor the 'date'
    pivot_date: datetime or str
        The date used as a reference for the floor operation.
        If a string is provided, it is supposed to be in UTC.

    Returns
    -------
    The closest previous datetime being 'pivot_date' + n * 'period'
    """

    # Make the pivot date an actual datetime in UTC
    if isinstance(pivot_date, str):
        ref_date = pd.to_datetime(pivot_date, utc=True)
    else:
        ref_date = pivot_date

    delta = date - ref_date
    nb_period = delta // pd.Timedelta(period)

    return pd.Timedelta(period) * nb_period + ref_date


def get_iso_period(period: Optional[Union[str, timedelta, pd.Timedelta]]):
    if period is None:
        return None
    elif isinstance(period, str):
        return period
    elif isinstance(period, (timedelta, pd.Timedelta)):
        return pd.Timedelta(period).isoformat()
    else:
        raise TypeError(f"Can't evaluate iso period from type: {type(period)}")


def to_int(s: Optional[str]):
    return None if s is None else int(s)


class Duration:
    def __init__(
        self,
        years: Optional[int] = None,
        months: Optional[int] = None,
        weeks: Optional[int] = None,
        days: Optional[int] = None,
        hours: Optional[int] = None,
        minutes: Optional[int] = None,
        seconds: Optional[int] = None,
    ):
        self.years = years
        self.months = months
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    @classmethod
    def from_iso(cls, period):
        m = re.match(
            r"^P(?:(?P<years>\d+)Y)?(?:(?P<weeks>\d+)W)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?T?(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:.\d+)?)S)?$",
            period,
        )
        return cls(**{k: to_int(v) for k, v in m.groupdict().items()})

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def to_timedelta(self):
        if self.years is not None or self.months is not None:
            raise ValueError("Pandas Timedelta doesn't accept years and months")

        return pd.Timedelta(**self.to_dict())

    def to_resample_rule(self):
        if list(self.to_dict().keys()) == ["years"]:
            return f"{self.years}YS"
        elif list(self.to_dict().keys()) == ["months"]:
            return f"{self.months}MS"
        elif list(self.to_dict().keys()) == ["weeks"]:
            return f"{self.weeks}W-MON"
        else:
            return self.to_timedelta()


def expand_dataframe_column(
    df: pd.DataFrame,
    col: str,
    add_prefix: bool = True,
    expected_keys: Optional[List[str]] = None,
):
    col_loc = df.columns.get_loc(col)

    # Expand the target column
    if df.shape[0] == 0:
        if expected_keys is None:
            expanded_col = df[col].to_frame()
        else:
            expanded_col = pd.DataFrame(index=df.index, columns=expected_keys)
    else:
        expanded_col = df[col].apply(pd.Series, dtype="object")

    if expanded_col.shape[1] == 0:
        expanded_col[col] = np.nan

    # Rename generated column using prefix
    if add_prefix is True:
        expanded_col = expanded_col.add_prefix(f"{col}_")

    # Concatenate parts of dataframe
    expanded_df = pd.concat(
        [df[df.columns[:col_loc]], expanded_col, df[df.columns[col_loc + 1 :]]], axis=1
    )

    return expanded_df


def concat_pages_to_dataframe(
    getter: Callable,
    parser: Callable,
    page: Optional[int] = None,
    get_all_pages: bool = True,
    multithread_pages: bool = False,
):
    # Init
    if page is None:
        page = 0

    def get_and_parse_page(page_num: int):
        page_response = getter(page_num)
        return parser(page_response)

    # Get first page
    response = getter(page_num=page)
    df = parser(response)

    total_pages = response["totalPages"]
    if get_all_pages is True and total_pages > 1:
        pages_to_get = range(1, total_pages)

        if multithread_pages is True:
            with ThreadPoolExecutor() as pool:
                page_dfs = list(pool.map(get_and_parse_page, pages_to_get))
        else:
            page_dfs = []
            for i in pages_to_get:
                page_dfs.append(get_and_parse_page(page_num=i))

        # Concatenate additional pages with the first one
        df = pd.concat([df] + page_dfs)

    # Concat dataframes
    return df


def join_list_query_param(param: Optional[Union[str, List[str]]]):
    if param is None or isinstance(param, str):
        return param
    else:
        return ",".join(param)
