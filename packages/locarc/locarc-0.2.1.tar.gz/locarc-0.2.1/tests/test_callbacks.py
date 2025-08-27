from pytest_httpx import HTTPXMock

from locarc.callbacks import ServiceCallback
from locarc.callbacks import TopicCallback
from locarc.events import EventProtocol
from locarc.models import Service
from locarc.models import Subscription
from locarc.models import Topic
from locarc.providers.inmemory import InMemoryEventProvider


def test_service_callback(
    httpx_mock: HTTPXMock,
    test_event: EventProtocol,
    test_service: Service,
    test_service_url: str,
) -> None:
    httpx_mock.add_response(
        method=test_service.method,
        url=test_service_url,
    )
    callback = ServiceCallback(test_service)
    callback(test_event)
    request = httpx_mock.get_request(
        method=test_service.method,
        url=test_service_url,
    )
    assert request is not None


def test_topic_callback(
    test_event: EventProtocol,
    test_event_provider: InMemoryEventProvider,
    test_topic: Topic,
    test_subscription: Subscription,
) -> None:
    test_event_provider.create_topic(test_topic)
    test_event_provider.create_subscription(test_subscription)
    callback = TopicCallback(test_topic, provider=test_event_provider)
    callback(test_event)
    assert test_subscription in test_event_provider._events
    assert test_event in test_event_provider._events[test_subscription]
    assert len(test_event_provider._events[test_subscription]) == 1
