"""Item."""

import difflib
import logging
import os
import shutil
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import PathIsSymlinkError
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import CopyItemCopyOutcome

logger = logging.getLogger(__name__)


class CopyItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        source: str,
        destination: str,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:
        """Set attributes."""
        self.source = source
        self.destination = destination
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

        if os.path.islink(self.source):
            raise PathIsSymlinkError(self.source)

        if os.path.islink(self.destination):
            raise PathIsSymlinkError(self.destination)

    def _get_changed_lines(self) -> Optional[List[str]]:
        """Get differences with destination file.

        Returns None if the changed_lines could not be determined, for example
        if the destination file is encrypted.
        """
        changed_lines = []

        destination_contents = []

        try:
            source_contents = open(self.source).readlines()
        except UnicodeDecodeError:
            return None

        if os.path.isfile(self.destination):
            try:
                destination_contents = open(self.destination).readlines()
            except UnicodeDecodeError:
                return None

        for line in difflib.unified_diff(
            destination_contents,
            source_contents,
            fromfile=self.source,
            tofile=self.destination,
            lineterm="",
            n=0,
        ):
            changed_lines.append(line)

        return changed_lines

    @property
    def outcomes(self) -> List[CopyItemCopyOutcome]:
        """Get outcomes of item."""
        outcomes = []

        changed_lines = self._get_changed_lines()

        if not os.path.exists(self.destination):
            copy = True
        elif changed_lines is None:
            copy = True
        else:
            copy = bool(changed_lines)

        if copy:
            outcomes.append(
                CopyItemCopyOutcome(
                    source=self.source,
                    destination=self.destination,
                    changed_lines=changed_lines,
                )
            )

        return outcomes

    def fulfill(self) -> List[CopyItemCopyOutcome]:
        """Fulfill outcomes."""
        outcomes = self.outcomes

        for outcome in outcomes:
            shutil.copyfile(outcome.source, outcome.destination)

        return outcomes

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, CopyItem):
            return False

        return other.source == self.source and other.destination == self.destination
