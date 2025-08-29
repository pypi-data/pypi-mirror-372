from typing import Optional, List, Union
from datetime import datetime
import io

import requests

from .. import _credentials
from .. import utils


__all__ = [
    "get_file_uploads",
    "get_file_upload_details",
    "get_file_from_file_upload",
    "upload_file",
]


def get_file_uploads(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    filename: Optional[str] = None,
    statuses: Optional[Union[str, List[str]]] = None,
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
    url = f"{api_credentials.base_url}/api/oianalytics/file-uploads"
    response = requests.get(
        url=url,
        params={
            "filename": filename,
            "statuses": statuses,
            "from": start_date_iso,
            "to": end_date_iso,
            "page": page,
            "size": page_size,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_file_upload_details(
    file_upload_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/file-uploads/{file_upload_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_file_from_file_upload(
    file_upload_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = (
        f"{api_credentials.base_url}/api/oianalytics/file-uploads/{file_upload_id}/file"
    )
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return io.BytesIO(response.content)


def upload_file(
    file_content: Union[io.StringIO, io.BytesIO],
    file_name: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/file-uploads"
    response = requests.post(
        url=url,
        files={"file": (file_name, file_content)},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
