from typing import Optional, Any, Callable

import pandas as pd

from .. import outputs
from .. import _dtos
from .. import get_single_obs_batch_data, get_single_obs_time_data

__all__ = [
    "get_input_data",
    "test_load_resources",
    "test_process_data",
    "test_full_model",
]


def get_input_data(
    model_execution: Optional[_dtos.ModelExecution] = None,
    rename_data_to_source_code_name: bool = True,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Get data
    if model_execution.pythonModelInstance.dataExchangeMode != "SINGLE_OBSERVATION":
        raise ValueError(
            "The provided model execution input is not in single observation mode"
        )

    if model_execution.pythonModelInstance.singleObservationContext.type == "time":
        return get_single_obs_time_data(
            model_execution=model_execution,
            rename_data_to_source_code_name=rename_data_to_source_code_name,
        )

    elif model_execution.pythonModelInstance.singleObservationContext.type == "batch":
        return get_single_obs_batch_data(
            model_execution=model_execution,
            rename_data_to_source_code_name=rename_data_to_source_code_name,
        )


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
    data: pd.DataFrame,
    resources: Optional[Any] = None,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Get default model_execution if not provided
    if model_execution is None:
        model_execution = _dtos.get_default_model_execution()

    # Init outputs storage
    model_outputs = outputs.OIModelOutputs()

    # Run process_data function
    output_data = data.apply(
        lambda r: pd.Series(process_data(resources=resources, **r.to_dict())),
        axis=1,
    )

    # list of time values sources codes names
    time_values_names = [
        col
        for col in output_data.columns
        if col
        in model_execution.get_data_output_dict(
            data_type="time", values_type="scalar", mode="reference"
        ).keys()
    ]

    # add time values output object
    if len(time_values_names) > 0:
        model_outputs.add_output(
            outputs.TimeValuesOutput(
                data=output_data[time_values_names],
            )
        )

    # list of vector time values sources codes names
    vector_time_values_names = [
        col
        for col in output_data.columns
        if col
        in model_execution.get_data_output_dict(
            data_type="time", values_type="vector", mode="object"
        ).keys()
    ]
    output_vector_time_values = output_data[vector_time_values_names]

    if len(vector_time_values_names) > 0:
        df_list = [
            pd.concat(
                output_vector_time_values[name].to_dict(),
                axis=1,
                sort=True,
            ).T
            for name in vector_time_values_names
        ]

        # create vector time values output object
        model_outputs.add_output(
            outputs.VectorTimeValuesOutput(
                data=df_list,
                data_reference=vector_time_values_names,
            )
        )

    single_obs_context_type = (
        model_execution.pythonModelInstance.singleObservationContext.type
    )

    if len(vector_time_values_names) > 0:
        df_list = [
            pd.concat(
                output_vector_time_values[name].to_dict(),
                axis=1,
                sort=True,
            ).T
            for name in vector_time_values_names
        ]

        # create vector time values output object
        model_outputs.add_output(
            outputs.VectorTimeValuesOutput(
                data=df_list,
                data_reference=vector_time_values_names,
            )
        )

    if single_obs_context_type == "batch":
        # list of batch values sources codes names
        batch_values_names = [
            col
            for col in output_data.columns
            if col
            in model_execution.get_data_output_dict(
                data_type="batch", values_type="scalar", mode="id"
            ).keys()
        ]

        if len(batch_values_names) > 0:
            model_outputs.add_output(
                outputs.BatchValuesOutput(
                    batch_type_id=model_execution.pythonModelInstance.singleObservationContext.batchPredicate.batchType.id,
                    data=output_data[batch_values_names],
                )
            )

        # list of vector batch values sources codes names
        vector_batch_values_names = [
            col
            for col in output_data.columns
            if col
            in model_execution.get_data_output_dict(
                data_type="batch", values_type="vector", mode="object"
            ).keys()
        ]
        # DataFrame containing only with vector batch values
        output_vector_batch_values = output_data[vector_batch_values_names]

        if len(vector_batch_values_names) > 0:
            df_list = [
                pd.concat(
                    output_vector_batch_values[name].to_dict(),
                    axis=1,
                    sort=True,
                ).T
                for name in vector_batch_values_names
            ]

            # create output object for batch vector values
            model_outputs.add_output(
                outputs.VectorBatchValuesOutput(
                    data_reference=vector_batch_values_names,
                    data=df_list,
                )
            )

        # list with batch features names
        features_names = [
            col
            for col in output_data.columns
            if col
            in model_execution.get_output_dict(output_types=["BATCH_TAG_KEY"]).keys()
        ]
        # DataFrame only with batches features
        output_features = output_data[features_names]

        # create output features object
        if len(features_names) > 0:
            model_outputs.add_output(
                outputs.BatchFeaturesOutput(
                    batch_type_id=model_execution.pythonModelInstance.singleObservationContext.batchPredicate.batchType.id,
                    data=output_features,
                )
            )

    # Output
    return model_outputs


def test_full_model(
    load_resources: Callable,
    process_data: Callable,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    # Load data
    data = get_input_data(model_execution=model_execution)

    # Load resources
    resources = test_load_resources(
        load_resources=load_resources, model_execution=model_execution
    )

    # Process data
    return test_process_data(
        process_data=process_data,
        data=data,
        resources=resources,
        model_execution=model_execution,
    )
