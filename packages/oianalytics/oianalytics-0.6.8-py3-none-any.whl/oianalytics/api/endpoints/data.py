from typing import Optional, List, Union
from datetime import datetime, timedelta

import requests
import pandas as pd

from .. import _credentials
from .. import utils


__all__ = [
    "get_data_list",
    "get_data_details",
    "get_time_values",
    "get_vector_time_values",
    "get_batch_values",
    "get_vector_batch_values",
    "get_multiple_data_values",
    "insert_time_values",
    "insert_vector_time_values",
]


def get_data_list(
    query: Optional[str] = None,
    types: Optional[List[str]] = None,
    measurement_id: Optional[str] = None,
    measurement_name: Optional[str] = None,
    tag_value_id: Optional[List[str]] = None,
    include_technical_data: Optional[bool] = False,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data"
    response = requests.get(
        url=url,
        params={
            "query": query,
            "types": types,
            "measurement-id": measurement_id,
            "measurement-name": measurement_name,
            "tag-value-id": tag_value_id,
            "include-technical-data": include_technical_data,
            "page": page,
            "size": page_size,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_data_details(
    data_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data/{data_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_time_values(
    data_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    number_of_values: Optional[int] = None,
    aggregation_period: Optional[Union[str, timedelta, pd.Timedelta]] = None,
    aggregation_function: Optional[str] = None,
    unit_id: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Format aggregation period
    aggregation_period_iso = utils.get_iso_period(aggregation_period)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data/{data_id}/values"
    response = requests.get(
        url=url,
        params={
            "from": start_date_iso,
            "to": end_date_iso,
            "aggregation": aggregation,
            "number-of-values": number_of_values,
            "aggregation-period": aggregation_period_iso,
            "aggregation-function": aggregation_function,
            "unit-id": unit_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_vector_time_values(
    vector_data_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    index_unit_id: Optional[str] = None,
    value_unit_id: Optional[str] = None,
    aggregation: str = "RAW_VALUES",
    index_aggregation: str = "RAW_VALUES",
    aggregation_period: Optional[Union[str, timedelta, pd.Timedelta]] = None,
    max_number_of_points: Optional[int] = None,
    aggregation_function: Optional[str] = None,
    index_aggregation_function: Optional[str] = None,
    index_aggregation_step_type: Optional[str] = None,
    index_aggregation_step_value: Optional[float] = None,
    min_index: Optional[float] = None,
    max_index: Optional[float] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Format aggregation period
    aggregation_period_iso = utils.get_iso_period(aggregation_period)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/vector-data/{vector_data_id}/values"
    response = requests.get(
        url=url,
        params={
            "from": start_date_iso,
            "to": end_date_iso,
            "aggregation": aggregation,
            "aggregation-function": aggregation_function,
            "aggregation-period": aggregation_period_iso,
            "max-number-of-points": max_number_of_points,
            "index-aggregation": index_aggregation,
            "index-aggregation-function": index_aggregation_function,
            "index-aggregation-step-type": index_aggregation_step_type,
            "index-aggregation-step-value": index_aggregation_step_value,
            "min-index": min_index,
            "max-index": max_index,
            "index-unit-id": index_unit_id,
            "value-unit-id": value_unit_id,
        },
        **api_credentials.auth_kwargs,
    )
    # Output
    response.raise_for_status()
    return response.json()


def get_batch_values(
    data_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    number_of_values: Optional[int] = None,
    aggregation_period: Optional[Union[str, timedelta, pd.Timedelta]] = None,
    aggregation_function: Optional[str] = None,
    batch_type_id: Optional[str] = None,
    batch_index_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Format aggregation period
    aggregation_period_iso = utils.get_iso_period(aggregation_period)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data/{data_id}/values"
    response = requests.get(
        url=url,
        params={
            "from": start_date_iso,
            "to": end_date_iso,
            "aggregation": aggregation,
            "number-of-values": number_of_values,
            "aggregation-period": aggregation_period_iso,
            "aggregation-function": aggregation_function,
            "batch-type-id": batch_type_id,
            "batch-index-id": batch_index_id,
            "unit-id": unit_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_vector_batch_values(
    vector_data_id: str,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    batch_ids: Optional[List[str]] = None,
    aggregation: str = "RAW_VALUES",
    aggregation_period: Optional[Union[str, timedelta, pd.Timedelta]] = None,
    max_number_of_points: Optional[int] = None,
    aggregation_function: Optional[str] = None,
    index_aggregation: str = "RAW_VALUES",
    index_aggregation_function: Optional[str] = None,
    index_aggregation_step_type: Optional[str] = None,
    index_aggregation_step_value: Optional[float] = None,
    min_index: Optional[float] = None,
    max_index: Optional[float] = None,
    index_unit_id: Optional[str] = None,
    value_unit_id: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Format aggregation period
    aggregation_period_iso = utils.get_iso_period(aggregation_period)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/vector-data/{vector_data_id}/values"
    response = requests.get(
        url=url,
        params={
            "from": start_date_iso,
            "to": end_date_iso,
            "batch-ids": batch_ids,
            "aggregation": aggregation,
            "aggregation-function": aggregation_function,
            "aggregation-period": aggregation_period_iso,
            "max-number-of-points": max_number_of_points,
            "index-aggregation": index_aggregation,
            "index-aggregation-function": index_aggregation_function,
            "index-aggregation-step-type": index_aggregation_step_type,
            "index-aggregation-step-value": index_aggregation_step_value,
            "min-index": min_index,
            "max-index": max_index,
            "index-unit-id": index_unit_id,
            "value-unit-id": value_unit_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_multiple_data_values(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    data_id: Optional[Union[str, List[str]]] = None,
    data_reference: Optional[Union[str, List[str]]] = None,
    number_of_values: Optional[int] = None,
    aggregation_period: Optional[Union[str, timedelta, pd.Timedelta]] = None,
    aggregation_function: Optional[Union[str, List[str]]] = None,
    unit_id: Optional[Union[str, List[str]]] = None,
    unit_label: Optional[Union[str, List[str]]] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Validation
    if not (data_id is None) ^ (data_reference is None):
        raise ValueError(
            "One and only one argument 'data_id' or 'data_reference' should be provided"
        )

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)
    end_date_iso = utils.get_zulu_isoformat(end_date)

    # Format aggregation period
    aggregation_period_iso = utils.get_iso_period(aggregation_period)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data/values"
    response = requests.get(
        url=url,
        params={
            "data-id": data_id,
            "data-reference": data_reference,
            "from": start_date_iso,
            "to": end_date_iso,
            "aggregation": aggregation,
            "number-of-values": number_of_values,
            "aggregation-period": aggregation_period_iso,
            "aggregation-function": aggregation_function,
            "unit-id": unit_id,
            "unit-label": unit_label,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def insert_time_values(
    data: List[dict],
    use_external_reference: bool = False,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/value-upload/time-values"
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


def insert_vector_time_values(
    data: List[dict],
    use_external_reference: bool = False,
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/value-upload/vector-time-values"
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
