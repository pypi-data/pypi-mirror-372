"""Item."""

import logging
import subprocess
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import CommandQueueFulfillFailed
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import CommandItemRunOutcome

logger = logging.getLogger(__name__)


class CommandItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        command: List[str],
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.command = command
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

    @property
    def outcomes(self) -> List[CommandItemRunOutcome]:
        """Get outcomes of item."""
        outcomes = []

        outcomes.append(CommandItemRunOutcome(command=self.command))

        return outcomes

    def fulfill(self) -> List[CommandItemRunOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            try:
                output = subprocess.run(
                    outcome.command,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                outcome.stdout = output.stdout
                outcome.stderr = output.stderr
            except subprocess.CalledProcessError as e:
                raise CommandQueueFulfillFailed(
                    self, command=outcome.command, stdout=e.stdout, stderr=e.stderr
                ) from e

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, CommandItem):
            return False

        return other.command == self.command
