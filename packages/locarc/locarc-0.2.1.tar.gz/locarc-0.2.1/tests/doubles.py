from typing import Any

from pydantic_core import to_json

from locarc.events import EventProtocol


class TestEvent(EventProtocol):
    def ack(self) -> None:
        pass

    def bytes(self) -> bytes:
        return to_json(self.json())

    def json(self) -> Any:
        return dict(foo="bar")
