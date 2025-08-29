type VersionTuple = tuple[int, int, int]
__version__: str
"""The version of the package."""
__commit_id__: str
"""The git commit ID of the current version."""
__version_tuple__: VersionTuple
"""The version of the package as a tuple."""

__all__ = [
    "__commit_id__",
    "__version__",
    "__version_tuple__",
]
