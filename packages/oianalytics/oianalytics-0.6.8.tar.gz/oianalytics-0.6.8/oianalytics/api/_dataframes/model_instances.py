from typing import Optional, Union, Tuple, Literal

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils


__all__ = ["get_model_instances", "get_single_model_instance"]


def get_model_instances(
    page: int = 0,
    page_size: int = 20,
    get_all_pages: bool = True,
    expand_creator: bool = True,
    expand_trigger: bool = True,
    expand_python_model: bool = True,
    multithread_pages: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """

    Parameters
    ----------
    page : int, default 0
        The requested page. It is ignored if 'get_all_pages' is set to True.
    page_size : int, default 20
        The size of the pages. It is ignored if 'get_all_pages' is set to True.
    get_all_pages : bool, default True
        Whether to list all model instances of all pages.
        If the value is set to True, the 'page' and 'page_size' arguments will be ignored, and the function will retrieve all pages.
    multithread_pages : bool, default True
        Whether to retrieve pages in multiple threads simultaneously.
        It is used only if 'get_all_pages' is set to True.
    expand_creator : bool, default True
        Whether to split the 'creator' column.
        If True, it is split into two columns: 'creator_id' and 'creator_friendlyName'.
    expand_trigger : bool, default True
        Whether to split the 'trigger' column.
        If True, it is split into two columns: 'trigger_type' and 'trigger_cron'.
    expand_python_model : bool, default True
        Whether to split the 'pythonModel' column.
        If True, it is split into two columns: 'pythonModel_id', 'pythonModel_name' and 'pythonModel_version'.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.DataFrame

    """

    if get_all_pages:
        page = 0
        page_size = 500

    def get_page(page_num: int) -> dict:
        return endpoints.model_instances.get_model_instances(
            page=page_num,
            page_size=page_size,
            api_credentials=api_credentials,
        )

    def parse_page(page_response: dict) -> pd.DataFrame:
        page_df = pd.DataFrame(page_response["content"])
        # Expected columns if content is empty
        if page_df.shape[0] == 0:
            page_df = pd.DataFrame(
                columns=[
                    "id",
                    "title",
                    "description",
                    "creator",
                    "creationDate",
                    "trigger," "active",
                    "lastSuccessfulExecution",
                    "pythonModel",
                    "upToDate",
                ],
            )
        # Set index
        page_df.set_index("id", inplace=True)
        return page_df

    df = utils.concat_pages_to_dataframe(
        getter=get_page,
        parser=parse_page,
        page=page,
        get_all_pages=get_all_pages,
        multithread_pages=multithread_pages,
    )

    if expand_creator:
        df = utils.expand_dataframe_column(
            df=df,
            col="creator",
        )

    if expand_trigger:
        df = utils.expand_dataframe_column(
            df=df,
            col="trigger",
        )

    if expand_python_model:
        df = utils.expand_dataframe_column(
            df=df,
            col="pythonModel",
        )
    # Output
    return df


def get_single_model_instance(
    model_instance_id: str,
    expand_creator: bool = True,
    expand_trigger: bool = True,
    expand_python_model: bool = True,
    create_parameters_dataframes: bool = False,
    extract_from_input_parameters: Optional[Literal["id", "reference"]] = "reference",
    extract_from_output_parameters: Optional[Literal["id", "reference"]] = "reference",
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> Union[pd.Series, Tuple[pd.Series, pd.DataFrame, pd.DataFrame]]:
    """

    Parameters
    ----------
    model_instance_id : str
        The ID of the retrieved python model instance.
    expand_creator : bool, default True
        Whether to split the 'creator' column.
        If True, it is split into two columns: 'creator_id' and 'creator_friendlyName'.
    expand_trigger : bool, default True
        Whether to split the 'trigger' column.
        If True, it is split into two columns: 'trigger_type' and 'trigger_cron'.
    expand_python_model : bool, default True
        Whether to split the 'pythonModel' column.
        If True, it is split into two columns: 'pythonModel_id', 'pythonModel_name' and 'pythonModel_version'.
    create_parameters_dataframes : bool, default False
        Create additional DataFrames with input-parameters and output-parameters.
        If True, the response is a tuple with:
          - one Series (model instance);
          - two DataFrames (the first one for the input parameters and the second for the output parameters).
    extract_from_input_parameters : {'id', 'reference', None}, default 'reference'
        Value to be exposed in the 'value' column. Used only if 'create_parameters_dataframes' is True.
    extract_from_output_parameters : {'id', 'reference', None}, default 'reference'
        Value to be exposed in the 'value' column. Used only if 'create_parameters_dataframes' is True.
    api_credentials : OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    pd.Series | tuple[pd.Series, pd.DataFrame, pd.DataFrame]
    """
    response = endpoints.model_instances.get_single_model_instance(
        model_instance_id=model_instance_id, api_credentials=api_credentials
    )
    df = pd.DataFrame([response])

    if len(df) == 0:
        if create_parameters_dataframes:
            return df.squeeze(), pd.DataFrame(), pd.DataFrame()
        else:
            return df.squeeze()

    df.set_index("id", inplace=True)

    if expand_creator:
        df = utils.expand_dataframe_column(
            df=df,
            col="creator",
        )

    if expand_trigger:
        df = utils.expand_dataframe_column(
            df=df,
            col="trigger",
        )

    if expand_python_model:
        df = utils.expand_dataframe_column(
            df=df,
            col="pythonModel",
        )

    if not create_parameters_dataframes:
        return df.squeeze()

    def expand_dict(d: dict) -> pd.DataFrame:
        if isinstance(d["value"], dict):
            d = d | {f"value_{key}": value for key, value in d["value"].items()}
            d.pop("value")
        df_expanded = pd.DataFrame([d])
        df_expanded.set_index("sourceCodeName", inplace=True)
        return df_expanded

    if extract_from_input_parameters is not None:
        for parameter in response["inputParameters"]:
            if isinstance(parameter["value"], dict):
                parameter["value"] = parameter["value"][extract_from_input_parameters]
        df_input = pd.DataFrame(response["inputParameters"])
        df_input.set_index("sourceCodeName", inplace=True)
    else:
        df_input = pd.concat(
            [expand_dict(parameter) for parameter in response["inputParameters"]],
            axis=0,
        )

    if extract_from_output_parameters is not None:
        for parameter in response["outputParameters"]:
            if isinstance(parameter["value"], dict):
                parameter["value"] = parameter["value"][extract_from_output_parameters]
        df_output = pd.DataFrame(response["outputParameters"])
        df_output.set_index("sourceCodeName", inplace=True)
    else:
        df_output = pd.concat(
            [expand_dict(parameter) for parameter in response["outputParameters"]],
            axis=0,
        )

    return df.squeeze(), df_input, df_output
