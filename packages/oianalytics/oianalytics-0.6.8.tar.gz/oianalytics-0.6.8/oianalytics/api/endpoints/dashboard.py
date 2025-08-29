import requests
from typing import Optional, Literal

from .. import _credentials


__all__ = ["get_dashboards", "get_single_dashboard"]


def get_dashboards(
    page: int = 0,
    page_size: int = 20,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/dashboard"
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


def get_single_dashboard(
    dashboard_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/dashboard/{dashboard_id}"
    response = requests.get(
        url=url,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
