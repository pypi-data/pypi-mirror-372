from typing import Optional

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils


__all__ = [
    "get_tag_keys",
    "get_single_tag_key",
    "get_tag_values",
    "get_single_tag_value",
    "create_tag_value",
    "create_tag_key",
]


def get_tag_keys(
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    List all the tag keys, ordered by position.

    Parameters
    ----------
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
        A pandas DataFrame containing tag keys indexed by tag key ID.
    """

    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    response = endpoints.tags.get_tag_keys(api_credentials)

    if len(response) > 0:
        df = pd.DataFrame(response)
        df.set_index("id", inplace=True)
    else:
        df = pd.DataFrame(columns=["key", "position", "usedForAccessControl"])
        df.index.name = "id"
        df = df.astype({"key": str, "position": int, "usedForAccessControl": bool})

    # Output
    return df


def get_single_tag_key(
    tag_key_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Retrieve the detail of a specific tag key with its ID.

    Parameters
    ----------
    tag_key_id : str
        The OIAnalytics ID of the tag key.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pandas.Series
        A pandas.Series containing tag key 'id', 'key', 'position' and 'usedForAccessControl'.
    """

    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    response = endpoints.tags.get_single_tag_key(
        tag_key_id=tag_key_id, api_credentials=api_credentials
    )

    ser = pd.Series(response, dtype=object)

    # Output
    return ser


def get_tag_values(
    tag_key_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    expand_tag_key: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    List all the tag values of a given tag key.

    Parameters
    ----------
    tag_key_id : str
        The OIAnalytics ID of the tag key.
    expand_tag_key : bool, default True
        Whether to split the column 'tagKey' into multiple columns.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
        A pandas DataFrame, indexed by tag value ID, containing tag values.
    """

    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Init
    if get_all_pages is True:
        page = 0
        page_size = 500

    def get_page(page_num: int):
        page_response = endpoints.tags.get_tag_values(
            tag_key_id=tag_key_id,
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )
        return page_response

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])

        # Expected columns if content is empty
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(columns=["id", "value", "tagKey"])

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

    if expand_tag_key:
        df = utils.expand_dataframe_column(
            df=df,
            col="tagKey",
            expected_keys=["id", "key", "position", "usedForAccessControl"],
        )

    # Output
    return df


def get_single_tag_value(
    tag_key_id: str,
    tag_value_id: str,
    expand_tag_key: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Retrieve the detail of a specific tag value with its tag-key ID and tag-value-ID.

    Parameters
    ----------
    tag_key_id : str
        The OIAnalytics ID of the tag key.
    tag_value_id : str
        The OIAnalytics ID of the tag value.
    expand_tag_key : bool
        Whether to split the column 'tagKey' into multiple columns.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        A pandas Series containing details of the tag value.
    """
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    response = endpoints.tags.get_single_tag_value(
        tag_key_id=tag_key_id,
        tag_value_id=tag_value_id,
        api_credentials=api_credentials,
    )

    df = pd.DataFrame([response])
    if len(df) > 0:
        df.set_index("id", inplace=True)
        if expand_tag_key:
            df = utils.expand_dataframe_column(
                df=df,
                col="tagKey",
            )

    ser = df.squeeze()

    # Output
    return ser


def create_tag_value(
    tag_key_id: str,
    value: str,
    expand_tagkey: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Create a new tag value for the given tag key on the provided command.

    Parameters
    ----------
    tag_key_id : str
        The ID of the tag key of the tag value to be created.
    value : str
        The value of the tag value.
    expand_tagkey : bool, default True
        Whether to split the column 'tagKey'.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        A pandas.Series with details of the new tag value that has been created.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    response = endpoints.tags.create_tag_value(
        tag_key_id=tag_key_id,
        value=value,
        api_credentials=api_credentials,
    )

    df = pd.DataFrame([response])

    if expand_tagkey:
        df = utils.expand_dataframe_column(
            df=df, col="tagKey",
        )

    # Output
    return df.squeeze()


def create_tag_key(
    key: str,
    position: int,
    used_for_access_control: bool,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Create a new tag key on the provided command.

    Parameters
    ----------
    key : str
        The key of the tag key.
    position : int
        The position of the tag key.
    used_for_access_control : str
        Whether this tag key is used to control access objects and data.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        Details of the created tag key.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    response = endpoints.tags.create_tag_key(
        key=key,
        position=position,
        used_for_access_control=used_for_access_control,
        api_credentials=api_credentials
    )

    ser = pd.Series(response, dtype=object)

    # Output
    return ser
