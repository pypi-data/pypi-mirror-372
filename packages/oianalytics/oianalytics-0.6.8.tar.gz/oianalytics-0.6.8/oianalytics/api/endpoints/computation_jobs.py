from typing import Optional, List, Union
from datetime import datetime

import requests

from .. import _credentials
from .. import utils


__all__ = [
    "create_temporal_computation_jobs",
    "create_batch_computation_jobs",
    "create_event_computation_jobs",
]


def create_temporal_computation_jobs(
    data_id: str,
    start_date: Union[str, datetime],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Format dates
    start_date_iso = utils.get_zulu_isoformat(start_date)

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/computation-jobs/continuous-data"
    response = requests.post(
        url=url,
        json={"dataId": data_id, "start": start_date_iso},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def create_batch_computation_jobs(
    batch_type_id: str,
    data_ids: Optional[List[str]] = None,
    batch_ids: Optional[List[str]] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/computation-jobs/batch-data"
    response = requests.post(
        url=url,
        json={
            "batchStructureId": batch_type_id,
            "dataIds": data_ids,
            "batchIds": batch_ids,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def create_event_computation_jobs(
    event_type_id: str,
    data_ids: Optional[List[str]] = None,
    event_ids: Optional[List[str]] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/computation-jobs/event-data"
    response = requests.post(
        url=url,
        json={
            "eventTypeId": event_type_id,
            "dataIds": data_ids,
            "eventIds": event_ids,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def toto():
    pass
