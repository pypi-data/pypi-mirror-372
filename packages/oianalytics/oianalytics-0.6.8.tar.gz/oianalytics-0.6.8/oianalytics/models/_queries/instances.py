from typing import Optional
import requests

from ... import api

__all__ = ["invoke_instance"]


def invoke_instance(
    model_instance_id: str,
    custom_input_data=None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/python-model-instances/{model_instance_id}/invoke"
    response = requests.post(
        url=url,
        json=custom_input_data,
        **api_credentials.auth_kwargs,
    )

    # Output
    response.raise_for_status()
    return response.json()
