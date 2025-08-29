"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    SystemdTmpFilesCreateItemCreateOutcome,
)
from cyberfusion.SystemdSupport.tmp_files import TmpFileConfigurationFile

logger = logging.getLogger(__name__)


class SystemdTmpFilesCreateItem(_Item):
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

    @property
    def outcomes(self) -> List[SystemdTmpFilesCreateItemCreateOutcome]:
        """Get outcomes of item."""
        outcomes = []

        outcomes.append(SystemdTmpFilesCreateItemCreateOutcome(path=self.path))

        return outcomes

    def fulfill(self) -> List[SystemdTmpFilesCreateItemCreateOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            TmpFileConfigurationFile(outcome.path).create()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdTmpFilesCreateItem):
            return False

        return other.path == self.path
