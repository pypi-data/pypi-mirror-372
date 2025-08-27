from functools import lru_cache

from locarc.events import EventProviderProtocol
from locarc.models import EventProviders


def create_inmemory_provider() -> EventProviderProtocol:
    from locarc.providers.inmemory import InMemoryEventProvider

    return InMemoryEventProvider()


def create_pubsub_provider() -> EventProviderProtocol:
    from google.auth.credentials import AnonymousCredentials
    from locarc.providers.pubsub import PubsubCredentials
    from locarc.providers.pubsub import PubsubEventProvider
    from locarc.providers.pubsub import PubsubSettings

    settings = PubsubSettings()
    credentials: AnonymousCredentials | None
    match settings.credentials:
        case PubsubCredentials.ANONYMOUS:
            credentials = AnonymousCredentials()
        case _:
            credentials = None
    return PubsubEventProvider.create(
        settings.project_id,
        credentials=credentials,
    )


@lru_cache
def get_event_provider(
    event_provider_name: EventProviders,
) -> EventProviderProtocol:
    match event_provider_name:
        case EventProviders.IN_MEMORY:
            return create_inmemory_provider()
        case EventProviders.PUBSUB:
            return create_pubsub_provider()
        # NOTE: add additional event provider here.
        case _:
            raise ValueError(f"Unsupported provider `{event_provider_name}`")
