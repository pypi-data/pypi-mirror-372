from pydantic import BaseModel, Field
from typing import Generic, TypeVar


class TopicConfigurationDTO(BaseModel):
    id: str = Field(..., description="Topic's id")


DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATION = TopicConfigurationDTO(
    id="database-operation"
)
DEFAULT_REQUEST_OPERATION_TOPIC_CONFIGURATION = TopicConfigurationDTO(
    id="request-operation"
)
DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIGURATION = TopicConfigurationDTO(
    id="resource-operation"
)
DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIGURATION = TopicConfigurationDTO(
    id="system-operation"
)
DEFAULT_OPERATION_TOPIC_CONFIGURATION = TopicConfigurationDTO(id="operation")
DEFAULT_RESOURCE_USAGE_TOPIC_CONFIGURATION = TopicConfigurationDTO(id="resource-usage")


class TopicsConfigurationDTO(BaseModel):
    database_operation: TopicConfigurationDTO = Field(
        default=DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATION,
        description="Database operation topic configurations",
    )
    request_operation: TopicConfigurationDTO = Field(
        default=DEFAULT_REQUEST_OPERATION_TOPIC_CONFIGURATION,
        description="Request operation topic configurations",
    )
    resource_operation: TopicConfigurationDTO = Field(
        default=DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIGURATION,
        description="Resource operation topic configurations",
    )
    system_operation: TopicConfigurationDTO = Field(
        default=DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIGURATION,
        description="System operation topic configurations",
    )
    operation: TopicConfigurationDTO = Field(
        default=DEFAULT_OPERATION_TOPIC_CONFIGURATION,
        description="Operation topic configurations",
    )
    resource_usage: TopicConfigurationDTO = Field(
        default=DEFAULT_RESOURCE_USAGE_TOPIC_CONFIGURATION,
        description="Resource usage topic configurations",
    )


TopicsConfigurationT = TypeVar("TopicsConfigurationT", bound=TopicsConfigurationDTO)


class PublisherConfigurationDTO(BaseModel, Generic[TopicsConfigurationT]):
    topics: TopicsConfigurationT = Field(..., description="Topics configurations")
