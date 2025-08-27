from typing import Any
from typing import Callable
from typing import Protocol

from locarc.models import Subscription
from locarc.models import Topic
from locarc.types import AnyFuture


class EventProtocol(Protocol):
    def ack(self) -> None:
        pass

    def bytes(self) -> bytes:
        pass

    def json(self) -> Any:
        pass


EventCallback = Callable[[EventProtocol], None]


class EventProviderProtocol(Protocol):
    def create_subscription(
        self,
        subscription: Subscription,
    ) -> None:
        pass

    def create_topic(
        self,
        topic: Topic,
    ) -> None:
        pass

    def publish_event(
        self,
        topic: Topic,
        event: EventProtocol,
    ) -> None:
        pass

    def listen_subscription(
        self,
        subscription: Subscription,
        callbacks: list[EventCallback],
    ) -> list[AnyFuture]:
        pass
