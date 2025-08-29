from collections.abc import Awaitable, Callable
from typing import Any
from weakref import WeakMethod, ref

Handler = Callable[..., Any]
AsyncHandler = Callable[..., Awaitable[Any]]


ReferenceType = WeakMethod | ref
SyncReference = WeakMethod[Handler] | ref[Handler]
AsyncReference = WeakMethod[AsyncHandler] | ref[AsyncHandler]

# NOTE: Not going to use this for now, moving to an event system with only a single handler so this is unnecessary for now
# Might try to reintroduce this or something like this later, will keep it for reference.


class HandlerStorage[T: AsyncReference | SyncReference, T2: Handler | AsyncHandler](set):  # pragma: no cover
    """A set of event handlers (by reference) with utility methods."""

    def add_handler(self, entry: T) -> None:
        """Add a reference to a handler if not already present."""
        if entry not in self:
            self.add(entry)

    def remove_by_ref(self, weak_ref: T) -> bool:
        """Remove a handler by its weak reference or reference. Returns True if found and removed."""
        if weak_ref in self:
            self.remove(weak_ref)
            return True
        return False

    def remove_entry(self, handler_name: str) -> bool:
        """Find and remove a handler entry by its name. Returns True if found and removed."""
        for weak_ref in self:
            handler: T2 | None = weak_ref()
            if handler is not None and handler.__name__ == handler_name:
                self.remove(weak_ref)
                return True
        return False

    def clear_all(self) -> None:
        """Remove all registered handler entries."""
        self.clear()


AsyncStorage = HandlerStorage[AsyncReference, AsyncHandler]
SyncStorage = HandlerStorage[SyncReference, Handler]
