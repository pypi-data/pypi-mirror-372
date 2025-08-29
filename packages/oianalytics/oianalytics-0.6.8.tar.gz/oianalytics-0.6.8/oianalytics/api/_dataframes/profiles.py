from typing import Optional, List
import pandas as pd

from .. import _credentials
from .. import endpoints


__all__ = [
    "get_permissions",
    "get_profiles",
    "get_single_profile",
    "create_profile",
]


def get_permissions(
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    List all permissions details.

    Parameters
    ----------
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all the permissions and their details.
        Index:
        - 'name': the name of the permission.
        Columns:
        - 'group': The group this permission belongs to.
        - 'type': The type of permission, can be yes/no or read/write.
        - 'subGroup': The sub-group this permission belongs to.
        - 'operation': The operation attached to the permission.
    """
    response = endpoints.profiles.get_permissions(
        api_credentials=api_credentials,
    )
    df = pd.DataFrame(response)
    if len(df) > 0:
        df.set_index("name", inplace=True)

    # Output
    return df


def get_profiles(
    page: int = 0,
    extract_mode: bool = False,
    permission_name: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    List profiles by page.

    Parameters
    ----------
    page : int, default 0.
        The page to retrieve, defaults to 0 e.g. the first page.
    extract_mode : bool, default False
        Whether to extract the key 'mode' for the requested permission name.
        Used only if permission_to_extract is not None.
    permission_name : str, optional
        The name of the permission whose mode is to be retrieved.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with the detail of the profiles at a given page.
        Index:
        - 'id': the OIAnalytics ID of the profile.
        Columns:
        - 'name': The name of the profile.
        - 'externalId': The external ID of the profile.
        - 'accessRights': The detail of all the permissions of the profile.
    """
    if extract_mode is True and permission_name is None:
        raise ValueError("permission_name cannot be None if extract_mode is True")

    response = endpoints.profiles.get_profiles(
        page=page,
        api_credentials=api_credentials,
    )
    df = pd.DataFrame(response["content"])

    if len(df) == 0:
        return df

    df.set_index("id", inplace=True)

    if extract_mode:
        df["accessRights"] = df["accessRights"].apply(
            lambda x: pd.DataFrame(x)
            .set_index("permission")
            .loc[permission_name, "mode"]
        )
        df = df.rename(columns={"accessRights": f"{permission_name}_accessRights_mode"})

    # Output
    return df


def get_single_profile(
    profile_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Retrieve the access rights associated with to a profile ID.

    Parameters
    ----------
    profile_id : str
        The OIAnalytics ID of the profile to retrieve.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        A pandas Series mapping the permissions and their modes.
    """
    response = endpoints.profiles.get_single_profile(
        profile_id=profile_id, api_credentials=api_credentials
    )
    df = pd.DataFrame(response["accessRights"])

    df.set_index("permission", inplace=True)

    # Output
    return df.squeeze()


def create_profile(
    name: str,
    external_id: Optional[str],
    access_rights: List[dict],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Create a new profile.

    Parameters
    ----------
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
    pd.Series
        Details of the profile that has just been created.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # endpoints
    response = endpoints.profiles.create_profile(
        name=name,
        external_id=external_id,
        access_rights=access_rights,
        api_credentials=api_credentials,
    )

    ser = pd.Series(response, dtype=object)

    return ser
