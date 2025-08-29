import requests
from typing import Optional, List, Any

from .. import _credentials


__all__ = [
    "get_azure_blob_sources",
    "get_single_azure_blob_source",
    "delete_azure_blob_source",
    "create_azure_blob_source",
    "update_azure_blob_source",
    "test_azure_blob_source",
]


def get_azure_blob_sources(
    page: int = 0,
    page_size: int = 20,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/azure-blob-polling-sources"
    response = requests.get(
        url=url,
        params={
            "page": page,
            "size": page_size,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_azure_blob_source(
    azure_blob_source_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/azure-blob-polling-sources/{azure_blob_source_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def create_azure_blob_source(
    name: str,
    tag_context: List[dict],
    enabled: bool,
    polling_rate: int,
    min_age: str,
    max_age: str,
    regex_pattern: str,
    container: str,
    account_name: str,
    custom_endpoint: Optional[Any],
    account_key: str,
    shared_access_signature: Optional[Any],
    path: str,
    preserve_files: bool,
    container_name_prepended: bool,
    include_subdirectories: bool,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
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
    dict
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

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/azure-blob-polling-sources"
    response = requests.post(
        url=url,
        json={
            "name": name,
            "tagContext": tag_context,
            "enabled": enabled,
            "pollingRate": polling_rate,
            "minAge": min_age,
            "maxAge": max_age,
            "regexPattern": regex_pattern,
            "container": container,
            "accountName": account_name,
            "customEndpoint": custom_endpoint,
            "accountKey": account_key,
            "sharedAccessSignature": shared_access_signature,
            "path": path,
            "preserveFiles": preserve_files,
            "containerNamePrepended": container_name_prepended,
            "includeSubdirectories": include_subdirectories,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_azure_blob_source(
    azure_blob_source_id: str,
    name: str,
    tag_context: List[dict],
    enabled: bool,
    polling_rate: int,
    min_age: str,
    max_age: str,
    regex_pattern: str,
    container: str,
    account_name: str,
    custom_endpoint: Optional[Any],
    account_key: str,
    shared_access_signature: Optional[Any],
    path: str,
    preserve_files: bool,
    container_name_prepended: bool,
    include_subdirectories: bool,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing azure blob source.

    Parameters
    ----------
    azure_blob_source_id : str
        The OIAnalytics ID of the azure blob source.
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
    int
        Status Code.
    """

    # validation
    if account_name is None and custom_endpoint is None:
        raise ValueError("one of 'account_name' and 'custom_endpoint' should be defined")
    elif account_name is not None and custom_endpoint is not None:
        raise ValueError("one of 'account_name' and 'custom_endpoint' should be None")

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/azure-blob-polling-sources/{azure_blob_source_id}"
    response = requests.put(
        url=url,
        json={
            "name": name,
            "tagContext": tag_context,
            "enabled": enabled,
            "pollingRate": polling_rate,
            "minAge": min_age,
            "maxAge": max_age,
            "regexPattern": regex_pattern,
            "container": container,
            "accountName": account_name,
            "customEndpoint": custom_endpoint,
            "accountKey": account_key,
            "sharedAccessSignature": shared_access_signature,
            "path": path,
            "preserveFiles": preserve_files,
            "containerNamePrepended": container_name_prepended,
            "includeSubdirectories": include_subdirectories,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def delete_azure_blob_source(
    azure_blob_source_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an azure blob polling source identified by its ID.

    Parameters
    ----------
    azure_blob_source_id : str
        The OIAnalytics ID of the azure blob polling source to be deleted.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    int
        Status Code.
    """
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/azure-blob-polling-sources/{azure_blob_source_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    response.raise_for_status()
    return response.status_code


def test_azure_blob_source(
    azure_blob_source_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/azure-blob-polling-sources/{azure_blob_source_id}/tests"
    response = requests.post(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
