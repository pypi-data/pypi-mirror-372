from pydantic import BaseModel


class ExampleInput(BaseModel):
    """Base class for all input data models for events."""

    model_config = {"arbitrary_types_allowed": True, "frozen": True, "extra": "forbid"}


__all__ = ["ExampleInput"]
