"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import DatabaseDropItemDropOutcome

from cyberfusion.DatabaseSupport.databases import Database
from cyberfusion.DatabaseSupport import DatabaseSupport

logger = logging.getLogger(__name__)


class DatabaseDropItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        server_software_name: str,
        name: str,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.server_software_name = server_software_name
        self.name = name
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        self.database = Database(
            support=DatabaseSupport(server_software_names=[self.server_software_name]),
            name=self.name,
            server_software_name=self.server_software_name,
        )

    @property
    def outcomes(self) -> List[DatabaseDropItemDropOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if self.database.exists:
            outcomes.append(DatabaseDropItemDropOutcome(database=self.database))

        return outcomes

    def fulfill(self) -> List[DatabaseDropItemDropOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            outcome.database.drop()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseDropItem):
            return False

        return (
            other.server_software_name == self.server_software_name
            and other.name == self.name
        )
