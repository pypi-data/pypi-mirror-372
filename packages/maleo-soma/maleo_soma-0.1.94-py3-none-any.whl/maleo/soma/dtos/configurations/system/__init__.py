from pydantic import BaseModel, Field
from .resource import ResourceConfigurationDTO


class SystemConfigurationDTO(BaseModel):
    resource: ResourceConfigurationDTO = Field(
        ..., description="Resource configuration"
    )
