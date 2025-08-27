"""Exceptions."""

from dataclasses import dataclass
from typing import List

from cyberfusion.QueueSupport.items import _Item


class ItemError(Exception):
    """Issues with item."""

    pass


@dataclass
class PathIsSymlinkError(ItemError):
    """Path is symlink."""

    path: str


@dataclass
class CommandQueueFulfillFailed(Exception):
    """Error occurred while fulfilling queue, with command item."""

    item: _Item
    command: List[str]
    stdout: str
    stderr: str

    def __str__(self) -> str:
        """Get string representation."""
        return f"Command:\n\n{self.command}\n\nStdout:\n\n{self.stdout}\n\nStderr:\n\n{self.stderr}"
