"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    SystemdUnitReloadItemReloadOutcome,
)
from cyberfusion.SystemdSupport.units import Unit

logger = logging.getLogger(__name__)


class SystemdUnitReloadItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        name: str,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.name = name
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        self.unit = Unit(self.name)

    @property
    def outcomes(self) -> List[SystemdUnitReloadItemReloadOutcome]:
        """Get outcomes of item."""
        outcomes = []

        outcomes.append(SystemdUnitReloadItemReloadOutcome(unit=self.unit))

        return outcomes

    def fulfill(self) -> List[SystemdUnitReloadItemReloadOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            outcome.unit.reload()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitReloadItem):
            return False

        return other.name == self.name
