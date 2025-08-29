"""A module for Bear Utils, providing various utilities and tools."""

from bear_utils.cache import BaseCacheFactory, ModifiedCache
from bear_utils.config.settings_manager import SettingsManager, get_settings_manager
from bear_utils.constants import DEVNULL, STDERR, STDOUT, ExitCode, HTTPStatusCode
from bear_utils.database import DatabaseManager, PostgresDB, SingletonDB
from bear_utils.events import AsyncEventBus, Event, EventBus, ExampleInput, ExampleResult, HandlerNotFoundError
from bear_utils.extras.responses import FunctionResponse
from bear_utils.files.file_handlers.file_handler_factory import FileHandlerFactory
from bear_utils.logger_manager import BaseLogger, BufferLogger, ConsoleLogger, FileLogger, LoggingClient, LoggingServer
from bear_utils.logger_manager._constants import VERBOSE, VERBOSE_CONSOLE_FORMAT
from bear_utils.time import DATE_FORMAT, DATE_TIME_FORMAT, EpochTimestamp, TimeConverter, TimeTools

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DEVNULL",
    "STDERR",
    "STDOUT",
    "VERBOSE",
    "VERBOSE_CONSOLE_FORMAT",
    "AsyncEventBus",
    "BaseCacheFactory",
    "BaseLogger",
    "BufferLogger",
    "ConsoleLogger",
    "DatabaseManager",
    "EpochTimestamp",
    "Event",
    "EventBus",
    "ExampleInput",
    "ExampleResult",
    "ExitCode",
    "FileHandlerFactory",
    "FileLogger",
    "FunctionResponse",
    "HTTPStatusCode",
    "HandlerNotFoundError",
    "LoggingClient",
    "LoggingServer",
    "ModifiedCache",
    "PostgresDB",
    "SettingsManager",
    "SingletonDB",
    "TimeConverter",
    "TimeTools",
    "get_settings_manager",
]
