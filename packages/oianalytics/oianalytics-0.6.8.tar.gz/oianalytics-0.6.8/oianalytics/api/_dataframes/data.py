from typing import Optional, Union, List
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils

__all__ = [
    "get_data_list",
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
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    expand_measurement: bool = True,
    extract_from_storage_unit: Optional[str] = "label",
    extract_from_tags: Optional[str] = "value",
    expand_tags: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get the configured data from the OIAnalytics API

    Parameters
    ----------
    query: str, optional
        A text to search for specific data
    types: list of str, optional
        An array of types to search for specific data types. If omitted then all types are considered.
    measurement_id: str, optional
        The measurement id all data should have. Cannot be used in conjunction with 'measurement_name'.
    measurement_name: str, optional
        The measurement name all data should have. Cannot be used in conjunction with 'measurement_id'.
    tag_value_id: list of str, optional
        An array of tag value ids the data should have.
    include_technical_data: bool, default False
        Whether to include the technical data.
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
    expand_measurement: bool, default True
        Whether the measurement information should be expanded into multiple columns.
    extract_from_storage_unit: {'id', 'label', None}, default 'label'
        What field should be extracted from storage unit information. If None, the full dictionary is kept.
    extract_from_tags: {'id', 'value', None}, default 'value'
        What field should be extracted for naming tags. If None, the full dictionary is kept.
    expand_tags: bool, default True
        Whether tags should be expanded into multiple columns.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A DataFrame listing data and their properties
    """

    # Args validation
    if extract_from_storage_unit not in ["id", "label", None]:
        raise ValueError(
            f"Unexpected value for 'extract_from_storage_unit': {extract_from_storage_unit}"
        )

    if extract_from_tags not in ["id", "value", None]:
        raise ValueError(
            f"Unexpected value for 'extract_from_tags': {extract_from_tags}"
        )

    # Init
    if get_all_pages is True:
        page = 0
        page_size = 500

    def get_page(page_num: int):
        page_response = endpoints.data.get_data_list(
            query=query,
            types=types,
            measurement_id=measurement_id,
            measurement_name=measurement_name,
            tag_value_id=tag_value_id,
            include_technical_data=include_technical_data,
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )
        return page_response

    def parse_page(page_response: dict):
        page_df = pd.DataFrame(page_response["content"])

        # Expected columns if content is empty
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=[
                    "dataType",
                    "id",
                    "reference",
                    "description",
                    "measurement",
                    "tags",
                ]
            )

        # Format dataframe
        if expand_measurement is True:
            page_df = utils.expand_dataframe_column(
                page_df,
                "measurement",
                expected_keys=[
                    "id",
                    "name",
                    "storageUnit",
                    "defaultUnitFamily",
                    "quantityName",
                ],
            )

            if extract_from_storage_unit == "id":
                page_df["measurement_storageUnit"] = page_df[
                    "measurement_storageUnit"
                ].apply(lambda su: su["id"])
            elif extract_from_storage_unit == "label":
                page_df["measurement_storageUnit"] = page_df[
                    "measurement_storageUnit"
                ].apply(lambda su: su["label"])

        # Extract from tags
        if extract_from_tags == "id":
            page_df["tags"] = page_df["tags"].apply(
                lambda tl: {t["tagKey"]["id"]: t["id"] for t in tl}
            )
        elif extract_from_tags == "value":
            page_df["tags"] = page_df["tags"].apply(
                lambda tl: {t["tagKey"]["key"]: t["value"] for t in tl}
            )

        if expand_tags is True and extract_from_tags is not None:
            page_df = utils.expand_dataframe_column(page_df, "tags", add_prefix=False)

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


def get_time_values(
    data_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    number_of_values: Optional[int] = None,
    aggregation_period: Optional[str] = None,
    aggregation_function: Optional[str] = None,
    unit_id: Optional[str] = None,
    name_data_from: str = "reference",
    append_unit_to_description: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get values from a temporal data from the OIAnalytics API

    Parameters
    ----------
    data_id: str
        The data id on which values are to be retrieved
    start_date: datetime or str
        The beginning of the period to be retrieved
    end_date: datetime or str
        The end of the period to be retrieved
    aggregation: {'RAW_VALUES', 'TIME'}
        How to aggregate the values. If 'TIME', aggregation period and function should be specified.
    number_of_values: int, optional
        If > 0 returns only the number of values specified. Only works for stored data.
    aggregation_period: str, optional
        Required in case 'aggregation' is 'TIME' and is the sampling period of the expected result.
        This period should be an ISO period as described in https://en.wikipedia.org/wiki/ISO_8601#Durations
    aggregation_function: str, optional
        Required in case 'aggregation' is 'TIME' and is the aggregation function to use to aggregate the values within
        the sampling period.
        Possible values are 'FIRST', 'LAST', 'LAST_MINUS_FIRST', 'SUM', 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STDEV',
        'PERCENTILE5', 'PERCENTILE95', 'DECILE1', 'DECILE9', 'QUARTILE1', 'QUARTILE9', 'COUNT', 'MEAN_MINUS_SIGMA',
        'MEAN_PLUS_SIGMA', 'MEAN_MINUS_TWO_SIGMA', 'MEAN_PLUS_TWO_SIGMA', 'MEAN_MINUS_THREE_SIGMA',
        'MEAN_PLUS_THREE_SIGMA', 'VALUE_CHANGE'.
    unit_id: str, optional
        The id of the unit to use to express the values. If not present a default unit will be used.
        This unit should be compatible with the physical quantity of the data queried.
    name_data_from: {'id', 'reference', 'description'}
        What field should be extracted for naming data.
    append_unit_to_description: bool, default True
        Only used when 'name_data_from' is 'description'. If True, the unit is added after the description.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A Series containing the values of the data, indexed by 'timestamp'
    """

    # Args validation
    if name_data_from not in ["id", "reference", "description"]:
        raise ValueError(f"Unexpected value for 'name_data_from': {name_data_from}")

    # Query endpoint
    data = endpoints.data.get_time_values(
        data_id=data_id,
        start_date=start_date,
        end_date=end_date,
        aggregation=aggregation,
        number_of_values=number_of_values,
        aggregation_period=aggregation_period,
        aggregation_function=aggregation_function,
        unit_id=unit_id,
        api_credentials=api_credentials,
    )

    # Format series
    if name_data_from == "id":
        data_name = data["data"]["id"]
    elif name_data_from == "reference":
        data_name = data["data"]["reference"]
    elif name_data_from == "description":
        data_name = data["data"]["description"]
        if append_unit_to_description is True:
            data_name = f'{data_name} ({data["unit"]["label"]})'
    else:
        raise ValueError(f"Unexpected value for 'name_data_from': {name_data_from}")

    if len(data["values"]) == 0:
        timestamp_index = pd.to_datetime(
            data["timestamps"], format="ISO8601"
        ).tz_localize("UTC")
    else:
        timestamp_index = pd.to_datetime(data["timestamps"], format="ISO8601")

    ser = pd.Series(
        name=data_name,
        index=timestamp_index,
        data=data["values"],
        dtype=float if len(data["values"]) == 0 else None,
    )

    ser.index.name = "timestamp"

    # Output
    return ser


def get_vector_time_values(
    vector_data_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
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
    index_unit_id: Optional[str] = None,
    value_unit_id: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> Union[pd.DataFrame, pd.Series]:
    """
    Get values from a vector temporal data from the OIAnalytics API

    Parameters
    ----------
    vector_data_id: string
        The data id on which values are to be retrieved
    start_date: datetime or string
        The beginning of the period to be retrieved
    end_date: datetime or string
        The end of the period to be retrieved
    index_unit_id: string, optional
        The id of the unit to express the index data set. If not present a default unit will be used.
        This unit should be compatible with the physical quantity of the data's index queried.
    value_unit_id: string, optional
        The id of the unit to express the values. If not presented, a default unit will be used.
        This unit should be compatible with the physical quantity of the data queried.
    aggregation: string {'RAW_VALUES', 'TIME', 'GLOBAL'}
        How to aggregate the values by time. If 'TIME', aggregation period and function should be specified.
    index_aggregation: string {'RAW_VALUES', 'RESAMPLE', 'GLOBAL'}
        How to aggregate the values by index.
        If 'RESAMPLE', index aggregation function, step type and step value should be specified.
        If 'GLOBAL', index aggregation function should be specified.
    aggregation_function: string, optional
        Required in case 'aggregation' is 'TIME' and is the aggregation function to use to aggregate the values within
        the sampling period.
        Possible values are: 'FIRST', 'LAST', 'LAST_MINUS_FIRST', 'SUM', 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STDEV',
        'PERCENTILE5', 'PERCENTILE95', 'DECILE1', 'DECILE9', 'QUARTILE1', 'QUARTILE9', 'COUNT', 'MEAN_MINUS_SIGMA',
        'MEAN_PLUS_SIGMA', 'MEAN_MINUS_TWO_SIGMA', 'MEAN_PLUS_TWO_SIGMA', 'MEAN_MINUS_THREE_SIGMA',
        'MEAN_PLUS_THREE_SIGMA', 'VALUE_CHANGE', 'UNIQUE', 'WEIGHTED_AVERAGE'.
    aggregation_period: string, optional
        Required in case 'aggregation' is 'TIME' and is the sampling period of the expected result.
        This period should be an ISO period as described in https://en.wikipedia.org/wiki/ISO_8601#Durations
    max_number_of_points: integer, optional
        The number of time intervals between 'start_date' and 'end_date'
    index_aggregation_function: string, optional
        Defines the index aggregation function
    index_aggregation_step_type: string, optional
        Method to define the interval for index aggregation; acceptable values: {"INTERVAL", "NUMBER_OF_POINTS"}.
    index_aggregation_step_value: float or int, optional
        Or index interval or number of points used for index aggregation, according to the choice of 'index_aggregation_step_type'.
    min_index: float, optional
        The minimum index value to be presented.
    max_index: float, optional
        The maximum index value to be presented.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A Series containing the values of the data, indexed by 'timestamps'
    """

    # Query endpoint
    data = endpoints.data.get_vector_time_values(
        vector_data_id=vector_data_id,
        start_date=start_date,
        end_date=end_date,
        index_unit_id=index_unit_id,
        value_unit_id=value_unit_id,
        aggregation=aggregation,
        index_aggregation=index_aggregation,
        aggregation_period=aggregation_period,
        max_number_of_points=max_number_of_points,
        aggregation_function=aggregation_function,
        index_aggregation_function=index_aggregation_function,
        index_aggregation_step_type=index_aggregation_step_type,
        index_aggregation_step_value=index_aggregation_step_value,
        min_index=min_index,
        max_index=max_index,
        api_credentials=api_credentials,
    )

    if data["type"] == "vector-time-values":
        df = pd.DataFrame(
            columns=data["indexes"],
            data=data["values"],
            dtype=float if len(data["values"]) == 0 else None,
        )
    elif data["type"] == "vector-time-range-values":
        dfs_list = []
        keys = []
        for key in ["lows", "values", "highs"]:
            if len(data[key]) > 0:
                dfs_list.append(
                    pd.DataFrame(
                        columns=data["indexes"],
                        data=data[key],
                        dtype=float if len(data[key]) == 0 else None,
                    )
                )
                keys.append(key)
        df = pd.concat(dfs_list, axis=1, keys=keys)
    elif data["type"] == "time-values":
        df = pd.Series(
            data=data["values"],
            dtype=float if len(data["values"]) == 0 else None,
        )
    elif data["type"] == "time-range-value":
        series_list = []
        cols = []
        for col in ["lows", "values", "highs"]:
            if len(data[col]) > 0:
                series_list.append(
                    pd.Series(
                        data=data[col],
                        dtype=float if len(data["values"]) == 0 else None,
                    )
                )
                cols.append(col)
        if len(cols) == 0:
            df = pd.DataFrame()
        else:
            df = pd.concat(series_list, axis=1, keys=cols)

    if len(data["values"]) == 0:
        df.index = pd.to_datetime(data["timestamps"], format="ISO8601").tz_localize(
            "UTC"
        )
    else:
        df.index = pd.to_datetime(data["timestamps"], format="ISO8601")

    df.index.name = "timestamp"

    # Output
    return df


def get_batch_values(
    data_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    number_of_values: Optional[int] = None,
    aggregation_period: Optional[str] = None,
    aggregation_function: Optional[str] = None,
    batch_type_id: Optional[str] = None,
    batch_index_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    name_data_from: str = "reference",
    append_unit_to_description: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get values from a batch data from the OIAnalytics API

    Parameters
    ----------
    data_id: str
        The data id on which values are to be retrieved
    start_date: datetime or str
        The beginning of the period to be retrieved
    end_date: datetime or str
        The end of the period to be retrieved
    aggregation: {'RAW_VALUES', 'TIME'}
        How to aggregate the values. If 'TIME', aggregation period and function should be specified.
    number_of_values: int, optional
        If > 0 returns only the number of values specified. Only works for stored data.
    aggregation_period: str, optional
        Required in case 'aggregation' is 'TIME' and is the sampling period of the expected result.
        This period should be an ISO period as described in https://en.wikipedia.org/wiki/ISO_8601#Durations
    aggregation_function: str, optional
        Required in case 'aggregation' is 'TIME' and is the aggregation function to use to aggregate the values within
        the sampling period.
        Possible values are 'FIRST', 'LAST', 'LAST_MINUS_FIRST', 'SUM', 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STDEV',
        'PERCENTILE5', 'PERCENTILE95', 'DECILE1', 'DECILE9', 'QUARTILE1', 'QUARTILE9', 'COUNT', 'MEAN_MINUS_SIGMA',
        'MEAN_PLUS_SIGMA', 'MEAN_MINUS_TWO_SIGMA', 'MEAN_PLUS_TWO_SIGMA', 'MEAN_MINUS_THREE_SIGMA',
        'MEAN_PLUS_THREE_SIGMA', 'VALUE_CHANGE'.
    batch_type_id: str, optional
        The id of the batch type that should be used to query the values.
        If not present the batch type of the data will be used.
        This batch type should be compatible with the data batch type e.g. it should exist a genealogy between this
        batch type and the batch type of the data.
    batch_index_id: str, optional
        The id of the batch timestamp index that should be used to query the values.
        If not present the batch timestamp will be used. The batch index should belong to the batch type
    unit_id: str, optional
        The id of the unit to use to express the values. If not present a default unit will be used.
        This unit should be compatible with the physical quantity of the data queried.
    name_data_from: {'id', 'reference', 'description'}
        What field should be extracted for naming data.
    append_unit_to_description: bool, default True
        Only used when 'name_data_from' is 'description'. If True, the unit is added after the description.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A Series containing the values of the data, indexed by 'batch_id', 'batch_name', 'batch_timestamp'
    """

    # Args validation
    if name_data_from not in ["id", "reference", "description"]:
        raise ValueError(f"Unexpected value for 'name_data_from': {name_data_from}")

    # Query endpoint
    data = endpoints.data.get_batch_values(
        data_id=data_id,
        start_date=start_date,
        end_date=end_date,
        aggregation=aggregation,
        number_of_values=number_of_values,
        aggregation_period=aggregation_period,
        aggregation_function=aggregation_function,
        batch_type_id=batch_type_id,
        batch_index_id=batch_index_id,
        unit_id=unit_id,
        api_credentials=api_credentials,
    )

    # Format series
    if name_data_from == "id":
        data_name = data["data"]["id"]
    elif name_data_from == "reference":
        data_name = data["data"]["reference"]
    elif name_data_from == "description":
        data_name = data["data"]["description"]
        if append_unit_to_description is True:
            data_name = f'{data_name} ({data["unit"]["label"]})'
    else:
        raise ValueError(f"Unexpected value for 'name_data_from': {name_data_from}")

    data_type = data["type"]

    if len(data["values"]) == 0:
        timestamp_index = pd.to_datetime(
            data["timestamps"], format="ISO8601"
        ).tz_localize("UTC")
    else:
        timestamp_index = pd.to_datetime(data["timestamps"], format="ISO8601")

    ser = pd.Series(
        name=data_name,
        index=[data["batchIds"], data["batchNames"], timestamp_index]
        if data_type == "batch-values"
        else timestamp_index,
        data=data["values"],
        dtype=float if len(data["values"]) == 0 else None,
    )

    if data_type == "batch-values":
        ser.index.names = ["batch_id", "batch_name", "batch_timestamp"]
    else:
        ser.index.name = "timestamp"

    # Output
    return ser


def get_vector_batch_values(
    vector_data_id: str,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
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
    batch_ids: Optional[List[str]] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> Union[pd.DataFrame, pd.Series]:
    """
    Get values from a vector temporal data from the OIAnalytics API

    Parameters
    ----------
    vector_data_id: string
        The data id on which values are to be retrieved
    start_date: datetime or string, optional
        The beginning of the period to be retrieved
    end_date: datetime or string, optional
        The end of the period to be retrieved
    index_unit_id: string
        The id of the unit to express the index data set. If not present a default unit will be used.
        This unit should be compatible with the physical quantity of the data's index queried.
    value_unit_id: string
        The id of the unit to express the values. If not presented, a default unit will be used.
        This unit should be compatible with the physical quantity of the data queried.
    aggregation: string {'RAW_VALUES', 'TIME'}
        How to aggregate the values by time. If 'TIME', aggregation period and function should be specified.
    index_aggregation: string, optional {'RAW_VALUES', 'RESAMPLE', 'GLOBAL'}
        How to aggregate the values by index.
        If 'RESAMPLE', index aggregation function, step type and step value should be specified.
        If 'GLOBAL', index aggregation function should be specified.
    aggregation_function: string, optional
        Required in case 'aggregation' is 'TIME' and is the aggregation function to use to aggregate the values within
        the sampling period.
        Possible values are: 'FIRST', 'LAST', 'LAST_MINUS_FIRST', 'SUM', 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STDEV',
        'PERCENTILE5', 'PERCENTILE95', 'DECILE1', 'DECILE9', 'QUARTILE1', 'QUARTILE9', 'COUNT', 'MEAN_MINUS_SIGMA',
        'MEAN_PLUS_SIGMA', 'MEAN_MINUS_TWO_SIGMA', 'MEAN_PLUS_TWO_SIGMA', 'MEAN_MINUS_THREE_SIGMA',
        'MEAN_PLUS_THREE_SIGMA', 'VALUE_CHANGE', 'UNIQUE', 'WEIGHTED_AVERAGE'.
    aggregation_period: string, optional
        Required in case 'aggregation' is 'TIME' and is the sampling period of the expected result.
        This period should be an ISO period as described in https://en.wikipedia.org/wiki/ISO_8601#Durations
    max_number_of_points: integer greater or equal to 1
        Maximum number of points inside the time interval after aggregation
    index_aggregation_function: string, optional
        Defines the index aggregation function
    index_aggregation_step_type: string, optional
        Method to define the interval for index aggregation; acceptable values: {"INTERVAL", "NUMBER_OF_POINTS"}.
    index_aggregation_step_value: float or int, optional
        Or index interval or number of points used for index aggregation, according to the choice of 'index_aggregation_step_type'.
    min_index: float, optional
        The minimum index value to be presented.
    max_index: float, optional
        The maximum index value to be presented.
    batch_ids: list of strings
        A list containing the batch ids
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A DataFrame or a Series containing the values of the data, indexed by <'batches-ids' and 'batches-names'> and / or only by <'timestamps'>.
    """

    # Query endpoint
    data = endpoints.data.get_vector_batch_values(
        vector_data_id=vector_data_id,
        start_date=start_date,
        end_date=end_date,
        batch_ids=batch_ids,
        aggregation=aggregation,
        index_aggregation=index_aggregation,
        aggregation_period=aggregation_period,
        aggregation_function=aggregation_function,
        max_number_of_points=max_number_of_points,
        index_aggregation_function=index_aggregation_function,
        index_aggregation_step_type=index_aggregation_step_type,
        index_aggregation_step_value=index_aggregation_step_value,
        min_index=min_index,
        max_index=max_index,
        index_unit_id=index_unit_id,
        value_unit_id=value_unit_id,
        api_credentials=api_credentials,
    )

    if len(data["values"]) == 0:
        timestamp_index = pd.to_datetime(
            data["timestamps"], format="ISO8601"
        ).tz_localize("UTC")
    else:
        timestamp_index = pd.to_datetime(data["timestamps"], format="ISO8601")

    if data["type"] in [
        "batch-vector-range-value",
        "batch-range-value",
        "vector-batch-values",
        "batch-values",
    ]:
        df_index = [data["batchIds"], data["batchNames"], timestamp_index]
        df_index_name = ["batch_id", "batch_name", "timestamp"]
    elif data["type"] in [
        "time-vector-range-value",
        "time-range-value",
        "vector-time-values",
        "time-values",
    ]:
        df_index = timestamp_index
        df_index_name = "timestamp"

    if data["type"] in ["vector-batch-values", "vector-time-values"]:
        df = pd.DataFrame(
            columns=data["indexes"],
            data=data["values"],
            dtype=float if len(data["values"]) == 0 else None,
        )
    elif data["type"] in ["time-values", "batch-values"]:
        df = pd.Series(
            data=data["values"],
            dtype=float if len(data["values"]) == 0 else None,
        )
    elif data["type"] in ["time-vector-range-value", "batch-vector-range-value"]:
        dfs_list = []
        keys = []
        for key in ["lows", "values", "highs"]:
            if len(data[key]) > 0:
                dfs_list.append(
                    pd.DataFrame(
                        columns=data["indexes"],
                        data=data[key],
                        dtype=float if len(data[key]) == 0 else None,
                    )
                )
                keys.append(key)
        df = pd.concat(dfs_list, axis=1, keys=keys)
    elif data["type"] in ["time-range-value", "batch-range-value"]:
        series_list = []
        cols = []
        for col in ["lows", "values", "highs"]:
            if len(data[col]) > 0:
                series_list.append(
                    pd.Series(
                        data=data[col],
                        dtype=float if len(data["values"]) == 0 else None,
                    )
                )
                cols.append(col)
        df = pd.concat(series_list, axis=1, keys=cols)

    df.index = df_index
    df.index.names = df_index_name

    # Output
    return df


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
    name_data_from: str = "reference",
    append_unit_to_description: bool = True,
    join_series_on: Optional[str] = "index",
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get values from multiple data at once from the OIAnalytics API

    Parameters
    ----------
    start_date: datetime or str
        The beginning of the period to be retrieved
    end_date: datetime or str
        The end of the period to be retrieved
    aggregation: {'RAW_VALUES', 'TIME'}
        How to aggregate the values. If 'TIME', aggregation period and function should be specified.
    data_id: str or list of str, optional
        The array of data id to query. Required if 'data_reference' is None.
    data_reference: str or list of str, optional
        The array of data reference to query. Required if 'data_id' is None.
    number_of_values: int, optional
        If > 0 returns only the number of values specified. Only works for stored data.
    aggregation_period: str, optional
        Required in case 'aggregation' is 'TIME' and is the sampling period of the expected result.
        This period should be an ISO period as described in https://en.wikipedia.org/wiki/ISO_8601#Durations
    aggregation_function: str, optional
        Required in case 'aggregation' is 'TIME' and is the aggregation function to use to aggregate the values within
        the sampling period.
        Possible values are 'FIRST', 'LAST', 'LAST_MINUS_FIRST', 'SUM', 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STDEV',
        'PERCENTILE5', 'PERCENTILE95', 'DECILE1', 'DECILE9', 'QUARTILE1', 'QUARTILE9', 'COUNT', 'MEAN_MINUS_SIGMA',
        'MEAN_PLUS_SIGMA', 'MEAN_MINUS_TWO_SIGMA', 'MEAN_PLUS_TWO_SIGMA', 'MEAN_MINUS_THREE_SIGMA',
        'MEAN_PLUS_THREE_SIGMA', 'VALUE_CHANGE'.
    unit_id: str or list of str, optional
        The array of unit id to use to express the values. If not present a default unit will be used.
        All units should be compatible with the physical quantity of the data queried.
        If provided should be the same size as the 'data_id' or 'data_reference' array.
        It cannot be used in conjunction with 'unit_label'.
    unit_label: str or list of str, optional
        The array of unit label to use to express the values. If not present a default unit will be used.
        All units should be compatible with the physical quantity of the data queried.
        If provided should be the same size as the data id or data reference array.
        It cannot be used in conjunction with 'unit_id'.
    name_data_from: {'id', 'reference', 'description'}
        What field should be extracted for naming data.
    append_unit_to_description: bool, default True
        Only used when 'name_data_from' is 'description'. If True, the unit is added after the description.
    join_series_on: {'index', 'timestamp', None}, default 'index'
        Joining strategy for data. 'index' will only work if data is homogeneous (i.e. only time values, or batch values
        on a single batch type). If 'timestamp', only the time index will be kept.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    If 'join_series_on' is None, each data is returned in a separate Series stored in a dictionary indexed by the data
    name.
    If 'join_series_on' is 'index' (default behaviour) or 'timestamp', a single DataFrame is returned, containing all
    the data in columns.
    """

    # Args validation
    if name_data_from not in ["id", "reference", "description"]:
        raise ValueError(f"Unexpected value for 'name_data_from': {name_data_from}")

    if join_series_on not in ["index", "timestamp", None]:
        raise ValueError(f"Unexpected value for 'join_series_on': {join_series_on}")

    # Query endpoint
    data_list = endpoints.data.get_multiple_data_values(
        start_date=start_date,
        end_date=end_date,
        aggregation=aggregation,
        data_id=data_id,
        data_reference=data_reference,
        number_of_values=number_of_values,
        aggregation_period=aggregation_period,
        aggregation_function=aggregation_function,
        unit_id=unit_id,
        unit_label=unit_label,
        api_credentials=api_credentials,
    )

    # Format series
    batch_types = {}
    data_series = {}
    for data in data_list:
        # Format series
        if name_data_from == "id":
            data_name = data["data"]["id"]
        elif name_data_from == "reference":
            data_name = data["data"]["reference"]
        elif name_data_from == "description":
            data_name = data["data"]["description"]
            if append_unit_to_description is True:
                data_name = f'{data_name} ({data["unit"]["label"]})'
        else:
            raise ValueError(f"Unexpected value for 'name_data_from': {name_data_from}")

        data_type = data["type"]
        batch_types[data_name] = (
            None if data_type == "time-values" else data["batchType"]["id"]
        )

        if len(data["values"]) == 0:
            timestamp_index = pd.to_datetime(
                data["timestamps"], format="ISO8601"
            ).tz_localize("UTC")
        else:
            timestamp_index = pd.to_datetime(data["timestamps"], format="ISO8601")

        ser = pd.Series(
            name=data_name,
            index=[
                data["batchIds"],
                data["batchNames"],
                timestamp_index,
            ]
            if data_type == "batch-values" and join_series_on != "timestamp"
            else timestamp_index,
            data=data["values"],
            dtype=float if len(data["values"]) == 0 else None,
        )

        if data_type == "batch-values" and join_series_on != "timestamp":
            ser.index.names = ["batch_id", "batch_name", "batch_timestamp"]
        else:
            ser.index.name = "timestamp"

        # Store results
        data_series[data_name] = ser

    # Join series
    if join_series_on == "index":
        n_batch_types = pd.Series(batch_types).nunique(dropna=False)
        if n_batch_types > 1:
            raise ValueError(
                "'join_series_on' cannot be set to 'index' on heterogeneous data"
            )
        data_series = pd.DataFrame(data_series)

    elif join_series_on == "timestamp":
        data_series = pd.DataFrame(data_series)

    # Output
    return data_series


def insert_time_values(
    data: Union[pd.Series, pd.DataFrame],
    units: Optional[dict] = None,
    use_external_reference: bool = False,
    timestamp_index_name: str = "timestamp",
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Insert time values stored in a Series or DataFrame through the OIAnalytics API

    Parameters
    ----------
    data: Series or DataFrame
        The time values to be sent to OIAnalytics. The index should be named 'timestamp'.
    units: dict, optional
        A dictionary indexed by data reference, specifying the values in which it is sent.
    use_external_reference: bool, default False
        Whether the data are named using their external reference (else the OIAnalytics reference is used).
    timestamp_index_name: str, default 'timestamp'
        Name of the index level containing the timestamp
    create_upload_event: bool, default True
        Whether to create an upload event with updated values.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A dictionary of the response from the API, containing the data insert report
    """

    # Init
    if units is None:
        units = {}

    if isinstance(data, pd.Series):
        data = pd.DataFrame(data)
    else:
        data = data.copy()

    # Build DTO
    payload = []

    try:
        data.index = (
            data.index.get_level_values(timestamp_index_name)
            .to_series()
            .apply(utils.get_zulu_isoformat)
            .rename("timestamp")
        )
    except Exception:
        raise ValueError(
            "The series or dataframe must have an index level named 'timestamp' containing datetime-like values"
        )

    for col in data.columns:
        ser = data[col]
        ser.name = "value"

        # Build payload for the data
        col_dict = {
            "dataReference": col,
            "unit": units.get(col, None),
            "values": (
                pd.DataFrame(ser).reset_index().dropna().to_dict(orient="records")
            ),
        }

        payload.append(col_dict)

    # Query endpoint
    response = endpoints.data.insert_time_values(
        data=payload,
        create_upload_event=create_upload_event,
        use_external_reference=use_external_reference,
        api_credentials=api_credentials,
    )

    # Output
    return response


def insert_vector_time_values(
    data: Union[pd.DataFrame, List[pd.DataFrame]],
    data_reference: Union[str, List[str]],
    index_units: Optional[dict] = None,
    values_units: Optional[dict] = None,
    use_external_reference: bool = False,
    timestamp_index_name: str = "timestamp",
    create_upload_event: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Insert time values stored in a DataFrame through the OIAnalytics API

    Parameters
    ----------
    data: dataframe or list of dataframes
        Element(s) containing the vector data time values to be inserted
    data_reference: string or list of strings
        The unique data reference for the data being inserted
    index_units: dictionary, optional
        A dictionary indexed by data reference, specifying the values in which it is sent
    values_units: dictionary, optional
        A dictionary indexed by data reference, specifying the values in which it is sent
    use_external_reference: bool, default False
        Whether the data are named using their external reference (else the OIAnalytics reference is used).
    create_upload_event: bool, default True
        Whether to create an upload event with updated values.
    timestamp_index_name: str, default 'timestamp'
        Name of the index level containing the timestamps
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A dictionary of the response from the API, containing the data insert report
    """

    # Init 'index_units
    if index_units is None:
        index_units = {}

    # Init values_units
    if values_units is None:
        values_units = {}

    # Init list of data and list of data_reference
    if isinstance(data, pd.DataFrame):
        data = [data.copy()]
        data_reference = [data_reference]

    # Build DTO
    payload = []
    for reference, df in zip(data_reference, data):
        try:
            timestamps = (
                df.index.get_level_values(timestamp_index_name)
                .to_series()
                .apply(utils.get_zulu_isoformat)
                .rename(timestamp_index_name)
            )
        except KeyError:
            raise KeyError(
                "The dataframe must have an index level named 'timestamp' containing datetime-like values"
            )
        # Build payload for the data
        payload.append(
            {
                "dataReference": reference,
                "indexUnit": index_units.get(reference, None),
                "valueUnit": values_units.get(reference, None),
                "timestamps": timestamps.tolist(),
                "indexes": df.columns.tolist(),
                "values": df.replace(np.nan, None).to_numpy().tolist(),
            }
        )

    # Query endpoint
    response = endpoints.data.insert_vector_time_values(
        data=payload,
        use_external_reference=use_external_reference,
        create_upload_event=create_upload_event,
        api_credentials=api_credentials,
    )

    # Output
    return response
