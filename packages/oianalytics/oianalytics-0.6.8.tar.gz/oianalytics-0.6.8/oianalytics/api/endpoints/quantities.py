from typing import Optional
import requests

from .. import _credentials


__all__ = ["get_quantities"]


def get_quantities(
    name: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/quantities"
    response = requests.get(
        url=url,
        params={"page": page, "size": page_size, "name": name},
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
