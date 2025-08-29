"""Tests for the new event bus system."""

import gc
import weakref
import pytest

from bear_utils.events.event_bus import EventBus
from bear_utils.events.async_event_bus import AsyncEventBus
from bear_utils.events.event_models import Event


@pytest.fixture
def sync_bus():
    """Clean sync event bus for testing."""
    return EventBus()


@pytest.fixture
def async_bus():
    """Clean async event bus for testing."""
    return AsyncEventBus()


class TestSyncEventBus:
    """Test sync event bus basic functionality."""

    def test_fire_simple_handler(self, sync_bus):
        """Test fire with simple handler and kwargs."""
        result_holder = {"value": ""}

        def simple_handler(damage: int, source: str = "unknown"):
            result_holder["value"] = f"{damage} damage from {source}"

        sync_bus.register("player_damage", simple_handler)
        sync_bus.fire("player_damage", damage=50, source="enemy")

        assert result_holder["value"] == "50 damage from enemy"

    def test_fire_with_callback(self, sync_bus):
        """Test fire with callback receiving handler result."""
        callback_result = {"value": ""}

        def handler(damage: int) -> str:
            return f"Dealt {damage} damage"

        def callback(result: str):
            callback_result["value"] = result

        sync_bus.register("attack", handler)
        sync_bus.fire("attack", damage=25, callback=callback)

        assert callback_result["value"] == "Dealt 25 damage"

    def test_fire_no_handler_silent(self, sync_bus):
        """Test fire with no handler fails silently."""
        sync_bus.fire("nonexistent_event", data="test")

    def test_emit_simple_event(self, sync_bus):
        """Test emit creating simple event."""

        def handler(event: Event) -> Event:
            return event.done(result={"processed": True}, msg="Processing complete")

        sync_bus.register("process", handler)
        result = sync_bus.emit("process", user_id=123)

        assert isinstance(result, Event)
        assert result.msg == "Processing complete"

    def test_emit_no_handler_error(self, sync_bus):
        """Test emit with no handler returns error event."""
        result = sync_bus.emit("nonexistent", data="test")

        assert isinstance(result, Event)
        assert not result.success

    def test_register_replaces_handler(self, sync_bus):
        """Test registering same event name replaces handler."""
        result_holder = {"count": 0}

        def handler1():
            result_holder["count"] += 1

        def handler2():
            result_holder["count"] += 10

        sync_bus.register("test", handler1)
        sync_bus.fire("test")
        assert result_holder["count"] == 1

        sync_bus.register("test", handler2)  # Replace
        sync_bus.fire("test")
        assert result_holder["count"] == 11  # 1 + 10, not 1 + 1 + 10


class TestAsyncEventBus:
    """Test async event bus basic functionality."""

    @pytest.mark.asyncio
    async def test_fire_simple_async_handler(self, async_bus):
        """Test fire with async handler."""
        result_holder = {"value": ""}

        async def async_handler(message: str):
            result_holder["value"] = f"Processed: {message}"

        async_bus.register("notify", async_handler)
        await async_bus.fire("notify", message="hello")

        assert result_holder["value"] == "Processed: hello"

    @pytest.mark.asyncio
    async def test_fire_with_async_callback(self, async_bus):
        """Test fire with async callback."""
        callback_result = {"value": ""}

        async def handler(value: int) -> int:
            return value * 2

        async def async_callback(result: int):
            callback_result["value"] = f"Result: {result}"

        async_bus.register("double", handler)
        await async_bus.fire("double", value=21, callback=async_callback)

        assert callback_result["value"] == "Result: 42"

    @pytest.mark.asyncio
    async def test_fire_with_sync_callback(self, async_bus):
        """Test fire with sync callback (mixed)."""
        callback_result = {"value": ""}

        async def handler(value: str) -> str:
            return value.upper()

        def sync_callback(result: str):
            callback_result["value"] = f"Got: {result}"

        async_bus.register("uppercase", handler)
        await async_bus.fire("uppercase", value="hello", callback=sync_callback)

        assert callback_result["value"] == "Got: HELLO"

    @pytest.mark.asyncio
    async def test_emit_async_event(self, async_bus):
        """Test emit with async handler."""

        async def handler(event: Event) -> Event:
            return event.done(result={"async": True}, msg="Async processing complete")

        async_bus.register("async_process", handler)
        result = await async_bus.emit("async_process", task_id=456)

        assert isinstance(result, Event)
        assert result.msg == "Async processing complete"


