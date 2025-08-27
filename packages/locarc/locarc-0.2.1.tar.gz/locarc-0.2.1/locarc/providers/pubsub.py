from enum import StrEnum
from os import environ
from typing import Any
from typing import Self

from pydantic import Field
from pydantic_core import from_json
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from locarc.errors import ARC_INSTALL_ERROR
from locarc.logger import LOGGER

try:
    from google.cloud.pubsub import PublisherClient
    from google.cloud.pubsub import SubscriberClient
    from google.cloud.pubsub_v1.subscriber.message import Message
except ImportError:
    LOGGER.error(
        "Missing google extra, please reinstall using `locarc[google]` dependency."
    )
    raise ARC_INSTALL_ERROR

from locarc.events import EventCallback
from locarc.events import EventProviderProtocol
from locarc.events import EventProtocol
from locarc.models import Subscription
from locarc.models import Topic
from locarc.types import AnyFuture
from locarc.utils import on_exit_signal


def _verify_pubsub_emulator_settings() -> None:
    if environ.get("PUBSUB_EMULATOR_HOST") is None:
        LOGGER.warning("`PUBSUB_EMULATOR_HOST` is not set")


class PubsubCredentials(StrEnum):
    ANONYMOUS = "anonymous"
    INFERED = "infered"


class PubsubSettings(BaseSettings):
    model_config = SettingsConfigDict()

    project_id: str = Field(validation_alias="GOOGLE_PROJECT_ID")
    credentials: PubsubCredentials = Field(validation_alias="GOOGLE_PUBSUB_CREDENTIALS")


class PubsubEvent(EventProtocol):
    def __init__(self, message: Message) -> None:
        self._message = message

    def ack(self) -> None:
        self._message.ack()

    def bytes(self) -> bytes:
        return self._message.data  # type: ignore[no-any-return]

    def json(self) -> Any:
        return from_json(self._message.data)


class PubsubEventProvider(EventProviderProtocol):
    def __init__(
        self,
        project_id: str,
        publisher: PublisherClient,
        subscriber: SubscriberClient,
    ) -> None:
        self._project_id = project_id
        self._publisher = publisher
        self._subscriber = subscriber

    @classmethod
    def create(
        cls,
        project_id: str,
        *,
        # TODO: infer from environ ? (e.g GOOGLE_APPLICATION_CREDENTIALS)
        credentials: Any | None = None,
    ) -> Self:
        _verify_pubsub_emulator_settings()
        publisher = PublisherClient(credentials=credentials)
        subscriber = SubscriberClient(credentials=credentials)
        return cls(project_id, publisher, subscriber)

    def create_subscription(
        self,
        subscription: Subscription,
    ) -> None:
        self._subscriber.create_subscription(
            request=dict(
                name=self._subscriber.subscription_path(
                    self._project_id,
                    subscription.id,
                ),
                topic=self._publisher.topic_path(
                    self._project_id,
                    subscription.topic,
                ),
            ),
        )

    def create_topic(
        self,
        topic: Topic,
    ) -> None:
        self._publisher.create_topic(
            request=dict(
                name=self._publisher.topic_path(
                    self._project_id,
                    topic.id,
                ),
            ),
        )

    def publish_event(
        self,
        topic: Topic,
        event: EventProtocol,
    ) -> None:
        self._publisher.publish(
            self._publisher.topic_path(
                self._project_id,
                topic.id,
            ),
            event.bytes(),
        )

    def listen_subscription(
        self,
        subscription: Subscription,
        callbacks: list[EventCallback],
    ) -> list[AnyFuture]:
        futures: list[AnyFuture] = []
        for callback in callbacks:
            future = self._subscriber.subscribe(
                self._subscriber.subscription_path(
                    self._project_id,
                    subscription.id,
                ),
                callback=callback,
            )
            on_exit_signal(future.cancel)
            futures.append(future)
        return futures
