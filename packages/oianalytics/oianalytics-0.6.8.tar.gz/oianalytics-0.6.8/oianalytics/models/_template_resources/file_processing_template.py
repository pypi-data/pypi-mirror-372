from datetime import datetime
import io

from oianalytics import models
import pandas as pd


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
    **kwargs
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


def process_file(
    file_content: io.BytesIO,
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
    **kwargs
):
    # # Arguments can be absent from the function signature as long **kwargs is present
    # # Only useful arguments can be kept
    # # Keeping **kwargs in the signature is strongly recommended for easier future compatibility
    # #
    # # The 'file_content' is provided automatically using api.endpoints.files.get_file_from_file_upload
    # # The output of 'load_resources' is sent through the 'resources' argument
    #
    # # The output of this function should be an object made for sending model results into OIAnalytics
    # # These are the output objects found in models.outputs
    # # Typically it would be a container for multiple output such as the following
    # df = pd.read_csv(file_content)
    # df["new_col"] = 1
    #
    # outputs = models.outputs.OIModelOutputs()
    #
    # # Specific outputs can be added to such a container (in this case the same file with changed separator)
    # outputs.add_output(
    #     models.outputs.FileOutput.from_pandas(
    #         data=df, file_name="my_file.csv", writing_kwargs={"sep": ";"}
    #     )
    # )
    #
    # # This object has then to be returned by the model
    # # The OIAnalytics application is responsible for sending and actually storing values
    # return outputs
    pass
