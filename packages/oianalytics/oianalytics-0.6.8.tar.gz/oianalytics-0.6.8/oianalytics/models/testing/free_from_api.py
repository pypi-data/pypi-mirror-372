from typing import Optional, Any, Callable

from .. import _dtos
from .. import outputs

__all__ = [
    "test_load_data",
    "test_load_resources",
    "test_process_data",
    "test_full_model",
]


def test_load_data(
    load_data: Callable,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Run load_data function
    return load_data(**model_execution.execution_kwargs)


def test_load_resources(
    load_resources: Callable,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Run load_resources function
    return load_resources(**model_execution.execution_kwargs)


def test_process_data(
    process_data: Callable,
    data: Optional[Any] = None,
    resources: Optional[Any] = None,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Run process_data function
    model_output = process_data(
        data=data, resources=resources, **model_execution.execution_kwargs
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
            outputs.BatchComputationJob,
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
    load_data: Callable,
    load_resources: Callable,
    process_data: Callable,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Run load_resources function
    resources = load_resources(**model_execution.execution_kwargs)

    # Run load_data function
    data = load_data(resources=resources, **model_execution.execution_kwargs)

    model_output = test_process_data(
        process_data=process_data,
        data=data,
        resources=resources,
    )

    return model_output
