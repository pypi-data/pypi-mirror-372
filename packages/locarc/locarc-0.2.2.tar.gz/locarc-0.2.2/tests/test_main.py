from pathlib import Path

from locarc.providers.inmemory import InMemoryEventProvider
from locarc.models import Arc
from locarc.models import Subscription
from locarc.models import Topic
from locarc.main import create_arc_topics
from locarc.main import create_arc_subscription
from locarc.main import parse_event_subscription_callback
from locarc.main import safe_load_arc_file
from locarc.main import wait_for_the_future_to_be_better


def test_create_arc_topics(
    in_memory_provider: InMemoryEventProvider,
    test_arc: Arc,
    test_topic: Topic,
) -> None:
    create_arc_topics(test_arc)
    assert len(in_memory_provider._topics) == 1
    assert test_topic in in_memory_provider._topics


def test_create_arc_subscription(
    in_memory_provider: InMemoryEventProvider,
    test_arc: Arc,
    test_subscription: Subscription,
) -> None:
    futures = create_arc_subscription(test_arc)
    assert test_subscription in in_memory_provider._subscriptions
    assert len(futures) == 1
    assert test_subscription in futures
    assert len(futures[test_subscription]) == 1


def test_parse_event_subscription_callback(
    test_arc: Arc,
    test_subscription: Subscription,
) -> None:
    callbacks = parse_event_subscription_callback(test_arc, test_subscription)
    assert len(callbacks) == 1


def test_safe_load_arc_file(
    examples: Path,
) -> None:
    topic_to_service = examples / "topic_to_service.yaml"
    arc = safe_load_arc_file(topic_to_service)
    assert arc.services is not None
    assert arc.subscriptions is not None
    assert arc.topics is not None
    assert len(arc.services) == 1
    assert len(arc.subscriptions) == 1
    assert len(arc.topics) == 1
    # TODO: assert contant.


def test_wait_for_the_future_to_be_better() -> None:
    wait_for_the_future_to_be_better(dict(), default_timeout=None)
