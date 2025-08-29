"""Synchronous event bus implementation."""

from contextlib import suppress
from typing import Any, overload

from bear_utils.events._base_event_bus import BaseEventBus
from bear_utils.events._handler_storage import Handler, SyncStorage
from bear_utils.events._inputs import ExampleInput
from bear_utils.events._results import ExampleResult
from bear_utils.events.event_models import BaseEvent, Event, HandlerNotFoundError


class EventBus(BaseEventBus[Handler]):
    """Synchronous event bus for registering and emitting sync handlers only."""

    def _create_storage(self) -> SyncStorage:
        """Create sync storage for handlers."""
        return SyncStorage()

    def register(self, event_name: str, handler: Handler) -> None:
        """Register a sync handler for a given event name.

        Args:
            event_name(str): The name of the event that will be used to call it in emit or fire.
            handler(Handler): The method or function itself to be called later.
        """
        self._handlers[event_name] = self._create_weak_ref(event_name, handler)

    @overload
    def emit(self, event_name: str, event_model: None, **kwargs) -> Event: ...

    @overload
    def emit[T: BaseEvent](self, event_name: str, event_model: T, **kwargs) -> T: ...

    def emit[T: BaseEvent](self, event_name: str, event_model: T | None = None, **kwargs) -> T | Event:
        """Emit an event to registered sync handler and return modified event.

        This is for times when you would expect results from your handlers. If no handler is found,
        the event will have its `msg` attribute set to "No handler registered for event."

        Args:
            event_name(str): The name of the event to emit
            event_model(T) (Optional): The event instance to use. If None, creates its own Event.
            **kwargs: Keyword arguments to pass to Event object if event is None
        Returns:
            T | Event: The processed event, with type matching event_model if provided.
        """
        handler: Handler | None = self._get_handler(event_name)
        # callback: Any = kwargs.pop("callback") # TODO: Do we want to support callbacks here?
        event: T | Event = event_model if event_model is not None else Event(name=event_name, **kwargs)
        if handler is None:
            event.fail(HandlerNotFoundError(event_name))
            return event

        with suppress(Exception):
            event = handler(event)  # Handler will be responsible for calling done() or fail() and error handling
        return event

    def fire(self, event_name: str, **kwargs) -> None:
        """Fire and forget - call handler without expecting return value.

        If handler isn't found, then nothing happens.

        Args:
            event_name(str): The name of the event to fire.
            **kwargs: Arbitrary keyword arguments to pass to the handler.
        """
        handler: Handler | None = self._get_handler(event_name)
        if handler is None:
            return
        with suppress(Exception):
            callback: Any = kwargs.pop("callback", None)
            result: Any = handler(**kwargs)
            if callback is not None and callable(callback):
                callback(result)


if __name__ == "__main__":
    # Lets think through how this might work
    from bear_utils.events._inputs import ExampleInput
    from bear_utils.events._results import ExampleResult

    bus = EventBus()

    class Input(ExampleInput):
        value: int

    class Output(ExampleResult):
        processed_value: int = 0

    class MultEvent(Event[Input, Output]): ...

    def multiply_by_two(event: MultEvent) -> MultEvent:
        """Example"""
        result = Output()
        try:
            if event.input_data is not None:
                result = Output(processed_value=event.input_data.value * 2)
                return event.done(msg="Multiplied value by two", result=result)
        except Exception as e:
            result.fail(e)
            return event.done(msg="Failed to multiply value", result=result)
        return event.done(msg="No input data provided", result=result)

    bus.register("test_event", multiply_by_two)
    event = MultEvent(name="test_event", input_data=Input(value=21))
    returned_value: MultEvent = bus.emit(event_name="test_event", event_model=event)  # return type shows correctly!
    print(returned_value.model_dump(exclude_none=True))

    def player_damage(damage: int) -> str:
        print(f"Player takes {damage} damage!")
        return f"Dealt {damage} damage"

    def got_hit(callback_res: Any) -> None:
        print(f"Callback received with result: {callback_res}")

    bus.register("player_hit", player_damage)

    bus.fire("player_hit", damage=15)

    bus.fire("player_hit", damage=25, callback=got_hit)
