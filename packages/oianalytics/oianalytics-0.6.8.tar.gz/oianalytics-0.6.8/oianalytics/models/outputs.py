from typing import Union, Optional, List
import io
import time
import traceback

import pandas as pd

from .. import api
from ._dtos import (
    get_default_model_execution,
    get_default_execution_report,
    ExecutionReport,
    CustomModelOutput,
)
from ._queries import update_instance_resource

__all__ = [
    "FileOutput",
    "InstanceResourceOutput",
    "TimeValuesOutput",
    "VectorTimeValuesOutput",
    "Delay",
    "BatchValuesOutput",
    "VectorBatchValuesOutput",
    "BatchFeaturesOutput",
    "BatchesOutput",
    "EventsOutput",
    "CustomTextOutput",
    "CustomJsonOutput",
    "BatchComputationJob",
    "OIModelOutputs",
]


# Output classes
class FileOutput:
    """
    This class contains the content to be sent in a file upload to Oi Analytics.

    Attributes
    ----------
    output_type : {'file'}
        Denotes the specific type of the current output object.
    file_name : str
        Name of the output file.
    content : io.StringIO | io.BytesIO
        Content of the output file.

    Methods
    -------
    from_pandas(self, data, file_name, file_type):
        Initialize an instance of FileOutput with content from pandas.Series or pandas.DataFrame.

    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Upload file to Oi Analytics.
    """

    def __init__(
        self,
        file_name: str,
        content: Union[io.StringIO, io.BytesIO],
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of FileOutput.

        Parameters
        ----------
        file_name : str
            Name of the output file.
        content : io.StringIO | io.BytesIO
            Content of the output file.
        """
        self.output_type = "file"
        self.file_name = file_name
        self.content = content
        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    @classmethod
    def from_pandas(
        cls,
        data: Union[pd.Series, pd.DataFrame],
        file_name: str,
        file_type: str = "csv",
        writing_kwargs: Optional[dict] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize an instance of FileOutput with data from pandas.Series or pandas.DataFrame.

        Parameters
        ----------
        data : pandas.Series | pandas.DataFrame
            Output data.
        file_name : str
            Name of the output file.
        file_type : str, default 'csv'
            Extension of the output file.
        writing_kwargs : dict, optional

        Returns
        -------
        object
            FileOutput.

        """
        # Init
        if writing_kwargs is None:
            writing_kwargs = {}

        bio = io.BytesIO()

        # Write data
        if file_type == "excel":
            data.to_excel(bio, **writing_kwargs)
        elif file_type == "csv":
            data.to_csv(bio, **writing_kwargs)
        else:
            raise NotImplementedError(f"Unsupported file_type: {file_type}")
        bio.seek(0)

        # Create object
        return cls(
            file_name=file_name,
            content=bio,
            raise_exceptions_on_send=raise_exceptions_on_send,
            log_exceptions_if_not_raised=log_exceptions_if_not_raised,
        )

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        **kwargs,
    ) -> None:
        """
        Upload file to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used
        execution_report : ExecutionReport, optional
            Execution report for external use
        raise_exceptions : bool, default False
            Whether to raise exception
        log_exceptions_if_not_raised : bool, default True
            Whether to print exception

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # get execution report
        if execution_report is None:
            execution_report = get_default_execution_report()
        # update execution report
        try:
            response = api.endpoints.files.upload_file(
                file_content=self.content,
                file_name=self.file_name,
                api_credentials=api_credentials,
            )
            execution_report.update(files_uploaded=1)
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class InstanceResourceOutput:
    """
    This class contains the content to be sent as an instance resource to Oi Analytics.

    Attributes
    ----------
    output_type : 'instance_resource'
        Denotes the specific type of the current output object.
    file_content : file_content
        Content of the instance resource output file.
    file_name : str
        Name of the instance resource output file.
    resource_file_id : resource_file_id
        Unique identifier of instance resource output file.
    model_instance_id : model_instance_id
        Unique identifier of model instance.

    Methods
    -------
    from_pandas(self, data, file_name, file_type):
        Create InstanceResourceOutput object from a pandas.Series or a pandas.DataFrame.

    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Upload instance resource to Oi Analytics.
    """

    def __init__(
        self,
        file_content: Union[io.StringIO, io.BytesIO],
        file_name: str,
        resource_file_id: str,
        model_instance_id: Optional[str] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of InstanceResourceOutput.

        Parameters
        ----------
        file_content : io.StringIO | io.BytesIO
            Content of the instance resource output file.
        file_name : str
            Name of the instance resource output file.
        resource_file_id : str
            Unique identifier of instance resource output file.
        model_instance_id : str, optional
            Unique identifier of model instance.
        """
        self.output_type = "instance_resource"
        self.file_content = file_content
        self.file_name = file_name
        self.resource_file_id = resource_file_id
        self.model_instance_id = model_instance_id
        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    @classmethod
    def from_pandas(
        cls,
        data: Union[pd.Series, pd.DataFrame],
        file_name: str,
        resource_file_id: str,
        model_instance_id: Optional[str] = None,
        file_type: str = "csv",
        writing_kwargs: Optional[dict] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """Create InstanceResourceOutput object from a pandas.Series or a pandas.DataFrame.

        Parameters
        ----------
        data : pandas.Series, pandas.DataFrame
            Data of instance resource output.
        file_name : str
            Name of instance resource output file.
        resource_file_id : str
            ID of insta,ce resource output file.
        model_instance_id : str, optional
            ID of model instance.
        file_type : str, default 'csv'
            Extension of the output file.
        writing_kwargs : dict, optional

        Returns
        -------
        object
            InstanceResourceOutput

        """
        # Init
        if writing_kwargs is None:
            writing_kwargs = {}

        bio = io.BytesIO()

        # Write data
        if file_type == "excel":
            data.to_excel(bio, **writing_kwargs)
        elif file_type == "csv":
            data.to_csv(bio, **writing_kwargs)
        else:
            raise NotImplementedError(f"Unsupported file_type: {file_type}")
        bio.seek(0)

        # Create object
        return cls(
            file_content=bio,
            file_name=file_name,
            resource_file_id=resource_file_id,
            model_instance_id=model_instance_id,
            raise_exceptions_on_send=raise_exceptions_on_send,
            log_exceptions_if_not_raised=log_exceptions_if_not_raised,
        )

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        **kwargs,
    ) -> None:
        """
        Upload instance resource to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials | None
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        log_exceptions_if_not_raised : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.

        Returns
        -------

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # get execution report
        if execution_report is None:
            execution_report = get_default_execution_report()
        # update execution report
        execution_report.update(files_uploaded=1)

        try:
            return update_instance_resource(
                file_content=self.file_content,
                file_name=self.file_name,
                resource_file_id=self.resource_file_id,
                model_instance_id=self.model_instance_id,
                api_credentials=api_credentials,
            )
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class TimeValuesOutput:
    """
    This class contains time values to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : 'time_values'
        Denotes the specific type of the current output object.
    data : pandas.Series | pandas.DataFrame
        Data structure containing time values.
    units : dict, optional
        Dictionary that maps ID of a time data to its corresponding unit.
    use_external_reference : bool, default False
        Whether to use external reference.
    timestamp_index_name : str, default 'timestamp'
        Index name of data containing time values.
    create_upload_event : bool, default True
        Whether to create a file upload event when uploading to Oi Analytics.

    Methods
    -------
    from_pandas(self, data, file_name, file_type):
        Initialize an instance of TimeValuesOutput with data from a pandas.Series or a pandas.DataFrame.

    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions: bool = False):
        Upload time values to Oi Analytics.
    """

    def __init__(
        self,
        data: Union[pd.Series, pd.DataFrame],
        units: Optional[dict] = None,
        rename_data: bool = True,
        use_external_reference: bool = False,
        timestamp_index_name: str = "timestamp",
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of TimeValuesOutput.

        Parameters
        ----------
        data : pandas.Series | pandas.DataFrame
            Data structure containing time values.
        units : dict, optional
            Dictionary that maps reference of a time data to its corresponding unit.
        rename_data : bool, default True
            Whether to rename data with its reference.
        use_external_reference : bool, default False
            Whether to use external reference.
        timestamp_index_name : str, default 'timestamp'
            Index name of data containing time values.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.
        """
        self.output_type = "time_values"
        self.create_upload_event = create_upload_event

        # Rename data if specified
        data_df = data.to_frame() if isinstance(data, pd.Series) else data

        if rename_data is True:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="any", values_type="scalar", mode="reference"
            )
            self.data = data_df.rename(columns=output_dict)
        else:
            self.data = data_df

        # Specify units
        if units is None:
            model_exec = get_default_model_execution()
            if model_exec is not None:
                self.units = {
                    output_data.reference: output_data.unit.label
                    for output_data in model_exec.get_data_output_dict(
                        data_type="any", values_type="scalar", mode="object"
                    ).values()
                }
            else:
                self.units = units
        else:
            self.units = units

        self.use_external_reference = use_external_reference

        self.timestamp_index_name = timestamp_index_name

        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload time values to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # get execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        # send data
        try:
            response = api.insert_time_values(
                data=self.data,
                units=self.units,
                use_external_reference=self.use_external_reference,
                timestamp_index_name=self.timestamp_index_name,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )
            # update execution report
            execution_report.update(
                time_values_updated=response.get(
                    "numberOfValuesSuccessfullyInserted", 0
                ),
                errors=len(response.get("errors", [])),
            )
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class VectorTimeValuesOutput:
    """
    This class contains vector time values to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'time_vector_values'}
        Denotes the specific type of the current output object.
    data : pandas.Series | pandas.DataFrame
        Data structure containing time values.
    data_reference : list of str
            List of data references (one data reference for each vector data).
    values_units : dict, optional
        Dictionary that maps ID of a time vector data to its corresponding values unit.
    index_units : dict, optional
        Dictionary that maps ID of a time vector data to its corresponding indexes unit.
    use_external_reference : bool, default False
        Whether to use external reference.
    timestamp_index_name : str, default 'timestamp'
        Index name of data containing time values.
    create_upload_event : bool, default True
        Whether to create a file upload event when uploading to Oi Analytics.

    Methods
    -------
    from_pandas(self, data, file_name, file_type):
        Initialize an instance of InstanceResourceOutput with data from a pandas.Series or a pandas.DataFrame.

    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions: bool = False):
        Upload vector time values to Oi Analytics.
    """

    def __init__(
        self,
        data: List[pd.DataFrame],
        data_reference: List[str],
        rename_data: bool = True,
        values_units: Optional[dict[str, str]] = None,
        index_units: Optional[dict[str, str]] = None,
        use_external_reference: bool = False,
        timestamp_index_name: str = "timestamp",
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """

        Parameters
        ----------
        data : list of pandas.DataFrame
            List of vector time values.
        data_reference : list of str
            List of data references (one data reference for each vector data).
        rename_data : bool, default True
            Whether to rename data.
        values_units : dict, optional
            Dictionary that maps vector data to its corresponding unit.
        index_units : dict, optional
            Dictionary that maps vector data index to its corresponding unit.
        use_external_reference : bool, default
            Whether to use external reference.
        timestamp_index_name : str, default 'timestamp'
            Index name of each pandas.DataFrame containing vector time values.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.
        """
        self.output_type = "time_vector_values"
        self.create_upload_event = create_upload_event

        if rename_data is True:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="time", values_type="vector", mode="reference"
            )
            data_reference = [
                output_dict[source_code_name] for source_code_name in data_reference
            ]

        self.data_reference = data_reference
        self.data = data

        # Specify values units
        if values_units is None:
            model_exec = get_default_model_execution()
            if model_exec is not None:
                self.values_units = {
                    output_data.reference: output_data.valueUnit.label
                    for output_data in model_exec.get_data_output_dict(
                        data_type="time", values_type="vector", mode="object"
                    ).values()
                    if output_data.reference in data_reference
                }
            else:
                self.values_units = values_units
        else:
            self.values_units = values_units

        # Specify index unit
        if index_units is None:
            model_exec = get_default_model_execution()
            if model_exec is not None:
                self.index_units = {
                    output_data.reference: output_data.indexUnit.label
                    for output_data in model_exec.get_data_output_dict(
                        data_type="time", values_type="vector", mode="object"
                    ).values()
                    if output_data.reference in data_reference
                }
            else:
                self.index_units = index_units
        else:
            self.index_units = index_units

        self.use_external_reference = use_external_reference

        self.timestamp_index_name = timestamp_index_name

        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload vector time values to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # get execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        # send data
        try:
            response = api.insert_vector_time_values(
                data=self.data,
                data_reference=self.data_reference,
                index_units=self.index_units,
                values_units=self.values_units,
                use_external_reference=self.use_external_reference,
                timestamp_index_name=self.timestamp_index_name,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )

            # update execution report
            execution_report.update(
                errors=len(response.get("errors", [])),
                time_vector_values_updated=response.get(
                    "numberOfValuesSuccessfullyInserted", 0
                ),
            )
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class BatchValuesOutput:
    """
    This class contains batch values to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'batch_values'}
        Denotes the specific type of the current output object.
    batch_type_id : str
        Unique identifier of batch type.
    data : pandas.Series | pandas.DataFrame
        Data structure containing time values.
    units : dict, optional
        Dictionary that maps ID of a time data to its corresponding unit.
    batch_id_index_name : str, default 'batch_id'
        Index name of data containing time values.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions: bool = False):
        Upload batch values to Oi Analytics.
    """

    def __init__(
        self,
        batch_type_id: str,
        data: Union[pd.Series, pd.DataFrame],
        units: Optional[dict] = None,
        batch_id_index_name: str = "batch_id",
        rename_data: bool = True,
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """

        Parameters
        ----------
        batch_type_id : str
            Unique identifier of the batch type.
        data : pandas.Series | pandas.DataFrame
            Batch values.
        units : dict, Optional
            Dictionary that maps vector data to its corresponding unit.
        batch_id_index_name : str, default 'batch_id'
            Index name of data containing batch values.
        rename_data : bool, default True
            Whether to rename with technical value (value id).
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.
        """
        self.output_type = "batch_values"
        self.batch_type_id = batch_type_id
        self.create_upload_event = create_upload_event

        # Rename data if specified
        data_df = data.to_frame() if isinstance(data, pd.Series) else data

        if rename_data is True:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="batch", values_type="scalar", mode="id"
            )
            self.data = data_df.rename(columns=output_dict)
        else:
            self.data = data_df

        # Specify units
        if units is None:
            model_exec = get_default_model_execution()
            if model_exec is not None:
                self.units = {
                    output_data.id: output_data.unit.id
                    for output_data in model_exec.get_data_output_dict(
                        data_type="batch", values_type="scalar", mode="object"
                    ).values()
                }
            else:
                self.units = None
        else:
            self.units = units

        self.batch_id_index_name = batch_id_index_name

        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload batch values to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # get execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        try:
            # send data
            response = api.update_batch_features_and_values(
                batch_type_id=self.batch_type_id,
                data=self.data,
                unit_ids=self.units,
                batch_id_index_name=self.batch_id_index_name,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )

            # update execution report
            execution_report.update(batch_values_updated=int(self.data.count().sum()))
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class VectorBatchValuesOutput:
    """
    This class contains vector batch values to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'batch_vector_values'}
        Denotes the specific type of the current output object.
    create_upload_event : bool, default True
        Whether to create a file upload event when uploading to Oi Analytics.
    data_reference : list of str
        The unique data references of the data being inserted.
    data : pandas.Series | pandas.DataFrame
        Data structure containing time values.
    values_units : dict, optional
        Dictionary that maps ID of a batch vector data to its corresponding value unit.
    index_units : dict, optional
        Dictionary that maps ID of a batch vector data to its corresponding index unit.
    batch_id_index_name : str, default 'batch_id'
        Index name of data containing time values.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions: bool = False):
        Upload vector batch values to OI Analytics.
    """

    def __init__(
        self,
        data: List[pd.DataFrame],
        data_reference: List[str],
        values_units: Optional[dict[str, str]] = None,
        index_units: Optional[dict[str, str]] = None,
        batch_id_index_name: str = "batch_id",
        rename_data: bool = True,
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """

        Parameters
        ----------
        data : list of data
            List of batch vector values.
        data_reference : list of str
            List of data references.
        values_units : dict, optional
            Dictionary that maps reference of a vector data to its corresponding unit.
        index_units : dict, None
            Dictionary that maps reference of a vector data to its corresponding index unit.
        batch_id_index_name : str, default 'batch_id'
            Index name of data containing batch values.
        rename_data : bool, default True
            Whether to rename with technical value (value id).
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.
        """
        self.output_type = "batch_vector_values"
        self.create_upload_event = create_upload_event

        if rename_data is True:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="batch", values_type="vector", mode="reference"
            )
            data_reference = [
                output_dict[source_code_name] for source_code_name in data_reference
            ]

        self.data_reference = data_reference
        self.data = data

        # Specify units
        if values_units is None:
            model_exec = get_default_model_execution()
            if model_exec is not None:
                self.values_units = {
                    output_data.reference: output_data.valueUnit.label
                    for output_data in model_exec.get_data_output_dict(
                        data_type="batch", values_type="vector", mode="object"
                    ).values()
                    if output_data.reference in data_reference
                }
        else:
            self.values_units = values_units

        # Specify units
        if index_units is None:
            model_exec = get_default_model_execution()
            if model_exec is not None:
                self.index_units = {
                    output_data.reference: output_data.indexUnit.label
                    for output_data in model_exec.get_data_output_dict(
                        data_type="batch", values_type="vector", mode="object"
                    ).values()
                    if output_data.reference in data_reference
                }
        else:
            self.index_units = index_units

        self.batch_id_index_name = batch_id_index_name

        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload vector batch values to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # get execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        # send data
        try:
            response = api.update_vector_batch_values(
                data=self.data,
                data_reference=self.data_reference,
                index_units=self.index_units,
                values_units=self.values_units,
                batch_id_index_name=self.batch_id_index_name,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )

            # update execution report
            execution_report.update(
                errors=len(response.get("errors", [])),
                batch_vector_values_updated=response.get(
                    "numberOfValuesSuccessfullyInserted", 0
                ),
            )
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class BatchFeaturesOutput:
    """
    This class contains batch features to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'batch_features'}
        Indicates the output type to be sent to Oi Analytics.
    batch_type_id : str
        Unique identifier of batch type.
    data : pandas.Series | pandas.DataFrame
        Data structure containing time values.
    batch_id_index_name : str, default 'batch_id'
        Index name of data containing batch features.
    create_upload_event : bool, optional
        Whether to create a file upload event when uploading to Oi Analytics.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions: bool = False):
        Upload batch features to OI Analytics.
    """

    def __init__(
        self,
        batch_type_id: str,
        data: Union[pd.Series, pd.DataFrame],
        rename_features: bool = True,
        batch_id_index_name: str = "batch_id",
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of BatchFeaturesOutput.

        Parameters
        ----------
        batch_type_id : str
            Unique identifier of the batch type.
        data : pandas.Series | pandas.DataFrame
            Data containing batch features output.
        rename_features : bool, default True
            Whether to rename features from source code names to data IDs.
        batch_id_index_name : str, default 'batch_id'
            Index name of data containing batch values.
        """
        self.output_type = "batch_features"
        self.batch_type_id = batch_type_id
        self.create_upload_event = create_upload_event

        # Rename data if specified
        data_df = data.to_frame() if isinstance(data, pd.Series) else data

        if rename_features is True:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Features can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="batch", values_type="categorical", mode="id"
            )
            self.data = data_df.rename(columns=output_dict)
        else:
            self.data = data_df

        self.batch_id_index_name = batch_id_index_name

        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload batch features to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, default True
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # update execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        # send data
        try:
            response = api.update_batch_features_and_values(
                batch_type_id=self.batch_type_id,
                data=self.data,
                feature_columns=list(self.data.columns),
                batch_id_index_name=self.batch_id_index_name,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )

            # update execution report
            execution_report.update(batch_tags_updated=int(self.data.count().sum()))
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class BatchesOutput:
    """
    This class contains batches to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'batches'}
        Denotes the specific type of the current output object.
    batch_type_id : str
        Unique identifier of batch type.
    steps : pandas.DataFrame
        The steps of the batches to insert. The DataFrame is indexed by batch name (named after batch_name_index_name).
            The content of this DataFrame must be:
            - The step ID (named after step_id_index_name)
            - The start and end dates of the steps (named after start_date_name and end_date_name)
            - Optional asset or tag localisation columns
    on_duplicates_keep : {'first', 'last', False}, default 'last'
        Indicate which DataFrame row to keep in case of duplicates (Cf. pd.DataFrame.drop_duplicates).
    batch_name_index_name : str, default 'batch_name'
        The name of the index level containing the batch name in the DataFrames.
    step_id_index_name : str, default 'step_id_index_name'
        The name of the index level (or column) containing the step id in the steps DataFrame.
    start_date_name : str, default 'start'
        The name of the column containing the start date of the steps id in the steps DataFrame.
    end_date_name : str, default 'end'
        The name of the column containing the end date of the steps id in the steps DataFrame.
    asset_localisation_column : str, optional
        The name of the column containing the asset IDs allowing the localisation of steps.
    tag_localisation_columns : str | list of str, optional
        The name of the columns containing the tag value IDs allowing the localisation of steps.
    vector_data_values : pandas.DataFrame | list of pandas.DataFrame, optional
        The vector data values to insert or update. Must be indexed by batch name (Cf. batch_name_index_name).
        Each column is a vector index.
    values : pandas.DataFrame, optional
        The data values to update or insert. The DataFrame must be indexed by batch name (Cf. batch_name_index_name).
        Each column is named after the data ID.
    values_unit_ids : dict, optional
        Dictionary that maps data id to its corresponding unit id.
    features : pandas.DataFrame, optional
        The feature values to update or insert. The DataFrame must be indexed by batch name (Cf. batch_name_index_name).
        Each column is named after the feature ID.
    vector_data_references : list of str, optional
        The list of the vector data references matching the list  of vector data values DataFrames.
    vector_data_index_units : dict, None
        Dictionary that maps reference of a vector data to its corresponding index unit.
    vector_data_values_units : dict, None
        Dictionary that maps reference of a vector data to its corresponding unit.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Upload batches to OI Analytics.
    """

    def __init__(
        self,
        batch_type_id: str,
        steps: pd.DataFrame,
        values: Optional[pd.DataFrame] = None,
        values_unit_ids: Optional[dict] = None,
        rename_data: bool = True,
        features: Optional[pd.DataFrame] = None,
        rename_features: bool = True,
        vector_data_values: Optional[Union[pd.DataFrame, List[pd.DataFrame]]] = None,
        vector_data_references: Optional[List[str]] = None,
        vector_data_index_units: Optional[dict] = None,
        vector_data_values_units: Optional[dict] = None,
        rename_vector_data: bool = True,
        on_duplicates_keep: str = "last",
        batch_name_index_name: str = "batch_name",
        step_id_index_name: str = "step_id",
        start_date_name: str = "start",
        end_date_name: str = "end",
        asset_localisation_column: Optional[str] = None,
        tag_localisation_columns: Optional[Union[str, List[str]]] = None,
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of BatchesOutput.

        Parameters
        ----------
        batch_type_id : str
            Unique identifier of the batch type.
        steps : pandas.DataFrame
            The steps of the batches to insert. The DataFrame is indexed by batch name (named after batch_name_index_name).
            The content of this DataFrame must be:
            - The step ID (named after step_id_index_name)
            - The start and end dates of the steps (named after start_date_name and end_date_name)
            - Optional asset or tag localisation columns
        values : pandas.DataFrame, optional
            The data values to update or insert. The DataFrame must be indexed by batch name (Cf. batch_name_index_name).
            Each column is named after the data ID.
        values_unit_ids : dict, optional
            Dictionary that maps data id to its corresponding unit id.
        rename_data : bool, default True
            Whether to rename data
        features : pandas.DataFrame, optional
            The feature values to update or insert. The DataFrame must be indexed by batch name (Cf. batch_name_index_name).
            Each column is named after the feature ID.
        rename_features : bool, default True
            Whether to rename features with IDs.
        vector_data_values : pandas.DataFrame | list of pandas.DataFrame, optional
            The vector data values to insert or update. Must be indexed by batch name (Cf. batch_name_index_name).
            Each column is a vector index.
        vector_data_references : list of str, optional
            The list of the vector data references matching the list  of vector data values DataFrames.
        vector_data_index_units : dict, None
            Dictionary that maps reference of a vector data to its corresponding index unit.
        vector_data_values_units : dict, None
            Dictionary that maps reference of a vector data to its corresponding unit.
        rename_vector_data : bool, default True
            Whether to rename the vector data.
        on_duplicates_keep : {'first', 'last', False}, default 'last'
            Indicate which DataFrame row to keep in case of duplicates (Cf. pd.DataFrame.drop_duplicates).
        batch_name_index_name : str, default 'batch_name'
            The name of the index level containing the batch name in the DataFrames.
        step_id_index_name : str, default 'step_id_index_name'
            The name of the index level (or column) containing the step id in the steps DataFrame.
        start_date_name : str, default 'start'
            The name of the column containing the start date of the steps id in the steps DataFrame.
        end_date_name : str, default 'end'
            The name of the column containing the end date of the steps id in the steps DataFrame.
        asset_localisation_column : str, optional
            The name of the column containing the asset IDs allowing the localisation of steps.
        tag_localisation_columns : str | list of str, optional
            The name of the columns containing the tag value IDs allowing the localisation of steps.
        """
        self.output_type = "batches"
        self.batch_type_id = batch_type_id
        self.steps = steps
        self.on_duplicates_keep = on_duplicates_keep
        self.batch_name_index_name = batch_name_index_name
        self.step_id_index_name = step_id_index_name
        self.start_date_name = start_date_name
        self.end_date_name = end_date_name
        self.asset_localisation_column = asset_localisation_column
        self.tag_localisation_columns = tag_localisation_columns
        self.vector_data_values = vector_data_values
        self.create_upload_event = create_upload_event

        # Rename data if specified
        if rename_data is True and values is not None:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="batch", values_type="scalar", mode="id"
            )

            # Rename values DataFrame
            self.values = values.rename(columns=output_dict)

            # Rename data in units dict
            if values_unit_ids is not None:
                self.values_unit_ids = {
                    output_dict[k]: v for k, v in values_unit_ids.items()
                }
            else:
                self.values_unit_ids = None
        else:
            self.values = values
            self.values_unit_ids = values_unit_ids

        # Rename features if specified
        if rename_features is True and features is not None:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Features can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="batch", values_type="categorical", mode="id"
            )

            # Rename values DataFrame
            self.features = features.rename(columns=output_dict)
        else:
            self.features = features

        # Rename vector data if specified
        if rename_vector_data is True and vector_data_values is not None:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Vector data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="batch", values_type="vector", mode="reference"
            )
            self.vector_data_references = [
                output_dict[source_code_name]
                for source_code_name in vector_data_references
            ]

            # Rename data in index units dict
            if vector_data_index_units is not None:
                self.vector_data_index_units = {
                    output_dict[k]: v for k, v in vector_data_index_units.items()
                }
            else:
                self.vector_data_index_units = None

            # Rename data in values units dict
            if vector_data_values_units is not None:
                self.vector_data_values_units = {
                    output_dict[k]: v for k, v in vector_data_values_units.items()
                }
            else:
                self.vector_data_values_units = None
        else:
            self.vector_data_references = vector_data_references
            self.vector_data_index_units = None
            self.vector_data_values_units = None

        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload batches to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, optional
            Whether to create a file upload event when uploading to Oi Analytics.

        Methods
        -------
        send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
            Upload batches to OI Analytics.

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # update execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        # send data
        try:
            response = api.create_or_update_batches(
                batch_type_id=self.batch_type_id,
                steps=self.steps,
                values=self.values,
                values_unit_ids=self.values_unit_ids,
                features=self.features,
                vector_data_values=self.vector_data_values,
                vector_data_references=self.vector_data_references,
                vector_data_index_units=self.vector_data_index_units,
                vector_data_values_units=self.vector_data_values_units,
                on_duplicates_keep=self.on_duplicates_keep,
                batch_name_index_name=self.batch_name_index_name,
                step_id_index_name=self.step_id_index_name,
                start_date_name=self.start_date_name,
                end_date_name=self.end_date_name,
                asset_localisation_column=self.asset_localisation_column,
                tag_localisation_columns=self.tag_localisation_columns,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )

            # update execution report
            execution_report.update(batch_created_updated=len(response))
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class EventsOutput:
    """
    This class contains events to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'events'}
        Denotes the specific type of the current output object.
    event_type_id : str
        Unique identifier of event type.
    events : pandas.DataFrame
        The events DataFrame containing all event information. The DataFrame can be indexed by event ID (optional for creation).
        The content of this DataFrame must include:
        - The start and end dates of the events (named after start_date_name and end_date_name)
        - The description of the events (named after description_name)
        - Data value columns (specified in value_columns)
        - Feature columns (specified in feature_columns)
        - Optional asset localisation column (specified in asset_column)
    value_columns : list of str, default []
        The list of columns in the events DataFrame containing event data values.
    feature_columns : list of str, default []
        The list of columns in the events DataFrame containing event feature values.
    asset_column : str, optional
        The name of the column in the events DataFrame containing the asset IDs.
    values_unit_ids : dict, optional
        Dictionary that maps data column names to their corresponding unit IDs.
    start_date_name : str, default 'start'
        The name of the column containing the start date of the events.
    end_date_name : str, default 'end'
        The name of the column containing the end date of the events.
    description_name : str, default 'description'
        The name of the column containing the description of the events.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, raise_exceptions, log_exceptions_if_not_raised):
        Upload events to OI Analytics.
    """

    def __init__(
        self,
        event_type_id: str,
        events: pd.DataFrame,
        value_columns: Optional[List[str]] = None,
        feature_columns: Optional[List[str]] = None,
        asset_column: Optional[str] = None,
        values_unit_ids: Optional[dict] = None,
        rename_data: bool = True,
        rename_features: bool = True,
        start_date_name: str = "start",
        end_date_name: str = "end",
        description_name: str = "description",
        create_upload_event: Optional[bool] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of EventsOutput.

        Parameters
        ----------
        event_type_id : str
            Unique identifier of the event type.
        events : pandas.DataFrame
            The events DataFrame containing all event information. The DataFrame can be indexed by event ID (optional for creation).
            The content of this DataFrame must include:
            - The start and end dates of the events (named after start_date_name and end_date_name)
            - The description of the events (named after description_name)
            - Data value columns (specified in value_columns)
            - Feature columns (specified in feature_columns)
            - Optional asset localisation column (specified in asset_column)
        value_columns : list of str, optional
            The list of columns in the events DataFrame containing event data values.
        feature_columns : list of str, optional
            The list of columns in the events DataFrame containing event feature values.
        asset_column : str, optional
            The name of the column in the events DataFrame containing the asset IDs.
        values_unit_ids : dict, optional
            Dictionary that maps data column names to their corresponding unit IDs.
        rename_data : bool, default True
            Whether to rename data columns from source code names to data IDs.
        rename_features : bool, default True
            Whether to rename feature columns from source code names to feature IDs.
        start_date_name : str, default 'start'
            The name of the column containing the start date of the events.
        end_date_name : str, default 'end'
            The name of the column containing the end date of the events.
        description_name : str, default 'description'
            The name of the column containing the description of the events.
        create_upload_event : bool, optional
            Whether to create a file upload event when uploading to Oi Analytics.
        """
        self.output_type = "events"
        self.event_type_id = event_type_id
        self.start_date_name = start_date_name
        self.end_date_name = end_date_name
        self.description_name = description_name
        self.asset_column = asset_column
        self.create_upload_event = create_upload_event

        # Initialize column lists
        if value_columns is None:
            value_columns = []
        if feature_columns is None:
            feature_columns = []

        # Copy the events DataFrame
        events_df = events.copy()

        # Rename data columns if specified
        if rename_data is True and value_columns:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Data can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="event", values_type="scalar", mode="id"
            )

            # Rename value columns in the DataFrame
            events_df = events_df.rename(columns=output_dict)
            self.value_columns = [
                output_dict[col] for col in value_columns if col in output_dict.keys()
            ]

            # Rename data in units dict
            if values_unit_ids is not None:
                self.values_unit_ids = {
                    output_dict[k]: v
                    for k, v in values_unit_ids.items()
                    if k in output_dict.keys()
                }
            else:
                self.values_unit_ids = None
        else:
            self.value_columns = value_columns
            self.values_unit_ids = values_unit_ids

        # Rename feature columns if specified
        if rename_features is True and feature_columns:
            model_exec = get_default_model_execution()
            if model_exec is None:
                raise ValueError(
                    "Features can't be renamed without a current model_exec set globally"
                )

            output_dict = model_exec.get_data_output_dict(
                data_type="event", values_type="categorical", mode="id"
            )

            # Rename feature columns in the DataFrame
            events_df = events_df.rename(columns=output_dict)
            self.feature_columns = [
                output_dict[col] for col in feature_columns if col in output_dict.keys()
            ]
        else:
            self.feature_columns = feature_columns

        self.events = events_df
        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload events to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        raise_exceptions : bool, default False
            Whether to raise exception.
        log_exceptions_if_not_raised : bool, default True
            Whether to log exception.
        create_upload_event : bool, optional
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------
        None
        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # update execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        if create_upload_event is None:
            if self.create_upload_event is None:
                model_exec = get_default_model_execution()
                if (
                    model_exec is not None
                    and model_exec.pythonModelInstance.dataExchangeMode
                    == "FILE_PROCESSING"
                ):
                    create_upload_event = False
                else:
                    create_upload_event = True
            else:
                create_upload_event = self.create_upload_event

        # send data
        try:
            response = api.create_or_update_events(
                event_type_id=self.event_type_id,
                events=self.events,
                value_columns=self.value_columns,
                feature_columns=self.feature_columns,
                asset_column=self.asset_column,
                values_unit_ids=self.values_unit_ids,
                start_date_name=self.start_date_name,
                end_date_name=self.end_date_name,
                description_name=self.description_name,
                create_upload_event=create_upload_event,
                api_credentials=api_credentials,
            )

            # update execution report
            execution_report.update(events_created_updated=len(response))
            return response
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class Delay:
    """
    This class contains time delays to be added to the execution of a Python model.

    Attributes
    ----------
    output_type : {'delay'}
        Denotes the specific type of the current output object.
    duration : int
        Time delay in the execution, in seconds.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Add time delays to Python model execution in OI Analytics.
    """

    def __init__(self, duration=5):
        """
        Initialize a new instance of Delay.

        Parameters
        ----------
        duration : int
            Time delay in the execution, in seconds.
        """
        self.output_type = "delay"
        self.duration = duration

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        **kwargs,
    ):
        """
        Add time delays to Python model execution in OI Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials | None
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.

        Returns
        -------

        """
        # update execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        time.sleep(self.duration)


class CustomTextOutput:
    """
    This class contains customized texts to be added to the model execution report.

    Attributes
    ----------
    type : {'text'}
        Denotes the specific type of the current output object.
    content : str
        Customized text to be added to the model execution report.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Add the customized text to the Python model execution report.
    """

    def __init__(
        self,
        content: str,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of CustomTextOutput.

        Parameters
        ----------
        content : str
        """
        self.type = "text"
        self.content = content
        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        **kwargs,
    ) -> None:
        """
        Add the customized text to the Python model execution report.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials | None
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport | None
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.

        Returns
        -------
        None

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # Get the default execution report if not provided
        if execution_report is None:
            execution_report = get_default_execution_report()

        # Update the execution report
        try:
            execution_report.customOutput = CustomModelOutput(
                type=self.type, content=self.content
            )
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class CustomJsonOutput:
    """
    This class contains customized json output to be added to the model execution report.

    Attributes
    ----------
    type : {'json'}
        Denotes the specific type of the current output object.
    content : list | str | dict
        Customized content to send added to the model execution report.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Add customized content to model execution report.
    """

    def __init__(
        self,
        content,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """

        Parameters
        ----------
        content : list | str | dict
        """
        self.type = "json"
        self.content = content
        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        **kwargs,
    ):
        """

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.

        Returns
        -------

        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # Get the default execution report if not provided
        if execution_report is None:
            execution_report = get_default_execution_report()

        # Update the execution report
        try:
            execution_report.customOutput = CustomModelOutput(
                type=self.type, content=self.content
            )
        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class BatchComputationJob:
    """
    This class contains a command to create a batch computation job in OIAnalytics.

    Attributes
    ----------
    output_type : {'batch_computation_job'}
        Indicates the output type to be sent to OIAnalytics
    batch_type_id : str
        The batch type ID attached to batches to be computed
    data_ids : list of str, optional
        List of data IDs to be computed. If empty, all batch data are computed
    batch_ids : list of str, optional
        List of batch IDs to be computed. If empty, all batches are computed
    """

    def __init__(
        self,
        batch_type_id: str,
        data_ids: Optional[List[str]] = None,
        batch_ids: Optional[List[str]] = None,
        raise_exceptions_on_send: bool = True,
        log_exceptions_if_not_raised: bool = True,
    ):
        """
        Initialize a new instance of BatchComputationJob

        Attributes
        ----------
        output_type : {'batch_computation_job'}
            Indicates the output type to be sent to OIAnalytics
        batch_type_id : str
            The batch type ID attached to batches to be computed
        data_ids : list of str, optional
            List of data IDs to be computed. If None, all batch data are computed
        batch_ids : list of str, optional
            List of batch IDs to be computed. If None, all batches are computed
        """

        self.output_type = "batch_computation_job"
        self.batch_type_id = batch_type_id
        self.data_ids = data_ids
        self.batch_ids = batch_ids
        self.raise_exceptions_on_send = raise_exceptions_on_send
        self.log_exceptions_if_not_raised = log_exceptions_if_not_raised

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        **kwargs,
    ) -> None:
        """
        Send the batch computation job creation command to OIAnalytics

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used
        execution_report : ExecutionReport, optional
            Execution report for external use
        print_exceptions : bool, default True
            Whether to print exception
        raise_exceptions : bool, default False
            Whether to raise exception

        Returns
        -------
        dict
            ID and computation job type, with the keys 'id' and 'type'
        """

        # Init optional args
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions_on_send
        if log_exceptions_if_not_raised is None:
            log_exceptions_if_not_raised = self.log_exceptions_if_not_raised

        # update execution report
        if execution_report is None:
            execution_report = get_default_execution_report()

        # send data
        try:
            response = api.endpoints.computation_jobs.create_batch_computation_jobs(
                batch_type_id=self.batch_type_id,
                data_ids=self.data_ids,
                batch_ids=self.batch_ids,
                api_credentials=api_credentials,
            )

            execution_report.update(batch_created_updated=len(self.batch_ids))

            return response

        except Exception:
            execution_report.update(errors=1)
            if raise_exceptions is True:
                raise
            if log_exceptions_if_not_raised is True:
                print(
                    f"Error when trying to send to OIAnalytics:\n{traceback.format_exc()}"
                )


