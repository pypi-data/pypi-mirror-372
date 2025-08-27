from concurrent.futures import Future
from types import FrameType
from typing import Any
from typing import Callable

from pydantic import BaseModel
from pydantic import ConfigDict

AnyCallable = Callable[..., Any]
AnyFuture = Future[Any]
SignalHandler = Callable[[int, FrameType | None], None]


class FrozenBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)
