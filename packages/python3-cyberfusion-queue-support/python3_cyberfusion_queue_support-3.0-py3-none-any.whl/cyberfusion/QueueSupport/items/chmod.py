"""Item."""

import logging
import os
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import PathIsSymlinkError
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import ChmodItemModeChangeOutcome
from cyberfusion.QueueSupport.utilities import get_decimal_permissions

logger = logging.getLogger(__name__)


class ChmodItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        path: str,
        mode: int,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.path = path
        self.mode = mode
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        if os.path.islink(self.path):
            raise PathIsSymlinkError(self.path)

    @property
    def outcomes(self) -> List[ChmodItemModeChangeOutcome]:
        """Get outcomes of item."""
        outcomes = []

        if not os.path.exists(self.path):
            outcomes.append(
                ChmodItemModeChangeOutcome(
                    path=self.path, old_mode=None, new_mode=self.mode
                )
            )
        else:
            old_mode = get_decimal_permissions(self.path)
            mode_changed = old_mode != self.mode

            if mode_changed:
                outcomes.append(
                    ChmodItemModeChangeOutcome(
                        path=self.path, old_mode=old_mode, new_mode=self.mode
                    )
                )

        return outcomes

    def fulfill(self) -> List[ChmodItemModeChangeOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            os.chmod(outcome.path, outcome.new_mode)

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, ChmodItem):
            return False

        return other.path == self.path and other.mode == self.mode
