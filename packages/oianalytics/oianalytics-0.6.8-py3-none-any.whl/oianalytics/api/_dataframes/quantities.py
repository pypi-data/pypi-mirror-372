from typing import Optional

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils


__all__ = ["get_quantities"]


def get_quantities(
    name: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    List physical quantities by page.

    Parameters
    ----------
    name : str, optional
        The text the quantity should contain. The search is performed in case-insensitive manner.
    page : int, default 0
        The page to retrieve. It is ignored if 'get_all_pages' is set to True.
    page_size : int, default 20.
        The size of one page. It is ignored if 'get_all_pages' is set to True.
    get_all_pages : bool = True
        Whether to get quantities of all pages.
        If the value is set to True, the 'page' and 'page_size' arguments will be ignored, and the function will retrieve all pages.
    multithread_pages : bool, default True
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
        A pandas Dataframe containing the quantities names indexed by their corresponding quantities ids.
    """

    if get_all_pages is True:
        page = 0
        page_size = 500

    def get_page(page_num: int) -> dict:
        return endpoints.quantities.get_quantities(
            name=name,
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )

    def parse_page(page_response: dict) -> pd.DataFrame:
        page_df = pd.DataFrame(page_response["content"], dtype=str)
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=[
                    "id",
                    "name",
                ]
            )
        page_df.set_index("id", inplace=True)
        return page_df

    df = utils.concat_pages_to_dataframe(
        getter=get_page,
        parser=parse_page,
        page=page,
        get_all_pages=get_all_pages,
        multithread_pages=multithread_pages,
    )

    # Output
    return df.squeeze()
