"""Indicator module.

This module contains the Indicator class, which is used to represent an indicator of a component.
"""

__all__ = ["HealthIndicator", "HealthIndicatorProvider"]

from abc import ABC, abstractmethod

from .health import Health


class HealthIndicator(ABC):
    """An abstract health indicator."""

    __slots__ = ()

    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the indicator."""

    @abstractmethod
    async def get_health(self) -> Health:
        """Returns the health information."""


class HealthIndicatorProvider(ABC):
    """A provider of health indicators."""

    __slots__ = ()

    @abstractmethod
    def get_health_indicator(self) -> HealthIndicator:
        """Returns the health indicator."""
