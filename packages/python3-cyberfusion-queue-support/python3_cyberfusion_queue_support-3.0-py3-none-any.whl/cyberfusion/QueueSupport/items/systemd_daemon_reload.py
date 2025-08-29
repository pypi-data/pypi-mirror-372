"""Item."""

import logging
from typing import List, Optional

from cyberfusion.SystemdSupport.manager import SystemdManager

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    SystemdDaemonReloadItemReloadOutcome,
)

logger = logging.getLogger(__name__)


class SystemdDaemonReloadItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

    @property
    def outcomes(self) -> List[SystemdDaemonReloadItemReloadOutcome]:
        """Get outcomes of item."""
        outcomes = []

        outcomes.append(SystemdDaemonReloadItemReloadOutcome())

        return outcomes

    def fulfill(self) -> List[SystemdDaemonReloadItemReloadOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for _ in outcomes:
            SystemdManager.daemon_reload()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdDaemonReloadItem):
            return False

        return True
