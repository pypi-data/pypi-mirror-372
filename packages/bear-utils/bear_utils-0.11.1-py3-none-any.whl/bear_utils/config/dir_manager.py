"""Directory Manager Module for Bear Utils."""

from functools import cached_property
from pathlib import Path
import shutil
import tempfile
from typing import ClassVar


class DirectoryManager:
    """A class to manage application directories."""

    _base_path: ClassVar[Path] = Path.home() / ".config"

    @classmethod
    def default_name(cls, name: str) -> str:
        """Set the default name for the base directory or return the current name."""
        if name:
            cls._base_path = cls._base_path / name
        return name

    def register_directory(self, name: str, path: Path) -> None:
        """Register a custom directory with a specific name."""
        self.dirs[name] = path

    def __getattr__(self, item: str) -> Path:
        """Get a registered directory by name."""
        if item in self.dirs:
            return self.dirs[item]
        raise AttributeError(f"'DirectoryManager' object has no attribute '{item}'")

    def __init__(self, name: str) -> None:
        """Initialize the DirectoryManager with a specific name."""
        self.dirs: dict[str, Path] = {}
        self.name: str = name
        self.default_name(name)

    def clear_temp(self) -> None:
        """Clear the temporary directory."""
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)

    @property
    def config(self) -> Path:
        """Get the path to the base configuration directory."""
        if not self._base_path.exists():
            self._base_path.mkdir(parents=True, exist_ok=True)
        return self._base_path

    @cached_property
    def settings_path(self) -> Path:
        """Get the path to the settings directory."""
        if not (self._base_path / "settings").exists():
            self.settings.mkdir(parents=True, exist_ok=True)
        return self._base_path / "settings"

    @property
    def temp_path(self) -> Path:
        """Get the path to the temporary directory."""
        if not self.name:
            raise ValueError("Name must be set to get the temporary path.")
        return Path(tempfile.gettempdir()) / self.name

    @cached_property
    def cache_path(self) -> Path:
        """Get the path to the cache directory."""
        if not (path := Path.home() / ".cache" / self.name).exists():
            path.mkdir(parents=True, exist_ok=True)
        return Path.home() / ".cache" / self.name


def get_config_path(name: str) -> Path:
    """Get the base path for bear_utils."""
    return DirectoryManager(name).config


def get_settings_path(name: str) -> Path:
    """Get the path to the settings directory."""
    return DirectoryManager(name).settings_path


def get_temp_path(name: str) -> Path:
    """Get the path to the temporary directory."""
    return DirectoryManager(name).temp_path


def clear_temp_directory(name: str) -> None:
    """Clear the temporary directory."""
    DirectoryManager(name).clear_temp()


__all__ = [
    "DirectoryManager",
    "clear_temp_directory",
    "get_config_path",
    "get_settings_path",
    "get_temp_path",
]
