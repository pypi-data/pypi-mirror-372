"""Item."""

import logging
from typing import List, Optional

from cyberfusion.DatabaseSupport.database_users import DatabaseUser
from cyberfusion.DatabaseSupport.servers import Server

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    DatabaseUserEnsureStateItemCreateOutcome,
    DatabaseUserEnsureStateItemEditPasswordOutcome,
)

from cyberfusion.DatabaseSupport import DatabaseSupport

logger = logging.getLogger(__name__)


class DatabaseUserEnsureStateItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        server_software_name: str,
        name: str,
        password: str,
        host: Optional[str] = None,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.server_software_name = server_software_name
        self.name = name
        self._password = password
        self.host = host
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        self.database_user = DatabaseUser(
            server=Server(
                support=DatabaseSupport(
                    server_software_names=[self.server_software_name]
                )
            ),
            name=self.name,
            server_software_name=self.server_software_name,
            password=self._password,
            host=self.host,
        )

    @property
    def outcomes(
        self,
    ) -> List[
        DatabaseUserEnsureStateItemCreateOutcome
        | DatabaseUserEnsureStateItemEditPasswordOutcome
    ]:
        """Get outcomes of item."""
        outcomes = []

        if not self.database_user.exists:
            outcomes.append(
                DatabaseUserEnsureStateItemCreateOutcome(
                    database_user=self.database_user
                )
            )
        elif self.database_user._get_password() != self._password:
            outcomes.append(
                DatabaseUserEnsureStateItemEditPasswordOutcome(
                    database_user=self.database_user
                )
            )

        return outcomes

    def fulfill(self) -> List[DatabaseUserEnsureStateItemCreateOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            if isinstance(outcome, DatabaseUserEnsureStateItemCreateOutcome):
                outcome.database_user.create()
            else:
                outcome.database_user.edit()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserEnsureStateItem):
            return False

        return (
            other.server_software_name == self.server_software_name
            and other.name == self.name
            and other.host == self.host
            and other._password == self._password
        )
