import pandas as pd
from typing import Optional

from .. import _credentials
from .. import endpoints
from .. import utils

__all__ = ["get_dashboards"]


def get_dashboards(
    page: int = 0,
    page_size: int = 20,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    List azure blob sources configured in OIAnalytics.

    Parameters
    ----------
    page : int
        The page to retrieve, defaults to 0 (first page).
    page_size : int
        The size of a page.
    get_all_pages : bool, default True
        Whether to list all pages of dashboards.
    multithread_pages : bool, default True
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A DataFrame with all the dashboards.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    if get_all_pages is True:
        page = 0

    def get_page(page_num: int):
        page_response = endpoints.dashboard.get_dashboards(
            page=page_num, page_size=page_size, api_credentials=api_credentials
        )
        return page_response

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])

        # Expected columns if content is empty
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(columns=["id", "title", "description", "type"])

        page_df.set_index("id", inplace=True)
        return page_df

    # Query endpoint
    df = utils.concat_pages_to_dataframe(
        getter=get_page,
        parser=parse_page,
        page=page,
        get_all_pages=get_all_pages,
        multithread_pages=multithread_pages,
    )

    # Output
    return df
