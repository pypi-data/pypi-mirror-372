"""Items."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from cyberfusion.QueueSupport.interfaces import ItemInterface

logger = logging.getLogger(__name__)


class _Item(ItemInterface, ABC):
    """Represents base item."""

    @abstractmethod
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
        fail_silently: bool = False,
    ) -> None:  # pragma: no cover
        """Set attributes."""
        self._reference = reference
        self._hide_outcomes = hide_outcomes
        self._fail_silently = fail_silently

    @property
    def hide_outcomes(self) -> bool:
        """Get if outcomes should be hidden."""
        return self._hide_outcomes

    @property
    def fail_silently(self) -> bool:
        """Get if queue process should be stopped on exception."""
        return self._fail_silently

    @property
    def reference(self) -> Optional[str]:
        """Get free-form reference, for users' own administrations."""
        return self._reference
