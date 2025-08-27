from concurrent.futures import CancelledError
from pathlib import Path
from typing_extensions import Annotated

from pydantic import ValidationError
from typer import run
from yaml import YAMLError  # type: ignore[import-untyped]
from yaml import load as load_yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from locarc.callbacks import ServiceCallback
from locarc.callbacks import TopicCallback
from locarc.constants import DEFAULT_ARC_FILE
from locarc.constants import OPTION_ARC_FILE
from locarc.constants import OPTION_DEFAULT_TIMEOUT
from locarc.events import EventCallback
from locarc.errors import ARC_ERROR
from locarc.errors import ARC_INVALID_YAML_ERROR
from locarc.errors import ARC_VALIDATION_ERROR
from locarc.logger import LOGGER
from locarc.models import Arc
from locarc.models import Subscription
from locarc.providers import get_event_provider
from locarc.types import AnyFuture


def safe_load_arc_file(
    arcfile: Path,
) -> Arc:
    with arcfile.open() as stream:
        try:
            return Arc(**load_yaml(stream, Loader=Loader))
        except ValidationError as e:
            LOGGER.error("Invalid YAML file:")
            for error in e.errors():
                message = error.get("msg")
                LOGGER.error(f"- ValidationError: {message}")
            raise ARC_VALIDATION_ERROR
        except YAMLError as e:
            LOGGER.error(f"Invalid YAML file, {e}, abort")
            raise ARC_INVALID_YAML_ERROR
        except Exception as e:
            LOGGER.error(f"Unexpected error occurs: {e}, abort")
            raise ARC_ERROR


def parse_event_subscription_callback(
    arc: Arc,
    subscription: Subscription,
) -> list[EventCallback]:
    callbacks: list[EventCallback] = []
    if subscription.destinations.services is not None:
        for service_id in subscription.destinations.services:
            callbacks.append(ServiceCallback(arc.get_service_by_id(service_id)))
    if subscription.destinations.topics is not None:
        for topic_id in subscription.destinations.topics:
            callbacks.append(TopicCallback(arc.get_topic_by_id(topic_id)))
    return callbacks


def create_arc_topics(arc: Arc) -> None:
    if arc.topics is not None:
        for topic in arc.topics:
            provider = get_event_provider(topic.provider)
            provider.create_topic(topic)


def create_arc_subscription(arc: Arc) -> dict[Subscription, list[AnyFuture]]:
    if arc.subscriptions is None:
        LOGGER.warning("No subscription defined in the arcfile, abort.")
        raise ARC_VALIDATION_ERROR
    futures: dict[Subscription, list[AnyFuture]] = {}
    for subscription in arc.subscriptions:
        try:
            arc.get_topic_by_id(
                subscription.topic
            )  # NOTE: ensure source topic is declared.
            callbacks = parse_event_subscription_callback(arc, subscription)
            provider = get_event_provider(subscription.provider)
            provider.create_subscription(subscription)
            futures[subscription] = provider.listen_subscription(
                subscription,
                callbacks,
            )
        except KeyError as e:
            LOGGER.error(e)
            raise ARC_VALIDATION_ERROR
    return futures


def wait_for_the_future_to_be_better(
    futures: dict[Subscription, list[AnyFuture]],
    default_timeout: float | None,
) -> None:
    for subscription, subscription_futures in futures.items():
        for callback_future in subscription_futures:
            timeout = subscription.timeout
            if timeout is None:
                timeout = default_timeout
            try:
                subscription_error = callback_future.exception(timeout=timeout)
                if subscription_error is not None:
                    LOGGER.error(
                        f"An error occurs while managing subscription {subscription.id}: {subscription_error}"
                    )
            except CancelledError:
                LOGGER.error(f"Subscription {subscription.id} was cancelled")
            except TimeoutError:
                LOGGER.error(f"Timeout reached for subscription {subscription.id}")


def entrypoint(
    *,
    arcfile: Annotated[Path, OPTION_ARC_FILE] = DEFAULT_ARC_FILE,
    default_timeout: Annotated[float | None, OPTION_DEFAULT_TIMEOUT] = None,
) -> None:
    arc = safe_load_arc_file(arcfile)
    create_arc_topics(arc)
    futures = create_arc_subscription(arc)
    wait_for_the_future_to_be_better(futures, default_timeout)


def main() -> None:
    run(entrypoint)


if __name__ == "__main__":
    main()
