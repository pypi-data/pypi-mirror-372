"""Asynchronous event bus implementation."""

from contextlib import suppress
from typing import Any, overload

from bear_utils.events._base_event_bus import BaseEventBus
from bear_utils.events._handler_storage import AsyncHandler
from bear_utils.events.event_models import BaseEvent, Event, HandlerNotFoundError
from bear_utils.extras._async_helpers import is_async_function


class AsyncEventBus(BaseEventBus[AsyncHandler]):
    """Asynchronous event bus for registering and emitting async handlers only."""

    def register(self, event_name: str, handler: AsyncHandler) -> None:
        """Register an async handler for a given event name.

        Args:
            event_name(str): The name of the event that will be used to call it in emit or fire.
            handler(AsyncHandler): The async method or async function itself to be called later.
        """
        self._handlers[event_name] = self._create_weak_ref(event_name, handler)

    @overload
    async def emit(self, event_name: str, event_model: None, **kwargs) -> Event: ...

    @overload
    async def emit[T: BaseEvent](self, event_name: str, event_model: T, **kwargs) -> T: ...

    async def emit[T: BaseEvent](self, event_name: str, event_model: T | None = None, **kwargs) -> T | Event:
        """Emit an event to all registered async handler and return modified event.

        This is for times when you would expect results from your handlers. If no handler is found,
        the event will have its `msg` attribute set to "No handler registered for event."

        Args:
            event_name(str): The name of the event to emit
            event_model(T) (Optional): The event instance to use. If None, creates its own Event.
            **kwargs: Keyword arguments to pass to Event object if event is None
        Returns:
            T | Event: The processed event, with type matching event_model if provided.
        """
        handler: AsyncHandler | None = self._get_handler(event_name)
        event: T | Event = event_model if event_model is not None else Event(name=event_name, **kwargs)
        if handler is None:
            event.fail(HandlerNotFoundError(event_name))
            return event

        with suppress(Exception):
            # Handler will be responsible for calling done() or fail() and error handling
            event = await handler(event)
        return event

    async def fire(self, event_name: str, **kwargs) -> None:
        """Fire and forget - create simple event and emit without returning."""
        handler: AsyncHandler | None = self._get_handler(event_name)
        if handler is None:
            return
        callback: Any = kwargs.pop("callback", None)
        result = ""

        with suppress(Exception):
            result: Any = await handler(**kwargs)

        if callback is not None:
            if is_async_function(callback):
                await callback(result)
            elif callable(callback):
                callback(result)
