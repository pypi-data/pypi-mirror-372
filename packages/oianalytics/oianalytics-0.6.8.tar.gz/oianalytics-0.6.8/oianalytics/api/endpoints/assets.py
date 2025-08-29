from typing import Optional, List, Dict, Any

import requests

from .. import _credentials


__all__ = [
    "get_asset_types",
    "get_single_asset_type",
    "delete_asset_type",
    "create_asset_type",
    "update_asset_type",
    "get_assets",
    "get_single_asset",
    "update_single_asset_tags_and_values",
    "delete_asset",
    "create_asset",
    "update_asset",
    "regenerate_asset_data",
]


def get_asset_types(
    page: Optional[int] = None,
    name: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/asset-types"
    response = requests.get(
        url=url,
        params={"page": page, "name": name},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_asset_type(
    asset_type_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/asset-types/{asset_type_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def delete_asset_type(
    asset_type_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an asset type identified by its ID. The deletion will fail if the asset type is used somewhere in the system.

    Parameters
    ----------
    asset_type_id : str
        The OIAnalytics ID of the asset type to retrieve.
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
    url = f"{api_credentials.base_url}/api/oianalytics/asset-types/{asset_type_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    response.raise_for_status()
    return response.status_code


def create_asset_type(
    name: str,
    nature: str,
    tag_context: List[dict],
    dataset: List[dict],
    resources: List[Any],
    static_dataset: Optional[Any],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/asset-types"
    response = requests.post(
        url=url,
        json={
            "name": name,
            "nature": nature,
            "tagContext": tag_context,
            "dataSet": dataset,
            "resources": resources,
            "staticDataSet": static_dataset,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_asset_type(
    asset_type_id: str,
    name: str,
    nature: str,
    tag_context: List[dict],
    dataset: List[Any],
    resources: List[Any],
    static_dataset: Any,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing asset type.

    Parameters
    ----------
    asset_type_id : str
        The OIAnalytics ID of the asset type to update.
    name : str
        The name of the asset type to update.
    nature : {'DEVICE', 'PHYSICAL_ASSET', 'LOGICAL_ASSET'}
        The nature of the asset type to update.
    tag_context : list of dict
        The array of tag values used to label the asset type.
    dataset : list of dict.
        The set of metadata defined at asset type level.
    resources : list of Any.
        The set of resources defined at asset type level.
    static_dataset : list of dict
    api_credentials

    Returns
    -------
    int
        Status Code
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/asset-types/{asset_type_id}"
    response = requests.put(
        url=url,
        json={
            "name": name,
            "nature": nature,
            "tagContext": tag_context,
            "dataSet": dataset,
            "resources": resources,
            "staticDataSet": static_dataset,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def get_assets(
    asset_type_id: str,
    tag_value_id: Optional[List[str]] = None,
    query: Optional[int] = None,
    page: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/assets"
    response = requests.get(
        url=url,
        params={
            "page": page,
            "query": query,
            "assetTypeId": asset_type_id,
            "tagValueIds": tag_value_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_asset(
    asset_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/assets/{asset_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_single_asset_tags_and_values(
    asset_id: str,
    tag_commands: Optional[List[Dict]] = None,
    value_commands: Optional[List[Dict]] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Init commands
    if tag_commands is None:
        tag_commands = []

    if value_commands is None:
        value_commands = []

    # Build payload
    payload = [
        {
            "assetId": asset_id,
            "tagCommands": tag_commands,
            "staticDataValueCommands": value_commands,
        }
    ]

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/assets/tags-and-values"
    response = requests.put(url=url, json=payload, **api_credentials.auth_kwargs)

    # Output
    response.raise_for_status()
    return response.status_code


def delete_asset(
    asset_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Delete an asset identified by its id.

    Parameters
    ----------
    asset_id : str
        The OIAnalytics ID of the asset to be deleted.
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
    url = f"{api_credentials.base_url}/api/oianalytics/assets/{asset_id}"
    response = requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )

    response.raise_for_status()
    return response.status_code


def create_asset(
    name: str,
    external_reference: str,
    description: str,
    asset_type_id: str,
    tag_values: List[dict],
    data_mappings: List[dict],
    static_data_values: List[dict],
    resource_ids: List[str],
    python_model_instances: List[dict],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/assets"
    response = requests.post(
        url=url,
        json={
            "name": name,
            "externalReference": external_reference,
            "description": description,
            "assetTypeId": asset_type_id,
            "tagValues": tag_values,
            "dataMappings": data_mappings,
            "staticDataValues": static_data_values,
            "resourceIds": resource_ids,
            "pythonModelInstances": python_model_instances,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_asset(
    asset_id: str,
    name: str,
    external_reference: str,
    description: str,
    asset_type_id: str,
    tag_values: List[dict],
    data_mappings: List[dict],
    static_data_values: List[dict],
    resource_ids: List[str],
    python_model_instances: List[dict],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing asset.

    Parameters
    ----------
    asset_id : str
        The OIAnalytics id of the asset to update.
    name : str
        The name of the asset to create.
    external_reference : str
        The reference of the asset in external system.
    description : str
        An optional description used to understand what this asset means.
    asset_type_id : str
        The asset type this asset is attached to.
    tag_values : list of dict
        The array of tag values used to label the asset.
    data_mappings : list of dict
        The data mapping between AssetTypeData and Data for this asset.
    static_data_values : list of values
        The static data value of asset static data attached to this asset.
    resource_ids : List[str]
        The OIAnalytics ID of the resource to attach to the asset.
    python_model_instances : List[dict]
        The instances of python models to create or update.
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
    url = f"{api_credentials.base_url}/api/oianalytics/assets/{asset_id}"
    response = requests.put(
        url=url,
        json={
            "name": name,
            "externalReference": external_reference,
            "description": description,
            "assetTypeId": asset_type_id,
            "tagValues": tag_values,
            "dataMappings": data_mappings,
            "staticDataValues": static_data_values,
            "resourceIds": resource_ids,
            "pythonModelInstances": python_model_instances,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def regenerate_asset_data(
    asset_type_id: str,
    asset_ids: List[str],
    data_ids: List[str],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
        Regenerate asset data for targetted assets and data.

        Parameters
        ----------
        asset_type_id : str
            The unique identifier of the considered asset type
        asset_ids : List[str]
            The list of assets to consider when regenerating the data
        data_ids : List[str]
            The list of data to regenerate

        Returns
        -------
        int
            Status code
        """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/asset-types/{asset_type_id}/asset-data-regenerations"
    response = requests.post(
        url=url,
        json={
            "assetIds": asset_ids,
            "dataIds": data_ids,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code
