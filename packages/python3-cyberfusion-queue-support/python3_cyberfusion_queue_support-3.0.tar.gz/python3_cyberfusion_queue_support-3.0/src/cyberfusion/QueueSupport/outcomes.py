"""Outcomes."""

from typing import List, Optional

from cyberfusion.DatabaseSupport.database_user_grants import DatabaseUserGrant
from cyberfusion.DatabaseSupport.database_users import DatabaseUser
from cyberfusion.DatabaseSupport.databases import Database

from cyberfusion.QueueSupport.interfaces import OutcomeInterface
from cyberfusion.SystemdSupport.units import Unit

from cyberfusion.QueueSupport.sentinels import UNKNOWN


class CopyItemCopyOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(
        self,
        *,
        source: str,
        destination: str,
        changed_lines: Optional[list[str]] = None,
    ) -> None:
        """Set attributes."""
        self.source = source
        self.destination = destination
        self.changed_lines = changed_lines

    def __str__(self) -> str:
        """Get human-readable string."""
        if self.changed_lines:
            changed_lines = "\nChanged lines:\n" + "\n".join(self.changed_lines)
        else:
            changed_lines = ""

        return f"Copy {self.source} to {self.destination}.{changed_lines}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, CopyItemCopyOutcome):
            return False

        return (
            other.source == self.source
            and other.destination == self.destination
            and other.changed_lines == self.changed_lines
        )


class MoveItemMoveOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, source: str, destination: str) -> None:
        """Set attributes."""
        self.source = source
        self.destination = destination

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Move {self.source} to {self.destination}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, MoveItemMoveOutcome):
            return False

        return other.source == self.source and other.destination == self.destination


class MkdirItemCreateOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, path: str) -> None:
        """Set attributes."""
        self.path = path

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Create {self.path}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, MkdirItemCreateOutcome):
            return False

        return other.path == self.path


class SystemdTmpFilesCreateItemCreateOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, path: str) -> None:
        """Set attributes."""
        self.path = path

    def __str__(self) -> str:
        """Get human-readable string."""
        return (
            f"Create tmp files according to tmp files configuration file at {self.path}"
        )

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdTmpFilesCreateItemCreateOutcome):
            return False

        return other.path == self.path


class UnlinkItemUnlinkOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, path: str) -> None:
        """Set attributes."""
        self.path = path

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Unlink {self.path}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, UnlinkItemUnlinkOutcome):
            return False

        return other.path == self.path


class RmTreeItemRemoveOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, path: str) -> None:
        """Set attributes."""
        self.path = path

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Remove directory tree {self.path}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, RmTreeItemRemoveOutcome):
            return False

        return other.path == self.path


class CommandItemRunOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(
        self,
        *,
        command: List[str],
        stdout: str | UNKNOWN = UNKNOWN,
        stderr: str | UNKNOWN = UNKNOWN,
    ) -> None:
        """Set attributes."""
        self.command = command
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Run {self.command}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, CommandItemRunOutcome):
            return False

        return (
            other.command == self.command
            and other.stdout == self.stdout
            and other.stderr == self.stderr
        )


class ChmodItemModeChangeOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, path: str, old_mode: Optional[int], new_mode: int) -> None:
        """Set attributes."""
        self.path = path
        self.old_mode = old_mode
        self.new_mode = new_mode

    def __str__(self) -> str:
        """Get human-readable string."""
        old_mode: Optional[str]

        if self.old_mode is not None:
            old_mode = oct(self.old_mode)
        else:
            old_mode = None

        return f"Change mode of {self.path} from {old_mode} to {oct(self.new_mode)}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, ChmodItemModeChangeOutcome):
            return False

        return (
            other.path == self.path
            and other.old_mode == self.old_mode
            and other.new_mode == self.new_mode
        )


class ChownItemOwnerChangeOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(
        self, *, path: str, old_owner_name: Optional[str], new_owner_name: str
    ) -> None:
        """Set attributes."""
        self.path = path
        self.old_owner_name = old_owner_name
        self.new_owner_name = new_owner_name

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Change owner of {self.path} from {self.old_owner_name} to {self.new_owner_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, ChownItemOwnerChangeOutcome):
            return False

        return (
            other.path == self.path
            and other.old_owner_name == self.old_owner_name
            and other.new_owner_name == self.new_owner_name
        )


class ChownItemGroupChangeOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(
        self, *, path: str, old_group_name: Optional[str], new_group_name: str
    ) -> None:
        """Set attributes."""
        self.path = path
        self.old_group_name = old_group_name
        self.new_group_name = new_group_name

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Change group of {self.path} from {self.old_group_name} to {self.new_group_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, ChownItemGroupChangeOutcome):
            return False

        return (
            other.path == self.path
            and other.old_group_name == self.old_group_name
            and other.new_group_name == self.new_group_name
        )


class SystemdUnitEnableItemEnableOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Enable {self.unit.name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitEnableItemEnableOutcome):
            return False

        return other.unit.name == self.unit.name


class SystemdDaemonReloadItemReloadOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(
        self,
    ) -> None:
        """Set attributes."""
        pass

    def __str__(self) -> str:
        """Get human-readable string."""
        return "Reload daemon"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdDaemonReloadItemReloadOutcome):
            return False

        return True


class SystemdUnitStartItemStartOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Start {self.unit.name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitStartItemStartOutcome):
            return False

        return other.unit.name == self.unit.name


class SystemdUnitDisableItemDisableOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Disable {self.unit.name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitDisableItemDisableOutcome):
            return False

        return other.unit.name == self.unit.name


class SystemdUnitRestartItemRestartOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Restart {self.unit.name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitRestartItemRestartOutcome):
            return False

        return other.unit.name == self.unit.name


class SystemdUnitReloadItemReloadOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Reload {self.unit.name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitReloadItemReloadOutcome):
            return False

        return other.unit.name == self.unit.name


class SystemdUnitStopItemStopOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, unit: Unit) -> None:
        """Set attributes."""
        self.unit = unit

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Stop {self.unit.name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitStopItemStopOutcome):
            return False

        return other.unit.name == self.unit.name


class DatabaseCreateItemCreateOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database: Database) -> None:
        """Set attributes."""
        self.database = database

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Create {self.database.name} in {self.database.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseCreateItemCreateOutcome):
            return False

        return (
            other.database.server_software_name == self.database.server_software_name
            and other.database.name == self.database.name
        )


class DatabaseDropItemDropOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database: Database) -> None:
        """Set attributes."""
        self.database = database

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Drop {self.database.name} in {self.database.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseDropItemDropOutcome):
            return False

        return (
            other.database.server_software_name == self.database.server_software_name
            and other.database.name == self.database.name
        )


class DatabaseUserEnsureStateItemCreateOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database_user: DatabaseUser) -> None:
        """Set attributes."""
        self.database_user = database_user

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Create {self.database_user.name} in {self.database_user.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserEnsureStateItemCreateOutcome):
            return False

        return (
            other.database_user.server_software_name
            == self.database_user.server_software_name
            and other.database_user.name == self.database_user.name
            and other.database_user.password == self.database_user.password
            and other.database_user.host == self.database_user.host
        )


class DatabaseUserEnsureStateItemEditPasswordOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database_user: DatabaseUser) -> None:
        """Set attributes."""
        self.database_user = database_user

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Edit password of {self.database_user.name} in {self.database_user.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserEnsureStateItemEditPasswordOutcome):
            return False

        print(
            other.database_user.server_software_name,
            other.database_user.name,
            other.database_user.password,
            other.database_user.host,
        )
        print(
            self.database_user.server_software_name,
            self.database_user.name,
            self.database_user.password,
            self.database_user.host,
        )

        return (
            other.database_user.server_software_name
            == self.database_user.server_software_name
            and other.database_user.name == self.database_user.name
            and other.database_user.password == self.database_user.password
            and other.database_user.host == self.database_user.host
        )


class DatabaseUserDropItemDropOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database_user: DatabaseUser) -> None:
        """Set attributes."""
        self.database_user = database_user

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Drop {self.database_user.name} in {self.database_user.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserDropItemDropOutcome):
            return False

        return (
            other.database_user.server_software_name
            == self.database_user.server_software_name
            and other.database_user.name == self.database_user.name
            and other.database_user.host == self.database_user.host
        )


class DatabaseUserGrantGrantItemGrantOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database_user_grant: DatabaseUserGrant) -> None:
        """Set attributes."""
        self.database_user_grant = database_user_grant

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Grant {self.database_user_grant.privilege_names} to {self.database_user_grant.table_name} in {self.database_user_grant.database_name} in {self.database_user_grant.database_user.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserGrantGrantItemGrantOutcome):
            return False

        return (
            other.database_user_grant.database_user.server_software_name
            == self.database_user_grant.database_user.server_software_name
            and other.database_user_grant.database_user.name
            == self.database_user_grant.database_user.name
            and other.database_user_grant.database_user.host
            == self.database_user_grant.database_user.host
            and other.database_user_grant.privilege_names
            == self.database_user_grant.privilege_names
            and other.database_user_grant.table_name
            == self.database_user_grant.table_name
        )


class DatabaseUserGrantRevokeItemRevokeOutcome(OutcomeInterface):
    """Represents outcome."""

    def __init__(self, *, database_user_grant: DatabaseUserGrant) -> None:
        """Set attributes."""
        self.database_user_grant = database_user_grant

    def __str__(self) -> str:
        """Get human-readable string."""
        return f"Revoke {self.database_user_grant.privilege_names} to {self.database_user_grant.table_name} in {self.database_user_grant.database_name} in {self.database_user_grant.database_user.server_software_name}"

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, DatabaseUserGrantRevokeItemRevokeOutcome):
            return False

        return (
            other.database_user_grant.database_user.server_software_name
            == self.database_user_grant.database_user.server_software_name
            and other.database_user_grant.database_user.name
            == self.database_user_grant.database_user.name
            and other.database_user_grant.database_user.host
            == self.database_user_grant.database_user.host
            and other.database_user_grant.privilege_names
            == self.database_user_grant.privilege_names
            and other.database_user_grant.table_name
            == self.database_user_grant.table_name
        )
