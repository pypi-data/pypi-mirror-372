"""Modern prompt helpers using Rich and Typer - because why reinvent the wheel?"""

from typing import Any, overload

from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from bear_utils.constants._exceptions import UserCancelledError
from bear_utils.constants._lazy_typing import OptBool, OptFloat, OptInt, OptStr


@overload
def ask_question(question: str, expected_type: type[bool], default: OptBool = None) -> bool: ...


@overload
def ask_question(question: str, expected_type: type[int], default: OptInt = None) -> int: ...


@overload
def ask_question(question: str, expected_type: type[float], default: OptFloat = None) -> float: ...


@overload
def ask_question(question: str, expected_type: type[str], default: OptStr = None) -> str: ...


def ask_question(question: str, expected_type: type, default: Any = None) -> Any:
    """Ask a question with automatic type validation and conversion."""
    try:
        if expected_type is bool:
            return Confirm.ask(question, default=default)
        if expected_type is int:
            return IntPrompt.ask(question, default=default)
        if expected_type is float:
            return FloatPrompt.ask(question, default=default)
        return Prompt.ask(question, default=default)
    except KeyboardInterrupt:
        raise UserCancelledError("User cancelled input") from None


def ask_yes_no(question: str, default: bool | None = None) -> bool:
    """Ask a yes/no question."""
    try:
        if default is not None:
            return Confirm.ask(question, default=default)
        return Confirm.ask(question)
    except KeyboardInterrupt:
        raise UserCancelledError("User cancelled input") from None


def restricted_prompt(
    question: str, valid_options: list[str], exit_command: str = "exit", case_sensitive: bool = False
) -> str | None:
    """Ask user to choose from a list of options."""
    try:
        choices: list[str] = [*valid_options, exit_command]
        result: str = Prompt.ask(question, choices=choices, case_sensitive=case_sensitive)
        return None if result == exit_command else result
    except KeyboardInterrupt:
        raise UserCancelledError("User cancelled input") from None


# Legacy class for backward compatibility (if anyone imported it)
class PromptHelpers:
    """Backward compatibility wrapper."""

    @staticmethod
    def ask_question(question: str, expected_type: type, default: Any = None) -> Any:
        """Backward compatibility wrapper for ask_question."""
        return ask_question(question, expected_type, default)

    @staticmethod
    def ask_yes_no(question: str, default: bool | None = None) -> bool:
        """Backward compatibility wrapper for ask_yes_no."""
        return ask_yes_no(question, default)

    @staticmethod
    def restricted_prompt(
        question: str,
        valid_options: list[str],
        exit_command: str = "exit",
        case_sensitive: bool = False,
    ) -> str | None:
        """Backward compatibility wrapper for restricted_prompt."""
        return restricted_prompt(question, valid_options, exit_command, case_sensitive)