class OIModelOutputs:
    """
    This class contains all the outputs objects to be sent to Oi Analytics.

    Attributes
    ----------
    output_type : {'outputs_queue'}
        Denotes the specific type of the current output object.
    model_outputs : list of objects
        List of output objects resulted from the model.

    Methods
    -------
    send_to_oianalytics(self, api_credentials, execution_report, print_exceptions, raise_exceptions):
        Upload all model outputs to Oi Analytics.
    """

    def __init__(self):
        self.output_type = "outputs_queue"
        self.model_outputs = []

    def add_output(
        self,
        output_object: Union[
            FileOutput,
            TimeValuesOutput,
            BatchValuesOutput,
            VectorTimeValuesOutput,
            VectorBatchValuesOutput,
            Delay,
            CustomTextOutput,
            CustomJsonOutput,
        ],
    ) -> None:
        """

        Parameters
        ----------
        output_object : FileOutput | TimeValuesOutput | BatchValuesOutput | VectorTimeValuesOutput | VectorBatchValuesOutput | Delay | CustomTextOutput | CustomJsonOutput

        Returns
        -------
        None

        """
        self.model_outputs.append(output_object)

    def send_to_oianalytics(
        self,
        api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
        execution_report: Optional[ExecutionReport] = None,
        raise_exceptions: Optional[bool] = None,
        log_exceptions_if_not_raised: Optional[bool] = None,
        create_upload_event: Optional[bool] = None,
    ) -> None:
        """
        Upload all model outputs to Oi Analytics.

        Parameters
        ----------
        api_credentials : api.OIAnalyticsAPICredentials, optional
            The credentials to use to query the API. If None, previously set default credentials are used.
        execution_report : ExecutionReport, optional
            Execution report for external use.
        print_exceptions : bool, default True
            Whether to print exception.
        raise_exceptions : bool, default False
            Whether to raise exception.
        create_upload_event : bool, optional
            Whether to create a file upload event when uploading to Oi Analytics.

        Returns
        -------
        None

        """
        for model_output in self.model_outputs:
            model_output.send_to_oianalytics(
                api_credentials=api_credentials,
                execution_report=execution_report,
                raise_exceptions=raise_exceptions,
                log_exceptions_if_not_raised=log_exceptions_if_not_raised,
                create_upload_event=create_upload_event,
            )
