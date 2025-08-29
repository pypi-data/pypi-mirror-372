"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    SystemdUnitStartItemStartOutcome,
)
from cyberfusion.SystemdSupport.units import Unit

logger = logging.getLogger(__name__)


class SystemdUnitStartItem(_Item):
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
    def outcomes(self) -> List[SystemdUnitStartItemStartOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if not self.unit.is_active:
            outcomes.append(SystemdUnitStartItemStartOutcome(unit=self.unit))

        return outcomes

    def fulfill(self) -> List[SystemdUnitStartItemStartOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            outcome.unit.start()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitStartItem):
            return False

        return other.name == self.name
