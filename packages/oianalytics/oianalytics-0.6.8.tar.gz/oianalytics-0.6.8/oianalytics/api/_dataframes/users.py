from typing import Optional, List

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils


__all__ = ["get_users", "get_user_details", "create_user"]


def get_users(
    page: int = 0,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    expand_profile: bool = True,
    extract_from_access_list: Optional[str] = "synthesis",
    expand_access_list: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get configured users from the OIAnalytics API

    Parameters
    ----------
    page: int, optional
        Page number to retrieve. If None, the first page will be retrieved.
        The argument is ignored if 'get_all_pages' is True.
    get_all_pages: bool, default True
        If True, paging is ignored and all elements are retrieved.
    multithread_pages: bool, default False
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    expand_profile: bool, default True
        Whether or not the profile information should be expanded into multiple columns.
    extract_from_access_list: {'all_access', 'tag_list', None}, default 'synthesis'
        What field should be extracted from access list information.
        'tag_list' will only extract the listed accessible tag keys.
        'all_access' will only extract whether or not the user has access to evefything.
        'synthesis' will combine the previous 2 extracting a list of accessible tag keys or 'All' for a full access.
        If None, the full dictionary is kept.
    expand_access_list: bool, default True
        Whether or not the access list information should be expanded into multiple columns.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A DataFrame listing users and their access information
    """

    # Args validation
    if extract_from_access_list not in ["all_access", "tag_list", "synthesis", None]:
        raise ValueError(
            f"Unexpected value for 'extract_from_access_list': {extract_from_access_list}"
        )

    if extract_from_access_list is None and expand_access_list is True:
        raise ValueError(
            "Access list cannot be expanded if 'extract_from_access_list' is None"
        )

    # Init
    if get_all_pages is True:
        page = 0

    def get_page(page_num: int):
        page_response = endpoints.users.get_users(
            page=page_num, api_credentials=api_credentials
        )
        return page_response

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])
        page_df["expirationDate"] = pd.to_datetime(
            page_df["expirationDate"], format="ISO8601"
        )
        if expand_profile is True:
            page_df = utils.expand_dataframe_column(page_df, "profile")

        # Format acess list
        if extract_from_access_list == "tag_list":
            page_df["accessList"] = page_df["accessList"].apply(
                lambda al: {a["tagKey"]: a["accessibleTagValues"] for a in al}
            )
        elif extract_from_access_list == "all_access":
            page_df["accessList"] = page_df["accessList"].apply(
                lambda al: {a["tagKey"]: a["allTagValuesAccessible"] for a in al}
            )
        elif extract_from_access_list == "synthesis":
            page_df["accessList"] = page_df["accessList"].apply(
                lambda al: {
                    a["tagKey"]: "All"
                    if a["allTagValuesAccessible"] is True
                    else a["accessibleTagValues"]
                    for a in al
                }
            )

        if expand_access_list is True and extract_from_access_list is not None:
            page_df = utils.expand_dataframe_column(
                page_df, "accessList", add_prefix=False
            )

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


def get_user_details(
    user_id: str,
    expand_profile: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Retrieve the detail of a specific user with its id.

    Parameters
    ----------
    user_id : str
        The OIAnalytics ID of the user to retrieve.
    expand_profile : bool, default True
        Whether to expand the 'profile' column.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        A pandas.Series with the details of a specific user.
    """
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    response = endpoints.users.get_user_details(
        user_id=user_id,
        api_credentials=api_credentials,
    )

    df = pd.DataFrame([response])

    if expand_profile:
        df = utils.expand_dataframe_column(
            df=df,
            col="profile",
        )

    # Output
    return df.squeeze()


def create_user(
    login: str,
    first_name: str,
    last_name: str,
    email: Optional[str],
    phone_number: Optional[str],
    language: str,
    timezone: str,
    login_allowed: bool,
    technical_user: bool,
    using_sso: bool,
    session_timeout: Optional[int],
    expiration_date: int,
    profile_id: str,
    tag_access_list: List[dict],
    expand_profile: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Create a new user.

    Parameters
    ----------
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
        The timezone of the user.
    login_allowed : bool
        Whether the user is allowed to log into the application.
    technical_user : bool
        Whether the user is technical.
    using_sso : bool
        Whether the user is using Single Sign-On (SSO) to authenticate into the application.
    session_timeout : int, optional
        The session timeout, in minutes. Must be at least 1440.
        If None, a default timeout will be used.
    expiration_date : int
        The expiration date after which the user can no longer log in.
    profile_id : str
        The OIAnalytics ID of the user’s profile.
    tag_access_list : list of dict
        The tag access used by the user.
        It is a list of dict, where each dict contain the following keys:
        - 'tagKeyId': The tag key ID of the tag access.
        - 'allTagValuesAccessible': Whether the user has access to all the tag values of the tag key.
        - 'accessibleTagValueIds': The tag value IDs of the tag access.
    expand_profile : bool, default True
        Whether to split the 'profile' column into 'profile_in' and 'profile_name'.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API.
        If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        Details of the user that has just been created.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # endpoint
    response = endpoints.users.create_user(
        login=login,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        language=language,
        timezone=timezone,
        login_allowed=login_allowed,
        technical_user=technical_user,
        using_sso=using_sso,
        session_timeout=session_timeout,
        expiration_date=expiration_date,
        profile_id=profile_id,
        tag_access_list=tag_access_list,
        api_credentials=api_credentials,
    )

    df = pd.DataFrame([response])

    if expand_profile:
        df = utils.expand_dataframe_column(
            df=df,
            col="profile",
        )

    return df.squeeze()
