from typing import Optional

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils


__all__ = ["get_units", "get_unit_families"]


def get_units(
    label: Optional[str] = None,
    quantity_id: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    expand_quantity: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    List units by page.

    Parameters
    ----------
    label : str, optional
        The label the unit should contain.
    quantity_id : str, optional
        The ID of the quantity the unit is attached to.
    page : int, default 0
        The page to retrieve. It is ignored if 'get_all_pages' is set to True.
    page_size : int, default 20.
        The size of one page. It is ignored if 'get_all_pages' is set to True.
    get_all_pages : bool, default True
        Whether to get units of all pages.
        If the value is set to True, the 'page' and 'page_size' arguments will be ignored, and the function will retrieve all pages.
    multithread_pages : bool, default True
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    expand_quantity: bool, default True
        Whether to expand the column 'quantity'.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
        A pandas DataFrame containing the units indexed by their correspondent units IDs.

    """
    if get_all_pages:
        page = 0
        page_size = 500

    def get_page(page_num: int) -> dict:
        return endpoints.units.get_units(
            label=label,
            quantity_id=quantity_id,
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )

    def parse_page(page_response: dict) -> pd.DataFrame:
        page_df = pd.DataFrame(page_response["content"])
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=[
                    "id",
                    "label",
                    "quantity",
                    "multiplicativeFactor",
                    "additiveFactor",
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

    if expand_quantity:
        df = utils.expand_dataframe_column(
            df=df,
            col="quantity",
        )

    # output
    return df


def get_unit_families(
    label: Optional[str] = None,
    main_unit_id: Optional[str] = None,
    quantity_id: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    expand_main_unit: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
        List unit families by page.

    Parameters
    ----------
    label : str, optional
        The label the unit should contain.
    main_unit_id : str, optional
        The ID of the main unit of the family.
    quantity_id : str, optional
        The ID of the quantity the unit is attached to.
    page : int, default 0
        The page to retrieve.
    page_size : int, default 20
        The size of one page.
    get_all_pages : bool, default True
        Whether to get unit families of all pages.
        If the value is set to True, the 'page' and 'page_size' arguments will be ignored, and the function will retrieve all pages.
    multithread_pages : bool, default True
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    expand_main_unit : bool, default True
        Whether to expand the mainUnit column.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
        A pandas DataFrame containing the unit families indexed by their correspondent unit families IDs.
    """

    if get_all_pages:
        page = 0
        page_size = 500

    def get_page(page_num: int) -> dict:
        return endpoints.units.get_unit_families(
            label=label,
            main_unit_id=main_unit_id,
            quantity_id=quantity_id,
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )

    def parse_page(page_response: dict) -> pd.DataFrame:
        page_df = pd.DataFrame(page_response["content"])
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=["id", "label", "mainUnit"],
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

    if expand_main_unit:
        df = utils.expand_dataframe_column(
            df=df,
            col="mainUnit",
        )

    # output
    return df
