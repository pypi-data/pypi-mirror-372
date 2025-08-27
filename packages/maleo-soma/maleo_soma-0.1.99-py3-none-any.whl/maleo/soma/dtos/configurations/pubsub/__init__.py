from pydantic import BaseModel, Field
from typing import Generic, Optional
from .publisher import TopicsConfigurationT, PublisherConfigurationDTO
from .subscription import SubscriptionsConfigurationT


class PubSubConfigurationDTO(
    BaseModel, Generic[TopicsConfigurationT, SubscriptionsConfigurationT]
):
    publisher: PublisherConfigurationDTO[TopicsConfigurationT] = Field(
        ...,
        description="Publisher's configurations",
    )
    subscriptions: Optional[SubscriptionsConfigurationT] = Field(
        None, description="Subscriptions's configurations"
    )
