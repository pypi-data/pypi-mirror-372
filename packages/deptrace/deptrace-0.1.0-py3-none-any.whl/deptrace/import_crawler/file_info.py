from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class FileInfo:
    """Information about a Python module."""

    full_path: Path

    @property
    def file_name(self) -> str:
        """The module's file name without path."""
        return self.full_path.name

    @property
    def dir_name(self) -> Path:
        """The directory containing this module."""
        return self.full_path.parent

    def __str__(self) -> str:
        return self.file_name

    def __repr__(self) -> str:
        return f"FileInfo(full_path={self.full_path})"