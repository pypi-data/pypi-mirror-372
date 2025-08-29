"""A set of command-line interface (CLI) utilities for bear_utils."""

from ._args import args_handler, args_parse
from .commands import GitCommand, OPShellCommand, UVShellCommand
from .shell._base_command import BaseShellCommand
from .shell._base_shell import SimpleShellSession, shell_session
from .shell._common import DEFAULT_SHELL

__all__ = [
    "DEFAULT_SHELL",
    "BaseShellCommand",
    "GitCommand",
    "OPShellCommand",
    "SimpleShellSession",
    "UVShellCommand",
    "args_handler",
    "args_parse",
    "shell_session",
]
