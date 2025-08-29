from typing import Optional, Union, List, Literal
from datetime import datetime

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils

__all__ = [
    "get_event_types",
    "get_event_type_details",
    "create_event_type",
    "get_events",
    "create_or_update_events",
]


def get_event_types(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    extract_from_tag_keys: Optional[str] = "value",
    extract_from_context: Optional[str] = "value",
    expand_context: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get the configured event types from the OIAnalytics API

    Parameters
    ----------
    page: int, optional
        Page number to retrieve. If None, the first page will be retrieved.
        The argument is ignored if 'get_all_pages' is True.
    page_size: int, optional
        The size of each page to retrieve. By default, 20 elements are retrieved.
        The argument is ignored if 'get_all_pages' is True.
    get_all_pages: bool, default True
        If True, paging is ignored and all elements are retrieved.
    multithread_pages: bool, default True
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    extract_from_tag_keys: {'id', 'value', 'dict', None}, default 'value'
        What field should be extracted from tag keys information.
        If 'dict', a dictionary in the form of {id: value} is built. If None, the full dictionary is kept.
    extract_from_context: {'id', 'value', None}, default 'value'
        What field should be extracted from context information. If None, the full dictionary is kept.
    expand_context: bool, default True
        Whether or not the context should be expanded into multiple columns.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pandas.DataFrame
        A DataFrame listing event types.
    """

    # Args validation
    if extract_from_tag_keys not in ["id", "value", "dict", None]:
        raise ValueError(
            f"Unexpected value for 'extract_from_tag_keys': {extract_from_tag_keys}"
        )

    if extract_from_context not in ["id", "value", None]:
        raise ValueError(
            f"Unexpected value for 'extract_from_context': {extract_from_context}"
        )

    if expand_context is True and extract_from_context is None:
        raise ValueError("Context cannot be expanded if 'extract_from_context' is None")

    # Init
    if get_all_pages is True:
        page = 0
        page_size = 500

    def get_page(page_num: int):
        page_response = endpoints.events.get_event_types(
            page=page_num, page_size=page_size, api_credentials=api_credentials
        )
        return page_response

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])

        # Expected columns if content is empty
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(columns=["id", "name", "tagKeys", "tagContext"])

        # Extract from tag keys
        if extract_from_tag_keys == "id":
            page_df["tagKeys"] = page_df["tagKeys"].apply(
                lambda l: [tk["id"] for tk in l]
            )
        elif extract_from_tag_keys == "value":
            page_df["tagKeys"] = page_df["tagKeys"].apply(
                lambda l: [tk["key"] for tk in l]
            )
        elif extract_from_tag_keys == "dict":
            page_df["tagKeys"] = page_df["tagKeys"].apply(
                lambda l: {tk["id"]: tk["key"] for tk in l}
            )

        # Extract from context
        if extract_from_context == "id":
            page_df["tagContext"] = page_df["tagContext"].apply(
                lambda context: {
                    c["tagKey"]["id"]: [atv["id"] for atv in c["accessibleTagValues"]]
                    for c in context
                }
            )
        elif extract_from_context == "value":
            page_df["tagContext"] = page_df["tagContext"].apply(
                lambda context: {
                    c["tagKey"]["key"]: [
                        atv["value"] for atv in c["accessibleTagValues"]
                    ]
                    for c in context
                }
            )

        if expand_context is True and extract_from_context is not None:
            page_df = utils.expand_dataframe_column(
                page_df, "tagContext", add_prefix=False
            )

        page_df.set_index("id", inplace=True)
        return page_df

    # Query endpoint
    df = utils.concat_pages_to_dataframe(
        getter=get_page,
        parser=parse_page,
        page=page,
        get_all_pages=get_all_pages,
        multithread_pages=multithread_pages,
    )

    # Output
    return df


def get_event_type_details(
    event_type_id: str,
    extract_from_tag_keys: Literal["id", "key", None] = "key",
    extract_from_asset_types: Literal["id", "name", None] = "name",
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Get the detail of an event type by its OIAnalytics ID.

    Parameters
    ----------
    event_type_id : str
        The ID of the event type to retrieve.
    extract_from_tag_keys : {'id', 'key', None}, default 'key'
        Key to be associated from the column 'tagKeys'.
    extract_from_asset_types : {'id', 'name', None}, default 'name'
        Key to be associated from the column 'assetTypes'.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        Details of the event type.
    """

    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = _credentials.get_default_oianalytics_credentials()

    dict_response = endpoints.events.get_event_type_details(
        event_type_id=event_type_id,
        api_credentials=api_credentials,
    )

    ser = pd.Series(dict_response, dtype=object)

    if extract_from_tag_keys is not None:
        ser.loc["tagKeys"] = [
            tag_key[extract_from_tag_keys] for tag_key in ser.loc["tagKeys"]
        ]

    if extract_from_asset_types is not None:
        ser.loc["assetTypes"] = [
            tag_key[extract_from_asset_types] for tag_key in ser.loc["assetTypes"]
        ]

    # Output
    return ser


def create_event_type(
    name: str,
    asset_type_ids: List[str],
    tag_keys: List[dict],
    tag_context: List[dict],
    extract_from_tag_keys: Literal["id", "key", None] = "key",
    extract_from_asset_types: Literal["id", "name", None] = "name",
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.Series:
    """
    Create an event type.

    Parameters
    ----------
    name : str
        The name of the event type to create.
    asset_type_ids : list of str
        The IDs of the types of asset that can fire this type of event.
    tag_keys : list of dict
        The array of source tag keys to create on the event type.
    tag_context : list of dict
        The array of tag access to attach to the event type to restrict access of users.
    extract_from_tag_keys : {'id', 'key', None}, default 'key'
        Key to be associated from the column 'tagKeys'.
    extract_from_asset_types : {'id', 'name', None}, default 'name'
        Key to be associated from the column 'assetTypes'.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series
        Details of the event that has been created.
    """

    dict_response = endpoints.events.create_event_type(
        name=name,
        asset_type_ids=asset_type_ids,
        tag_keys=tag_keys,
        tag_context=tag_context,
        api_credentials=api_credentials,
    )

    ser = pd.Series(dict_response, dtype=object)

    if extract_from_tag_keys is not None:
        ser.loc["tagKeys"] = [
            tag_key[extract_from_tag_keys] for tag_key in ser.loc["tagKeys"]
        ]

    if extract_from_asset_types is not None:
        ser.loc["assetTypes"] = [
            tag_key[extract_from_asset_types] for tag_key in ser.loc["assetTypes"]
        ]

    # Output
    return ser


def get_events(
    event_type_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    description: Optional[str] = None,
    features_value_ids: Optional[Union[str, List[str]]] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    expand_event_type: bool = True,
    extract_from_features: Optional[str] = "key",
    expand_features: bool = True,
    extract_from_values: Optional[str] = "reference",
    append_unit_to_description: bool = True,
    extract_from_assets: Optional[str] = "name",
    expand_values: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get event instances from the OIAnalytics API

    Parameters
    ----------
    event_type_id: str
        The id of the event type to be retrieved
    start_date: datetime or str
        The beginning of the period to be retrieved
    end_date: datetime or str
        The end of the period to be retrieved
    description: str, optional
        A string that should be contained by all events description returned
    features_value_ids: str or list of str, optional
        Possibly multiple feature value ids each returned event should match.
        If for a given feature multiple feature value ids are provided than a event will be returned if it
        contains one of them.
    page: int, optional
        Page number to retrieve. If None, the first page will be retrieved.
        The argument is ignored if 'get_all_pages' is True.
    page_size: int, optional
        The size of each page to retrieve. By default, 20 elements are retrieved.
        The argument is ignored if 'get_all_pages' is True.
    get_all_pages: bool, default True
        If True, paging is ignored and all elements are retrieved.
    multithread_pages: bool, default False
        Only used when getting all pages. If True, pages are retrieved in multiple threads simultaneously.
    expand_event_type: bool, default True
        Whether or not the event type information should be expanded into multiple columns.
    extract_from_features: {'id', 'value', None}, default 'value'
        What field should be extracted from features information. If None, the full dictionary is kept.
    expand_features: bool, default True
        Whether or not the features should be expanded into multiple columns.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing event dates, data and features values.
    """

    # Args validation
    if extract_from_features not in ["id", "key", None]:
        raise ValueError(
            f"Unexpected value for 'extract_from_features': {extract_from_features}"
        )

    if expand_features is True and extract_from_features is None:
        raise ValueError(
            "Features cannot be expanded if 'extract_from_features' is None"
        )

    # Init
    if get_all_pages is True:
        page = 0
        page_size = 500

    def get_page(page_num: int):
        page_response = endpoints.events.get_events(
            event_type_id=event_type_id,
            start_date=start_date,
            end_date=end_date,
            description=description,
            features_value_ids=features_value_ids,
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )
        return page_response

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])

        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=[
                    "id",
                    "eventType",
                    "description",
                    "start",
                    "end",
                    "duration",
                    "tagValues",
                    "values",
                    "assets",
                ]
            )

        # Format dataframe
        if expand_event_type is True:
            page_df = utils.expand_dataframe_column(
                page_df, "eventType", expected_keys=["id", "name"]
            )

        if extract_from_features == "id":
            page_df["tagValues"] = page_df["tagValues"].apply(
                lambda fl: {f["eventTagKey"]["id"]: f["value"] for f in fl}
            )
        elif extract_from_features == "key":
            page_df["tagValues"] = page_df["tagValues"].apply(
                lambda fl: {f["eventTagKey"]["key"]: f["value"] for f in fl}
            )

        if expand_features is True and extract_from_features is not None:
            page_df = utils.expand_dataframe_column(
                page_df, "tagValues", add_prefix=False
            )

        # Format values
        if extract_from_values == "id":
            page_df["values"] = page_df["values"].apply(
                lambda values: {val["data"]["id"]: val["value"] for val in values}
            )
        elif extract_from_values == "reference":
            page_df["values"] = page_df["values"].apply(
                lambda values: {
                    val["data"]["reference"]: val["value"] for val in values
                }
            )
        elif extract_from_values == "description":
            if append_unit_to_description is True:
                page_df["values"] = page_df["values"].apply(
                    lambda values: {
                        f'{val["data"]["description"]} ({val["unit"]["label"]})': val[
                            "value"
                        ]
                        for val in values
                    }
                )
            else:
                page_df["values"] = page_df["values"].apply(
                    lambda values: {
                        val["data"]["description"]: val["value"] for val in values
                    }
                )

        if expand_values is True and extract_from_values is not None:
            page_df = utils.expand_dataframe_column(page_df, "values", add_prefix=False)

        # Format assets
        if extract_from_assets is not None:
            page_df["assets"] = page_df["assets"].apply(
                lambda assets: [asset[extract_from_assets] for asset in assets]
            )

        page_df.set_index("id", inplace=True)

        # Output
        return page_df

    # Query endpoint
    df = utils.concat_pages_to_dataframe(
        getter=get_page,
        parser=parse_page,
        page=page,
        get_all_pages=get_all_pages,
        multithread_pages=multithread_pages,
    )

    # Dates
    df["start"] = pd.to_datetime(df["start"], format="ISO8601")
    df["end"] = pd.to_datetime(df["end"], format="ISO8601")

    # Output
    return df


def create_or_update_events(
    event_type_id: str,
    events: pd.DataFrame,
    value_columns: List[str] = [],
    feature_columns: List[str] = [],
    asset_column: Optional[List[dict]] = None,
    values_unit_ids: Optional[dict] = None,
    start_date_name: str = "start",
    end_date_name: str = "end",
    description_name: str = "description",
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Create or update events, with values and features

    Parameters
    ----------
    event_type_id: str
        The id of the batch type to be retrieved.
    events: pd.DataFrame
        The values to update or insert. The DataFrame must be indexed by index id.
        Each column is named after the data or feature ID.
    value_columns: list of strings, default []
        The list of columns containing event data values.
    feature_columns: list of strings, default []
        The list of columns containing event feature values.
    asset_column: str, optional, default None
        The name of the column containing assets.
    values_unit_ids: dict, optional
        A dictionary where keys are data IDs and values are the corresponding unit IDs
    start_date_name: str, default 'start'
        The name of the column containing the start date of the steps id in the steps DataFrame
    end_date_name: str, default 'end'
        The name of the column containing the end date of the steps id in the steps DataFrame
    description_name: string, default 'description'
        The name of the column containing the events description
    create_upload_event: bool, default True
        Whether to create an upload event with updated values.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A dictionary of the response from the API, containing the list of created or updated events
    """

    # Init
    if values_unit_ids is None:
        values_unit_ids = {}

    # Serialization function
    def build_single_event_payload(event: pd.Series):
        # Init
        event_command = {
            "id": None if pd.isna(event.name) else event.name,
            "start": utils.get_zulu_isoformat(event[start_date_name]),
            "end": utils.get_zulu_isoformat(event[end_date_name]),
            "description": event[description_name],
            "tagValues": [
                {"tagKeyId": feat, "tagValueValue": event[feat]}
                for feat in feature_columns
            ],
            "values": [
                {
                    "dataId": val,
                    "value": None if pd.isna(event[val]) else event[val],
                    "unitId": values_unit_ids.get(val),
                }
                for val in value_columns
            ],
            "assetIds": None if asset_column is None else event[asset_column],
        }

        return event_command

    # Build payload
    payload = events.apply(build_single_event_payload, axis=1).to_list()

    # Query endpoint
    response = endpoints.events.create_or_update_events(
        event_type_id=event_type_id,
        events=payload,
        create_upload_event=create_upload_event,
        api_credentials=api_credentials,
    )

    # Output
    return response
