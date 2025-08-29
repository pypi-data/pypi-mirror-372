from typing import Union, List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta

import pandas as pd
from pydantic import (
    BaseModel,
    field_validator,
    StrictStr,
    StrictBool,
    StrictInt,
    StrictFloat,
)

from .. import api

__all__ = [
    "ModelExecution",
    "get_default_model_execution",
    "set_default_model_execution",
    "CustomModelOutput",
    "ExecutionReport",
    "get_default_execution_report",
    "set_default_execution_report",
]


class CustomModelOutput(BaseModel):
    type: str
    content: Union[List, StrictStr, Dict]


class ExecutionReport(BaseModel):
    testMode: StrictBool
    status: str = "FAILURE"
    customOutput: Optional[CustomModelOutput] = None
    numberOfTimeValuesCreatedOrUpdated: StrictInt = 0
    numberOfTimeValuesDeleted: StrictInt = 0
    numberOfBatchValuesCreatedOrUpdated: StrictInt = 0
    numberOfBatchTagsCreatedOrUpdated: StrictInt = 0
    numberOfBatchCreatedOrUpdated: StrictInt = 0
    numberOfEventCreatedOrUpdated: StrictInt = 0
    numberOfEventValuesCreatedOrUpdated: StrictInt = 0
    numberOfEventTagsCreatedOrUpdated: StrictInt = 0
    numberOfBatchRelationsCreatedOrUpdated: StrictInt = 0
    numberOfErrors: StrictInt = 0
    numberOfTimeVectorValuesCreatedOrUpdated: StrictInt = 0
    numberOfBatchVectorValuesCreatedOrUpdated: StrictInt = 0
    numberOfFilesUploaded: StrictInt = 0

    def update(
        self,
        time_values_updated: StrictInt = 0,
        time_values_deleted: StrictInt = 0,
        batch_values_updated: StrictInt = 0,
        batch_tags_updated: StrictInt = 0,
        batch_created_updated: StrictInt = 0,
        events_created_updated: StrictInt = 0,
        event_values_updated: StrictInt = 0,
        event_tags_updated: StrictInt = 0,
        batch_relations_updated: StrictInt = 0,
        errors: StrictInt = 0,
        time_vector_values_updated: StrictInt = 0,
        batch_vector_values_updated: StrictInt = 0,
        files_uploaded: StrictInt = 0,
    ):
        self.numberOfTimeValuesCreatedOrUpdated += time_values_updated
        self.numberOfTimeValuesDeleted += time_values_deleted
        self.numberOfBatchValuesCreatedOrUpdated += batch_values_updated
        self.numberOfBatchTagsCreatedOrUpdated += batch_tags_updated
        self.numberOfBatchCreatedOrUpdated += batch_created_updated
        self.numberOfEventCreatedOrUpdated += events_created_updated
        self.numberOfEventValuesCreatedOrUpdated += event_values_updated
        self.numberOfEventTagsCreatedOrUpdated += event_tags_updated
        self.numberOfBatchRelationsCreatedOrUpdated += batch_relations_updated
        self.numberOfErrors += errors
        self.numberOfTimeVectorValuesCreatedOrUpdated += time_vector_values_updated
        self.numberOfBatchVectorValuesCreatedOrUpdated += batch_vector_values_updated
        self.numberOfFilesUploaded += files_uploaded

    def set_as_default_report(self):
        set_default_execution_report(self)


# Credentials
class BasicAuthCredentials(BaseModel):
    baseUrl: StrictStr
    login: StrictStr
    pwd: StrictStr

    def to_object(self):
        return api.OIAnalyticsAPICredentials(
            base_url=self.baseUrl, login=self.login, pwd=self.pwd
        )


class TokenCredentials(BaseModel):
    baseUrl: StrictStr
    token: StrictStr

    def to_object(self):
        return api.OIAnalyticsAPICredentials(base_url=self.baseUrl, token=self.token)


Credentials = Union[BasicAuthCredentials, TokenCredentials]


