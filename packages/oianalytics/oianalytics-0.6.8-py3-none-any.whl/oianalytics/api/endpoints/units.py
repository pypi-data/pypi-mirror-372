from typing import Optional
import requests

from .. import _credentials


__all_ = ["get_units", "get_unit_families"]


def get_units(
    label: Optional[str] = None,
    quantity_id: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/units"
    response = requests.get(
        url=url,
        params={
            "page": page,
            "size": page_size,
            "label": label,
            "quantityId": quantity_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()


def get_unit_families(
    label: Optional[str] = None,
    main_unit_id: Optional[str] = None,
    quantity_id: Optional[str] = None,
    page: int = 0,
    page_size: int = 20,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> dict:
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/unit-families"
    response = requests.get(
        url=url,
        params={
            "page": page,
            "size": page_size,
            "label": label,
            "mainUnitId": main_unit_id,
            "quantityId": quantity_id,
        },
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
