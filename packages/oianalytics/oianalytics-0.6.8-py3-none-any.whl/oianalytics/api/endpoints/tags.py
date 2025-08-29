from typing import Optional
import requests

from oianalytics.api import _credentials


__all__ = [
    "get_tag_keys",
    "get_single_tag_key",
    "delete_single_tag_key",
    "get_tag_values",
    "get_single_tag_value",
    "delete_single_tag_value",
    "create_tag_value",
    "update_tag_value",
    "create_tag_key",
    "update_tag_key",
]


def get_tag_keys(
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_tag_key(
    tag_key_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def delete_single_tag_key(
    tag_key_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an existing tag key with a given ID.

    Parameters
    ----------
    tag_key_id : str
        The OIAnalytics ID of the tag key.
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

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def get_tag_values(
    tag_key_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}/values"
    response = requests.get(
        url=url,
        params={"page": page, "size": page_size},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_tag_value(
    tag_key_id: str,
    tag_value_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}/values/{tag_value_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def delete_single_tag_value(
    tag_key_id: str,
    tag_value_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an existing tag value with a given id.

    Parameters
    ----------
    tag_key_id : str
        The OIAnalytics ID of the tag key.
    tag_value_id : str
        The OIAnalytics ID of the tag value.
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

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}/values/{tag_value_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    response.raise_for_status()
    return response.status_code


def create_tag_value(
    tag_key_id: str,
    value: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}/values"
    response = requests.post(
        url=url,
        json={"value": value},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_tag_value(
    tag_key_id: str,
    tag_value_id: str,
    value: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing tag value.

    Parameters
    ----------
    tag_key_id : str
        The OIAnalytics ID of the tag key of the tag value to be updated.
    tag_value_id : str
        The OIAnalytics ID of the tag value to be updated.
    value : str
        The new value of the tag value.
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

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}/values/{tag_value_id}"
    response = requests.put(
        url=url,
        json={"value": value},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def create_tag_key(
    key: str,
    position: int,
    used_for_access_control: bool,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys"
    response = requests.post(
        url=url,
        json={
            "key": key,
            "position": position,
            "usedForAccessControl": used_for_access_control,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_tag_key(
    tag_key_id: str,
    key: str,
    position: int,
    used_for_access_control: bool,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing tag key based on a command.

    Parameters
    ----------
    tag_key_id : str
    key : str
        The key of the tag key.
    position : int
        The position of the tag key.
    used_for_access_control : bool
        Whether this tag key is used to control access objects and data.
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

    url = f"{api_credentials.base_url}/api/oianalytics/tag-keys/{tag_key_id}"
    response = requests.put(
        url=url,
        json={
            "key": key,
            "position": position,
            "usedForAccessControl": used_for_access_control,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code
