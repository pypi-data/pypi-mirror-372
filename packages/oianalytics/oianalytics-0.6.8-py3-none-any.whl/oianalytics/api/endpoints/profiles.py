from typing import Optional, List
import requests

from .. import _credentials


__all__ = [
    "get_permissions",
    "get_profiles",
    "get_single_profile",
    "delete_profile",
    "create_profile",
    "update_profile",
]


def get_permissions(
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/profiles/permissions"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_profiles(
    page: int = 0,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/profiles"
    response = requests.get(
        url=url,
        params={"page": page},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_profile(
    profile_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/profiles/{profile_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def delete_profile(
    profile_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an existing profile with a given id.

    Parameters
    ----------
    profile_id : str
        The OIAnalytics ID of the profile to retrieve.
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
    url = f"{api_credentials.base_url}/api/oianalytics/profiles/{profile_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    response.raise_for_status()
    return response.status_code


def create_profile(
    name: str,
    external_id: Optional[str],
    access_rights: List[dict],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/profiles"
    response = requests.post(
        url=url,
        json={
            "name": name,
            "externalId": external_id,
            "accessRights": access_rights,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_profile(
    profile_id: str,
    name: str,
    external_id: Optional[str],
    access_rights: List[dict],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing user.

    Parameters
    ----------
    profile_id : str
        The OIAnalytics ID of the profile to update.
    name : str
        The name of the profile.
    external_id : str
        The ID of a group in identity provider to associate with the profile.
    access_rights : list of dict
        The access rights associated with this profile.
        Each dictionary in the list contains the following keys:
        - 'permission': str, the permission the access right defines.
        - 'mode': {'YES', 'NO','READ',WRITE'}, the mode of access right is permitted.
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
    url = f"{api_credentials.base_url}/api/oianalytics/profiles/{profile_id}"
    response = requests.put(
        url=url,
        json={
            "name": name,
            "externalId": external_id,
            "accessRights": access_rights,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code
