from datetime import datetime

from oianalytics import models


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


def process_data(
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
    # Arguments can be absent from the function signature as long **kwargs is present
    # Only useful arguments can be kept
    # Keeping **kwargs in the signature is strongly recommended for easier future compatibility
    #
    # Input data should be provided as arguments, using their source code name
    # The output should be a dictionary using output source code names as keys
    # The basic following example (which converts a temperature from Celsius to Kelvin) is properly structured
    # def process_data(temp_c, **kwargs):
    #     temp_k = temp_c + 273.15
    #     return {"temp_k": temp_k}
    pass
