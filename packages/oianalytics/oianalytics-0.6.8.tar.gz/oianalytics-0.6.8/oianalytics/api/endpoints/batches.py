from typing import Optional, List, Union
from datetime import datetime

import requests

from .. import _credentials
from .. import utils


__all__ = [
    "get_batch_types",
    "get_batch_type_details",
    "get_single_batch",
    "get_batches",
    "update_batch_value",
    "update_batch_feature_value",
    "update_batch_features_and_values",
    "update_vector_batch_values",
    "create_batch",
    "update_batch",
    "create_or_update_batches",
    "delete_batch",
    "get_batch_relations",
    "get_single_batch_relation",
]


# Batches
def get_batch_types(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types"
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


def get_batch_type_details(
    batch_type_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}"
    response = requests.get(url=url, **api_credentials.auth_kwargs)

    # Output
    response.raise_for_status()
    return response.json()


def get_single_batch(
    batch_type_id: str,
    batch_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/{batch_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_batches(
    batch_type_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    name: Optional[str] = None,
    features_value_ids: Optional[Union[str, List[str]]] = None,
    asset_ids: Optional[Union[str, List[str]]] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches"
    response = requests.get(
        url=url,
        params={
            "start": start_date_iso,
            "end": end_date_iso,
            "name": name,
            "feature-values": utils.join_list_query_param(features_value_ids),
            "asset-id": utils.join_list_query_param(asset_ids),
            "page": page,
            "size": page_size,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_batch_value(
    batch_type_id: str,
    batch_id: str,
    data_id: str,
    value: Union[int, float],
    unit_id: Optional[str] = None,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/{batch_id}/value"
    response = requests.put(
        url=url,
        json={
            "dataId": data_id,
            "value": value,
            "unitId": unit_id,
        },
        params={"create-upload-event": create_upload_event},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def update_batch_feature_value(
    batch_type_id: str,
    batch_id: str,
    feature_id: str,
    value: str,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/{batch_id}/feature"
    response = requests.put(
        url=url,
        json={
            "batchTagKeyId": feature_id,
            "batchTagValueValue": value,
        },
        params={"create-upload-event": create_upload_event},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def update_batch_features_and_values(
    batch_type_id: str,
    data: List[dict],
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/features-and-values"
    response = requests.put(
        url=url,
        json=data,
        params={"create-upload-event": create_upload_event},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def update_vector_batch_values(
    data: List[dict],
    use_external_reference: bool = False,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/value-upload/vector-batch-values"
    response = requests.post(
        url=url,
        json=data,
        params={
            "use-external-reference": use_external_reference,
            "create-upload-event": create_upload_event,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def create_batch(
    batch_type_id: str,
    name: str,
    steps: List[dict],
    tag_values_by_id: Optional[List[str]] = None,
    tag_values_by_values: Optional[List[dict]] = None,
    values: Optional[List[dict]] = None,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Init
    if tag_values_by_id is None:
        tag_values_by_id = []

    if tag_values_by_values is None:
        tag_values_by_values = []

    if values is None:
        values = []

    # Build payload
    batch_data = {
        "name": name,
        "steps": steps,
        "tagValuesById": tag_values_by_id,
        "tagValuesByValue": tag_values_by_values,
        "values": values,
    }

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches"
    response = requests.post(
        url=url,
        json=batch_data,
        params={"create-upload-event": create_upload_event},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def update_batch(
    batch_type_id: str,
    batch_id: str,
    name: str,
    steps: List[dict],
    tag_values_by_id: Optional[List[str]] = None,
    tag_values_by_values: Optional[List[dict]] = None,
    values: Optional[List[dict]] = None,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> int:
    """
    Update an existing batch.

    Parameters
    ----------
    batch_type_id : str
        The OIAnalytics ID of the batch type the batch belongs to.
    batch_id : str
        The OIAnalytics ID of the batch to update. Must be an existing ID of a batch.
    name : str
        The new name of the batch.
    steps : list of dict
        The array of steps the batch has been through.
        These steps are merged with existing step.
        Any existing step on a given step id will be overwritten by the command.
        Each step is a dict with the following keys:
        - stepId: str; the id of the step in the batch type.
        - start: str; the start of the step in ISO format.
        - end : str; the end of the step in ISO format.
        - localisationType : {'NO_LOCALISATION', 'TAG_VALUES', 'ASSET'}; the type of localisation for this step.
        - localisationAssetId : list of str; the ids of the asset used to localise the step.
        - localisationTagValueIds : list of str; the ids of the tag value used to localise the step.
    tag_values_by_id : list of str, optional
        The array of batch feature id to create on the batch.
        This is an array of string.
        It is merged with existing feature values on an already existing feature id will be overwritten.
    tag_values_by_values : list of dict
        The array of batch feature values to add to the batch.
        It is merged with existing feature values on an already existing feature id will be overwritten.
        Each dict has the following keys:
        - batchTagKeyId: str; the ID of the feature.
        - batchTagValueValue: str; the value of the feature.
    values : list of dict
        The array of values to create on the batch.
        It is merged with existing feature values on an already existing feature id will be overwritten.
        Each dict has the following keys:
        - dataId: str; the ID of the data.
        - value: float | int, optional; the value (if None, the data will be deleted if it previously existed).
        - unitId: str; the ID of the unit the value is expressed in (in its absent, the storage unit of the measurement will be used).
    create_upload_event : bool, default True
        Whether to create an upload event with updated values.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API.
        If None, previously set default credentials are used.

    Returns
    -------
    int
        Status Code.
    """
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Init
    if tag_values_by_id is None:
        tag_values_by_id = []

    if tag_values_by_values is None:
        tag_values_by_values = []

    if values is None:
        values = []

    # Build payload
    batch_data = {
        "name": name,
        "steps": steps,
        "tagValuesById": tag_values_by_id,
        "tagValuesByValue": tag_values_by_values,
        "values": values,
    }

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/{batch_id}"
    response = requests.put(
        url=url,
        json=batch_data,
        params={"create-upload-event": create_upload_event},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.status_code


def create_or_update_batches(
    batch_type_id: str,
    batches: List[dict],
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/create-or-update"
    response = requests.post(
        url=url,
        json=batches,
        params={"create-upload-event": create_upload_event},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def delete_batch(
    batch_type_id: str,
    batch_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> None:
    """
    Delete a batch identified by its id.

    Parameters
    ----------
    batch_type_id : str
        The OIAnalytics ID of the batch type the batch belongs to.
    batch_id : str
        The OIAnalytics ID of the batch to set the value to. Must be an existing id of a batch.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    None

    """
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches/{batch_id}"
    requests.delete(
        url=url,
        **api_credentials.auth_kwargs,
    )


# Batch Relations
def get_batch_relations(
    batch_structure_relation_id: Optional[str] = None,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    source_batch_name: Optional[str] = None,
    destination_batch_name: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-relations"
    response = requests.get(
        url=url,
        params={
            "batchStructureRelationId": batch_structure_relation_id,
            "start": start_date_iso,
            "end": end_date_iso,
            "sourceBatchName": source_batch_name,
            "destinationBatchName": destination_batch_name,
            "page": page,
            "size": page_size,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_single_batch_relation(
    batch_relation_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-relations/{batch_relation_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
