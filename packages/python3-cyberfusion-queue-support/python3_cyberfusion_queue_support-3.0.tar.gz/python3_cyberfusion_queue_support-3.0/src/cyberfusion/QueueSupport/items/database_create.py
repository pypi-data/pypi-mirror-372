"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import DatabaseCreateItemCreateOutcome

from cyberfusion.DatabaseSupport.databases import Database
from cyberfusion.DatabaseSupport import DatabaseSupport

logger = logging.getLogger(__name__)


class DatabaseCreateItem(_Item):
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
    def outcomes(self) -> List[DatabaseCreateItemCreateOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if not self.database.exists:
            outcomes.append(DatabaseCreateItemCreateOutcome(database=self.database))

        return outcomes

    def fulfill(self) -> List[DatabaseCreateItemCreateOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            outcome.database.create()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseCreateItem):
            return False

        return (
            other.server_software_name == self.server_software_name
            and other.name == self.name
        )
