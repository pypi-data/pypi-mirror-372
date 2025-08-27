from concurrent.futures import ThreadPoolExecutor

from locarc.events import EventCallback
from locarc.events import EventProtocol
from locarc.events import EventProviderProtocol
from locarc.models import Subscription
from locarc.models import Topic
from locarc.types import AnyFuture


class InMemoryEventProvider(EventProviderProtocol):
    def __init__(self) -> None:
        self._closed = False
        self._events: dict[Subscription, list[EventProtocol]] = {}
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._subscriptions: list[Subscription] = []
        self._topics: list[Topic] = []

    def close(self) -> None:
        self._closed = True
        self._executor.shutdown(wait=False)

    def create_subscription(
        self,
        subscription: Subscription,
    ) -> None:
        self._events[subscription] = []
        self._subscriptions.append(subscription)

    def create_topic(
        self,
        topic: Topic,
    ) -> None:
        self._topics.append(topic)

    def publish_event(
        self,
        topic: Topic,
        event: EventProtocol,
    ) -> None:
        if topic not in self._topics:
            raise ValueError(f"Unknown topic `{topic.id}`")
        for subscription in self._subscriptions:
            if subscription.topic == topic.id:
                self._events[subscription].append(event)

    def listen_subscription(
        self,
        subscription: Subscription,
        callbacks: list[EventCallback],
    ) -> list[AnyFuture]:
        futures: list[AnyFuture] = []
        for callback in callbacks:

            def _subscription_task() -> None:
                while not self._closed:
                    for event in self._events[subscription]:
                        callback(event)

            futures.append(self._executor.submit(_subscription_task))
        return futures
