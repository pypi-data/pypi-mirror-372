"""Item."""

import grp
import logging
import os
import pwd
from grp import getgrgid
from pwd import getpwuid
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import PathIsSymlinkError
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    ChownItemGroupChangeOutcome,
    ChownItemOwnerChangeOutcome,
)

logger = logging.getLogger(__name__)


def get_uid(username: str) -> int:
    """Get UID by username."""
    return pwd.getpwnam(username).pw_uid


def get_gid(group_name: str) -> int:
    """Get GID by group name."""
    return grp.getgrnam(group_name).gr_gid


class ChownItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        path: str,
        owner_name: str,
        group_name: str,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.path = path
        self.owner_name = owner_name
        self.group_name = group_name
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        if os.path.islink(self.path):
            raise PathIsSymlinkError(self.path)

    @property
    def outcomes(
        self,
    ) -> List[ChownItemOwnerChangeOutcome | ChownItemGroupChangeOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if not os.path.exists(self.path):
            outcomes.extend(
                [
                    ChownItemOwnerChangeOutcome(
                        path=self.path,
                        old_owner_name=None,
                        new_owner_name=self.owner_name,
                    ),
                    ChownItemGroupChangeOutcome(
                        path=self.path,
                        old_group_name=None,
                        new_group_name=self.group_name,
                    ),
                ]
            )
        else:
            try:
                old_owner_name = getpwuid(os.stat(self.path).st_uid).pw_name
            except KeyError:
                old_owner_name = "(no user with UID exists)"

            try:
                old_group_name = getgrgid(os.stat(self.path).st_gid).gr_name
            except KeyError:
                old_group_name = "(no group with GID exists)"

            owner_name_changed = old_owner_name != self.owner_name
            group_name_changed = old_group_name != self.group_name

            if owner_name_changed:
                outcomes.append(
                    ChownItemOwnerChangeOutcome(
                        path=self.path,
                        old_owner_name=old_owner_name,
                        new_owner_name=self.owner_name,
                    )
                )

            if group_name_changed:
                outcomes.append(
                    ChownItemGroupChangeOutcome(
                        path=self.path,
                        old_group_name=old_group_name,
                        new_group_name=self.group_name,
                    )
                )

        return outcomes

    def fulfill(
        self,
    ) -> List[ChownItemOwnerChangeOutcome | ChownItemGroupChangeOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            if isinstance(outcome, ChownItemOwnerChangeOutcome):
                os.chown(
                    outcome.path,
                    uid=get_uid(outcome.new_owner_name),
                    gid=-1,
                )
            else:
                os.chown(
                    outcome.path,
                    uid=-1,
                    gid=get_gid(outcome.new_group_name),
                )

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, ChownItem):
            return False

        return (
            other.path == self.path
            and other.owner_name == self.owner_name
            and other.group_name == self.group_name
        )
