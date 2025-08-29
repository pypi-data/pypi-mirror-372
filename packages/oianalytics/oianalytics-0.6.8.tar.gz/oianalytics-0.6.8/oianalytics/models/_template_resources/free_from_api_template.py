from datetime import datetime

from oianalytics import api, models


def load_resources(
    model_instance_id: str,
    test_mode: bool,
    current_execution_date: datetime,
    last_execution_date: datetime,
    input_parameters: dict,
    input_parameter_references: dict,
    input_parameter_ids: dict,
    output_parameters: dict,
    output_parameter_references: dict,
    output_parameter_ids: dict,
    **kwargs,
):
    # # Arguments can be absent from the function signature as long **kwargs is present
    # # Only useful arguments can be kept
    # # Keeping **kwargs in the signature is strongly recommended for easier future compatibility
    #
    # # Here's an example on how to retrieve an instance resource
    # my_resource = models.get_resource_file(
    #     resource_file_id=input_parameter_ids["my_resource_sourcecodename"]
    # )
    #
    # # The resources to be used in the 'process_data' function have to be returned
    # # It can be any format since the 'process_data' is responsible of its usage
    # return my_resource
    # return {"my_first_resource": my_resource}
    pass


def load_data(
    resources,
    model_instance_id: str,
    test_mode: bool,
    current_execution_date: datetime,
    last_execution_date: datetime,
    input_parameters: dict,
    input_parameter_references: dict,
    input_parameter_ids: dict,
    output_parameters: dict,
    output_parameter_references: dict,
    output_parameter_ids: dict,
    **kwargs,
):
    # # Arguments can be absent from the function signature as long **kwargs is present
    # # Only useful arguments can be kept
    # # Keeping **kwargs in the signature is strongly recommended for easier future compatibility
    #
    # # The output of 'load_resources' is sent through the 'resources' argument
    #
    # # Here's an example on how to retrieve a single time data values
    # time_data = api.get_time_values(
    #     data_id=input_parameter_ids["my_timedata_sourcecodename"],
    #     start_date=last_execution_date,
    #     end_date=current_execution_date,
    #     aggregation="RAW_VALUES",
    # )
    #
    # # The data to be used in the 'process_data' function has to be returned
    # # It can be any format since the 'process_data' is responsible of its usage
    # return time_data
    # return {"my_time_data": time_data}
    pass


def process_data(
    data,
    resources,
    model_instance_id: str,
    test_mode: bool,
    current_execution_date: datetime,
    last_execution_date: datetime,
    input_parameters: dict,
    input_parameter_references: dict,
    input_parameter_ids: dict,
    output_parameters: dict,
    output_parameter_references: dict,
    output_parameter_ids: dict,
    **kwargs,
):
    # # Arguments can be absent from the function signature as long **kwargs is present
    # # Only useful arguments can be kept
    # # Keeping **kwargs in the signature is strongly recommended for easier future compatibility
    #
    # # The output of 'load_data' is sent through the 'data' argument
    # # The output of 'load_resources' is sent through the 'resources' argument
    #
    # # The output of this function should be an object made for sending model results into OIAnalytics
    # # These are the output objects found in models.outputs
    # # Typically it would be a container for multiple output such as the following
    # outputs = models.outputs.OIModelOutputs()
    #
    # # Specific outputs can be added to such a container
    # outputs.add_output(
    #     models.outputs.FileOutput.from_pandas(
    #         data=data, file_name="my_time_values.csv", writing_kwargs={"sep": ";"}
    #     )
    # )
    #
    # # This object has then to be returned by the model
    # # The OIAnalytics application is responsible for sending and actually storing values
    # return outputs
    pass
