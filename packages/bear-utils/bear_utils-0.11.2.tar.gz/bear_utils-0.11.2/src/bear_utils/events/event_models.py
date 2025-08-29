"""Event system models using Pydantic for type safety and validation."""

from enum import IntEnum
from typing import Self
from uuid import UUID, uuid4

from bear_epoch_time import EpochTimestamp
from pydantic import BaseModel, Field, field_serializer


class EventPriority(IntEnum):
    """Event priority levels for handler execution order."""

    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


class BaseEvent(BaseModel):
    """Base class for all events in the system."""

    name: str = Field(default=...)
    msg: str | None = Field(default=None)
    timestamp: EpochTimestamp = Field(default_factory=EpochTimestamp.now)
    success: bool = Field(default=True)

    model_config = {"arbitrary_types_allowed": True}

    def ts_to_string(self, fmt: str) -> str:
        """Return the timestamp as a human-readable string."""
        return self.timestamp.to_string(fmt=fmt)

    def _base_done(self, msg: str = "") -> Self:
        """Update the event's timestamp to the current time."""
        self.msg = msg
        self.timestamp = EpochTimestamp.now()
        return self

    def fail(self, exception: Exception) -> None:
        """Mark the event as failed with an exception message."""
        self.success = False
        self.msg = str(exception)

    @field_serializer("timestamp", mode="plain")
    def serialize_timestamp(self, ts: EpochTimestamp) -> str:
        """Serialize the timestamp field to ISO format."""
        return ts.to_string()


class Event[T_Input, T_Results](BaseEvent):
    """Generic event with typed data payload."""

    event_id: UUID = Field(default_factory=uuid4)
    input_data: T_Input | None = Field(default=None)
    results: T_Results | None = Field(default=None)

    def _insert_results(self, result: T_Results) -> None:
        """Insert results into the event."""
        self.results = result

    def done(self, result: T_Results, msg: str = "") -> Self:
        """Tasks to complete when event processing is done.

        Args:
            msg (str): Message indicating the status of event processing.
            **kwargs: Additional keyword arguments to be passed to insert_results.
                result (T_Results): The results to insert into the event.
        """
        super()._base_done(msg=msg)
        self._insert_results(result)
        return self


class HandlerNotFoundError(Exception):
    """Exception raised when an event handler is not found."""

    def __init__(self, event_name: str) -> None:
        """A handler was not found for the given event name."""
        super().__init__(f"No handler found for event: {event_name}")
