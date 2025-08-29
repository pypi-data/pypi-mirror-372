from typing import Optional, Union, List, Callable
import io
from datetime import datetime

import pandas as pd

from .. import _credentials
from .. import endpoints
from .. import utils

__all__ = ["get_file_uploads", "read_file_from_file_upload"]


def get_file_uploads(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    filename: Optional[str] = None,
    statuses: Optional[Union[str, List[str]]] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    get_all_pages: bool = True,
    multithread_pages: bool = True,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get a list of file uploads from the OIAnalytics API

    Parameters
    ----------
    start_date: datetime or str
        The beginning of the period to be retrieved
    end_date: datetime or str
        The end of the period to be retrieved
    filename: str, optional
        A portion of text the filename uploaded should contain.
    statuses: str or list of str, optional
        Statuses to filter the file uploads.
        Available statuses are 'PENDING', 'NO_PARSER_FOUND', 'RUNNING', 'DEACTIVATED_PARSER_FOUND', 'SUCCESS', 'ERROR'.
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
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    A DataFrame listing file uploads
    """

    # Init
    if get_all_pages is True:
        page = 0
        page_size = 500

    def get_page(page_num: int):
        page_response = endpoints.files.get_file_uploads(
            start_date=start_date,
            end_date=end_date,
            filename=filename,
            statuses=statuses,
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
                    "id",
                    "creationInstant",
                    "startInstant",
                    "endInstant",
                    "status",
                    "uploader",
                    "filename",
                ]
            )

        for col in ["creationInstant", "startInstant", "endInstant"]:
            page_df[col] = pd.to_datetime(page_df[col], format="ISO8601")
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


def read_file_from_file_upload(
    file_upload_id: str,
    parser: Callable = pd.read_csv,
    parser_kwargs: Optional[dict] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Get the content of a file from previous file uploads and read it

    Parameters
    ----------
    file_upload_id: str
        The id of the file to be retrieved
    parser: callable, default pd.read_csv
        A function which is applied to the file content BytesIO
    parser_kwargs: dict, optional
        A dictionary containing kwargs to be used in the parser function when reading the file
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to query the API. If None, previously set default credentials are used.

    Returns
    -------
    The result of the file content parsing built as following: parser(file_content, **parser_kwargs)
    """

    # Init
    if parser_kwargs is None:
        parser_kwargs = {}

    # Query endpoint
    response = endpoints.files.get_file_from_file_upload(
        file_upload_id=file_upload_id, api_credentials=api_credentials
    )

    # Output
    return parser(response, **parser_kwargs)
