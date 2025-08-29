from pydantic import BaseModel


class ExampleResult(BaseModel):
    """A sample result class on a per handler basis."""

    success: bool = True
    exception: str | None = None

    def fail(self, exception: Exception) -> None:
        """Mark the result as failed with an exception message."""
        self.success = False
        self.exception = str(exception)
