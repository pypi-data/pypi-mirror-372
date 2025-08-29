from typing import Optional
import json

from .. import utils
from .. import _dtos
from ... import api

__all__ = ["load_model", "parse_model_execution", "setup_tests"]


def load_model(model_source_path: str):
    return utils.load_module_from_file(model_source_path)


def parse_model_execution(model_execution_str: str):
    return _dtos.ModelExecution(**json.loads(model_execution_str))


def setup_tests(
    credentials: Optional[api.OIAnalyticsAPICredentials] = None,
    model_execution: Optional[_dtos.ModelExecution] = None,
):
    if credentials is not None:
        credentials.set_as_default_credentials()
        print("Provided credentials have been set as default ones")
    else:
        print("No API credentials were provided for setting the default ones")

    if model_execution is not None:
        model_execution.set_as_default_model_execution()
        print("Provided model execution has been set as the default one")
    else:
        print(
            "No model execution configuration was provided for setting the default one"
        )
