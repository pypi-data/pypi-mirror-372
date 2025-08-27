from os import environ
from pathlib import Path
from typing import Any
from typing import Generator

from pydantic_core import to_json
from pytest import fixture
from pytest_mock import MockerFixture

from locarc.events import EventProtocol
from locarc.models import Arc
from locarc.models import EventProviders
from locarc.models import Service
from locarc.models import Subscription
from locarc.models import SubscriptionDestinations
from locarc.models import Topic
from locarc.providers.inmemory import InMemoryEventProvider

environ.update(GOOGLE_PROJECT_ID="test-project")
environ.update(GOOGLE_PUBSUB_CREDENTIALS="anonymous")
environ.update(PUBSUB_EMULATOR_HOST="pubsub:19341")


class TestEvent(EventProtocol):
    def ack(self) -> None:
        pass

    def bytes(self) -> bytes:
        return to_json(self.json())

    def json(self) -> Any:
        return dict(foo="bar")


@fixture
def examples() -> Path:
    return Path(__file__).parent.parent / "examples"


@fixture
def test_event() -> EventProtocol:
    return TestEvent()


@fixture
def test_event_provider() -> Generator[InMemoryEventProvider, None, None]:
    provider = InMemoryEventProvider()
    yield provider
    provider.close()


@fixture
def in_memory_provider(
    mocker: MockerFixture,
    test_event_provider: InMemoryEventProvider,
) -> InMemoryEventProvider:
    mock = mocker.patch("locarc.main.get_event_provider")
    mock.return_value = test_event_provider
    return test_event_provider


@fixture
def test_topic() -> Topic:
    return Topic(
        id="test_topic",
        provider=EventProviders.IN_MEMORY,
    )


@fixture
def test_service_url() -> str:
    return "http://test.svc/"


@fixture
def test_service(
    test_service_url: str,
) -> Service:
    return Service(
        id="test_service",
        url=test_service_url[:-1],
    )


@fixture
def test_subscription(
    test_service: Service,
    test_topic: Topic,
) -> Subscription:
    return Subscription(
        id="test_subscription",
        destinations=SubscriptionDestinations(services=[test_service.id]),
        provider=EventProviders.IN_MEMORY,
        topic=test_topic.id,
    )


@fixture
def test_arc(
    test_service: Service, test_subscription: Subscription, test_topic: Topic
) -> Arc:
    return Arc(
        services=[test_service],
        subscriptions=[test_subscription],
        topics=[test_topic],
    )
