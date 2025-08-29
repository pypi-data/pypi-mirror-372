import io
from typing import Callable, Optional, Any

from .. import _dtos, outputs
from ...api import endpoints

__all__ = [
    "test_load_resources",
    "test_process_file",
    "test_full_model",
    "get_file_content",
]


def test_load_resources(
    load_resources: Callable,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Run load_resources function
    return load_resources(**model_execution.execution_kwargs)


def test_process_file(
    process_file: Callable,
    file_content: io.BytesIO,
    resources: Optional[Any] = None,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Run process_file function
    model_output = process_file(
        file_content=file_content,
        resources=resources,
        **model_execution.execution_kwargs
    )

    if not isinstance(
        model_output,
        (
            outputs.OIModelOutputs,
            outputs.FileOutput,
            outputs.TimeValuesOutput,
            outputs.VectorTimeValuesOutput,
            outputs.BatchValuesOutput,
            outputs.VectorBatchValuesOutput,
            outputs.BatchFeaturesOutput,
            outputs.CustomJsonOutput,
            outputs.CustomTextOutput,
            outputs.Delay,
        ),
    ):
        print(
            "Warning: the model output should be an instance of an output class from oianalytics.models.outputs"
        )

    return model_output


def test_full_model(
    load_resources: Callable,
    process_file: Callable,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Load file content
    file_content = endpoints.files.get_file_from_file_upload(
        file_upload_id=model_execution.executionContext.uploadEventId,
    )

    # Run load_resources function
    resources = load_resources(**model_execution.execution_kwargs)

    model_output = test_process_file(
        process_file=process_file,
        file_content=file_content,
        resources=resources,
    )

    return model_output


def get_file_content(model_execution: Optional[_dtos.ModelExecution] = None):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()
    # call the endpoint
    return endpoints.files.get_file_from_file_upload(
        file_upload_id=model_execution.executionContext.uploadEventId,
    )
