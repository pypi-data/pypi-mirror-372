"""Item."""

import logging
import os
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import PathIsSymlinkError
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import UnlinkItemUnlinkOutcome

logger = logging.getLogger(__name__)


class UnlinkItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        path: str,
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

    @property
    def outcomes(self) -> List[UnlinkItemUnlinkOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if os.path.exists(self.path):
            outcomes.append(
                UnlinkItemUnlinkOutcome(
                    path=self.path,
                )
            )

        return outcomes

    def fulfill(self) -> List[UnlinkItemUnlinkOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            os.unlink(outcome.path)

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, UnlinkItem):
            return False

        return other.path == self.path
