from typing import Optional, List

import requests

from .. import _credentials


__all__ = ["get_users", "get_user_details", "delete_user", "create_user", "update_user"]


def get_users(
    page: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/users"
    response = requests.get(
        url=url,
        params={"page": page},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_user_details(
    user_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/users/{user_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def delete_user(
    user_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an existing user with a given id.

    Parameters
    ----------
    user_id : str
        The OIAnalytics ID of the user to delete.
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
    url = f"{api_credentials.base_url}/api/oianalytics/users/{user_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    response.raise_for_status()
    return response.status_code


def create_user(
    login: str,
    first_name: str,
    last_name: str,
    email: Optional[str],
    phone_number: Optional[str],
    language: Optional[str],
    timezone: Optional[str],
    login_allowed: Optional[bool],
    technical_user: Optional[bool],
    using_sso: Optional[bool],
    session_timeout: Optional[int],
    expiration_date: int,
    profile_id: str,
    tag_access_list: List[dict],
    main_dashboard_id: Optional[str] = None,
    main_notebook_id: Optional[str] = None,
    main_input_form_id: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/users"
    response = requests.post(
        url=url,
        json={
            "login": login,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phoneNumber": phone_number,
            "language": language,
            "timezone": timezone,
            "loginAllowed": login_allowed,
            "technicalUser": technical_user,
            "usingSSO": using_sso,
            "sessionTimeoutInMinutes": session_timeout,
            "expirationDate": expiration_date,
            "profileId": profile_id,
            "tagAccessList": tag_access_list,
            "mainDashboardId": main_dashboard_id,
            "mainNotebookId": main_notebook_id,
            "mainInputFormId": main_input_form_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_user(
    user_id: str,
    login: str,
    first_name: str,
    last_name: str,
    email: str,
    phone_number: Optional[str],
    language: Optional[str],
    timezone: Optional[str],
    login_allowed: Optional[bool],
    technical_user: Optional[bool],
    using_sso: Optional[bool],
    session_timeout: Optional[int],
    expiration_date: int,
    profile_id: str,
    tag_access_list: List[dict],
    main_dashboard_id: Optional[str] = None,
    main_notebook_id: Optional[str] = None,
    main_input_form_id: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing user.

    Parameters
    ----------
    user_id : str
        The OIAnalytics ID of the user.
    login : str
        The login of the user.
    first_name : str
        The first name of the user.
    last_name : str
        The last name of the user.
    email : str
        The email of the user.
    phone_number : str, optional
        The phone number of the user.
    language : str
        The display language of the user.
    timezone : str
        The display language of the user.
    login_allowed : bool
        Whether the user is allowed to log in the application.
    technical_user : bool
        Whether the user is technical.
    using_sso : bool
        Whether the user is using sso to authenticate to the application.
    session_timeout : int, optional
        The session timeout, in minutes. Must be at least 1440.
        If None, a default timeout will be used.
    expiration_date : int
        The expiration date of the user. After this date, the user can no longer log in.
    profile_id : str
        The OIAnalytics ID of the user’s profile.
    tag_access_list : list of dict
        The tag access used of the user.
        It is a list of dict, where each dict contains the following keys:
        - 'tagKeyId': str, the tag key ID of the tag access
        - 'allTagValuesAccessible': bool, whether the user has access to all the tag values of the tag key
        - 'accessibleTagValueIds': list of str, the tag value IDs of the tag access.

    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.
    main_dashboard_id : str, optional
        The main of the dashboard of the user.
    main_notebook_id : str, optional
        The main of the notebook of the user.
    main_input_form_id : str, optional
        The main of the input form of the user.

    Returns
    -------
    int
        Status Code.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/users/{user_id}"
    response = requests.put(
        url=url,
        json={
            "login": login,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phoneNumber": phone_number,
            "language": language,
            "timezone": timezone,
            "loginAllowed": login_allowed,
            "technicalUser": technical_user,
            "usingSSO": using_sso,
            "sessionTimeoutInMinutes": session_timeout,
            "expirationDate": expiration_date,
            "profileId": profile_id,
            "tagAccessList": tag_access_list,
            "mainDashboardId": main_dashboard_id,
            "mainNotebookId": main_notebook_id,
            "mainInputFormId": main_input_form_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code
