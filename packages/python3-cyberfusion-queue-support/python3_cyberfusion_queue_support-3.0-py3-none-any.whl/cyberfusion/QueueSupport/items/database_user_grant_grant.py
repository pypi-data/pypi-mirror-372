"""Item."""

import logging
from typing import List, Optional

from cyberfusion.DatabaseSupport.database_user_grants import DatabaseUserGrant
from cyberfusion.DatabaseSupport.database_users import DatabaseUser
from cyberfusion.DatabaseSupport.servers import Server
from cyberfusion.DatabaseSupport.tables import Table

from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import DatabaseUserGrantGrantItemGrantOutcome

from cyberfusion.DatabaseSupport.databases import Database
from cyberfusion.DatabaseSupport import DatabaseSupport

logger = logging.getLogger(__name__)


class DatabaseUserGrantGrantItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        server_software_name: str,
        database_name: str,
        database_user_name: str,
        database_user_host: Optional[str] = None,
        privilege_names: List[str],
        table_name: Optional[str],
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.server_software_name = server_software_name
        self.database_name = database_name
        self.database_user_name = database_user_name
        self.database_user_host = database_user_host
        self.privilege_names = privilege_names
        self.table_name = table_name
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        self._database = Database(
            support=DatabaseSupport(server_software_names=[self.server_software_name]),
            name=self.database_name,
            server_software_name=self.server_software_name,
        )

        self._database_user = DatabaseUser(
            server=Server(
                support=DatabaseSupport(
                    server_software_names=[self.server_software_name]
                )
            ),
            name=self.database_user_name,
            server_software_name=self.server_software_name,
            host=self.database_user_host,
        )

        if self.table_name:
            self._table = Table(
                database=self._database,
                name=self.table_name,
            )
        else:
            self._table = None

        self.database_user_grant = DatabaseUserGrant(
            database=self._database,
            database_user=self._database_user,
            privilege_names=self.privilege_names,
            table=self._table,
        )

    @property
    def outcomes(self) -> List[DatabaseUserGrantGrantItemGrantOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if not self.database_user_grant.exists:
            outcomes.append(
                DatabaseUserGrantGrantItemGrantOutcome(
                    database_user_grant=self.database_user_grant
                )
            )

        return outcomes

    def fulfill(self) -> List[DatabaseUserGrantGrantItemGrantOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            outcome.database_user_grant.grant()

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserGrantGrantItem):
            return False

        return (
            other.server_software_name == self.server_software_name
            and other.database_user_name == self.database_user_name
            and other.database_user_host == self.database_user_host
            and other.database_name == self.database_name
            and other.privilege_names == self.privilege_names
            and other.table_name == self.table_name
        )
