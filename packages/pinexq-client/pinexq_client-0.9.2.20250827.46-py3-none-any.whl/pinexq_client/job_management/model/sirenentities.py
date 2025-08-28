from pydantic import BaseModel, ConfigDict, Field

from pinexq_client.core import Entity
from pinexq_client.job_management.model.open_api_generated import (
    InfoHtoOpenApiProperties,
    EntryPointHtoOpenApiProperties,
    JobsRootHtoOpenApiProperties,
    JobQueryResultHtoOpenApiProperties,
    JobHtoOpenApiProperties,
    WorkDataHtoOpenApiProperties,
    ProcessingStepHtoOpenApiProperties,
    WorkDataQueryResultHtoOpenApiProperties,
    WorkDataRootHtoOpenApiProperties,
    ProcessingStepRootHtoOpenApiProperties,
    ProcessingStepQueryResultHtoOpenApiProperties,
    JobUsedTagsHtoOpenApiProperties,
    ProcessingStepUsedTagsHtoOpenApiProperties,
    UserHtoOpenApiProperties,
    WorkDataUsedTagsQueryResultHtoOpenApiProperties,
)


# ToDo: make these Generics bound to Entity


class EntryPointEntity(Entity):
    properties: EntryPointHtoOpenApiProperties | None = None


class InfoEntity(Entity):
    properties: InfoHtoOpenApiProperties | None = None


class JobsRootEntity(Entity):
    properties: JobsRootHtoOpenApiProperties | None = None


class JobQueryResultEntity(Entity):
    properties: JobQueryResultHtoOpenApiProperties | None = None


class JobEntity(Entity):
    properties: JobHtoOpenApiProperties | None = None


class WorkDataEntity(Entity):
    properties: WorkDataHtoOpenApiProperties | None = None


class WorkDataRootEntity(Entity):
    properties: WorkDataRootHtoOpenApiProperties | None = None


class WorkDataQueryResultEntity(Entity):
    properties: WorkDataQueryResultHtoOpenApiProperties | None = None


class ProcessingStepEntity(Entity):
    properties: ProcessingStepHtoOpenApiProperties | None = None


class ProcessingStepsRootEntity(Entity):
    properties: ProcessingStepRootHtoOpenApiProperties | None = None


class ProcessingStepQueryResultEntity(Entity):
    properties: ProcessingStepQueryResultHtoOpenApiProperties | None = None


class WorkDataUsedTagsQueryResultEntity(Entity):
    properties: WorkDataUsedTagsQueryResultHtoOpenApiProperties | None = None


class ProcessingStepUsedTagsEntity(Entity):
    properties: ProcessingStepUsedTagsHtoOpenApiProperties | None = None


class JobUsedTagsEntity(Entity):
    properties: JobUsedTagsHtoOpenApiProperties | None = None


# this needs to be added since the openapi.spec does not have this object.
class InputDataSlotHtoProperties(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    is_configured: bool | None = Field(None, alias="IsConfigured")
    name: str = Field("", alias="Name")
    title: str | None = Field(None, alias="Title")
    description: str | None = Field(None, alias="Description")
    media_type: str | None = Field(None, alias="MediaType")


class InputDataSlotEntity(Entity):
    properties: InputDataSlotHtoProperties | None = None


# this needs to be added since the openapi.spec does not have this object.
class OutputDataSlotHtoProperties(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    name: str = Field("", alias="Name")
    title: str | None = Field(None, alias="Title")
    description: str | None = Field(None, alias="Description")
    media_type: str | None = Field(None, alias="MediaType")


class OutputDataSlotEntity(Entity):
    properties: OutputDataSlotHtoProperties | None = None


class UserEntity(Entity):
    properties: UserHtoOpenApiProperties | None = None
