"""Tests for modern prompt_helpers module."""

from unittest.mock import patch

import pytest
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from bear_utils.cli.prompt_helpers import PromptHelpers, ask_question, ask_yes_no, restricted_prompt
from bear_utils.constants._exceptions import UserCancelledError


class TestAskQuestion:
    """Test the ask_question function with different types."""

    @patch.object(Prompt, 'ask')
    def test_ask_question_string(self, mock_prompt):
        """Test asking for string input."""
        mock_prompt.return_value = "hello world"
        result = ask_question("Enter text:", str, default="default")
        assert result == "hello world"
        mock_prompt.assert_called_once_with("Enter text:", default="default")

    @patch.object(IntPrompt, 'ask')  
    def test_ask_question_int(self, mock_prompt):
        """Test asking for integer input."""
        mock_prompt.return_value = 42
        result = ask_question("Enter number:", int, default=10)
        assert result == 42
        mock_prompt.assert_called_once_with("Enter number:", default=10)

    @patch.object(FloatPrompt, 'ask')
    def test_ask_question_float(self, mock_prompt):
        """Test asking for float input."""  
        mock_prompt.return_value = 3.14
        result = ask_question("Enter decimal:", float, default=1.0)
        assert result == 3.14
        mock_prompt.assert_called_once_with("Enter decimal:", default=1.0)

    @patch.object(Confirm, 'ask')
    def test_ask_question_bool(self, mock_prompt):
        """Test asking for boolean input."""
        mock_prompt.return_value = True
        result = ask_question("Continue?", bool, default=False)
        assert result is True
        mock_prompt.assert_called_once_with("Continue?", default=False)

    @patch.object(Prompt, 'ask')
    def test_ask_question_keyboard_interrupt(self, mock_prompt):
        """Test KeyboardInterrupt handling."""
        mock_prompt.side_effect = KeyboardInterrupt()
        with pytest.raises(UserCancelledError):
            ask_question("Enter text:", str)


class TestAskYesNo:
    """Test the ask_yes_no function."""

    @patch.object(Confirm, 'ask')
    def test_ask_yes_no_true(self, mock_confirm):
        """Test yes/no returning True."""
        mock_confirm.return_value = True
        result = ask_yes_no("Continue?", default=False)
        assert result is True
        mock_confirm.assert_called_once_with("Continue?", default=False)

    @patch.object(Confirm, 'ask')  
    def test_ask_yes_no_false(self, mock_confirm):
        """Test yes/no returning False."""
        mock_confirm.return_value = False
        result = ask_yes_no("Continue?", default=True)
        assert result is False
        mock_confirm.assert_called_once_with("Continue?", default=True)

    @patch.object(Confirm, 'ask')
    def test_ask_yes_no_keyboard_interrupt(self, mock_confirm):
        """Test KeyboardInterrupt handling."""
        mock_confirm.side_effect = KeyboardInterrupt()
        with pytest.raises(UserCancelledError):
            ask_yes_no("Continue?")


class TestRestrictedPrompt:
    """Test the restricted_prompt function."""

    @patch.object(Prompt, 'ask')
    def test_restricted_prompt_valid_option(self, mock_prompt):
        """Test selecting a valid option."""
        mock_prompt.return_value = "option1"
        result = restricted_prompt("Choose:", ["option1", "option2"])
        assert result == "option1"
        mock_prompt.assert_called_once_with(
            "Choose:", 
            choices=["option1", "option2", "exit"],
            case_sensitive=False
        )

    @patch.object(Prompt, 'ask')
    def test_restricted_prompt_exit(self, mock_prompt):
        """Test exiting with exit command."""
        mock_prompt.return_value = "exit"
        result = restricted_prompt("Choose:", ["option1", "option2"]) 
        assert result is None
        
    @patch.object(Prompt, 'ask')
    def test_restricted_prompt_custom_exit(self, mock_prompt):
        """Test custom exit command."""
        mock_prompt.return_value = "quit"
        result = restricted_prompt("Choose:", ["option1"], exit_command="quit")
        assert result is None
        mock_prompt.assert_called_once_with(
            "Choose:",
            choices=["option1", "quit"], 
            case_sensitive=False
        )

    @patch.object(Prompt, 'ask')
    def test_restricted_prompt_case_sensitive(self, mock_prompt):
        """Test case sensitive mode."""
        mock_prompt.return_value = "Option1"
        result = restricted_prompt("Choose:", ["Option1"], case_sensitive=True)
        assert result == "Option1"
        mock_prompt.assert_called_once_with(
            "Choose:",
            choices=["Option1", "exit"],
            case_sensitive=True
        )

    @patch.object(Prompt, 'ask')
    def test_restricted_prompt_keyboard_interrupt(self, mock_prompt):
        """Test KeyboardInterrupt handling."""
        mock_prompt.side_effect = KeyboardInterrupt()
        with pytest.raises(UserCancelledError):
            restricted_prompt("Choose:", ["option1"])


class TestPromptHelpersBackwardCompatibility:
    """Test the PromptHelpers class for backward compatibility."""

    @patch('bear_utils.cli.prompt_helpers.ask_question')
    def test_prompt_helpers_ask_question(self, mock_ask):
        """Test backward compatibility wrapper."""
        mock_ask.return_value = "test"
        result = PromptHelpers.ask_question("Question?", str, "default")
        assert result == "test"
        mock_ask.assert_called_once_with("Question?", str, "default")

    @patch('bear_utils.cli.prompt_helpers.ask_yes_no')
    def test_prompt_helpers_ask_yes_no(self, mock_ask_yes_no):
        """Test backward compatibility wrapper."""
        mock_ask_yes_no.return_value = True
        result = PromptHelpers.ask_yes_no("Question?", False)
        assert result is True
        mock_ask_yes_no.assert_called_once_with("Question?", False)

    @patch('bear_utils.cli.prompt_helpers.restricted_prompt')
    def test_prompt_helpers_restricted_prompt(self, mock_restricted):
        """Test backward compatibility wrapper."""
        mock_restricted.return_value = "option1"
        result = PromptHelpers.restricted_prompt("Question?", ["option1"], "quit", True)
        assert result == "option1"
        mock_restricted.assert_called_once_with("Question?", ["option1"], "quit", True)