class TestEventBusCommon:
    """Test common behavior across both bus types."""

    def test_unregister(self, sync_bus):
        """Test unregistering events."""

        def handler():
            pass

        sync_bus.register("test", handler)
        assert sync_bus.unregister("test") is True
        assert sync_bus.unregister("nonexistent") is False

    def test_clear_all(self, sync_bus):
        """Test clearing all handlers."""

        def handler():
            pass

        sync_bus.register("test1", handler)
        sync_bus.register("test2", handler)

        sync_bus.clear()

        # Should not call handlers after clear
        sync_bus.fire("test1")
        sync_bus.fire("test2")


class TestAdvancedEventBus:
    """Test advanced functionality and edge cases."""

    def test_weak_ref_function_cleanup(self, sync_bus):
        """Test that function handlers are cleaned up when garbage collected."""
        call_count = {"count": 0}

        def create_handler():
            def handler(value: int):
                call_count["count"] += value

            return handler

        # Register handler and get weak reference to it
        handler = create_handler()
        handler_ref = weakref.ref(handler)
        sync_bus.register("test", handler)

        # Handler should work
        sync_bus.fire("test", value=1)
        assert call_count["count"] == 1

        # Delete handler and force garbage collection
        del handler
        gc.collect()

        # Handler should be gone
        assert handler_ref() is None

        # Event should not call anything (no error, but no effect)
        sync_bus.fire("test", value=10)
        assert call_count["count"] == 1  # Still 1, not 11

    def test_weak_ref_method_cleanup(self, sync_bus):
        """Test that method handlers are cleaned up when object is deleted."""
        call_count = {"count": 0}

        class TestClass:
            def handler_method(self, value: int):
                call_count["count"] += value

        # Create object and register method
        obj = TestClass()
        obj_ref = weakref.ref(obj)
        sync_bus.register("method_test", obj.handler_method)

        # Method should work
        sync_bus.fire("method_test", value=5)
        assert call_count["count"] == 5

        # Delete object and force cleanup
        del obj
        gc.collect()

        # Object should be gone
        assert obj_ref() is None

        # Method call should do nothing
        sync_bus.fire("method_test", value=10)
        assert call_count["count"] == 5  # Still 5, not 15

    def test_handler_exceptions_suppressed(self, sync_bus):
        """Test that handler exceptions are suppressed gracefully."""
        success_count = {"count": 0}

        def failing_handler(value: int):
            if value > 10:
                raise ValueError("Value too high!")
            success_count["count"] += value

        sync_bus.register("risky", failing_handler)

        # Should work normally
        sync_bus.fire("risky", value=5)
        assert success_count["count"] == 5

        # Should suppress exception and continue
        sync_bus.fire("risky", value=20)  # This will throw but be suppressed
        assert success_count["count"] == 5  # No change

        # Should work again
        sync_bus.fire("risky", value=3)
        assert success_count["count"] == 8

    def test_emit_handler_exceptions_in_event(self, sync_bus):
        """Test that emit handles exceptions and modifies event accordingly."""

        def failing_handler(event: Event) -> Event:
            raise RuntimeError("Handler crashed!")

        sync_bus.register("crash_test", failing_handler)
        result = sync_bus.emit("crash_test", data="test")

        # Event should still be returned (exception suppressed)
        assert isinstance(result, Event)
        # The specific behavior depends on your implementation

    def test_complex_typed_event(self, sync_bus: EventBus):
        """Test complex event with typed input and output."""
        from bear_utils.events._inputs import ExampleInput
        from bear_utils.events._results import ExampleResult

        class UserInput(ExampleInput):
            user_id: int
            action: str

        class ProcessResult(ExampleResult):
            success: bool = False
            message: str = ""

        class UserActionEvent(Event[UserInput, ProcessResult]):
            pass

        def process_user_action(event: UserActionEvent) -> UserActionEvent:
            if event.input_data and event.input_data.action == "login":
                result = ProcessResult(success=True, message="Login successful")
                return event.done(result=result, msg="User action processed")

            result = ProcessResult(success=False, message="Unknown action")
            return event.done(result=result, msg="Action not recognized")

        sync_bus.register("user_action", process_user_action)

        # Test successful case
        input_data = UserInput(user_id=123, action="login")
        event = UserActionEvent(name="user_action", input_data=input_data)
        result: UserActionEvent = sync_bus.emit("user_action", event_model=event)

        assert isinstance(result, UserActionEvent)
        assert result.results is not None
        assert result.results.success is True
        assert result.results.message == "Login successful"
        assert result.msg == "User action processed"

        # Test failure case
        input_data2 = UserInput(user_id=456, action="invalid")
        event2 = UserActionEvent(name="user_action", input_data=input_data2)
        result2: UserActionEvent = sync_bus.emit("user_action", event_model=event2)

        assert isinstance(result2, UserActionEvent)
        assert result2.results is not None
        assert result2.results.success is False
        assert result2.results.message == "Unknown action"
