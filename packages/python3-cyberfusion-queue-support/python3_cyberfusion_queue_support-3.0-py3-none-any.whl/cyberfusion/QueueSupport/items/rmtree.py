"""Item."""

import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import PathIsSymlinkError
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import RmTreeItemRemoveOutcome

logger = logging.getLogger(__name__)


class RmTreeItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        path: str,
        min_depth: int,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.path = path
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        if os.path.islink(self.path):
            raise PathIsSymlinkError(self.path)

        if not os.path.isabs(path):
            raise ValueError("Path must be absolute")

        if min_depth < 1:
            raise ValueError("min_depth must be greater than 0")

        depth = len(Path(os.path.normpath(path)).parents)

        if depth < min_depth:
            raise ValueError(f"Path doesn't have enough depth: {depth} < {min_depth}")

    @property
    def outcomes(self) -> List[RmTreeItemRemoveOutcome]:
        """Get outcomes of calling self.fulfill."""
        outcomes = []

        if os.path.exists(self.path):
            outcomes.append(
                RmTreeItemRemoveOutcome(
                    path=self.path,
                )
            )

        return outcomes

    def fulfill(self) -> List[RmTreeItemRemoveOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            shutil.rmtree(outcome.path)

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, RmTreeItem):
            return False

        return other.path == self.path
