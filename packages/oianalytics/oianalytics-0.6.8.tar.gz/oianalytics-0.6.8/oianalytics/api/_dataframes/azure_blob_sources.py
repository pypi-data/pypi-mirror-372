from typing import Optional, List, Any

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils


__all__ = [
    "get_azure_blob_sources",
    "get_single_azure_blob_source",
    "create_azure_blob_source",
]


def get_azure_blob_sources(
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
    page : int, default 0
        The page to retrieve. It is ignored if 'get_all_pages' is set to True.
    page_size : int, default 20.
        The size of a page. It is ignored if 'get_all_pages' is set to True.
    get_all_pages : bool, default True
        Whether to get all pages at once.
        If the value is set to True, the 'page' and 'page_size' arguments will be ignored, and the function will retrieve all pages.
    multithread_pages : bool, default True
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the details of all the azure blob sources, indexed by their IDs.

    """

    if get_all_pages:
        page = 0
        page_size = 500

    def get_page(page_num: int):
        return endpoints.azure_blob_sources.get_azure_blob_sources(
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])
        # Expected columns if content is empty
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=[
                    "id",
                    "tagContext",
                    "enabled",
                    "name",
                    "pollingRate",
                    "minAge",
                    "maxAge",
                    "regexPattern",
                    "container",
                    "accountName",
                    "customEndpoint",
                    "path",
                    "preserveFiles",
                    "containerNamePrepended",
                    "includeSubdirectories",
                ]
            )
        # Set index
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


def get_single_azure_blob_source(
    azure_blob_source_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Get a specific azure blob source configured in OIAnalytics by its ID.

    Parameters
    ----------
    azure_blob_source_id : str
        The OIAnalytics ID of the azure blob polling source to retrieve.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        A pandas Series object that stores the details of a specific azure blob sourced.

    """
    # get response from the endpoint as a dictionary
    response = endpoints.azure_blob_sources.get_single_azure_blob_source(
        azure_blob_source_id=azure_blob_source_id, api_credentials=api_credentials
    )
    # build a pandas Series with the dictionary
    ser = pd.Series(response, dtype=object)

    # Output
    return ser


def create_azure_blob_source(
    name: str,
    tag_context: List[dict],
    enabled: bool,
    polling_rate: int,
    min_age: str,
    max_age: str,
    regex_pattern: str,
    container: str,
    account_name: Optional[str],
    custom_endpoint: Optional[str],
    account_key: str,
    shared_access_signature: Optional[Any],
    path: str,
    preserve_files: bool,
    container_name_prepended: bool,
    include_subdirectories: bool,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Create a new azure blob source.

    Parameters
    ----------
    name : str
        The name of the azure blob polling source.
    tag_context : List[dict]
        The tag context of the polling source.
    enabled : bool
        Whether the polling of this source is enabled.
    polling_rate : int
        The duration between two polls in seconds.
    min_age : str
        The minimum age a file should have to be considered by a poll.
    max_age : str
        The maximum age a file should have to be considered by a poll.
    regex_pattern : str
        A regex the file name should match to be considered by a poll.
    container : str
        The azure container to poll.
    account_name : str, optional
        The name of the azure account. It must be None if 'custom_endpoint' is not None.
    custom_endpoint : str, optional
        A custom endpoint to use in place of the standard azure endpoint.
        It must be None if 'account_name' is not None.
    account_key : str
        The secret account key attached to the account if the authentication mode requested is by account key.
    shared_access_signature : Any
        The shared access signature to access the resource if the authentication mode requested is by shared access signature.
    path : str
        The path to poll within the container.
    preserve_files : bool
        Whether to preserve files after a pool. If False, then files are deleted.
    container_name_prepended : bool
        If true then the name of the container is added to the file name to form the final name in OIAnalytics.
    include_subdirectories : bool
        If true look for all files also included in sub-directories of the main path that was polled.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        Details of the azure blob source that has been created.
    """

    # validation
    if account_name is None and custom_endpoint is None:
        raise ValueError("one of 'account_name' and 'custom_endpoint' should be defined")
    elif account_name is not None and custom_endpoint is not None:
        raise ValueError("one of 'account_name' and 'custom_endpoint' should be None")

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # endpoint
    response = endpoints.azure_blob_sources.create_azure_blob_source(
        name=name,
        tag_context=tag_context,
        enabled=enabled,
        polling_rate=polling_rate,
        min_age=min_age,
        max_age=max_age,
        regex_pattern=regex_pattern,
        container=container,
        account_name=account_name,
        custom_endpoint=custom_endpoint,
        account_key=account_key,
        shared_access_signature=shared_access_signature,
        path=path,
        preserve_files=preserve_files,
        container_name_prepended=container_name_prepended,
        include_subdirectories=include_subdirectories,
        api_credentials=api_credentials,
    )

    ser = pd.Series(response, dtype=object)
    ser.name = ser.loc["name"]

    # Output
    return ser