# Cron Trigger
class CronTrigger(BaseModel):
    type: StrictStr
    cron: StrictStr

    @field_validator("type")
    def check_type(cls, value):
        if value != "cron-trigger":
            raise ValueError("Trigger type should be 'cron-trigger'")
        return value


# File Reception Trigger
class FileReceptionTrigger(BaseModel):
    type: StrictStr

    @field_validator("type")
    def check_type(cls, value):
        if value != "file-reception":
            raise ValueError("Trigger type should be 'file-reception'")
        return value


# Manual only trigger
class ManualOnlyTrigger(BaseModel):
    type: StrictStr

    @field_validator("type")
    def check_type(cls, value):
        if value != "manual-only":
            raise ValueError("Trigger type should be 'manual-only'")
        return value


Trigger = Union[CronTrigger, FileReceptionTrigger, ManualOnlyTrigger]


# Model inputs & outputs
class StringParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[StrictStr] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "STRING":
            raise ValueError("'type' should be 'STRING'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class SecretParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[StrictStr] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "SECRET":
            raise ValueError("'type' should be 'SECRET'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class BooleanParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[StrictBool] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "BOOLEAN":
            raise ValueError("'type' should be 'BOOLEAN'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class NumericParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[Union[StrictInt, StrictFloat]] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "NUMERIC":
            raise ValueError("'type' should be 'NUMERIC'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class FileParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[StrictStr] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "FILE":
            raise ValueError("'type' should be 'FILE'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class PeriodParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[str] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "PERIOD":
            raise ValueError("'type' should be 'PERIOD'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class DurationParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[timedelta] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "DURATION":
            raise ValueError("'type' should be 'DURATION'")
        return value

    @field_validator("value", mode="before")
    def parse_value(cls, value):
        if value is None:
            return None
        else:
            return pd.Timedelta(value, unit="ms").to_pytimedelta()

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class InstantParameter(BaseModel):
    type: Literal["INSTANT"]
    sourceCodeName: StrictStr
    value: Optional[datetime] = None

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value


class UnitValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class UnitParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[UnitValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "UNIT":
            raise ValueError("'type' should be 'UNIT'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class MeasurementValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class MeasurementParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[MeasurementValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "MEASUREMENT":
            raise ValueError("'type' should be 'MEASUREMENT'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class TagKeyValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class TagKeyParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[TagKeyValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "TAG_KEY":
            raise ValueError("'type' should be 'TAG_KEY'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class TagValueValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class TagValueParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[TagValueValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "TAG_VALUE":
            raise ValueError("'type' should be 'TAG_VALUE'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class DataUnit(BaseModel):
    id: StrictStr
    label: StrictStr


class DataValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr
    dataType: StrictStr
    unit: DataUnit
    aggregationFunction: Optional[StrictStr] = None


class VectorDataValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr
    dataType: StrictStr
    valueUnit: DataUnit
    indexUnit: DataUnit
    aggregationFunction: Optional[StrictStr] = None


class DataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[DataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "DATA":
            raise ValueError("'type' should be 'DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class VectorDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[VectorDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "VECTOR_DATA":
            raise ValueError("'type' should be 'VECTOR_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class StoredContinuousDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[DataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "STORED_CONTINUOUS_DATA":
            raise ValueError("'type' should be 'STORED_CONTINUOUS_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class BatchType(BaseModel):
    id: StrictStr
    name: StrictStr


class BatchDataValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr
    dataType: StrictStr
    unit: DataUnit
    aggregationFunction: Optional[StrictStr] = None
    batchType: BatchType


class EventDataValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr
    dataType: StrictStr
    unit: DataUnit
    aggregationFunction: Optional[StrictStr] = None


class BatchVectorDataValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr
    dataType: StrictStr
    valueUnit: DataUnit
    indexUnit: DataUnit
    aggregationFunction: Optional[StrictStr] = None
    indexAggregationFunction: Optional[StrictStr] = None
    batchType: BatchType
    batchesIds: Optional[List[StrictStr]] = None


class StoredBatchDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[BatchDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "STORED_BATCH_DATA":
            raise ValueError("'type' should be 'STORED_BATCH_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class StoredEventDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[EventDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "STORED_EVENT_DATA":
            raise ValueError("'type' should be 'STORED_EVENT_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class StoredBatchVectorDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[BatchVectorDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "STORED_BATCH_VECTOR_DATA":
            raise ValueError("'type' should be 'STORED_BATCH_VECTOR_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class StoredTimeVectorDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[VectorDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "STORED_CONTINUOUS_VECTOR_DATA":
            raise ValueError("'type' should be 'STORED_CONTINUOUS_VECTOR_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class ComputedContinuousDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[DataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "COMPUTED_CONTINUOUS_DATA":
            raise ValueError("'type' should be 'COMPUTED_CONTINUOUS_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class ComputedBatchDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[BatchDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "COMPUTED_BATCH_DATA":
            raise ValueError("'type' should be 'COMPUTED_BATCH_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class BatchTimeDataParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[BatchDataValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "BATCH_TIME_DATA":
            raise ValueError("'type' should be 'BATCH_TIME_DATA'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class BatchPredicateBatchType(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class BatchTagValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr

    @field_validator("type")
    def check_type(cls, value):
        if value != "batch-tag-value":
            raise ValueError("Batch tag value type should be 'batch-tag-value'")
        return value


class BatchPredicateValue(BaseModel):
    type: StrictStr
    batchType: BatchPredicateBatchType
    featureFilters: List[BatchTagValue]

    @field_validator("type")
    def check_type(cls, value):
        if value != "batch-predicate":
            raise ValueError("Batch predicate type should be 'batch-predicate'")
        return value


class BatchPredicateParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[BatchPredicateValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "BATCH_PREDICATE":
            raise ValueError("'type' should be 'BATCH_PREDICATE'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.batchType.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.batchType.id


class BatchStructureValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class BatchStructureParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[BatchStructureValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "BATCH_STRUCTURE":
            raise ValueError("'type' should be 'BATCH_STRUCTURE'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class BatchTagKeyParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[TagKeyValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "BATCH_TAG_KEY":
            raise ValueError("'type' should be 'BATCH_TAG_KEY'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class BatchTagValueParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[TagValueValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "BATCH_TAG_VALUE":
            raise ValueError("'type' should be 'BATCH_TAG_KEY'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class EventTypeValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class EventTypeParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[EventTypeValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "EVENT_TYPE":
            raise ValueError("'type' should be 'EVENT_TYPE'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class EventTagKeyValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class EventTagKeyParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[EventTagKeyValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "EVENT_TAG_KEY":
            raise ValueError("'type' should be 'EVENT_TAG_KEY'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class EventTagValueValue(BaseModel):
    type: StrictStr
    id: StrictStr
    reference: StrictStr


class EventTagValueParameter(BaseModel):
    type: StrictStr
    sourceCodeName: StrictStr
    value: Optional[EventTagValueValue] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value != "EVENT_TAG_VALUE":
            raise ValueError("'type' should be 'EVENT_TAG_VALUE'")
        return value

    @property
    def readable_value(self):
        if self.value is None:
            return None
        else:
            return self.value.reference

    @property
    def technical_value(self):
        if self.value is None:
            return None
        else:
            return self.value.id


class TimeDataParametersListValue(BaseModel):
    type: Literal["temporal-data-list"]
    dataList: List[DataValue]


class TimeDataParametersList(BaseModel):
    type: Literal["TEMPORAL_DATA_LIST"]
    sourceCodeName: StrictStr
    value: TimeDataParametersListValue

    @property
    def readable_value(self) -> List[StrictStr]:
        return [value.reference for value in self.value.dataList]

    @property
    def technical_value(self) -> List[StrictStr]:
        return [value.id for value in self.value.dataList]


class BatchDataParametersListValue(BaseModel):
    type: Literal["batch-data-list"]
    dataList: List[BatchDataValue]


class BatchDataParametersList(BaseModel):
    type: Literal["BATCH_DATA_LIST"]
    sourceCodeName: StrictStr
    value: BatchDataParametersListValue

    @property
    def readable_value(self) -> List[StrictStr]:
        return [value.reference for value in self.value.dataList]

    @property
    def technical_value(self) -> List[StrictStr]:
        return [value.id for value in self.value.dataList]


InstanceParameter = Union[
    StringParameter,
    SecretParameter,
    BooleanParameter,
    NumericParameter,
    FileParameter,
    PeriodParameter,
    DurationParameter,
    InstantParameter,
    UnitParameter,
    MeasurementParameter,
    TagKeyParameter,
    TagValueParameter,
    DataParameter,
    TimeDataParametersList,
    BatchDataParametersList,
    StoredContinuousDataParameter,
    StoredBatchDataParameter,
    StoredTimeVectorDataParameter,
    StoredBatchVectorDataParameter,
    ComputedContinuousDataParameter,
    ComputedBatchDataParameter,
    BatchTimeDataParameter,
    BatchPredicateParameter,
    BatchStructureParameter,
    BatchTagKeyParameter,
    BatchTagValueParameter,
    StoredEventDataParameter,
    EventTypeParameter,
    EventTagKeyParameter,
    EventTagValueParameter,
]


# Model instance
class SingleObservationTimeContext(BaseModel):
    type: StrictStr
    overlappingPeriod: timedelta
    aggregationPeriod: StrictStr

    @field_validator("type")
    def check_type(cls, value):
        if value != "time":
            raise ValueError("Single observation type should be 'time'")
        return value

    @field_validator("overlappingPeriod", mode="before")
    def parse_overlapping_period(cls, value):
        return pd.Timedelta(value).to_pytimedelta()


class SingleObservationBatchContext(BaseModel):
    type: StrictStr
    batchPredicate: BatchPredicateValue
    overlappingPeriod: timedelta

    @field_validator("type")
    def check_type(cls, value):
        if value != "batch":
            raise ValueError("Single observation type should be 'batch'")
        return value

    @field_validator("overlappingPeriod", mode="before")
    def parse_overlapping_period(cls, value):
        return pd.Timedelta(value).to_pytimedelta()


SingleObservationContext = Union[
    SingleObservationBatchContext, SingleObservationTimeContext
]


class ExecutionContext(BaseModel):
    type: StrictStr
    initiator: StrictStr
    lastSuccessfulExecutionInstant: Optional[datetime] = None
    currentExecutionInstant: datetime
    customData: Optional[Any] = None
    uploadEventId: Optional[StrictStr] = None
    fileName: Optional[StrictStr] = None


class ModelInstance(BaseModel):
    id: StrictStr
    trigger: Trigger
    active: StrictBool
    dataExchangeMode: StrictStr
    singleObservationContext: Optional[SingleObservationContext] = None
    inputParameters: List[InstanceParameter]
    outputParameters: List[InstanceParameter]


# Model execution
class ModelExecution(BaseModel):
    testMode: StrictBool
    credentials: Optional[Credentials] = None
    lastSuccessfulExecutionInstant: Optional[datetime] = None
    currentExecutionInstant: datetime
    executionContext: ExecutionContext
    pythonModelInstance: ModelInstance

    def set_as_default_model_execution(self):
        set_default_model_execution(self)

    def find_inputs_by_types(self, input_types: Optional[List[str]] = None):
        if input_types is None:
            return self.pythonModelInstance.inputParameters
        else:
            return [
                param
                for param in self.pythonModelInstance.inputParameters
                if param.type in input_types
            ]

    def find_input_by_sourcecodename(self, source_code_name: str):
        for param in self.pythonModelInstance.inputParameters:
            if param.sourceCodeName == source_code_name:
                return param
            raise KeyError(
                f"No input parameter is referenced by the source code name {source_code_name}"
            )

    def find_outputs_by_types(self, output_types: Optional[List[str]] = None):
        if output_types is None:
            return self.pythonModelInstance.outputParameters
        else:
            return [
                param
                for param in self.pythonModelInstance.outputParameters
                if param.type in output_types
            ]

    def find_output_by_sourcecodename(self, source_code_name: str):
        for param in self.pythonModelInstance.outputParameters:
            if param.sourceCodeName == source_code_name:
                return param
            raise KeyError(
                f"No output parameter is referenced by the source code name {source_code_name}"
            )

    def get_input_dict(
        self,
        input_types: Optional[List[str]] = None,
        mode: str = "object",
        exclude_empty_values: bool = True,
    ):
        input_params = self.find_inputs_by_types(input_types)
        if mode == "reference":
            input_dict = {
                param.sourceCodeName: param.readable_value for param in input_params
            }
        elif mode == "id":
            input_dict = {
                param.sourceCodeName: param.technical_value for param in input_params
            }
        elif mode == "object":
            input_dict = {param.sourceCodeName: param.value for param in input_params}
        else:
            raise ValueError(f"Unknown 'mode': {mode}")

        if exclude_empty_values is True:
            input_dict = {k: v for k, v in input_dict.items() if v is not None}

        return input_dict

    def get_output_dict(
        self,
        output_types: Optional[List[str]] = None,
        mode: str = "object",
        exclude_empty_values: bool = True,
    ):
        output_params = self.find_outputs_by_types(output_types)
        if mode == "reference":
            output_dict = {
                param.sourceCodeName: param.readable_value for param in output_params
            }
        elif mode == "id":
            output_dict = {
                param.sourceCodeName: param.technical_value for param in output_params
            }
        elif mode == "object":
            output_dict = {param.sourceCodeName: param.value for param in output_params}
        else:
            raise ValueError(f"Unknown value for 'mode': {mode}")

        if exclude_empty_values is True:
            output_dict = {k: v for k, v in output_dict.items() if v is not None}

            return output_dict

    def get_data_input_dict(
        self,
        data_type: str = "any",
        values_type: str = "any",
        strict: bool = False,
        mode: str = "object",
        exclude_empty_values: bool = True,
    ):
        """
        Parameters
        ----------
        data_type: {'any, 'time', 'batch'}
        values_type: {'any', 'scalar', 'vector'}
        strict: bool
        mode: {'object', 'reference', 'id'}
        exclude_empty_values: bool
        """
        if data_type == "any" and values_type == "any":
            input_types = [
                "DATA",
                "STORED_CONTINUOUS_DATA",
                "STORED_BATCH_DATA",
                "COMPUTED_CONTINUOUS_DATA",
                "TEMPORAL_DATA_LIST",
                "COMPUTED_BATCH_DATA",
                "BATCH_TIME_DATA",
                "BATCH_DATA_LIST",
                "BATCH_TAG_KEY",
                "STORED_CONTINUOUS_VECTOR_DATA",
                "STORED_BATCH_VECTOR_DATA",
            ]
        elif data_type == "any" and values_type == "scalar":
            input_types = [
                "DATA",
                "STORED_CONTINUOUS_DATA",
                "STORED_BATCH_DATA",
                "COMPUTED_CONTINUOUS_DATA",
                "TEMPORAL_DATA_LIST",
                "COMPUTED_BATCH_DATA",
                "BATCH_TIME_DATA",
                "BATCH_DATA_LIST",
                "BATCH_TAG_KEY",
            ]
        elif data_type == "any" and values_type == "vector":
            input_types = [
                "STORED_CONTINUOUS_VECTOR_DATA",
                "STORED_BATCH_VECTOR_DATA",
            ]
        elif data_type == "time" and values_type == "any":
            input_types = [
                "STORED_CONTINUOUS_DATA",
                "COMPUTED_CONTINUOUS_DATA",
                "STORED_CONTINUOUS_VECTOR_DATA",
                "TEMPORAL_DATA_LIST",
            ]
            if strict is False:
                input_types.append("DATA")
        elif data_type == "time" and values_type == "scalar":
            input_types = [
                "STORED_CONTINUOUS_DATA",
                "COMPUTED_CONTINUOUS_DATA",
                "TEMPORAL_DATA_LIST",
            ]
            if strict is False:
                input_types.append("DATA")
        elif data_type == "time" and values_type == "vector":
            input_types = ["STORED_CONTINUOUS_VECTOR_DATA"]
            if strict is False:
                input_types.append("VECTOR_DATA")
        elif data_type == "batch" and values_type == "any":
            input_types = [
                "STORED_BATCH_DATA",
                "COMPUTED_BATCH_DATA",
                "BATCH_TIME_DATA",
                "BATCH_DATA_LIST",
                "BATCH_TAG_KEY",
                "STORED_BATCH_VECTOR_DATA",
            ]
            if strict is False:
                input_types.append("DATA")
        elif data_type == "batch" and values_type == "scalar":
            input_types = [
                "STORED_BATCH_DATA",
                "COMPUTED_BATCH_DATA",
                "BATCH_TIME_DATA",
                "BATCH_DATA_LIST",
                "BATCH_TAG_KEY",
            ]
            if strict is False:
                input_types.append("DATA")
        elif data_type == "batch" and values_type == "vector":
            input_types = ["STORED_BATCH_VECTOR_DATA"]
            if strict is False:
                input_types.append("VECTOR_DATA")
        else:
            raise ValueError(f"Unknown 'data_type': {data_type}")

        return self.get_input_dict(
            input_types=input_types,
            mode=mode,
            exclude_empty_values=exclude_empty_values,
        )

    def get_data_output_dict(
        self,
        data_type: str = "any",
        values_type: str = "any",
        strict: bool = False,
        mode: str = "object",
        exclude_empty_values: bool = True,
    ):
        """
        Parameters
        ----------
        data_type: {'any, 'time', 'batch', 'event'}
        values_type: {'any', 'scalar', 'categorical', 'vector'}
        strict: bool
        mode: {'object', 'reference', 'id'}
        exclude_empty_values: bool
        """
        if data_type == "any":
            if values_type == "any":
                output_types = [
                    "DATA",
                    "STORED_CONTINUOUS_DATA",
                    "STORED_BATCH_DATA",
                    "COMPUTED_CONTINUOUS_DATA",
                    "COMPUTED_BATCH_DATA",
                    "BATCH_TIME_DATA",
                    "BATCH_TAG_KEY",
                    "STORED_BATCH_VECTOR_DATA",
                    "STORED_CONTINUOUS_VECTOR_DATA",
                    "STORED_EVENT_DATA",
                    "EVENT_TAG_KEY",
                ]
            elif values_type == "scalar":
                output_types = [
                    "DATA",
                    "STORED_CONTINUOUS_DATA",
                    "STORED_BATCH_DATA",
                    "COMPUTED_CONTINUOUS_DATA",
                    "COMPUTED_BATCH_DATA",
                    "BATCH_TIME_DATA",
                    "STORED_EVENT_DATA",
                ]
            elif values_type == "categorical":
                output_types = [
                    "BATCH_TAG_KEY",
                    "EVENT_TAG_KEY",
                ]
            elif values_type == "vector":
                output_types = [
                    "STORED_CONTINUOUS_VECTOR_DATA",
                    "STORED_BATCH_VECTOR_DATA",
                ]

        elif data_type == "time":
            if values_type == "any":
                output_types = [
                    "STORED_CONTINUOUS_DATA",
                    "COMPUTED_CONTINUOUS_DATA",
                    "STORED_CONTINUOUS_VECTOR_DATA",
                ]
                if strict is False:
                    output_types.append("DATA")
            elif values_type == "scalar":
                output_types = ["STORED_CONTINUOUS_DATA", "COMPUTED_CONTINUOUS_DATA"]
                if strict is False:
                    output_types.append("DATA")
            elif values_type == "vector":
                output_types = ["STORED_CONTINUOUS_VECTOR_DATA"]
                if strict is False:
                    output_types.append("VECTOR_DATA")

        elif data_type == "batch":
            if values_type == "any":
                output_types = [
                    "STORED_BATCH_DATA",
                    "COMPUTED_BATCH_DATA",
                    "BATCH_TIME_DATA",
                    "BATCH_TAG_KEY",
                    "STORED_BATCH_VECTOR_DATA",
                ]
                if strict is False:
                    output_types.append("DATA")
            elif values_type == "scalar":
                output_types = [
                    "STORED_BATCH_DATA",
                    "COMPUTED_BATCH_DATA",
                    "BATCH_TIME_DATA",
                ]
                if strict is False:
                    output_types.append("DATA")
            elif values_type == "categorical":
                output_types = [
                    "BATCH_TAG_KEY",
                ]
            elif values_type == "vector":
                output_types = ["STORED_BATCH_VECTOR_DATA"]
                if strict is False:
                    output_types.append("VECTOR_DATA")

        elif data_type == "event":
            if values_type == "any":
                output_types = ["STORED_EVENT_DATA", "EVENT_TAG_KEY"]
                if strict is False:
                    output_types.append("DATA")
            elif values_type == "scalar":
                output_types = ["STORED_EVENT_DATA"]
                if strict is False:
                    output_types.append("DATA")
            elif values_type == "categorical":
                output_types = ["EVENT_TAG_KEY"]

        else:
            raise ValueError(f"Unknown 'data_type': {data_type}")

        return self.get_output_dict(
            output_types=output_types,
            mode=mode,
            exclude_empty_values=exclude_empty_values,
        )

    @property
    def execution_kwargs(self):
        return {
            "model_instance_id": self.pythonModelInstance.id,
            "test_mode": self.testMode,
            "execution_context": self.executionContext.dict(),
            "current_execution_date": self.currentExecutionInstant,
            "last_execution_date": self.lastSuccessfulExecutionInstant,
            "input_parameters": self.get_input_dict(mode="object"),
            "input_parameter_references": self.get_input_dict(mode="reference"),
            "input_parameter_ids": self.get_input_dict(mode="id"),
            "output_parameters": self.get_output_dict(mode="object"),
            "output_parameter_references": self.get_output_dict(mode="reference"),
            "output_parameter_ids": self.get_output_dict(mode="id"),
            "custom_input_data": self.executionContext.customData,
        }

    def get_execution_argument_value(self, argument_name: str):
        return self.execution_kwargs[argument_name]


# Current event
DEFAULT_EVENT: Optional[ModelExecution] = None


def set_default_model_execution(event: ModelExecution):
    """
    Put an execution event into a global variable, for external use

    Parameters
    ----------
    event: ModelExecution
    """

    global DEFAULT_EVENT
    DEFAULT_EVENT = event


def get_default_model_execution():
    global DEFAULT_EVENT
    return DEFAULT_EVENT


# Current summary
DEFAULT_EXECUTION_REPORT: Optional[ExecutionReport] = None


def set_default_execution_report(execution_report: ExecutionReport):
    """
    Put an execution report into a global variable, for external use

    Parameters
    ----------
    execution_report: ExecutionReport
    """

    global DEFAULT_EXECUTION_REPORT
    DEFAULT_EXECUTION_REPORT = execution_report


def get_default_execution_report():
    """
    Get the current default execution report.
    If none has been set yet, it creates an empty one.

    Returns
    -------
    The current default execution report
    """

    global DEFAULT_EXECUTION_REPORT
    if DEFAULT_EXECUTION_REPORT is None:
        DEFAULT_EXECUTION_REPORT = ExecutionReport(testMode=True)
    return DEFAULT_EXECUTION_REPORT
