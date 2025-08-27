from enum import StrEnum

from pydantic import HttpUrl

from locarc.types import FrozenBaseModel


class EventProviders(StrEnum):
    IN_MEMORY = "in_memory"
    PUBSUB = "pubsub"


class Topic(FrozenBaseModel):
    id: str
    provider: EventProviders


class ServiceMethod(StrEnum):
    POST = "POST"


class Service(FrozenBaseModel):
    id: str
    url: HttpUrl

    method: ServiceMethod = ServiceMethod.POST
    path: str = "/"


class SubscriptionDestinations(FrozenBaseModel):
    services: frozenset[str] | None = None
    topics: frozenset[str] | None = None


class Subscription(FrozenBaseModel):
    id: str
    destinations: SubscriptionDestinations
    provider: EventProviders
    timeout: float | None = None
    topic: str


class Arc(FrozenBaseModel):
    services: frozenset[Service] | None = None
    subscriptions: frozenset[Subscription] | None = None
    topics: frozenset[Topic]

    def get_service_by_id(self, service_id: str) -> Service:
        if self.services is None:
            raise KeyError("No service are declared in arc file.")
        for service in self.services:
            if service.id == service_id:
                return service
        raise KeyError(f"Service `{service_id} is not declared in arc file.")

    def get_topic_by_id(self, topic_id: str) -> Topic:
        if self.topics is None:
            raise KeyError("No topic are declared in arc file.")
        for topic in self.topics:
            if topic.id == topic_id:
                return topic
        raise KeyError(f"Topic `{topic_id} is not declared in arc file.")
