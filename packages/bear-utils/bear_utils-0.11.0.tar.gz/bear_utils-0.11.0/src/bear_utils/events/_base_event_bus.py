"""Base event bus abstract class for shared functionality."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import MethodType
from typing import Any
from weakref import WeakMethod, ref

from bear_utils.events._handler_storage import AsyncReference, ReferenceType, SyncReference
from bear_utils.events.event_models import BaseEvent


class BaseEventBus[T_Handler: Callable[..., Any]](ABC):
    """Abstract base class for event buses with shared functionality."""

    ### NOT ABSTRACT METHODS ###

    def __init__(self) -> None:
        """Initialize empty event bus."""
        self._handlers: dict[str, ReferenceType] = {}

    def unregister(self, event_name: str) -> bool:
        """Unregister an event. Returns True if found and removed.

        Args:
            event_name(str): The name of the event to remove from the handlers data structure.

        Returns:
            bool: Returns True if found and removed without error, else False.
        """
        if event_name not in self._handlers:
            return False
        try:
            del self._handlers[event_name]
        except Exception:
            return False
        return True

    def _get_handler(self, event_name: str) -> T_Handler | None:
        """Get handler for an event from the referencee.

        Args:
            event_name(str): The name of the event whose handler is getting pulled from the reference.
        """
        if event_name in self._handlers:
            return self._handlers[event_name]()
        return None

    def _make_cleanup_callback(self, event_name: str) -> Callable[..., None]:
        """Create callback for weak references culling."""

        def cleanup(weak_ref: Any) -> None:
            if event_name in self._handlers and self._handlers[event_name] is weak_ref:
                del self._handlers[event_name]

        return cleanup

    def _create_weak_ref(self, event_name: str, handler: T_Handler) -> AsyncReference | SyncReference:
        """Create appropriate weak reference for a handler."""
        if isinstance(handler, MethodType):
            return WeakMethod(handler, self._make_cleanup_callback(event_name))
        return ref(handler, self._make_cleanup_callback(event_name))

    def clear(self) -> None:
        """Clear all events."""
        self._handlers.clear()

    ### ABSTRACT METHODS ###

    @abstractmethod
    def register(self, event_name: str, handler: T_Handler) -> None:
        """Register a handler for a given event name.

        Args:
            event_name(str): The name of the event that will be used to call it in emit or fire.
            handler(T_Handler): The method or function itself to be called later.
        """

    @abstractmethod
    def emit[T_Event: BaseEvent](
        self,
        event_name: str,
        event_model: T_Event | None = None,
        **kwargs,
    ) -> T_Event | Any:
        """Emit an event by name with optional event instance or arbitrary arguments.

        This is for times when you would expect results from your handlers.

        Args:
            event_name(str): The name of the event to emit
            event_model(T_Event) (Optional): The event instance to use. If None, creates SimpleEvent.
            **kwargs: Keyword arguments to create SimpleEvent if event is None

        Returns:
            T_Event: The processed event
        """

    @abstractmethod
    def fire(self, event_name: str, **kwargs) -> Any:
        """Fire an event by name with optional event instance or arbitrary arguments.

        You would usually not expect any return values from this method.

        Args:
            event_name(str): The name of the event to fire
            event(T_Event) (Optional): The event instance to use. If None, creates SimpleEvent.
            **kwargs: Keyword arguments to create SimpleEvent if event is None

        Note:
            Use either event parameter OR kwargs, not both.
        """
