"""Interfaces."""

from abc import ABCMeta, abstractmethod
from typing import List


class OutcomeInterface(metaclass=ABCMeta):
    """Interface for outcomes."""

    @abstractmethod
    def __str__(self) -> str:  # pragma: no cover
        """Get human-readable string."""
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:  # pragma: no cover
        """Get equality based on attributes."""
        pass


class ItemInterface(metaclass=ABCMeta):
    """Interface for items."""

    @property
    @abstractmethod
    def outcomes(self) -> List[OutcomeInterface]:  # pragma: no cover
        """Get outcomes of item."""
        pass

    @abstractmethod
    def fulfill(self) -> List[OutcomeInterface]:  # pragma: no cover
        """Fulfill outcomes."""
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:  # pragma: no cover
        """Get equality based on attributes."""
        pass
